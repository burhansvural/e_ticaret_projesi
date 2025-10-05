"""
API Service - Handles all API requests
"""

import requests
from typing import Optional, Dict, Any, Union

from admin_panel.config import API_URL, API_TIMEOUT


class APIService:
    """Centralized API service for all backend requests"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.base_url = API_URL
        self.timeout = API_TIMEOUT
    
    def set_token(self, token: Union[str,None] ):
        """Set authentication token"""
        self.access_token = token
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        return requests.get(
            url,
            params=params,
            headers=self.get_headers(),
            timeout=self.timeout
        )
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> requests.Response:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        return requests.post(
            url,
            data=data,
            json=json,
            headers=self.get_headers(),
            timeout=self.timeout
        )
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> requests.Response:
        """Make PUT request"""
        url = f"{self.base_url}{endpoint}"
        return requests.put(
            url,
            data=data,
            json=json,
            headers=self.get_headers(),
            timeout=self.timeout
        )
    
    def delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request"""
        url = f"{self.base_url}{endpoint}"
        return requests.delete(
            url,
            headers=self.get_headers(),
            timeout=self.timeout
        )
    
    # Specific API methods
    
    def get_products(self) -> Dict[str, Any]:
        """Get all products"""
        response = self.get("/products/")
        response.raise_for_status()
        return response.json()
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get single product"""
        response = self.get(f"/products/{product_id}")
        response.raise_for_status()
        return response.json()
    
    def create_product(self, product_data: Dict) -> Dict[str, Any]:
        """Create new product"""
        response = self.post("/products/", json=product_data)
        response.raise_for_status()
        return response.json()
    
    def update_product(self, product_id: int, product_data: Dict) -> Dict[str, Any]:
        """Update product"""
        response = self.put(f"/products/{product_id}", json=product_data)
        response.raise_for_status()
        return response.json()
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        response = self.delete(f"/products/{product_id}")
        response.raise_for_status()
        # 204 No Content response has no body
        return response.status_code == 204
    
    def get_orders(self) -> Dict[str, Any]:
        """Get all orders"""
        response = self.get("/orders/")
        response.raise_for_status()
        return response.json()
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get single order"""
        response = self.get(f"/orders/{order_id}")
        response.raise_for_status()
        return response.json()
    
    def update_order(self, order_id: int, order_data: Dict) -> Dict[str, Any]:
        """Update order"""
        response = self.put(f"/orders/{order_id}", json=order_data)
        response.raise_for_status()
        return response.json()
    
    def update_order_item_preparation(self, order_id: int, product_id: int, prep_data: Dict) -> Dict[str, Any]:
        """Update order item preparation status"""
        response = self.put(
            f"/orders/{order_id}/items/{product_id}/preparation",
            json=prep_data
        )
        response.raise_for_status()
        return response.json()
    
    def get_customers(self) -> Dict[str, Any]:
        """Get all customers"""
        response = self.get("/users/")
        response.raise_for_status()
        return response.json()
    
    def get_categories(self) -> Dict[str, Any]:
        """Get all categories"""
        response = self.get("/categories/")
        response.raise_for_status()
        return response.json()
    
    def create_category(self, category_data: Dict) -> Dict[str, Any]:
        """Create new category"""
        response = self.post("/categories/", json=category_data)
        response.raise_for_status()
        return response.json()
    
    def update_category(self, category_id: int, category_data: Dict) -> Dict[str, Any]:
        """Update category"""
        response = self.put(f"/categories/{category_id}", json=category_data)
        response.raise_for_status()
        return response.json()
    
    def delete_category(self, category_id: int) -> bool:
        """Delete category"""
        response = self.delete(f"/categories/{category_id}")
        response.raise_for_status()
        # 204 No Content response has no body
        return response.status_code == 204
    
    def upload_image(self, file_data) -> Dict[str, Any]:
        """Upload image"""
        files = {"file": file_data}
        url = f"{self.base_url}/upload-image/"
        # Authorization header ekle (multipart/form-data için Content-Type otomatik)
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        response = requests.post(url, files=files, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()