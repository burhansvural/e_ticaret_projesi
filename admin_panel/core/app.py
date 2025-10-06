"""
Main Admin Panel Application
"""
import flet as ft

from admin_panel.components import NotificationManager, ModalManager, Sidebar
from admin_panel.config import Config
from admin_panel.services import APIService, AuthService
from admin_panel.views import (
    AuthView, DashboardView, ProductsView, OrdersView, CustomersView, CategoriesView,
    InventoryView, SalesReportsView, ProductPerformanceView, CustomerAnalyticsView,
    CampaignsView, CouponsView, EmailMarketingView,
    GeneralSettingsView, UserManagementView, NotificationsSettingsView, SystemLogsView,
    ShippingCompaniesView, ShipmentTrackingView, DeliveryZonesView,
    BlogPostsView, PagesView, FAQView, MediaLibraryView,
    IncomeReportView, ExpensesView, InvoicesView, PaymentMethodsView,
    ProductsListView, AddProductView, BulkProductsView, ProductAttributesView, BrandsView,
    OrdersListView, PendingOrdersView, ProcessingOrdersView, ShippingOrdersView,
    CompletedOrdersView, CancelledOrdersView, ReturnRequestsView,
    CustomersListView, CustomerGroupsView, ReviewsView, LoyaltyProgramView, CustomerMessagesView,
    TaxSettingsView, CashFlowView, BankAccountsView, ShippingRatesView,
    SMSCampaignsView, BannersView, SEOSettingsView, SocialMediaView,
    StockReportsView, FinancialReportsView, TrafficAnalyticsView,
    RolesPermissionsView, BackupView, APISettingsView, IntegrationsView,
    # Stock Management
    StockMovementsView, LowStockAlertsView, ManualStockEntryView, ManualStockExitView,
    # Supplier Management
    SuppliersListView, AddSupplierView, PurchaseInvoicesView, AddPurchaseInvoiceView
)


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
        self.views = {}  # Dictionary to store all views
        
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
        # Main views
        self.views['dashboard'] = DashboardView(self.page, self.api_service, self.notification_manager)
        self.views['products'] = ProductsView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['orders'] = OrdersView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['customers'] = CustomersView(self.page, self.api_service, self.notification_manager)
        self.views['categories'] = CategoriesView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        
        # Product Management
        self.views['products_list'] = ProductsListView(self.page, self.api_service, self.notification_manager)
        self.views['add_product'] = AddProductView(self.page, self.api_service, self.notification_manager)
        self.views['inventory'] = InventoryView(self.page, self.api_service, self.notification_manager)
        self.views['bulk_products'] = BulkProductsView(self.page, self.api_service, self.notification_manager)
        self.views['product_attributes'] = ProductAttributesView(self.page, self.api_service, self.notification_manager)
        self.views['brands'] = BrandsView(self.page, self.api_service, self.notification_manager)
        
        # Stock Management
        self.views['stock_movements'] = StockMovementsView(self.page, self.api_service, self.notification_manager)
        self.views['low_stock_alerts'] = LowStockAlertsView(self.page, self.api_service, self.notification_manager)
        self.views['manual_stock_entry'] = ManualStockEntryView(self.page, self.api_service, self.notification_manager)
        self.views['manual_stock_exit'] = ManualStockExitView(self.page, self.api_service, self.notification_manager)
        
        # Supplier Management
        self.views['suppliers_list'] = SuppliersListView(self.page, self.api_service, self.notification_manager)
        self.views['add_supplier'] = AddSupplierView(self.page, self.api_service, self.notification_manager)
        self.views['purchase_invoices'] = PurchaseInvoicesView(self.page, self.api_service, self.notification_manager)
        self.views['add_purchase_invoice'] = AddPurchaseInvoiceView(self.page, self.api_service, self.notification_manager)
        
        # Order Management
        self.views['orders_list'] = OrdersListView(self.page, self.api_service, self.notification_manager)
        self.views['pending_orders'] = PendingOrdersView(self.page, self.api_service, self.notification_manager)
        self.views['processing_orders'] = ProcessingOrdersView(self.page, self.api_service, self.notification_manager)
        self.views['shipping_orders'] = ShippingOrdersView(self.page, self.api_service, self.notification_manager)
        self.views['completed_orders'] = CompletedOrdersView(self.page, self.api_service, self.notification_manager)
        self.views['cancelled_orders'] = CancelledOrdersView(self.page, self.api_service, self.notification_manager)
        self.views['return_requests'] = ReturnRequestsView(self.page, self.api_service, self.notification_manager)
        
        # Customer Management
        self.views['customers_list'] = CustomersListView(self.page, self.api_service, self.notification_manager)
        self.views['customer_groups'] = CustomerGroupsView(self.page, self.api_service, self.notification_manager)
        self.views['reviews'] = ReviewsView(self.page, self.api_service, self.notification_manager)
        self.views['loyalty_program'] = LoyaltyProgramView(self.page, self.api_service, self.notification_manager)
        self.views['customer_messages'] = CustomerMessagesView(self.page, self.api_service, self.notification_manager)
        
        # Finance
        self.views['income_report'] = IncomeReportView(self.page, self.api_service, self.notification_manager)
        self.views['expenses'] = ExpensesView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['invoices'] = InvoicesView(self.page, self.api_service, self.notification_manager)
        self.views['payment_methods'] = PaymentMethodsView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['tax_settings'] = TaxSettingsView(self.page, self.api_service, self.notification_manager)
        self.views['cash_flow'] = CashFlowView(self.page, self.api_service, self.notification_manager)
        self.views['bank_accounts'] = BankAccountsView(self.page, self.api_service, self.notification_manager)
        
        # Shipping & Logistics
        self.views['shipping_companies'] = ShippingCompaniesView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['shipment_tracking'] = ShipmentTrackingView(self.page, self.api_service, self.notification_manager)
        self.views['delivery_zones'] = DeliveryZonesView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['shipping_rates'] = ShippingRatesView(self.page, self.api_service, self.notification_manager)
        
        # Marketing
        self.views['campaigns'] = CampaignsView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['coupons'] = CouponsView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['email_marketing'] = EmailMarketingView(self.page, self.api_service, self.notification_manager)
        self.views['sms_campaigns'] = SMSCampaignsView(self.page, self.api_service, self.notification_manager)
        self.views['banners'] = BannersView(self.page, self.api_service, self.notification_manager)
        self.views['seo_settings'] = SEOSettingsView(self.page, self.api_service, self.notification_manager)
        self.views['social_media'] = SocialMediaView(self.page, self.api_service, self.notification_manager)
        
        # Reports & Analytics
        self.views['sales_reports'] = SalesReportsView(self.page, self.api_service, self.notification_manager)
        self.views['product_performance'] = ProductPerformanceView(self.page, self.api_service, self.notification_manager)
        self.views['customer_analytics'] = CustomerAnalyticsView(self.page, self.api_service, self.notification_manager)
        self.views['stock_reports'] = StockReportsView(self.page, self.api_service, self.notification_manager)
        self.views['financial_reports'] = FinancialReportsView(self.page, self.api_service, self.notification_manager)
        self.views['traffic_analytics'] = TrafficAnalyticsView(self.page, self.api_service, self.notification_manager)
        
        # Content Management
        self.views['blog_posts'] = BlogPostsView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['pages'] = PagesView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['faq'] = FAQView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['media_library'] = MediaLibraryView(self.page, self.api_service, self.notification_manager)
        
        # System & Settings
        self.views['general_settings'] = GeneralSettingsView(self.page, self.api_service, self.notification_manager)
        self.views['user_management'] = UserManagementView(self.page, self.api_service, self.notification_manager, self.modal_manager)
        self.views['roles_permissions'] = RolesPermissionsView(self.page, self.api_service, self.notification_manager)
        self.views['notifications'] = NotificationsSettingsView(self.page, self.api_service, self.notification_manager)
        self.views['backup'] = BackupView(self.page, self.api_service, self.notification_manager)
        self.views['system_logs'] = SystemLogsView(self.page, self.api_service, self.notification_manager)
        self.views['api_settings'] = APISettingsView(self.page, self.api_service, self.notification_manager)
        self.views['integrations'] = IntegrationsView(self.page, self.api_service, self.notification_manager)
    
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
        
        # Check if view exists
        if view_name in self.views:
            view = self.views[view_name]
            self.content_area.content = view.build()
            
            # Load data if view has load_data method
            if hasattr(view, 'load_data'):
                view.load_data()
            # Fallback to old method names for backward compatibility
            elif view_name == "products" and hasattr(view, 'load_products'):
                view.load_products()
            elif view_name == "orders" and hasattr(view, 'load_orders'):
                view.load_orders()
            elif view_name == "customers" and hasattr(view, 'load_customers'):
                view.load_customers()
            elif view_name == "categories" and hasattr(view, 'load_categories'):
                view.load_categories()
        else:
            # Show error if view not found
            self.content_area.content = ft.Column([
                ft.Text(f"View '{view_name}' not found", size=20, color=ft.Colors.RED)
            ])
        
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
            self.views = {}
            
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