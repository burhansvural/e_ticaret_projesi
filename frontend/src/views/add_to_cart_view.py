import flet as ft

class AddToCartView(ft.View):
    def __init__(self, app, product_data):
        self.app = app
        self.product_data = product_data
        self.quantity = 1  # Varsayılan miktar
        
        # UI bileşenleri
        self.quantity_text = ft.Text(str(self.quantity), size=24, weight=ft.FontWeight.BOLD)
        self.total_price_text = ft.Text(f"{self.product_data['price']:.2f} TL", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
        
        super().__init__(
            route="/add-to-cart",
            controls=[self.build()],
            padding=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    def build(self):
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=self.go_back,
                            tooltip="Geri Dön"
                        ),
                        ft.Text("Sepete Ekle", size=24, weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Ürün Bilgileri
                ft.Container(
                    content=ft.Row([
                        # Ürün Resmi
                        ft.Container(
                            content=ft.Image(
                                src=self.product_data.get('image_url', '/static/default_product.png'),
                                width=200,
                                height=200,
                                fit=ft.ImageFit.COVER,
                                border_radius=10
                            ),
                            width=200,
                            height=200,
                            border_radius=10,
                            bgcolor=ft.Colors.GREY_100
                        ),
                        
                        # Ürün Detayları
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    self.product_data['name'],
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_900
                                ),
                                ft.Text(
                                    self.product_data.get('description', 'Açıklama bulunmuyor'),
                                    size=16,
                                    color=ft.Colors.GREY_700
                                ),
                                ft.Divider(),
                                ft.Text(
                                    f"Birim Fiyat: {self.product_data['price']:.2f} TL/kg",
                                    size=18,
                                    weight=ft.FontWeight.W_500
                                ),
                            ], spacing=10),
                            expand=True,
                            padding=ft.padding.only(left=20)
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.only(bottom=30)
                ),
                
                # Miktar Seçimi
                ft.Container(
                    content=ft.Column([
                        ft.Text("Miktar Seçin", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Row([
                                # Azalt butonu
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE,
                                    on_click=self.decrease_quantity,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.RED_100,
                                        color=ft.Colors.RED_700,
                                        shape=ft.CircleBorder()
                                    ),
                                    tooltip="Azalt"
                                ),
                                
                                # Miktar gösterimi
                                ft.Container(
                                    content=ft.Row([
                                        self.quantity_text,
                                        ft.Text("kg", size=18, color=ft.Colors.GREY_600)
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    width=100,
                                    alignment=ft.alignment.center
                                ),
                                
                                # Artır butonu
                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    on_click=self.increase_quantity,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.GREEN_100,
                                        color=ft.Colors.GREEN_700,
                                        shape=ft.CircleBorder()
                                    ),
                                    tooltip="Artır"
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            padding=20
                        ),
                        
                        # Hızlı miktar seçimi
                        ft.Text("Hızlı Seçim:", size=16, weight=ft.FontWeight.W_500),
                        ft.Row([
                            ft.ElevatedButton("0.5 kg", on_click=lambda e: self.set_quantity(0.5)),
                            ft.ElevatedButton("1 kg", on_click=lambda e: self.set_quantity(1)),
                            ft.ElevatedButton("2 kg", on_click=lambda e: self.set_quantity(2)),
                            ft.ElevatedButton("5 kg", on_click=lambda e: self.set_quantity(5)),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                    ], spacing=15),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=10
                ),
                
                # Toplam Fiyat
                ft.Container(
                    content=ft.Row([
                        ft.Text("Toplam:", size=20, weight=ft.FontWeight.BOLD),
                        self.total_price_text
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(vertical=20, horizontal=10),
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10
                ),
                
                # Aksiyon Butonları
                ft.Container(
                    content=ft.Row([
                        # Alışverişe Devam Et
                        ft.ElevatedButton(
                            text="Alışverişe Devam Et",
                            icon=ft.Icons.SHOPPING_CART_OUTLINED,
                            on_click=self.continue_shopping,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15)
                            ),
                            expand=True
                        ),
                        
                        # Satın Al
                        ft.ElevatedButton(
                            text="Satın Al",
                            icon=ft.Icons.PAYMENT,
                            on_click=self.buy_now,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREEN_600,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15)
                            ),
                            expand=True
                        ),
                    ], spacing=20),
                    padding=ft.padding.only(top=30)
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def decrease_quantity(self, e):
        """Miktarı azalt"""
        if self.quantity > 0.5:
            self.quantity = max(0.5, self.quantity - 0.5)
            self.update_quantity_display()
    
    def increase_quantity(self, e):
        """Miktarı artır"""
        if self.quantity < 50:  # Maksimum 50kg
            self.quantity += 0.5
            self.update_quantity_display()
    
    def set_quantity(self, quantity):
        """Belirli bir miktarı ayarla"""
        self.quantity = quantity
        self.update_quantity_display()
    
    def update_quantity_display(self):
        """Miktar ve toplam fiyat gösterimini güncelle"""
        self.quantity_text.value = str(self.quantity)
        total_price = self.quantity * self.product_data['price']
        self.total_price_text.value = f"{total_price:.2f} TL"
        self.app.page.update()
    
    def continue_shopping(self, e):
        """Sepete ekle ve alışverişe devam et"""
        # Ürünü sepete ekle
        product_id = self.product_data['id']
        current_quantity = self.app.shopping_cart.get(product_id, 0)
        self.app.shopping_cart[product_id] = current_quantity + self.quantity
        
        # Başarı mesajı göster
        self.app.page.snack_bar = ft.SnackBar(
            ft.Text(f"'{self.product_data['name']}' ({self.quantity} kg) sepete eklendi!"),
            open=True
        )
        
        # Sepet sayacını güncelle
        total_items = sum(self.app.shopping_cart.values())
        self.app.cart_item_count_text.value = str(int(total_items))
        
        # Ana sayfaya dön
        self.app.page.go("/")
    
    def buy_now(self, e):
        """Sepete ekle ve satın alma sayfasına git"""
        # Ürünü sepete ekle
        product_id = self.product_data['id']
        current_quantity = self.app.shopping_cart.get(product_id, 0)
        self.app.shopping_cart[product_id] = current_quantity + self.quantity
        
        # Sepet sayacını güncelle
        total_items = sum(self.app.shopping_cart.values())
        self.app.cart_item_count_text.value = str(int(total_items))
        
        # Satın alma sayfasına git
        self.app.page.go("/checkout")
    
    def go_back(self, e):
        """Geri dön"""
        self.app.page.go("/")