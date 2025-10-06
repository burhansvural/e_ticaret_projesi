# backend/main.py

import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status, Response, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, AsyncGenerator
from dotenv import load_dotenv
import logging

# Environment variables'ları yükle
load_dotenv()

from backend import models, schemas
from .database import SessionLocal, engine
from .security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    get_current_user, get_current_admin_user, LoginAttemptTracker,
    SecurityAuditLogger, validate_file_upload, sanitize_input, validate_sql_input,
    PasswordValidator, limiter, verify_token, blacklist_token, cleanup_expired_blacklisted_tokens,
    get_token_jti, rate_limit_handler
)
from .middleware import setup_cors, setup_security_middleware

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Veritabanı ve Statik Dosya Yapılandırması ---
models.Base.metadata.create_all(bind=engine)

async def periodic_blacklist_cleanup():
    """Blacklist temizliğini periyodik olarak yapar"""
    while True:
        try:
            # Her 24 saatte bir temizlik yap
            await asyncio.sleep(24 * 60 * 60)  # 24 saat
            
            cleaned_count = cleanup_expired_blacklisted_tokens()
            if cleaned_count > 0:
                logger.info(f"Otomatik blacklist temizliği: {cleaned_count} token temizlendi")
        except Exception as e:
            logger.error(f"Blacklist temizliği hatası: {e}")

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Uygulama yaşam döngüsü yöneticisi"""
    # Startup
    cleanup_task = asyncio.create_task(periodic_blacklist_cleanup())
    logger.info("Otomatik blacklist temizliği başlatıldı")
    
    try:
        yield
    finally:
        # Shutdown
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("Otomatik blacklist temizliği durduruldu")

app = FastAPI(
    title="E-Ticaret API",
    version="2.0.0",
    description="Güvenli E-Ticaret Backend API",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    lifespan=lifespan
)

# Güvenlik middleware'lerini ekle
setup_cors(app)
setup_security_middleware(app)

# Rate limiting'i ekle
app.state.limiter = limiter

# Rate limit exception handler'ı ekle
from slowapi.errors import RateLimitExceeded
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# "static" klasörünü /static URL'si altında sun
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Dependency (Veritabanı Oturumu) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- YENİ: WebSocket Bağlantı Yöneticisi ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Yöneticiyi global olarak oluştur
manager = ConnectionManager()


# --- YENİ: WebSocket Endpoint'i ---
@app.websocket("/ws/products_updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # İstemciden gelebilecek mesajları dinle (şimdilik kullanmıyoruz)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)



# --- API UÇ NOKTALARI ---

# Güvenli resim yükleme endpoint'i
@app.post("/upload-image/")
@limiter.limit("10/minute")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_admin_user)
):
    try:
        # Dosya içeriğini oku
        file_content = await file.read()
        
        # Güvenlik kontrolü
        validate_file_upload(file_content, file.filename)
        
        # Güvenli dosya adı oluştur
        import uuid
        file_extension = os.path.splitext(file.filename)[1].lower()
        safe_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join("static", safe_filename)
        
        # Dosyayı kaydet
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        url = f"http://127.0.0.1:8000/static/{safe_filename}"
        
        # Güvenlik logu
        SecurityAuditLogger.log_security_event(
            "file_upload",
            current_user.id,
            {"filename": file.filename, "safe_filename": safe_filename, "size": len(file_content)},
            request
        )
        
        return {"url": url, "filename": safe_filename}
        
    except Exception as e:
        logger.error(f"Dosya yükleme hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dosya yüklenirken bir hata oluştu"
        )


@app.post("/products/", response_model=schemas.Product)
async def create_product(
    request: Request,
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
): 
    # Girdi sanitizasyonu
    product.name = sanitize_input(product.name)
    if product.description:
        product.description = sanitize_input(product.description, allow_html=False)
    
    # SQL injection kontrolü (ek güvenlik katmanı)
    validation_checks = [
        validate_sql_input(product.name),
        validate_sql_input(product.description) if product.description else True
    ]
    
    if not all(validation_checks):
        SecurityAuditLogger.log_security_event(
            "potential_sql_injection_attempt_product_creation",
            current_user.id,
            {"product_name": product.name, "product_description": product.description},
            request
        )
        raise HTTPException(status_code=400, detail="Geçersiz karakter kullanımı tespit edildi.")
    
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Güvenlik logu - ürün oluşturma
    SecurityAuditLogger.log_security_event(
        "product_created",
        current_user.id,
        {
            "product_id": db_product.id,
            "product_name": db_product.name,
            "price": db_product.price,
            "category_id": db_product.category_id
        },
        request
    )
    
    # BİLDİRİM GÖNDER
    await manager.broadcast("products_updated")
    return db_product


@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    request: Request,
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    # Önce silinecek ürünü veritabanında bul
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        # Ürün yoksa hata döndür
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # Güvenlik logu - ürün silme (silmeden önce bilgileri kaydet)
    SecurityAuditLogger.log_security_event(
        "product_deleted",
        current_user.id,
        {
            "product_id": db_product.id,
            "product_name": db_product.name,
            "price": db_product.price,
            "category_id": db_product.category_id
        },
        request
    )

    # Ürünü veritabanından sil
    db.delete(db_product)
    db.commit()

    # BİLDİRİM GÖNDER
    await manager.broadcast("products_updated")

    # Başarılı silme işleminde genellikle boş bir yanıt döneriz.
    # status_code=204, "İşlem başarılı ama döndürecek bir içerik yok" demektir.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/products/{product_id}", response_model=schemas.Product)
async def update_product(
    request: Request,
    product_id: int, 
    product: schemas.ProductUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    # Önce güncellenecek ürünü veritabanında bul
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        # Ürün yoksa hata döndür
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # Eski değerleri güvenlik logu için kaydet
    old_values = {
        "name": db_product.name,
        "price": db_product.price,
        "category_id": db_product.category_id,
        "stock_quantity": db_product.stock_quantity
    }

    # Gelen veriyi (product) bir dictionary'e çevir
    update_data = product.model_dump(exclude_unset=True)

    # update_data'daki her bir anahtar-değer çifti için
    # db_product nesnesinin ilgili özelliğini güncelle
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.add(db_product)  # Oturuma ekle (SQLAlchemy değişikliği anlar)
    db.commit()  # Değişiklikleri veritabanına kaydet
    db.refresh(db_product)  # Güncellenmiş veriyi veritabanından yeniden al

    # Güvenlik logu - ürün güncelleme
    SecurityAuditLogger.log_security_event(
        "product_updated",
        current_user.id,
        {
            "product_id": db_product.id,
            "old_values": old_values,
            "new_values": update_data,
            "updated_fields": list(update_data.keys())
        },
        request
    )

    # BİLDİRİM GÖNDER GÜNCELLENDİ BİLDİRİMİ
    await manager.broadcast("products_updated")

    return db_product


@app.post("/users/register")
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Kullanıcı kaydı başlat - SADECE doğrulama kodu gönderir, veritabanına kaydetmez!
    Kullanıcı doğrulama kodunu girdikten sonra /users/verify-email endpoint'i ile kayıt tamamlanır.
    """
    from .email_service import EmailService
    from .pending_registrations_redis import pending_registration_manager, PendingRegistration
    
    email_service = EmailService()
    
    # Girdi sanitizasyonu ve doğrulaması
    user.email = sanitize_input(user.email.lower())  # Email'i küçük harfe çevir
    user.first_name = sanitize_input(user.first_name)
    user.last_name = sanitize_input(user.last_name)
    user.phone = sanitize_input(user.phone) if user.phone else None
    
    # SQL injection kontrolü (ek güvenlik katmanı)
    if not all([
        validate_sql_input(user.email),
        validate_sql_input(user.first_name),
        validate_sql_input(user.last_name)
    ]):
        SecurityAuditLogger.log_security_event(
            "potential_sql_injection_attempt",
            None,
            {"email": user.email, "first_name": user.first_name, "last_name": user.last_name},
            request
        )
        raise HTTPException(status_code=400, detail="Geçersiz karakter kullanımı tespit edildi.")
    
    # E-postanın aynı is_admin değeri ile zaten kayıtlı olup olmadığını kontrol et
    is_admin = getattr(user, 'is_admin', False)  # UserCreate'den is_admin al
    db_user = db.query(models.User).filter(
        models.User.email == user.email,
        models.User.is_admin == is_admin
    ).first()
    if db_user:
        admin_type = "admin" if is_admin else "kullanıcı"
        SecurityAuditLogger.log_security_event(
            "registration_attempt_existing_email",
            None,
            {"email": user.email, "is_admin": is_admin},
            request
        )
        raise HTTPException(status_code=400, detail=f"Bu e-posta adresi zaten {admin_type} olarak kayıtlı.")

    # Şifre güvenlik kontrolü
    password_validation = PasswordValidator.validate_password(user.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=400, 
            detail={"message": "Şifre güvenlik gereksinimlerini karşılamıyor", "errors": password_validation["errors"]}
        )

    # Güvenli şifre hashleme
    hashed_password = hash_password(user.password)

    # 6 haneli doğrulama kodu oluştur
    verification_code = email_service.generate_verification_token(user.email)
    
    # Bekleyen kayıt oluştur (VERİTABANINA KAYDETME!)
    pending_registration = PendingRegistration(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        address=sanitize_input(user.address) if user.address else None,
        verification_code=verification_code,
        created_by_ip=request.client.host,
        is_admin=is_admin
    )
    
    # Geçici kayıt listesine ekle
    pending_registration_manager.add_registration(pending_registration)
    
    # E-mail doğrulama e-postası gönder
    user_name = f"{user.first_name} {user.last_name}"
    email_sent = email_service.send_verification_email(
        user.email, 
        user_name, 
        verification_code
    )
    
    # Güvenlik logu
    SecurityAuditLogger.log_security_event(
        "user_registration_initiated",
        None,
        {"email": user.email, "email_sent": email_sent},
        request
    )
    
    if not email_sent:
        logger.warning(f"E-posta gönderilemedi: {user.email}")
        raise HTTPException(status_code=500, detail="Doğrulama e-postası gönderilemedi. Lütfen daha sonra tekrar deneyin.")
    
    return {
        "message": "Doğrulama kodu e-posta adresinize gönderildi. Lütfen e-postanızı kontrol edin.",
        "email": user.email
    }

