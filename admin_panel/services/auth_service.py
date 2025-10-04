"""
Authentication Service
"""

import requests
from typing import Optional, Dict, Any

from admin_panel.config import API_URL, API_TIMEOUT


class AuthService:
    """Handles authentication operations"""
    
    def __init__(self, api_service=None):
        self.api_service = api_service
        self.base_url = API_URL
        self.timeout = API_TIMEOUT
    
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new admin user"""
        response = requests.post(
            f"{self.base_url}/users/register",
            json={
                **user_data,
                "is_admin": True  # Always register as admin in admin panel
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def verify_email(self, email: str, code: str) -> Dict[str, Any]:
        """Verify email with code"""
        response = requests.post(
            f"{self.base_url}/users/verify-email",
            json={
                "email": email,
                "code": code,
                "is_admin": True  # Admin verification
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login admin user"""
        response = requests.post(
            f"{self.base_url}/users/login",
            json={
                "email": email,
                "password": password,
                "is_admin": True  # Admin login
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """Get current user info"""
        response = requests.get(
            f"{self.base_url}/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()