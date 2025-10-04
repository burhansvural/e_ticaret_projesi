# frontend/src/components/product_card.py
import flet as ft

class ProductCard(ft.Card):
    def __init__(self, product_data, on_add_to_cart_click):
        super().__init__()
        self.product_id = product_data.get('id')
        self.product_name = product_data.get('name')
        self.product_price = product_data.get('price')
        self.content = ft.Column([
            ft.Image(src=product_data.get('image_url'), height=150, fit=ft.ImageFit.COVER, error_content=ft.Container(content=ft.Icon(ft.Icons.NO_PHOTOGRAPHY, size=50), bgcolor=ft.Colors.GREY_200, alignment=ft.alignment.center)),
            ft.Container(padding=ft.padding.all(10), content=ft.Column([
                ft.Text(self.product_name, weight=ft.FontWeight.BOLD, size=16),
                ft.Text(f"{self.product_price:.2f} TL", size=14, color=ft.Colors.GREEN_700),
                ft.FilledButton(text="Sepete Ekle", icon=ft.Icons.ADD_SHOPPING_CART, on_click=lambda e: on_add_to_cart_click(self), width=200)
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        ], spacing=0)