@app.post("/users/login", response_model=schemas.UserLoginResponse)
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    user_login: schemas.UserLogin, 
    db: Session = Depends(get_db)
):
    # Girdi sanitizasyonu ve doğrulaması
    user_login.email = sanitize_input(user_login.email.lower())
    
    # SQL injection kontrolü (ek güvenlik katmanı)
    if not validate_sql_input(user_login.email):
        SecurityAuditLogger.log_security_event(
            "potential_sql_injection_attempt_login",
            None,
            {"email": user_login.email},
            request
        )
        raise HTTPException(status_code=400, detail="Geçersiz karakter kullanımı tespit edildi.")
    
    # Hesap kilitleme kontrolü
    if LoginAttemptTracker.is_locked(user_login.email):
        SecurityAuditLogger.log_security_event(
            "login_attempt_locked_account",
            None,
            {"email": user_login.email},
            request
        )
        raise HTTPException(
            status_code=423, 
            detail="Hesabınız geçici olarak kilitlenmiştir. Lütfen daha sonra tekrar deneyin."
        )
    
    # Kullanıcıyı e-posta ve is_admin ile bul
    db_user = db.query(models.User).filter(
        models.User.email == user_login.email,
        models.User.is_admin == user_login.is_admin
    ).first()
    if not db_user:
        LoginAttemptTracker.record_failed_attempt(user_login.email)
        user_type = "admin" if user_login.is_admin else "kullanıcı"
        SecurityAuditLogger.log_security_event(
            "login_failed_user_not_found",
            None,
            {"email": user_login.email, "is_admin": user_login.is_admin},
            request
        )
        raise HTTPException(status_code=401, detail=f"Geçersiz {user_type} kullanıcı adı/şifre")
    
    # Şifre kontrolü
    if not verify_password(user_login.password, db_user.hashed_password):
        LoginAttemptTracker.record_failed_attempt(user_login.email)
        SecurityAuditLogger.log_security_event(
            "login_failed_wrong_password",
            db_user.id,
            {"email": user_login.email},
            request
        )
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı/şifre")
    
    # E-mail doğrulama kontrolü
    if db_user.is_verified is False:
        SecurityAuditLogger.log_security_event(
            "login_failed_unverified_email",
            db_user.id,
            {"email": user_login.email},
            request
        )
        raise HTTPException(
            status_code=401, 
            detail="E-posta adresinizi doğrulamanız gerekiyor. Lütfen e-posta kutunuzu kontrol edin."
        )
    
    if db_user.is_active is False:
        SecurityAuditLogger.log_security_event(
            "login_failed_inactive_account",
            db_user.id,
            {"email": user_login.email},
            request
        )
        raise HTTPException(status_code=401, detail="Hesabınız aktif değil.")
    
    # Başarılı giriş - giriş denemelerini temizle
    LoginAttemptTracker.clear_attempts(user_login.email)
    
    # Son giriş bilgilerini güncelle
    db_user.last_login = datetime.now()
    db_user.last_login_ip = request.client.host
    db.commit()
    
    # JWT token'ları oluştur
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    
    # Access token'dan JTI'yi çıkar (güvenlik için)
    access_jti = get_token_jti(access_token)
    
    # Refresh token'ı veritabanına kaydet (güvenlik için)
    from datetime import timedelta
    session_expires = datetime.now() + timedelta(days=7)
    
    db_session = models.UserSession(
        user_id=db_user.id,
        session_token=access_jti or "unknown",  # Access token'ın JTI'si
        refresh_token=refresh_token,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        expires_at=session_expires
    )
    db.add(db_session)
    db.commit()
    
    # Güvenlik logu
    SecurityAuditLogger.log_security_event(
        "login_successful",
        db_user.id,
        {"email": user_login.email, "session_id": db_session.id},
        request
    )
    
    return schemas.UserLoginResponse(
        user=db_user,
        tokens=schemas.TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60  # 30 dakika
        ),
        message="Giriş başarılı!"
    )

