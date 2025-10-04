"""
Main Admin Panel Application
"""
import flet as ft

from admin_panel.components import NotificationManager, ModalManager, Sidebar
from admin_panel.config import Config
from admin_panel.services import APIService, AuthService
from admin_panel.views import AuthView, DashboardView, ProductsView, OrdersView, CustomersView, CategoriesView


class AdminPanel:
    """Main Admin Panel Application Class"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()
        
        # Initialize services
        self.api_service = APIService()
        self.auth_service = AuthService(self.api_service)
        
        # Initialize managers
        self.notification_manager = NotificationManager(page)
        self.modal_manager = ModalManager(page)
        
        # State management
        self.current_view = "dashboard"
        self.access_token = None
        self.current_user = None
        
        # UI components
        self.sidebar = None
        self.content_area = None
        self.main_layout = None
        
        # Initialize views (will be created after login)
        self.auth_view = None
        self.dashboard_view = None
        self.products_view = None
        self.orders_view = None
        self.customers_view = None
        self.categories_view = None
        
        # Start with login screen
        self.show_login()
    
    def _setup_page(self):
        """Configure page settings"""
        self.page.title = Config.APP_TITLE
        self.page.window_width = Config.WINDOW_WIDTH
        self.page.window_height = Config.WINDOW_HEIGHT
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
    
    def show_login(self):
        """Show login screen"""
        self.auth_view = AuthView(
            page=self.page,
            auth_service=self.auth_service,
            notification_manager=self.notification_manager,
            on_login_success=self.on_login_success
        )
        self.auth_view.show_login()
    
    def on_login_success(self, data: dict):
        """Handle successful login"""
        # Backend'den gelen data formatı: {"user": {...}, "tokens": {...}, "message": "..."}
        user = data.get("user", {})
        tokens = data.get("tokens", {})
        access_token = tokens.get("access_token")
        
        self.access_token = access_token
        self.current_user = user
        self.api_service.set_token(access_token)
        
        self.notification_manager.show_success(
            f"Hoş geldiniz, {user.get('first_name', 'Admin')}!"
        )
        
        # Initialize views with authenticated services
        self._initialize_views()
        
        # Show main panel
        self.show_main_panel()
    
    def _initialize_views(self):
        """Initialize all views after authentication"""
        self.dashboard_view = DashboardView(
            page=self.page,
            api_service=self.api_service,
            notification_manager=self.notification_manager
        )
        
        self.products_view = ProductsView(
            page=self.page,
            api_service=self.api_service,
            notification_manager=self.notification_manager,
            modal_manager=self.modal_manager
        )
        
        self.orders_view = OrdersView(
            page=self.page,
            api_service=self.api_service,
            notification_manager=self.notification_manager,
            modal_manager=self.modal_manager
        )
        
        self.customers_view = CustomersView(
            page=self.page,
            api_service=self.api_service,
            notification_manager=self.notification_manager
        )
        
        self.categories_view = CategoriesView(
            page=self.page,
            api_service=self.api_service,
            notification_manager=self.notification_manager,
            modal_manager=self.modal_manager
        )
    
    def show_main_panel(self):
        """Show main admin panel with sidebar and content area"""
        # Create sidebar
        self.sidebar = Sidebar(
            page=self.page,
            current_user=self.current_user,
            on_menu_click=self.navigate_to,
            on_logout=self.logout
        )
        
        # Create content area
        self.content_area = ft.Container(
            expand=True,
            padding=20,
            content=ft.Column([])
        )
        
        # Create main layout
        self.main_layout = ft.Row([
            self.sidebar.build(),
            ft.VerticalDivider(width=1),
            self.content_area
        ], expand=True, spacing=0)
        
        # Update page
        self.page.controls.clear()
        self.page.add(self.main_layout)
        
        # Show dashboard by default
        self.navigate_to("dashboard")
    
    def navigate_to(self, view_name: str):
        """Navigate to a specific view"""
        self.current_view = view_name
        
        # Update sidebar active state
        if self.sidebar:
            self.sidebar.set_current_view(view_name)
        
        # Clear content area
        self.content_area.content = ft.Column([])
        
        # Show appropriate view and load data
        if view_name == "dashboard":
            self.content_area.content = self.dashboard_view.build()
            self.dashboard_view.load_data()
        elif view_name == "products":
            self.content_area.content = self.products_view.build()
            self.products_view.load_products()
        elif view_name == "orders":
            self.content_area.content = self.orders_view.build()
            self.orders_view.load_orders()
        elif view_name == "customers":
            self.content_area.content = self.customers_view.build()
            self.customers_view.load_customers()
        elif view_name == "categories":
            self.content_area.content = self.categories_view.build()
            self.categories_view.load_categories()
        
        self.page.update()
    
    def logout(self):
        """Handle logout"""
        def confirm_logout(e):
            self.modal_manager.close_modal()
            
            # Clear authentication
            self.access_token = None
            self.current_user = None
            self.api_service.set_token(None)
            
            # Clear views
            self.dashboard_view = None
            self.products_view = None
            self.orders_view = None
            self.customers_view = None
            self.categories_view = None
            
            # Show login screen
            self.notification_manager.show_info("Çıkış yapıldı")
            self.show_login()
        
        def cancel_logout(e):
            self.modal_manager.close_modal()
        
        # Show confirmation dialog
        self.modal_manager.show_confirmation(
            title="Çıkış Yap",
            message="Çıkış yapmak istediğinizden emin misiniz?",
            on_confirm=confirm_logout,
            on_cancel=cancel_logout
        )