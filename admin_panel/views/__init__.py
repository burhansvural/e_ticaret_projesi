"""
Views Module
"""

from .auth_view import AuthView
from .dashboard_view import DashboardView
from .products_view import ProductsView
from .orders_view import OrdersView
from .customers_view import CustomersView
from .categories_view import CategoriesView

# Inventory
from .inventory_view import InventoryView

# Reports
from .reports_view import SalesReportsView, ProductPerformanceView, CustomerAnalyticsView

# Marketing
from .marketing_view import CampaignsView, CouponsView, EmailMarketingView

# Settings
from .settings_view import (
    GeneralSettingsView, UserManagementView, 
    NotificationsSettingsView, SystemLogsView
)

# Shipping
from .shipping_view import ShippingCompaniesView, ShipmentTrackingView, DeliveryZonesView

# Content
from .content_view import BlogPostsView, PagesView, FAQView, MediaLibraryView

# Finance
from .finance_view import IncomeReportView, ExpensesView, InvoicesView, PaymentMethodsView

# Simple placeholder views
from .simple_views import (
    # Product Management
    ProductsListView, AddProductView, BulkProductsView, 
    ProductAttributesView, BrandsView,
    
    # Order Management
    OrdersListView, PendingOrdersView, ProcessingOrdersView,
    ShippingOrdersView, CompletedOrdersView, CancelledOrdersView, ReturnRequestsView,
    
    # Customer Management
    CustomersListView, CustomerGroupsView, ReviewsView, 
    LoyaltyProgramView, CustomerMessagesView,
    
    # Finance
    TaxSettingsView, CashFlowView, BankAccountsView,
    
    # Shipping
    ShippingRatesView,
    
    # Marketing
    SMSCampaignsView, BannersView, SEOSettingsView, SocialMediaView,
    
    # Reports
    StockReportsView, FinancialReportsView, TrafficAnalyticsView,
    
    # Settings
    RolesPermissionsView, BackupView, APISettingsView, IntegrationsView
)

# Stock Management Views
from .stock_views import (
    StockMovementsView, LowStockAlertsView, 
    ManualStockEntryView, ManualStockExitView
)

# Supplier and Purchase Management Views
from .supplier_views import (
    SuppliersListView, AddSupplierView,
    PurchaseInvoicesView, AddPurchaseInvoiceView
)

__all__ = [
    'AuthView',
    'DashboardView',
    'ProductsView',
    'OrdersView',
    'CustomersView',
    'CategoriesView',
    'InventoryView',
    'SalesReportsView',
    'ProductPerformanceView',
    'CustomerAnalyticsView',
    'CampaignsView',
    'CouponsView',
    'EmailMarketingView',
    'GeneralSettingsView',
    'UserManagementView',
    'NotificationsSettingsView',
    'SystemLogsView',
    'ShippingCompaniesView',
    'ShipmentTrackingView',
    'DeliveryZonesView',
    'BlogPostsView',
    'PagesView',
    'FAQView',
    'MediaLibraryView',
    'IncomeReportView',
    'ExpensesView',
    'InvoicesView',
    'PaymentMethodsView',
    'ProductsListView',
    'AddProductView',
    'BulkProductsView',
    'ProductAttributesView',
    'BrandsView',
    'OrdersListView',
    'PendingOrdersView',
    'ProcessingOrdersView',
    'ShippingOrdersView',
    'CompletedOrdersView',
    'CancelledOrdersView',
    'ReturnRequestsView',
    'CustomersListView',
    'CustomerGroupsView',
    'ReviewsView',
    'LoyaltyProgramView',
    'CustomerMessagesView',
    'TaxSettingsView',
    'CashFlowView',
    'BankAccountsView',
    'ShippingRatesView',
    'SMSCampaignsView',
    'BannersView',
    'SEOSettingsView',
    'SocialMediaView',
    'StockReportsView',
    'FinancialReportsView',
    'TrafficAnalyticsView',
    'RolesPermissionsView',
    'BackupView',
    'APISettingsView',
    'IntegrationsView',
    # Stock Management
    'StockMovementsView',
    'LowStockAlertsView',
    'ManualStockEntryView',
    'ManualStockExitView',
    # Supplier and Purchase Management
    'SuppliersListView',
    'AddSupplierView',
    'PurchaseInvoicesView',
    'AddPurchaseInvoiceView',
]