"""
Sidebar Component
"""

import flet as ft
from typing import Callable, Optional


class Sidebar:
    """Sidebar navigation component"""
    
    def __init__(self, page: ft.Page, current_user: Optional[dict], on_menu_click: Callable = None, 
                 on_navigate: Callable = None, on_logout: Callable = None):
        self.page = page
        self.current_user = current_user
        # Support both parameter names for backward compatibility
        self.on_navigate = on_menu_click or on_navigate
        self.on_logout = on_logout
        self.current_view = "dashboard"
    
    def set_current_view(self, view_name: str):
        """Set current active view"""
        self.current_view = view_name
    
    def build(self) -> ft.Container:
        """Build sidebar UI"""
        # User info section
        user_info = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=30, color=ft.Colors.WHITE),
                    ft.Column([
                        ft.Text(
                            self.current_user.get("email", "Admin") if self.current_user else "Admin",
                            size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text("Admin", size=10, color=ft.Colors.BLUE_GREY_300)
                    ], spacing=0)
                ], spacing=10),
                ft.Container(height=5),
                ft.ElevatedButton(
                    "Çıkış Yap",
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda e: self.on_logout(),
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    width=250
                )
            ], spacing=5),
            bgcolor=ft.Colors.BLUE_GREY_800,
            border_radius=8,
            margin=ft.margin.all(10)
        )
        
        return ft.Container(
            width=280,
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=ft.padding.all(0),
            content=ft.Column([
                # Header
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=40, color=ft.Colors.WHITE),
                        ft.Text("Admin Panel", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("E-Ticaret Yönetimi", size=12, color=ft.Colors.BLUE_GREY_300)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                ),
                ft.Divider(color=ft.Colors.BLUE_GREY_700, height=1),
                
                # User info
                user_info,
                
                # Menu items
                ft.Container(
                    expand=True,
                    padding=ft.padding.symmetric(vertical=10),
                    content=ft.ListView([
                        self._create_menu_item("Dashboard", ft.Icons.DASHBOARD, "dashboard"),
                        
                        # Product Management
                        self._create_menu_section("Ürün Yönetimi", ft.Icons.INVENTORY),
                        self._create_submenu_item("Ürün Listesi", ft.Icons.LIST, "products"),
                        self._create_submenu_item("Ürün Ekle", ft.Icons.ADD_CIRCLE, "add_product"),
                        self._create_submenu_item("Kategoriler", ft.Icons.CATEGORY, "categories"),
                        self._create_submenu_item("Toplu Ürün İşlemleri", ft.Icons.UPLOAD_FILE, "bulk_products"),
                        self._create_submenu_item("Ürün Özellikleri", ft.Icons.TUNE, "product_attributes"),
                        self._create_submenu_item("Markalar", ft.Icons.BRANDING_WATERMARK, "brands"),
                        
                        # Stock Management
                        self._create_menu_section("Stok Yönetimi", ft.Icons.WAREHOUSE),
                        self._create_submenu_item("Stok Hareketleri", ft.Icons.SWAP_HORIZ, "stock_movements"),
                        self._create_submenu_item("Düşük Stok Uyarıları", ft.Icons.WARNING_AMBER, "low_stock_alerts"),
                        self._create_submenu_item("Stok Girişi", ft.Icons.ADD_BOX, "manual_stock_entry"),
                        self._create_submenu_item("Stok Çıkışı", ft.Icons.REMOVE_CIRCLE, "manual_stock_exit"),
                        self._create_submenu_item("Stok Raporu", ft.Icons.INVENTORY, "inventory"),
                        
                        # Supplier Management
                        self._create_menu_section("Tedarikçi Yönetimi", ft.Icons.BUSINESS),
                        self._create_submenu_item("Tedarikçiler", ft.Icons.BUSINESS, "suppliers_list"),
                        self._create_submenu_item("Yeni Tedarikçi", ft.Icons.ADD_BUSINESS, "add_supplier"),
                        self._create_submenu_item("Alış Faturaları", ft.Icons.RECEIPT, "purchase_invoices"),
                        self._create_submenu_item("Yeni Fatura/İrsaliye", ft.Icons.ADD_SHOPPING_CART, "add_purchase_invoice"),
                        
                        # Order Management
                        self._create_menu_section("Sipariş Yönetimi", ft.Icons.SHOPPING_CART),
                        self._create_submenu_item("Tüm Siparişler", ft.Icons.RECEIPT_LONG, "orders_list"),
                        self._create_submenu_item("Bekleyen Siparişler", ft.Icons.PENDING, "pending_orders"),
                        self._create_submenu_item("Hazırlanıyor", ft.Icons.INVENTORY_2, "processing_orders"),
                        self._create_submenu_item("Kargoda", ft.Icons.LOCAL_SHIPPING, "shipping_orders"),
                        self._create_submenu_item("Teslim Edildi", ft.Icons.CHECK_CIRCLE, "completed_orders"),
                        self._create_submenu_item("İptal Edilen", ft.Icons.CANCEL, "cancelled_orders"),
                        self._create_submenu_item("İade Talepleri", ft.Icons.KEYBOARD_RETURN, "return_requests"),
                        
                        # Customer Management
                        self._create_menu_section("Müşteri Yönetimi", ft.Icons.PEOPLE),
                        self._create_submenu_item("Müşteri Listesi", ft.Icons.PERSON, "customers_list"),
                        self._create_submenu_item("Müşteri Grupları", ft.Icons.GROUP, "customer_groups"),
                        self._create_submenu_item("Yorumlar & Değerlendirmeler", ft.Icons.COMMENT, "reviews"),
                        self._create_submenu_item("Sadakat Programı", ft.Icons.CARD_GIFTCARD, "loyalty_program"),
                        self._create_submenu_item("Müşteri Mesajları", ft.Icons.MESSAGE, "customer_messages"),
                        
                        # Accounting & Finance
                        self._create_menu_section("Muhasebe", ft.Icons.ACCOUNT_BALANCE),
                        self._create_submenu_item("Gelir Raporu", ft.Icons.ATTACH_MONEY, "income_report"),
                        self._create_submenu_item("Gider Yönetimi", ft.Icons.MONEY_OFF, "expenses"),
                        self._create_submenu_item("Faturalar", ft.Icons.RECEIPT, "invoices"),
                        self._create_submenu_item("Ödeme Yöntemleri", ft.Icons.PAYMENT, "payment_methods"),
                        self._create_submenu_item("Vergi Ayarları", ft.Icons.CALCULATE, "tax_settings"),
                        self._create_submenu_item("Kasa Hareketleri", ft.Icons.ACCOUNT_BALANCE_WALLET, "cash_flow"),
                        self._create_submenu_item("Banka Hesapları", ft.Icons.ACCOUNT_BALANCE, "bank_accounts"),
                        
                        # Shipping & Logistics
                        self._create_menu_section("Kargo & Lojistik", ft.Icons.LOCAL_SHIPPING),
                        self._create_submenu_item("Kargo Firmaları", ft.Icons.BUSINESS, "shipping_companies"),
                        self._create_submenu_item("Kargo Takip", ft.Icons.TRACK_CHANGES, "shipment_tracking"),
                        self._create_submenu_item("Teslimat Bölgeleri", ft.Icons.MAP, "delivery_zones"),
                        self._create_submenu_item("Kargo Ücretleri", ft.Icons.LOCAL_ATM, "shipping_rates"),
                        
                        # Marketing & Promotions
                        self._create_menu_section("Pazarlama", ft.Icons.CAMPAIGN),
                        self._create_submenu_item("Kampanyalar", ft.Icons.LOCAL_OFFER, "campaigns"),
                        self._create_submenu_item("İndirim Kuponları", ft.Icons.CONFIRMATION_NUMBER, "coupons"),
                        self._create_submenu_item("E-posta Pazarlama", ft.Icons.EMAIL, "email_marketing"),
                        self._create_submenu_item("SMS Kampanyaları", ft.Icons.SMS, "sms_campaigns"),
                        self._create_submenu_item("Banner Yönetimi", ft.Icons.IMAGE, "banners"),
                        self._create_submenu_item("SEO Ayarları", ft.Icons.SEARCH, "seo_settings"),
                        self._create_submenu_item("Sosyal Medya", ft.Icons.SHARE, "social_media"),
                        
                        # Reports & Analytics
                        self._create_menu_section("Raporlar & Analiz", ft.Icons.ANALYTICS),
                        self._create_submenu_item("Satış Raporları", ft.Icons.TRENDING_UP, "sales_reports"),
                        self._create_submenu_item("Ürün Performansı", ft.Icons.BAR_CHART, "product_performance"),
                        self._create_submenu_item("Müşteri Analizi", ft.Icons.PEOPLE_OUTLINE, "customer_analytics"),
                        self._create_submenu_item("Stok Raporları", ft.Icons.INVENTORY, "stock_reports"),
                        self._create_submenu_item("Finansal Raporlar", ft.Icons.ACCOUNT_BALANCE_WALLET, "financial_reports"),
                        self._create_submenu_item("Trafik Analizi", ft.Icons.TRAFFIC, "traffic_analytics"),
                        
                        # Content Management
                        self._create_menu_section("İçerik Yönetimi", ft.Icons.ARTICLE),
                        self._create_submenu_item("Blog Yazıları", ft.Icons.ARTICLE, "blog_posts"),
                        self._create_submenu_item("Sayfalar", ft.Icons.PAGES, "pages"),
                        self._create_submenu_item("SSS", ft.Icons.HELP, "faq"),
                        self._create_submenu_item("Medya Kütüphanesi", ft.Icons.PHOTO_LIBRARY, "media_library"),
                        
                        # System & Settings
                        self._create_menu_section("Sistem Yönetimi", ft.Icons.SETTINGS),
                        self._create_submenu_item("Genel Ayarlar", ft.Icons.TUNE, "general_settings"),
                        self._create_submenu_item("Kullanıcı Yönetimi", ft.Icons.ADMIN_PANEL_SETTINGS, "user_management"),
                        self._create_submenu_item("Roller & İzinler", ft.Icons.SECURITY, "roles_permissions"),
                        self._create_submenu_item("Bildirimler", ft.Icons.NOTIFICATIONS, "notifications"),
                        self._create_submenu_item("Yedekleme", ft.Icons.BACKUP, "backup"),
                        self._create_submenu_item("Sistem Logları", ft.Icons.DESCRIPTION, "system_logs"),
                        self._create_submenu_item("API Ayarları", ft.Icons.API, "api_settings"),
                        self._create_submenu_item("Entegrasyonlar", ft.Icons.EXTENSION, "integrations"),
                    ], spacing=2)
                )
            ], spacing=0)
        )
    
    def _create_menu_item(self, title: str, icon, view_name: str) -> ft.Container:
        """Create main menu item"""
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icon, color=ft.Colors.WHITE),
                title=ft.Text(title, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                on_click=lambda e: self.on_navigate(view_name)
            ),
            bgcolor=ft.Colors.BLUE_600 if self.current_view == view_name else None,
            border_radius=ft.border_radius.all(8),
            margin=ft.margin.symmetric(horizontal=10, vertical=2)
        )
    
    def _create_menu_section(self, title: str, icon) -> ft.Container:
        """Create menu section header"""
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            content=ft.Row([
                ft.Icon(icon, size=18, color=ft.Colors.BLUE_GREY_400),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
            ], spacing=10)
        )
    
    def _create_submenu_item(self, title: str, icon, view_name: str) -> ft.Container:
        """Create submenu item"""
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Container(width=20),  # Indentation
                title=ft.Row([
                    ft.Icon(icon, size=16, color=ft.Colors.BLUE_GREY_300),
                    ft.Text(title, color=ft.Colors.BLUE_GREY_100, size=13)
                ], spacing=10),
                on_click=lambda e: self.on_navigate(view_name)
            ),
            bgcolor=ft.Colors.BLUE_700 if self.current_view == view_name else None,
            border_radius=ft.border_radius.all(6),
            margin=ft.margin.symmetric(horizontal=15, vertical=1)
        )