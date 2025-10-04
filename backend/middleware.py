# backend/middleware.py

import time
import json
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from .security import SecurityHeaders, SecurityAuditLogger, SecurityConfig

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Güvenlik middleware sınıfı"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Request boyutu kontrolü
        if hasattr(request, 'content_length') and request.content_length:
            if request.content_length > SecurityConfig.MAX_REQUEST_SIZE:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request boyutu çok büyük"}
                )
        
        # Şüpheli User-Agent kontrolü
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "zap"]
        if any(agent in user_agent for agent in suspicious_agents):
            SecurityAuditLogger.log_security_event(
                "suspicious_user_agent",
                None,
                {"user_agent": user_agent},
                request
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Erişim reddedildi"}
            )
        
        # Response'u işle
        response = await call_next(request)
        
        # Güvenlik başlıklarını ekle
        security_headers = SecurityHeaders.get_security_headers()
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # İşlem süresini logla
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Yavaş istekleri logla
        if process_time > 5.0:  # 5 saniyeden uzun
            logger.warning(f"Yavaş istek: {request.method} {request.url} - {process_time:.2f}s")
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """İstek loglama middleware sınıfı"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Hassas endpoint'leri logla
        sensitive_paths = ["/users/login", "/users/register", "/admin"]
        
        if any(path in str(request.url) for path in sensitive_paths):
            SecurityAuditLogger.log_security_event(
                "api_access",
                None,
                {
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": dict(request.query_params)
                },
                request
            )
        
        response = await call_next(request)
        
        # Hata durumlarını logla
        if response.status_code >= 400:
            logger.warning(
                f"HTTP {response.status_code}: {request.method} {request.url}"
            )
        
        return response

# RateLimitMiddleware kaldırıldı - slowapi kullanılıyor

def setup_cors(app):
    """CORS yapılandırması"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=SecurityConfig.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-API-Key"
        ],
        expose_headers=["X-Process-Time"],
        max_age=3600,
    )

def setup_security_middleware(app):
    """Güvenlik middleware'lerini ekle"""
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    # RateLimitMiddleware kaldırıldı - slowapi kullanılıyor

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware sınıfı"""
    
    def __init__(self, app, whitelist: list = None):
        super().__init__(app)
        self.whitelist = whitelist or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.whitelist:
            return await call_next(request)
        
        client_ip = request.client.host
        
        # Admin endpoint'leri için IP kontrolü
        if "/admin" in str(request.url.path):
            if client_ip not in self.whitelist:
                SecurityAuditLogger.log_security_event(
                    "unauthorized_admin_access",
                    None,
                    {"client_ip": client_ip, "path": str(request.url.path)},
                    request
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Bu IP adresinden admin paneline erişim izni yok"}
                )
        
        return await call_next(request)

class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """Content-Type doğrulama middleware sınıfı"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # POST, PUT, PATCH istekleri için Content-Type kontrolü
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            # Dosya yükleme endpoint'leri hariç
            if "/upload" not in str(request.url.path):
                if not content_type.startswith("application/json"):
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "Content-Type application/json olmalıdır"}
                    )
        
        return await call_next(request)