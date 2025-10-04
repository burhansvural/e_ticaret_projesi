"""
Views Module
"""

from .auth_view import AuthView
from .dashboard_view import DashboardView
from .products_view import ProductsView
from .orders_view import OrdersView
from .customers_view import CustomersView
from .categories_view import CategoriesView

__all__ = [
    'AuthView',
    'DashboardView',
    'ProductsView',
    'OrdersView',
    'CustomersView',
    'CategoriesView'
]