# Refresh token endpoint'i
@app.post("/users/refresh", response_model=schemas.TokenRefreshResponse)
@limiter.limit("10/minute")
async def refresh_access_token(
    request: Request,
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    # Refresh token'ı doğrula
    payload = verify_token(refresh_request.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz token payload"
        )
    
    # Veritabanında refresh token'ı kontrol et
    db_session = db.query(models.UserSession).filter(
        models.UserSession.refresh_token == refresh_request.refresh_token,
        models.UserSession.is_active.is_(True),
        models.UserSession.expires_at > datetime.now()
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token bulunamadı veya süresi dolmuş"
        )
    
    # Kullanıcıyı kontrol et
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı veya aktif değil"
        )
    
    # Yeni access token oluştur
    new_access_token = create_access_token(data={"sub": str(user.id)})
    
    # Session'ı güncelle
    db_session.last_activity = datetime.now()
    db_session.session_token = new_access_token[:50]
    db.commit()
    
    # Güvenlik logu
    SecurityAuditLogger.log_security_event(
        "token_refreshed",
        user.id,
        {"session_id": db_session.id},
        request
    )
    
    return schemas.TokenRefreshResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 dakika
    )

# Logout endpoint'i
@app.post("/users/logout")
async def logout_user(
    request: Request,
    logout_request: schemas.LogoutRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Access token'ı blacklist'e ekle
    access_token = None
    if hasattr(request, 'headers') and 'authorization' in request.headers:
        auth_header = request.headers.get('authorization', '')
        if auth_header.startswith('Bearer '):
            access_token = auth_header[7:]  # "Bearer " kısmını çıkar
            blacklist_token(access_token, current_user.id, "logout")
    
    # Refresh token'ı devre dışı bırak
    refresh_blacklisted = False
    if logout_request.refresh_token:
        # Refresh token'ı da blacklist'e ekle
        blacklist_token(logout_request.refresh_token, current_user.id, "logout")
        
        # UserSession'ı da devre dışı bırak
        db_session = db.query(models.UserSession).filter(
            models.UserSession.refresh_token == logout_request.refresh_token,
            models.UserSession.user_id == current_user.id
        ).first()
        
        if db_session:
            db_session.is_active = False
            db.commit()
            refresh_blacklisted = True
    
    # Güvenlik logu
    SecurityAuditLogger.log_security_event(
        "logout_successful",
        current_user.id,
        {
            "access_token_blacklisted": bool(access_token),
            "refresh_token_blacklisted": refresh_blacklisted,
            "session_invalidated": refresh_blacklisted
        },
        request
    )
    
    return {"message": "Başarıyla çıkış yapıldı"}

# Eski endpoint'i de koruyalım (geriye uyumluluk için)
@app.post("/users/", response_model=schemas.User)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    return await register_user(request, user, db)

# Kullanıcı listesi (Admin için)
@app.get("/users/", response_model=List[schemas.User])
def get_users(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    
    # Güvenlik logu - kullanıcı listesi görüntüleme
    SecurityAuditLogger.log_security_event(
        "users_list_accessed",
        current_user.id,
        {"skip": skip, "limit": limit, "total_users": len(users)},
        request
    )
    
    return users

# E-mail doğrulama endpoint'i (6 haneli kod ile)
@app.post("/users/verify-email", response_model=schemas.EmailVerificationResponse)
def verify_email(
    verification_data: schemas.EmailVerificationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Doğrulama kodunu kontrol et ve kullanıcıyı VERİTABANINA KAYDET
    Bu endpoint çağrılana kadar kullanıcı veritabanında YOKTUR!
    """
    from .pending_registrations_redis import pending_registration_manager
    
    # is_admin bilgisini al (varsayılan: False)
    is_admin = getattr(verification_data, 'is_admin', False)
    
    # Bekleyen kaydı bul ve doğrula
    pending_registration = pending_registration_manager.verify_and_remove(
        verification_data.email,
        verification_data.code,
        is_admin=is_admin
    )
    
    if not pending_registration:
        raise HTTPException(
            status_code=400,
            detail="Doğrulama kodu geçersiz veya süresi dolmuş. Lütfen yeni bir doğrulama kodu isteyin."
        )
    
    # E-postanın aynı is_admin değeri ile zaten kayıtlı olup olmadığını kontrol et (güvenlik için)
    db_user = db.query(models.User).filter(
        models.User.email == pending_registration.email,
        models.User.is_admin == pending_registration.is_admin
    ).first()
    if db_user:
        user_type = "admin" if pending_registration.is_admin else "kullanıcı"
        raise HTTPException(status_code=400, detail=f"Bu e-posta adresi zaten {user_type} olarak kayıtlı.")
    
    # ŞİMDİ kullanıcıyı veritabanına kaydet
    db_user = models.User(
        email=pending_registration.email,
        hashed_password=pending_registration.hashed_password,
        first_name=pending_registration.first_name,
        last_name=pending_registration.last_name,
        phone=pending_registration.phone,
        address=pending_registration.address,
        is_admin=pending_registration.is_admin,  # is_admin bilgisini ekle
        is_active=True,  # Doğrulandı, aktif
        is_verified=True,  # Doğrulandı
        verification_token=None,  # Artık gerek yok
        verification_token_expires=None,  # Artık gerek yok
        created_by_ip=pending_registration.created_by_ip
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Güvenlik logu
    user_type = "admin" if pending_registration.is_admin else "user"
    SecurityAuditLogger.log_security_event(
        "user_registration_completed",
        db_user.id,
        {"email": pending_registration.email, "is_admin": pending_registration.is_admin},
        request
    )
    
    logger.info(f"✅ Kullanıcı başarıyla kaydedildi ({user_type}): {pending_registration.email}")
    
    return schemas.EmailVerificationResponse(
        message="E-posta adresiniz başarıyla doğrulandı! Artık giriş yapabilirsiniz.",
        success=True
    )

# E-mail doğrulama e-postası yeniden gönderme
@app.post("/resend-verification", response_model=schemas.ResendVerificationResponse)
def resend_verification_email(email: str, db: Session = Depends(get_db)):
    """
    Doğrulama kodunu yeniden gönder
    Bekleyen kayıtlar için yeni kod oluşturur
    """
    from .email_service import EmailService
    from .pending_registrations_redis import pending_registration_manager
    
    email_service = EmailService()
    
    # Önce bekleyen kayıtlarda ara
    pending_registration = pending_registration_manager.get_registration(email)
    
    if pending_registration:
        # Yeni doğrulama kodu oluştur
        new_code = email_service.generate_verification_token(email)
        
        # Redis'te bekleyen kaydı güncelle (TTL'i de sıfırlar)
        update_success = pending_registration_manager.update_verification_code(email, new_code)
        
        if not update_success:
            raise HTTPException(status_code=500, detail="Doğrulama kodu güncellenemedi.")
        
        # E-posta gönder
        user_name = f"{pending_registration.first_name} {pending_registration.last_name}"
        email_sent = email_service.send_verification_email(
            email, 
            user_name, 
            new_code
        )
        
        if email_sent:
            return schemas.ResendVerificationResponse(
                message="Yeni doğrulama kodu e-posta adresinize gönderildi.",
                success=True
            )
        else:
            raise HTTPException(status_code=500, detail="E-posta gönderilemedi.")
    
    # Veritabanında kayıtlı ama doğrulanmamış kullanıcı var mı kontrol et
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        if db_user.is_verified:
            return schemas.ResendVerificationResponse(
                message="E-posta adresiniz zaten doğrulanmış.",
                success=True
            )
    
    # Ne bekleyen kayıt ne de veritabanında kayıt var
    raise HTTPException(
        status_code=404,
        detail="Bu e-posta adresi ile bekleyen bir kayıt bulunamadı. Lütfen önce kayıt olun."
    )


# --- Sipariş Oluşturma Endpoint'i ---
@app.post("/orders/", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Giriş yapmış kullanıcının ID'sini kullan
    owner_id = current_user.id

    total_price = 0
    order_items_to_create = []

    for item_data in order.items:
        # Ürünün güncel fiyatını veritabanından kontrol et
        product = db.query(models.Product).filter(models.Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"ID: {item_data.product_id} olan ürün bulunamadı.")

        price_for_this_item = product.price * item_data.quantity
        total_price += price_for_this_item

        # Veritabanına kaydedilecek OrderItem nesnesini oluştur
        db_order_item = models.OrderItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price_per_item=product.price
        )
        order_items_to_create.append(db_order_item)

    # Ana sipariş nesnesini oluştur
    db_order = models.Order(
        owner_id=owner_id,
        total_price=total_price,
        items=order_items_to_create
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# --- Siparişleri Listeleme Endpoint'i (Admin için) ---
@app.get("/orders/", response_model=list[schemas.Order])
def read_orders(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    
    # Güvenlik logu - sipariş listesi görüntüleme
    SecurityAuditLogger.log_security_event(
        "orders_list_accessed",
        current_user.id,
        {"skip": skip, "limit": limit, "total_orders": len(orders)},
        request
    )
    
    return orders

# --- Tek Sipariş Getirme Endpoint'i ---
@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    
    # Kullanıcı sadece kendi siparişlerini görebilir (admin hariç)
    if not getattr(current_user, 'is_admin', False) and db_order.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu siparişi görme yetkiniz yok")
    
    return db_order

# --- Sipariş Güncelleme Endpoint'i (Admin için) ---
@app.put("/orders/{order_id}", response_model=schemas.Order)
async def update_order(
    request: Request,
    order_id: int, 
    order_update: schemas.OrderStatusUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    
    # Geçerli durumları kontrol et
    valid_statuses = ["pending", "preparing", "ready", "shipped", "delivered", "cancelled"]
    if order_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Geçersiz durum. Geçerli durumlar: {valid_statuses}")
    
    # Eski durumu kaydet
    old_status = db_order.status
    
    # Sipariş durumunu güncelle
    db_order.status = order_update.status
    if order_update.notes:
        db_order.notes = order_update.notes
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Güvenlik logu - sipariş durumu güncelleme
    SecurityAuditLogger.log_security_event(
        "order_status_updated",
        current_user.id,
        {
            "order_id": order_id,
            "old_status": old_status,
            "new_status": order_update.status,
            "notes": order_update.notes
        },
        request
    )
    
    return db_order


# --- Kategori API'leri ---
@app.post("/categories/", response_model=schemas.Category)
async def create_category(
    request: Request,
    category: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    # Aynı isimde kategori var mı kontrol et
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Bu isimde bir kategori zaten mevcut")
    
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # Güvenlik logu - kategori oluşturma
    SecurityAuditLogger.log_security_event(
        "category_created",
        current_user.id,
        {"category_id": db_category.id, "category_name": db_category.name},
        request
    )
    
    return db_category

@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

@app.get("/categories/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    return db_category

@app.put("/categories/{category_id}", response_model=schemas.Category)
async def update_category(
    request: Request,
    category_id: int, 
    category: schemas.CategoryUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    # Aynı isimde başka kategori var mı kontrol et (kendisi hariç)
    existing_category = db.query(models.Category).filter(
        models.Category.name == category.name,
        models.Category.id != category_id
    ).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Bu isimde bir kategori zaten mevcut")
    
    # Eski değerleri kaydet
    old_name = db_category.name
    
    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # Güvenlik logu - kategori güncelleme
    SecurityAuditLogger.log_security_event(
        "category_updated",
        current_user.id,
        {
            "category_id": category_id,
            "old_name": old_name,
            "new_values": update_data
        },
        request
    )
    
    return db_category

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    request: Request,
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    # Bu kategoriye ait ürün var mı kontrol et
    products_count = db.query(models.Product).filter(models.Product.category_id == category_id).count()
    if products_count > 0:
        raise HTTPException(status_code=400, detail=f"Bu kategoriye ait {products_count} ürün bulunuyor. Önce ürünleri başka kategoriye taşıyın veya silin.")
    
    # Güvenlik logu - kategori silme (silmeden önce bilgileri kaydet)
    SecurityAuditLogger.log_security_event(
        "category_deleted",
        current_user.id,
        {"category_id": db_category.id, "category_name": db_category.name},
        request
    )
    
    db.delete(db_category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Güvenlik Endpoint'leri ---

@app.post("/admin/revoke-user-tokens/{user_id}")
async def revoke_user_tokens(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Admin: Belirli bir kullanıcının tüm token'larını iptal eder"""
    # Kullanıcının var olup olmadığını kontrol et
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Kullanıcının tüm aktif session'larını devre dışı bırak
    active_sessions = db.query(models.UserSession).filter(
        models.UserSession.user_id == user_id,
        models.UserSession.is_active.is_(True)
    ).all()
    
    revoked_count = 0
    for session in active_sessions:
        # Session'ı devre dışı bırak
        session.is_active = False
        
        # Refresh token'ı blacklist'e ekle
        if session.refresh_token:
            blacklist_token(session.refresh_token, user_id, "admin_revoke")
            revoked_count += 1
    
    db.commit()
    
    # Güvenlik logu
    SecurityAuditLogger.log_security_event(
        "admin_revoke_user_tokens",
        current_user.id,
        {
            "target_user_id": user_id,
            "target_user_email": target_user.email,
            "revoked_sessions": revoked_count
        },
        request
    )
    
    return {
        "message": f"Kullanıcının {revoked_count} aktif oturumu iptal edildi",
        "revoked_sessions": revoked_count
    }

@app.post("/admin/cleanup-blacklist")
async def cleanup_blacklist(
    request: Request,
    current_user: models.User = Depends(get_current_admin_user)
):
    """Admin: Süresi dolmuş blacklist token'larını temizler"""
    cleaned_count = cleanup_expired_blacklisted_tokens()
    
    # Güvenlik logu
    SecurityAuditLogger.log_security_event(
        "admin_cleanup_blacklist",
        current_user.id,
        {"cleaned_tokens": cleaned_count},
        request
    )
    
    return {
        "message": f"{cleaned_count} süresi dolmuş token temizlendi",
        "cleaned_count": cleaned_count
    }

@app.post("/auth/logout")
async def logout_user(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı çıkışı"""
    SecurityAuditLogger.log_security_event(
        "user_logout",
        current_user.id,
        {},
        request
    )
    return {"message": "Başarıyla çıkış yapıldı"}

@app.post("/auth/change-password")
async def change_password(
    request: Request,
    password_data: schemas.PasswordChange,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Şifre değiştirme"""
    # Mevcut şifreyi kontrol et
    if not verify_password(password_data.current_password, current_user.hashed_password):
        SecurityAuditLogger.log_security_event(
            "password_change_failed_wrong_current",
            current_user.id,
            {},
            request
        )
        raise HTTPException(status_code=400, detail="Mevcut şifre yanlış")
    
    # Yeni şifreyi hashle ve kaydet
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.password_changed_at = datetime.now()
    db.commit()
    
    SecurityAuditLogger.log_security_event(
        "password_changed",
        current_user.id,
        {},
        request
    )
    
    return {"message": "Şifre başarıyla değiştirildi"}

@app.post("/auth/request-password-reset")
@limiter.limit("3/hour")
async def request_password_reset(
    request: Request,
    reset_request: schemas.PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Şifre sıfırlama isteği"""
    from .email_service import EmailService
    import secrets
    
    email_service = EmailService()
    
    # Kullanıcıyı bul
    user = db.query(models.User).filter(models.User.email == reset_request.email).first()
    if not user:
        # Güvenlik için her zaman başarılı mesajı döndür
        return {"message": "Eğer bu e-posta adresi kayıtlıysa, şifre sıfırlama linki gönderildi"}
    
    # Eski token'ları geçersiz kıl
    db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.user_id == user.id,
        models.PasswordResetToken.is_used.is_(False)
    ).update({"is_used": True})
    
    # Yeni token oluştur
    reset_token = secrets.token_urlsafe(32)
    token_expires = datetime.now() + timedelta(hours=1)  # 1 saat geçerli
    
    db_token = models.PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=token_expires
    )
    db.add(db_token)
    db.commit()
    
    # E-posta gönder (implementasyon gerekli)
    # email_service.send_password_reset_email(user.email, reset_token)
    
    SecurityAuditLogger.log_security_event(
        "password_reset_requested",
        user.id,
        {"email": reset_request.email},
        request
    )
    
    return {"message": "Eğer bu e-posta adresi kayıtlıysa, şifre sıfırlama linki gönderildi"}

@app.post("/auth/reset-password")
async def reset_password(
    request: Request,
    reset_data: schemas.PasswordReset,
    db: Session = Depends(get_db)
):
    """Şifre sıfırlama"""
    # Token'ı kontrol et
    db_token = db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token == reset_data.token,
        models.PasswordResetToken.is_used.is_(False),
        models.PasswordResetToken.expires_at > datetime.now()
    ).first()
    
    if not db_token:
        SecurityAuditLogger.log_security_event(
            "password_reset_failed_invalid_token",
            None,
            {"token": reset_data.token[:8] + "..."},
            request
        )
        raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş token")
    
    # Kullanıcıyı bul
    user = db.query(models.User).filter(models.User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Şifreyi güncelle
    user.hashed_password = hash_password(reset_data.new_password)
    user.password_changed_at = datetime.now()
    
    # Token'ı kullanılmış olarak işaretle
    db_token.is_used = True
    db_token.used_at = datetime.now()
    
    db.commit()
    
    SecurityAuditLogger.log_security_event(
        "password_reset_successful",
        user.id,
        {},
        request
    )
    
    return {"message": "Şifre başarıyla sıfırlandı"}

@app.get("/auth/me", response_model=schemas.User)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini döndür"""
    return current_user

@app.get("/admin/security-logs", response_model=List[schemas.SecurityLog])
async def get_security_logs(
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Güvenlik loglarını listele (Admin)"""
    logs = db.query(models.SecurityLog).offset(skip).limit(limit).order_by(
        models.SecurityLog.created_at.desc()
    ).all()
    return logs

@app.get("/admin/users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Tüm kullanıcıları listele (Admin)"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.put("/admin/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    request: Request,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı aktiflik durumunu değiştir (Admin)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    user.is_active = not user.is_active
    db.commit()
    
    SecurityAuditLogger.log_security_event(
        "user_status_changed",
        current_user.id,
        {"target_user_id": user_id, "new_status": "active" if user.is_active is True else "inactive"},
        request
    )
    
    return {"message": f"Kullanıcı {'aktif' if user.is_active is True else 'pasif'} duruma getirildi"}


# --- STOK YÖNETİMİ ENDPOINT'LERİ ---

@app.get("/stock/movements/")
async def get_stock_movements(
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Stok hareketlerini listele (Admin)"""
    query = db.query(models.StockMovement)
    
    # Filtreler
    if product_id:
        query = query.filter(models.StockMovement.product_id == product_id)
    if movement_type:
        query = query.filter(models.StockMovement.movement_type == movement_type)
    
    movements = query.order_by(models.StockMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    # Ürün adlarını ekle
    result = []
    for movement in movements:
        movement_dict = {
            "id": movement.id,
            "product_id": movement.product_id,
            "product_name": movement.product.name if movement.product else "N/A",
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "description": movement.description,
            "reference": movement.reference,
            "created_by": movement.created_by,
            "created_at": movement.created_at.isoformat() if movement.created_at else None
        }
        result.append(movement_dict)
    
    return result


@app.post("/stock/movements/")
async def create_stock_movement(
    request: Request,
    movement: schemas.StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Yeni stok hareketi oluştur (Admin)"""
    # Ürünü kontrol et
    product = db.query(models.Product).filter(models.Product.id == movement.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    # Stok hareketi oluştur
    db_movement = models.StockMovement(
        product_id=movement.product_id,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        description=movement.description,
        reference=movement.reference,
        created_by=current_user.id
    )
    db.add(db_movement)
    
    # Ürün stok miktarını güncelle
    if movement.movement_type == "entry":
        product.stock_quantity += movement.quantity
    elif movement.movement_type == "exit":
        if product.stock_quantity < movement.quantity:
            raise HTTPException(status_code=400, detail="Yetersiz stok")
        product.stock_quantity -= movement.quantity
    
    db.commit()
    db.refresh(db_movement)
    
    # Güvenlik logu
    SecurityAuditLogger.log_security_event(
        "stock_movement_created",
        current_user.id,
        {
            "movement_id": db_movement.id,
            "product_id": movement.product_id,
            "movement_type": movement.movement_type,
            "quantity": movement.quantity
        },
        request
    )
    
    # WebSocket bildirimi
    await manager.broadcast("products_updated")
    
    return {
        "id": db_movement.id,
        "product_id": db_movement.product_id,
        "product_name": product.name,
        "movement_type": db_movement.movement_type,
        "quantity": db_movement.quantity,
        "description": db_movement.description,
        "reference": db_movement.reference,
        "created_by": db_movement.created_by,
        "created_at": db_movement.created_at.isoformat() if db_movement.created_at else None
    }


@app.get("/stock/low-stock/")
async def get_low_stock_products(
    threshold: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Düşük stoklu ürünleri listele (Admin)"""
    products = db.query(models.Product).filter(
        models.Product.stock_quantity <= threshold
    ).order_by(models.Product.stock_quantity.asc()).all()
    
    return products


@app.get("/stock/summary/")
async def get_stock_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Stok özeti (Admin)"""
    from sqlalchemy import func
    
    # Toplam ürün sayısı
    total_products = db.query(func.count(models.Product.id)).scalar()
    
    # Düşük stoklu ürün sayısı (10'dan az)
    low_stock_count = db.query(func.count(models.Product.id)).filter(
        models.Product.stock_quantity <= 10
    ).scalar()
    
    # Stokta olmayan ürün sayısı
    out_of_stock_count = db.query(func.count(models.Product.id)).filter(
        models.Product.stock_quantity == 0
    ).scalar()
    
    # Toplam stok değeri
    total_stock_value = db.query(
        func.sum(models.Product.price * models.Product.stock_quantity)
    ).scalar() or 0
    
    return {
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "total_stock_value": float(total_stock_value)
    }


# ============================================================================
# TEDARİKÇİ YÖNETİMİ (SUPPLIER MANAGEMENT)
# ============================================================================

@app.get("/suppliers/", response_model=List[schemas.Supplier])
async def get_suppliers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Tedarikçi listesini getir (Admin)
    
    - **skip**: Atlanacak kayıt sayısı
    - **limit**: Getirilecek maksimum kayıt sayısı
    - **is_active**: Aktif/pasif filtresi
    - **search**: Tedarikçi adı veya iletişim kişisi araması
    """
    query = db.query(models.Supplier)
    
    # Aktif/pasif filtresi
    if is_active is not None:
        query = query.filter(models.Supplier.is_active == is_active)
    
    # Arama filtresi
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Supplier.name.ilike(search_pattern),
                models.Supplier.contact_person.ilike(search_pattern)
            )
        )
    
    # Sıralama ve sayfalama
    suppliers = query.order_by(models.Supplier.name).offset(skip).limit(limit).all()
    
    return suppliers


@app.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Belirli bir tedarikçinin detaylarını getir (Admin)"""
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı")
    return supplier


@app.post("/suppliers/", response_model=schemas.Supplier, status_code=201)
async def create_supplier(
    supplier: schemas.SupplierCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Yeni tedarikçi oluştur (Admin)
    
    - **name**: Tedarikçi adı (zorunlu)
    - **contact_person**: İletişim kişisi
    - **email**: E-posta adresi
    - **phone**: Telefon numarası
    - **address**: Adres
    - **tax_number**: Vergi numarası
    - **notes**: Notlar
    - **is_active**: Aktif durumu
    """
    # Aynı isimde tedarikçi var mı kontrol et
    existing = db.query(models.Supplier).filter(models.Supplier.name == supplier.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu isimde bir tedarikçi zaten mevcut")
    
    # Yeni tedarikçi oluştur
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    
    # Güvenlik kaydı
    await security_logger.log_action(
        user_id=current_user.id,
        action="supplier_created",
        details=f"Yeni tedarikçi oluşturuldu: {db_supplier.name}",
        ip_address="admin_panel"
    )
    
    # WebSocket bildirimi
    await manager.broadcast({
        "type": "supplier_created",
        "supplier": {
            "id": db_supplier.id,
            "name": db_supplier.name
        }
    })
    
    return db_supplier


@app.put("/suppliers/{supplier_id}", response_model=schemas.Supplier)
async def update_supplier(
    supplier_id: int,
    supplier_update: schemas.SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Tedarikçi bilgilerini güncelle (Admin)"""
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı")
    
    # Güncelleme verilerini uygula
    update_data = supplier_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    
    db_supplier.updated_at = datetime.now()
    db.commit()
    db.refresh(db_supplier)
    
    # Güvenlik kaydı
    await security_logger.log_action(
        user_id=current_user.id,
        action="supplier_updated",
        details=f"Tedarikçi güncellendi: {db_supplier.name}",
        ip_address="admin_panel"
    )
    
    # WebSocket bildirimi
    await manager.broadcast({
        "type": "supplier_updated",
        "supplier": {
            "id": db_supplier.id,
            "name": db_supplier.name
        }
    })
    
    return db_supplier


@app.delete("/suppliers/{supplier_id}", status_code=204)
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Tedarikçiyi sil (Admin)"""
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı")
    
    # İlişkili satın almalar var mı kontrol et
    purchase_count = db.query(models.Purchase).filter(models.Purchase.supplier_id == supplier_id).count()
    if purchase_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bu tedarikçiye ait {purchase_count} adet satın alma kaydı var. Önce bunları silmelisiniz."
        )
    
    supplier_name = db_supplier.name
    db.delete(db_supplier)
    db.commit()
    
    # Güvenlik kaydı
    await security_logger.log_action(
        user_id=current_user.id,
        action="supplier_deleted",
        details=f"Tedarikçi silindi: {supplier_name}",
        ip_address="admin_panel"
    )
    
    # WebSocket bildirimi
    await manager.broadcast({
        "type": "supplier_deleted",
        "supplier_id": supplier_id
    })
    
    return None


# ============================================================================
# SATIN ALMA YÖNETİMİ (PURCHASE MANAGEMENT)
# ============================================================================

@app.get("/purchases/", response_model=List[schemas.Purchase])
async def get_purchases(
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Satın alma listesini getir (Admin)
    
    - **skip**: Atlanacak kayıt sayısı
    - **limit**: Getirilecek maksimum kayıt sayısı
    - **supplier_id**: Tedarikçi filtresi
    - **status**: Durum filtresi (pending, completed, cancelled)
    - **start_date**: Başlangıç tarihi (YYYY-MM-DD)
    - **end_date**: Bitiş tarihi (YYYY-MM-DD)
    """
    query = db.query(models.Purchase).join(models.Supplier)
    
    # Tedarikçi filtresi
    if supplier_id:
        query = query.filter(models.Purchase.supplier_id == supplier_id)
    
    # Durum filtresi
    if status:
        query = query.filter(models.Purchase.status == status)
    
    # Tarih filtreleri
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(models.Purchase.purchase_date >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Geçersiz başlangıç tarihi formatı (YYYY-MM-DD)")
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # Günün sonuna kadar dahil et
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(models.Purchase.purchase_date <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Geçersiz bitiş tarihi formatı (YYYY-MM-DD)")
    
    # Sıralama ve sayfalama
    purchases = query.order_by(models.Purchase.purchase_date.desc()).offset(skip).limit(limit).all()
    
    # Tedarikçi adlarını ekle
    result = []
    for purchase in purchases:
        purchase_dict = schemas.Purchase.from_orm(purchase).dict()
        purchase_dict['supplier_name'] = purchase.supplier.name
        
        # Satın alma kalemlerini ekle
        items = db.query(models.PurchaseItem).filter(
            models.PurchaseItem.purchase_id == purchase.id
        ).all()
        
        purchase_dict['items'] = []
        for item in items:
            item_dict = schemas.PurchaseItem.from_orm(item).dict()
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if product:
                item_dict['product_name'] = product.name
            purchase_dict['items'].append(item_dict)
        
        result.append(purchase_dict)
    
    return result


@app.get("/purchases/{purchase_id}", response_model=schemas.Purchase)
async def get_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """Belirli bir satın almanın detaylarını getir (Admin)"""
    purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Satın alma bulunamadı")
    
    # Tedarikçi adını ekle
    purchase_dict = schemas.Purchase.from_orm(purchase).dict()
    purchase_dict['supplier_name'] = purchase.supplier.name
    
    # Satın alma kalemlerini ekle
    items = db.query(models.PurchaseItem).filter(
        models.PurchaseItem.purchase_id == purchase.id
    ).all()
    
    purchase_dict['items'] = []
    for item in items:
        item_dict = schemas.PurchaseItem.from_orm(item).dict()
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            item_dict['product_name'] = product.name
        purchase_dict['items'].append(item_dict)
    
    return purchase_dict


@app.post("/purchases/", response_model=schemas.Purchase, status_code=201)
async def create_purchase(
    purchase: schemas.PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Yeni satın alma oluştur (Admin)
    
    - **supplier_id**: Tedarikçi ID (zorunlu)
    - **invoice_number**: Fatura numarası
    - **purchase_date**: Satın alma tarihi
    - **notes**: Notlar
    - **items**: Satın alma kalemleri (en az 1 adet)
    
    Satın alma oluşturulduğunda:
    - Ürün stokları otomatik olarak artırılır
    - Stok hareketi kaydı oluşturulur
    """
    # Tedarikçi kontrolü
    supplier = db.query(models.Supplier).filter(models.Supplier.id == purchase.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı")
    
    # Fatura numarası kontrolü
    if purchase.invoice_number:
        existing = db.query(models.Purchase).filter(
            models.Purchase.invoice_number == purchase.invoice_number
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu fatura numarası zaten kullanılıyor")
    
    # Toplam tutarı hesapla
    total_amount = 0
    for item in purchase.items:
        # Ürün kontrolü
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Ürün bulunamadı: {item.product_id}")
        
        total_amount += item.quantity * item.unit_price
    
    # Satın alma oluştur
    db_purchase = models.Purchase(
        supplier_id=purchase.supplier_id,
        invoice_number=purchase.invoice_number,
        purchase_date=purchase.purchase_date or datetime.now(),
        total_amount=total_amount,
        notes=purchase.notes,
        status="pending",
        created_by=current_user.id
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    # Satın alma kalemlerini oluştur ve stokları güncelle
    for item in purchase.items:
        # Satın alma kalemi
        db_item = models.PurchaseItem(
            purchase_id=db_purchase.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        db.add(db_item)
        
        # Ürün stokunu artır
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        product.stock_quantity += item.quantity
        
        # Stok hareketi kaydı oluştur
        stock_movement = models.StockMovement(
            product_id=item.product_id,
            movement_type="entry",
            quantity=item.quantity,
            description=f"Satın alma - Fatura: {purchase.invoice_number or 'N/A'}",
            reference=f"PURCHASE-{db_purchase.id}",
            created_by=current_user.id
        )
        db.add(stock_movement)
    
    db.commit()
    
    # Güvenlik kaydı
    await security_logger.log_action(
        user_id=current_user.id,
        action="purchase_created",
        details=f"Yeni satın alma oluşturuldu: {supplier.name} - {total_amount} TL",
        ip_address="admin_panel"
    )
    
    # WebSocket bildirimi
    await manager.broadcast({
        "type": "purchase_created",
        "purchase": {
            "id": db_purchase.id,
            "supplier_name": supplier.name,
            "total_amount": total_amount
        }
    })
    
    # Satın almayı detaylarıyla birlikte döndür
    return await get_purchase(db_purchase.id, db, current_user)


@app.put("/purchases/{purchase_id}", response_model=schemas.Purchase)
async def update_purchase(
    purchase_id: int,
    purchase_update: schemas.PurchaseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Satın alma bilgilerini güncelle (Admin)
    
    Not: Satın alma kalemleri güncellenemez, sadece genel bilgiler güncellenebilir
    """
    db_purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    if not db_purchase:
        raise HTTPException(status_code=404, detail="Satın alma bulunamadı")
    
    # Güncelleme verilerini uygula
    update_data = purchase_update.dict(exclude_unset=True)
    
    # Tedarikçi değişiyorsa kontrol et
    if 'supplier_id' in update_data:
        supplier = db.query(models.Supplier).filter(
            models.Supplier.id == update_data['supplier_id']
        ).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı")
    
    # Fatura numarası değişiyorsa kontrol et
    if 'invoice_number' in update_data and update_data['invoice_number']:
        existing = db.query(models.Purchase).filter(
            models.Purchase.invoice_number == update_data['invoice_number'],
            models.Purchase.id != purchase_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu fatura numarası zaten kullanılıyor")
    
    for field, value in update_data.items():
        setattr(db_purchase, field, value)
    
    db_purchase.updated_at = datetime.now()
    db.commit()
    db.refresh(db_purchase)
    
    # Güvenlik kaydı
    await security_logger.log_action(
        user_id=current_user.id,
        action="purchase_updated",
        details=f"Satın alma güncellendi: ID {purchase_id}",
        ip_address="admin_panel"
    )
    
    # WebSocket bildirimi
    await manager.broadcast({
        "type": "purchase_updated",
        "purchase_id": purchase_id
    })
    
    return await get_purchase(purchase_id, db, current_user)


@app.delete("/purchases/{purchase_id}", status_code=204)
async def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """
    Satın almayı sil (Admin)
    
    Not: Satın alma silindiğinde stok miktarları geri alınır
    """
    db_purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    if not db_purchase:
        raise HTTPException(status_code=404, detail="Satın alma bulunamadı")
    
    # Satın alma kalemlerini al ve stokları geri al
    items = db.query(models.PurchaseItem).filter(
        models.PurchaseItem.purchase_id == purchase_id
    ).all()
    
    for item in items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            # Stok miktarını azalt
            product.stock_quantity -= item.quantity
            if product.stock_quantity < 0:
                product.stock_quantity = 0
            
            # Ters stok hareketi kaydı oluştur
            stock_movement = models.StockMovement(
                product_id=item.product_id,
                movement_type="exit",
                quantity=item.quantity,
                description=f"Satın alma silindi - ID: {purchase_id}",
                reference=f"PURCHASE-DELETE-{purchase_id}",
                created_by=current_user.id
            )
            db.add(stock_movement)
        
        # Satın alma kalemini sil
        db.delete(item)
    
    # Satın almayı sil
    db.delete(db_purchase)
    db.commit()
    
    # Güvenlik kaydı
    await security_logger.log_action(
        user_id=current_user.id,
        action="purchase_deleted",
        details=f"Satın alma silindi: ID {purchase_id}",
        ip_address="admin_panel"
    )
    
    # WebSocket bildirimi
    await manager.broadcast({
        "type": "purchase_deleted",
        "purchase_id": purchase_id
    })
    
    return None


# Health check endpoint
@app.get("/health")
async def health_check():
    """Sistem sağlık kontrolü - Redis dahil"""
    from .pending_registrations_redis import pending_registration_manager
    
    # Redis sağlık kontrolü
    redis_health = pending_registration_manager.health_check()
    
    # Pending registrations istatistikleri
    stats = pending_registration_manager.get_stats()
    
    return {
        "status": "healthy" if redis_health.get("status") == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "2.2.0",
        "redis": redis_health,
        "pending_registrations": {
            "total": stats.get("total_pending", 0),
            "redis_connected": stats.get("redis_connected", False)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)