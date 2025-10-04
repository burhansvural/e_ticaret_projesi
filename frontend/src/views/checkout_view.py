import flet as ft
import requests

class CheckoutView(ft.View):
    def __init__(self, app):
        self.app = app
        
        super().__init__(
            route="/checkout",
            controls=[self.build()],
            padding=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    def build(self):
        # Sepet boşsa
        if not self.app.shopping_cart:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=100, color=ft.Colors.GREY_400),
                    ft.Text("Sepetiniz Boş", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    ft.Text("Alışverişe başlamak için ürün ekleyin", size=16, color=ft.Colors.GREY_500),
                    ft.ElevatedButton(
                        text="Alışverişe Başla",
                        icon=ft.Icons.SHOPPING_BAG,
                        on_click=lambda e: self.app.page.go("/"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                            padding=ft.padding.symmetric(horizontal=30, vertical=15)
                        )
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                alignment=ft.alignment.center
            )
        
        # Sepet dolu ise
        cart_items = []
        total_price = 0
        
        for product_id, quantity in self.app.shopping_cart.items():
            if product_id in self.app.all_products:
                product = self.app.all_products[product_id]
                item_total = quantity * product['price']
                total_price += item_total
                
                cart_items.append(self.create_cart_item(product, quantity, item_total))
        
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: self.app.page.go("/"),
                            tooltip="Geri Dön"
                        ),
                        ft.Text("Sepetim", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Icon(ft.Icons.SHOPPING_CART, color=ft.Colors.BLUE_600),
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Sepet İçeriği
                ft.Container(
                    content=ft.Column([
                        ft.Text("Sepetinizdeki Ürünler", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        *cart_items
                    ], spacing=10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREY_300)
                ),
                
                # Toplam Fiyat
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Ara Toplam:", size=16),
                            ft.Text(f"{total_price:.2f} TL", size=16, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text("Kargo:", size=16),
                            ft.Text("Ücretsiz", size=16, color=ft.Colors.GREEN_600, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(),
                        ft.Row([
                            ft.Text("TOPLAM:", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{total_price:.2f} TL", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=10),
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10,
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREEN_200)
                ),
                
                # Aksiyon Butonları
                ft.Container(
                    content=ft.Row([
                        # Alışverişe Devam Et
                        ft.ElevatedButton(
                            text="Alışverişe Devam",
                            icon=ft.Icons.SHOPPING_BAG_OUTLINED,
                            on_click=lambda e: self.app.page.go("/"),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREY_600,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15)
                            ),
                            expand=True
                        ),
                        
                        # Sepeti Temizle
                        ft.ElevatedButton(
                            text="Sepeti Temizle",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=self.clear_cart,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_600,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15)
                            ),
                            expand=True
                        ),
                        
                        # Satın Al
                        ft.ElevatedButton(
                            text="Satın Al",
                            icon=ft.Icons.PAYMENT,
                            on_click=self.proceed_to_payment,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREEN_600,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15)
                            ),
                            expand=True
                        ),
                    ], spacing=15),
                    padding=ft.padding.only(top=30)
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def create_cart_item(self, product, quantity, item_total):
        """Sepet öğesi oluştur"""
        return ft.Container(
            content=ft.Row([
                # Ürün Resmi
                ft.Container(
                    content=ft.Image(
                        src=product.get('image_url', '/static/default_product.png'),
                        width=80,
                        height=80,
                        fit=ft.ImageFit.COVER,
                        border_radius=8
                    ),
                    width=80,
                    height=80,
                    border_radius=8,
                    bgcolor=ft.Colors.GREY_100
                ),
                
                # Ürün Bilgileri
                ft.Container(
                    content=ft.Column([
                        ft.Text(product['name'], size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Birim Fiyat: {product['price']:.2f} TL/kg", size=14, color=ft.Colors.GREY_600),
                        ft.Text(f"Miktar: {quantity} kg", size=14, color=ft.Colors.BLUE_600),
                    ], spacing=5),
                    expand=True,
                    padding=ft.padding.only(left=15)
                ),
                
                # Fiyat ve İşlemler
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{item_total:.2f} TL", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.REMOVE,
                                on_click=self.create_decrease_handler(product['id']),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_100,
                                    color=ft.Colors.RED_700,
                                    shape=ft.CircleBorder(),
                                    padding=5
                                ),
                                tooltip="Azalt"
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                on_click=self.create_increase_handler(product['id']),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.GREEN_100,
                                    color=ft.Colors.GREEN_700,
                                    shape=ft.CircleBorder(),
                                    padding=5
                                ),
                                tooltip="Artır"
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                on_click=self.create_remove_handler(product['id']),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.GREY_100,
                                    color=ft.Colors.GREY_700,
                                    shape=ft.CircleBorder(),
                                    padding=5
                                ),
                                tooltip="Kaldır"
                            ),
                        ], spacing=5)
                    ], horizontal_alignment=ft.CrossAxisAlignment.END),
                    width=150
                )
            ], alignment=ft.MainAxisAlignment.START),
            padding=15,
            border_radius=8,
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.all(1, ft.Colors.GREY_200)
        )
    
    def create_decrease_handler(self, product_id):
        """Miktar azaltma handler'ı oluştur"""
        def handler(e):
            self.decrease_item_quantity(product_id)
        return handler
    
    def create_increase_handler(self, product_id):
        """Miktar artırma handler'ı oluştur"""
        def handler(e):
            self.increase_item_quantity(product_id)
        return handler
    
    def create_remove_handler(self, product_id):
        """Ürün kaldırma handler'ı oluştur"""
        def handler(e):
            self.remove_item(product_id)
        return handler

    def decrease_item_quantity(self, product_id):
        """Ürün miktarını azalt"""
        if product_id in self.app.shopping_cart:
            current_quantity = self.app.shopping_cart[product_id]
            if current_quantity > 0.5:
                self.app.shopping_cart[product_id] = current_quantity - 0.5
                self.update_cart_display()
            else:
                self.remove_item(product_id)
    
    def increase_item_quantity(self, product_id):
        """Ürün miktarını artır"""
        if product_id in self.app.shopping_cart:
            current_quantity = self.app.shopping_cart[product_id]
            if current_quantity < 50:  # Maksimum 50kg
                self.app.shopping_cart[product_id] = current_quantity + 0.5
                self.update_cart_display()
    
    def remove_item(self, product_id):
        """Ürünü sepetten kaldır"""
        if product_id in self.app.shopping_cart:
            del self.app.shopping_cart[product_id]
            self.update_cart_display()
    
    def clear_cart(self, e):
        """Sepeti temizle"""
        def confirm_clear(e):
            self.app.shopping_cart.clear()
            self.update_cart_display()
            self.app.page.close(dialog)
            self.app.page.snack_bar = ft.SnackBar(ft.Text("Sepet temizlendi!"), open=True)
            self.app.page.update()
        
        def cancel_clear(e):
            self.app.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Sepeti Temizle"),
            content=ft.Text("Sepetinizdeki tüm ürünleri kaldırmak istediğinizden emin misiniz?"),
            actions=[
                ft.TextButton("İptal", on_click=cancel_clear),
                ft.TextButton("Evet, Temizle", on_click=confirm_clear),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.app.page.open(dialog)
    
    def proceed_to_payment(self, e):
        """Ödeme işlemine geç"""
        # Kullanıcı giriş kontrolü
        if not self.app.current_user:
            self.app.page.snack_bar = ft.SnackBar(
                ft.Text("Satın alma işlemi için giriş yapmanız gerekiyor!"),
                open=True
            )
            self.app.page.go("/auth")
            return
        
        # Ödeme sayfasına git (şimdilik basit bir onay)
        total_price = sum(
            self.app.shopping_cart[pid] * self.app.all_products[pid]['price']
            for pid in self.app.shopping_cart
            if pid in self.app.all_products
        )
        
        def confirm_purchase(e):
            # Gerçek sipariş oluştur
            success = self.create_real_order()
            
            if success:
                # Sipariş tamamlandı
                self.app.shopping_cart.clear()
                self.app.cart_item_count_text.value = "0"
                self.app.page.close(dialog)
                self.app.page.snack_bar = ft.SnackBar(
                    ft.Text("🎉 Siparişiniz başarıyla tamamlandı! Teşekkür ederiz."),
                    open=True
                )
                self.app.page.go("/")
            else:
                self.app.page.close(dialog)
                self.app.page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Sipariş oluşturulurken bir hata oluştu. Lütfen tekrar deneyin."),
                    open=True
                )
        
        def cancel_purchase(e):
            self.app.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Siparişi Onayla"),
            content=ft.Column([
                ft.Text(f"Toplam Tutar: {total_price:.2f} TL", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Siparişinizi onaylıyor musunuz?", size=16),
                ft.Text("(Bu demo bir uygulamadır, gerçek ödeme yapılmayacaktır)", size=12, color=ft.Colors.GREY_600)
            ], tight=True),
            actions=[
                ft.TextButton("İptal", on_click=cancel_purchase),
                ft.TextButton("Onayla", on_click=confirm_purchase),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.app.page.open(dialog)
    
    def update_cart_display(self):
        """Sepet görünümünü güncelle"""
        # Sepet sayacını güncelle
        total_items = sum(self.app.shopping_cart.values())
        self.app.cart_item_count_text.value = str(int(total_items))
        
        # Sayfanın kontrollerini yeniden oluştur
        self.controls = [self.build()]
        self.update()
    
    def create_real_order(self):
        """Gerçek sipariş oluştur"""
        try:
            # Sipariş verilerini hazırla
            order_items = []
            for product_id, quantity in self.app.shopping_cart.items():
                if product_id in self.app.all_products:
                    order_items.append({
                        "product_id": product_id,
                        "quantity": int(quantity)  # Backend integer bekliyor
                    })
            
            order_data = {
                "items": order_items
            }
            
            # API'ye sipariş gönder
            response = requests.post(
                "http://127.0.0.1:8000/orders/",
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Sipariş oluşturma hatası: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Sipariş oluşturma hatası: {e}")
            return False