# frontend/src/app.py
import flet as ft


from .api import listen_for_updates_in_thread, fetch_products_from_api
from .components.product_card import ProductCard
from .views.main_view import MainView
from .views.auth_view import AuthView
from .views.email_verification_view import EmailVerificationView
from .views.add_to_cart_view import AddToCartView
from .views.checkout_view import CheckoutView


class ECommerceApp:
    def __init__(self, page: ft.Page):
        self.page = page
        page.title = "Flet E-Ticaret Mağazası"

        self.all_products = {}
        self.shopping_cart = {}
        self.current_user = None  # Giriş yapmış kullanıcı bilgisi

        # Paylaşılan kontroller
        self.cart_item_count_text = ft.Text("0", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.products_container = ft.Stack(expand=True)

        # YENİ KRİTİK EKLEME: Sayfa düzeyinde SnackBar bileşenini tanımlama
        page.snack_bar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.WHITE),
            duration=3000,
            bgcolor=ft.Colors.BLUE_500,  # Başlangıç rengi
            open=False
        )

        # Olay ve rota yöneticileri
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.pubsub.subscribe(self.on_message)

        # Arka plan işlerini başlat
        listen_for_updates_in_thread(self.page)
        self.page.go(page.route if page.route else "/")

    def on_message(self, message):
        if message == "products_update":
            self.fetch_products()

    def fetch_products(self):
        products_data = fetch_products_from_api()

        self.products_container.controls.clear()
        if products_data is None:
            self.products_container.controls.append(ft.Row([ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED),
                                                            ft.Text("API'ye ulaşılamıyor.", color=ft.Colors.RED)],
                                                           alignment=ft.MainAxisAlignment.CENTER))
        elif not products_data:
            self.products_container.controls.append(
                ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE), ft.Text("Mağazada henüz hiç ürün bulunmuyor.")],
                       alignment=ft.MainAxisAlignment.CENTER))
        else:
            self.all_products = {p['id']: p for p in products_data}
            products_grid = ft.GridView(expand=True, runs_count=5, max_extent=200, child_aspect_ratio=0.7, spacing=10,
                                        run_spacing=10)
            for product in products_data:
                products_grid.controls.append(ProductCard(product, self.add_to_cart))
            self.products_container.controls.append(products_grid)
        self.page.update()

    def add_to_cart(self, product_card: ProductCard):
        """Sepete ekle butonuna tıklandığında çalışır - Sepete Ekle sayfasına yönlendirir"""
        product_id = product_card.product_id
        if product_id in self.all_products:
            product_data = self.all_products[product_id]
            # Sepete ekle sayfasına git
            self.page.go(f"/add-to-cart/{product_id}")

    def route_change(self, route):
        self.page.views.clear()

        # Rota kontrolü
        if self.page.route == "/auth":
            self.page.views.append(AuthView(self))
        elif self.page.route.startswith("/verify-email"):
            # E-mail doğrulama sayfası
            verification_view = EmailVerificationView(self)
            self.page.views.append(ft.View(
                "/verify-email",
                [verification_view.build()],
                padding=0
            ))
        elif self.page.route.startswith("/add-to-cart/"):
            # Sepete ekle sayfası
            product_id_str = self.page.route.split("/")[-1]
            try:
                product_id = int(product_id_str)
                if product_id in self.all_products:
                    product_data = self.all_products[product_id]
                    self.page.views.append(AddToCartView(self, product_data))
                else:
                    # Ürün bulunamadı, ana sayfaya yönlendir
                    self.page.go("/")
                    return
            except ValueError:
                # Geçersiz ürün ID'si, ana sayfaya yönlendir
                self.page.go("/")
                return
        elif self.page.route == "/checkout":
            # Sepet/Satın alma sayfası
            self.page.views.append(CheckoutView(self))
        elif self.page.route == "/orders":
            # Sipariş takip sayfası
            from .views.orders_view import OrdersView
            self.page.views.append(OrdersView(self))
        else:
            # Ana sayfayı oluştur ve ekle
            self.page.views.append(MainView(self))
            
            if self.page.route == "/":
                self.fetch_products()

        self.page.update()

    def view_pop(self, view):
        self.page.views.pop()
        if self.page.views:
            self.page.go(self.page.views[-1].route)
        else:
            self.page.go("/")