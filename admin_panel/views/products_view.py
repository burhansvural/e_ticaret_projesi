"""
Products View - Product list and management
"""

import flet as ft
from typing import Optional

from admin_panel.services import APIService


class ProductsView:
    """Products management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
        
        # Data
        self.products = []
        self.categories = []
        self.filtered_products = []
        
        # UI Components
        self.products_table = None
        self.search_field = None
        self.category_filter = None
        self.stock_filter = None
        self.total_products_text = None
        self.loading_indicator = None
    
    def build(self) -> ft.Control:
        """Build products list UI"""
        # Header
        header = ft.Row([
            ft.Text("Ürün Listesi", size=32, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Yeni Ürün Ekle",
                icon=ft.Icons.ADD,
                on_click=lambda e: self.show_add_product_form(),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Search and filters
        self.search_field = ft.TextField(
            label="Ürün Ara",
            hint_text="Ürün adı veya açıklama...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.apply_filters(),
            expand=True
        )
        
        self.category_filter = ft.Dropdown(
            label="Kategori",
            hint_text="Tüm Kategoriler",
            options=[ft.dropdown.Option("all", "Tüm Kategoriler")],
            value="all",
            on_change=lambda e: self.apply_filters(),
            width=200
        )
        
        self.stock_filter = ft.Dropdown(
            label="Stok Durumu",
            hint_text="Tümü",
            options=[
                ft.dropdown.Option("all", "Tümü"),
                ft.dropdown.Option("in_stock", "Stokta Var"),
                ft.dropdown.Option("low_stock", "Stok Azalıyor"),
                ft.dropdown.Option("out_of_stock", "Stokta Yok"),
            ],
            value="all",
            on_change=lambda e: self.apply_filters(),
            width=200
        )
        
        filters_row = ft.Row([
            self.search_field,
            self.category_filter,
            self.stock_filter,
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Yenile",
                on_click=lambda e: self.load_data()
            )
        ], spacing=10)
        
        # Stats
        self.total_products_text = ft.Text("Toplam: 0 ürün", size=14, color=ft.Colors.GREY_700)
        
        # Products table
        self.products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Görsel", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ürün Adı", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Kategori", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fiyat", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stok", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Birim", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.GREY_100,
        )
        
        # Loading indicator
        self.loading_indicator = ft.ProgressRing(visible=False)
        
        table_container = ft.Container(
            content=ft.Column([
                ft.Row([self.total_products_text, self.loading_indicator], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Column([self.products_table], scroll=ft.ScrollMode.AUTO, expand=True),
            ], expand=True),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            header,
            ft.Container(height=10),
            filters_row,
            ft.Container(height=10),
            table_container
        ], spacing=0, expand=True)
    
    def load_data(self):
        """Load products and categories from API"""
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            # Load products
            response = self.api_service.get_products()
            self.products = response if isinstance(response, list) else []
            
            # Load categories
            try:
                cat_response = self.api_service.get_categories()
                self.categories = cat_response if isinstance(cat_response, list) else []
                self._update_category_filter()
            except Exception as e:
                print(f"Kategoriler yüklenemedi: {e}")
                self.categories = []
            
            self.filtered_products = self.products.copy()
            self._update_table()
            
        except Exception as e:
            self.notification_manager.show_error(f"Ürünler yüklenemedi: {e}")
            self.products = []
            self.filtered_products = []
        finally:
            self.loading_indicator.visible = False
            self.page.update()
    
    def _update_category_filter(self):
        """Update category filter dropdown"""
        options = [ft.dropdown.Option("all", "Tüm Kategoriler")]
        for cat in self.categories:
            options.append(ft.dropdown.Option(str(cat.get('id')), cat.get('name', 'Bilinmeyen')))
        self.category_filter.options = options
        self.page.update()
    
    def apply_filters(self):
        """Apply search and filters"""
        search_text = self.search_field.value.lower() if self.search_field.value else ""
        category_id = self.category_filter.value
        stock_status = self.stock_filter.value
        
        self.filtered_products = []
        
        for product in self.products:
            # Search filter
            if search_text:
                name = product.get('name', '').lower()
                desc = product.get('description', '').lower()
                if search_text not in name and search_text not in desc:
                    continue
            
            # Category filter
            if category_id != "all":
                if str(product.get('category_id')) != category_id:
                    continue
            
            # Stock filter
            stock = product.get('stock_quantity', 0)
            if stock_status == "in_stock" and stock <= 10:
                continue
            elif stock_status == "low_stock" and (stock == 0 or stock > 10):
                continue
            elif stock_status == "out_of_stock" and stock > 0:
                continue
            
            self.filtered_products.append(product)
        
        self._update_table()
    
    def _update_table(self):
        """Update products table"""
        self.products_table.rows.clear()
        
        for product in self.filtered_products:
            # Get category name
            category_name = "Kategorisiz"
            category_id = product.get('category_id')
            if category_id:
                for cat in self.categories:
                    if cat.get('id') == category_id:
                        category_name = cat.get('name', 'Bilinmeyen')
                        break
            
            # Stock status
            stock = product.get('stock_quantity', 0)
            if stock == 0:
                stock_color = ft.Colors.RED
                stock_text = f"{stock} (Yok)"
            elif stock <= 10:
                stock_color = ft.Colors.ORANGE
                stock_text = f"{stock} (Az)"
            else:
                stock_color = ft.Colors.GREEN
                stock_text = str(stock)
            
            # Image
            image_url = product.get('image_url')
            if image_url:
                image_widget = ft.Image(
                    src=image_url,
                    width=50,
                    height=50,
                    fit=ft.ImageFit.COVER,
                    border_radius=5
                )
            else:
                image_widget = ft.Container(
                    content=ft.Icon(ft.Icons.IMAGE, size=30, color=ft.Colors.GREY_400),
                    width=50,
                    height=50,
                    bgcolor=ft.Colors.GREY_200,
                    border_radius=5,
                    alignment=ft.alignment.center
                )
            
            self.products_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(image_widget),
                    ft.DataCell(ft.Text(product.get('name', ''), max_lines=2)),
                    ft.DataCell(ft.Text(category_name)),
                    ft.DataCell(ft.Text(f"₺{product.get('price', 0):.2f}")),
                    ft.DataCell(ft.Text(stock_text, color=stock_color, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(product.get('unit', 'adet'))),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                icon_color=ft.Colors.GREEN,
                                tooltip="Görüntüle",
                                on_click=lambda e, p=product: self.view_product(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Düzenle",
                                on_click=lambda e, p=product: self.edit_product(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Sil",
                                on_click=lambda e, p=product: self.delete_product(p)
                            )
                        ], spacing=0)
                    )
                ])
            )
        
        # Update stats
        self.total_products_text.value = f"Toplam: {len(self.filtered_products)} ürün"
        self.page.update()
    
    def view_product(self, product):
        """View product details"""
        # Get category name
        category_name = "Kategorisiz"
        category_id = product.get('category_id')
        if category_id:
            for cat in self.categories:
                if cat.get('id') == category_id:
                    category_name = cat.get('name', 'Bilinmeyen')
                    break
        
        # Image
        image_url = product.get('image_url')
        if image_url:
            image_widget = ft.Image(
                src=image_url,
                width=200,
                height=200,
                fit=ft.ImageFit.COVER,
                border_radius=10
            )
        else:
            image_widget = ft.Container(
                content=ft.Icon(ft.Icons.IMAGE, size=100, color=ft.Colors.GREY_400),
                width=200,
                height=200,
                bgcolor=ft.Colors.GREY_200,
                border_radius=10,
                alignment=ft.alignment.center
            )
        
        details = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SHOPPING_BAG, color=ft.Colors.BLUE),
                ft.Text("Ürün Detayları", size=20, weight=ft.FontWeight.BOLD)
            ]),
            ft.Divider(),
            image_widget,
            ft.Container(height=10),
            ft.Text(f"ID: {product.get('id')}", size=14, color=ft.Colors.GREY_700),
            ft.Text(f"Ürün Adı: {product.get('name')}", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"Kategori: {category_name}", size=14),
            ft.Text(f"Fiyat: ₺{product.get('price', 0):.2f}", size=16, color=ft.Colors.GREEN),
            ft.Text(f"Stok: {product.get('stock_quantity', 0)} {product.get('unit', 'adet')}", size=14),
            ft.Container(height=10),
            ft.Text("Açıklama:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(product.get('description', 'Açıklama yok'), size=14, color=ft.Colors.GREY_700),
            ft.Container(height=20),
            ft.Row([
                ft.TextButton("Kapat", on_click=lambda e: self.modal_manager.close_modal())
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
        
        self.modal_manager.show_modal(details, title="Ürün Detayları")
    
    def show_add_product_form(self):
        """Show add product form"""
        name_field = ft.TextField(label="Ürün Adı *", hint_text="Ürün adını girin")
        description_field = ft.TextField(
            label="Açıklama",
            hint_text="Ürün açıklaması",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        price_field = ft.TextField(label="Fiyat *", hint_text="0.00", keyboard_type=ft.KeyboardType.NUMBER)
        stock_field = ft.TextField(label="Stok Miktarı *", hint_text="0", keyboard_type=ft.KeyboardType.NUMBER, value="0")
        unit_field = ft.Dropdown(
            label="Birim *",
            options=[
                ft.dropdown.Option("adet", "Adet"),
                ft.dropdown.Option("kg", "Kilogram"),
                ft.dropdown.Option("gram", "Gram"),
                ft.dropdown.Option("litre", "Litre"),
                ft.dropdown.Option("ml", "Mililitre"),
            ],
            value="adet"
        )
        
        category_options = [ft.dropdown.Option("", "Kategorisiz")]
        for cat in self.categories:
            category_options.append(ft.dropdown.Option(str(cat.get('id')), cat.get('name')))
        
        category_field = ft.Dropdown(
            label="Kategori",
            options=category_options,
            value=""
        )
        
        # Image upload components
        selected_file_path = None
        uploaded_image_url = None
        
        image_preview = ft.Container(
            content=ft.Icon(ft.Icons.IMAGE, size=80, color=ft.Colors.GREY_400),
            width=150,
            height=150,
            bgcolor=ft.Colors.GREY_200,
            border_radius=10,
            alignment=ft.alignment.center
        )
        
        file_name_text = ft.Text("Dosya seçilmedi", size=12, color=ft.Colors.GREY_600, italic=True)
        
        def on_file_picked(e: ft.FilePickerResultEvent):
            nonlocal selected_file_path
            if e.files and len(e.files) > 0:
                selected_file_path = e.files[0].path
                file_name_text.value = e.files[0].name
                file_name_text.color = ft.Colors.GREEN
                file_name_text.italic = False
                
                # Show preview
                try:
                    image_preview.content = ft.Image(
                        src=selected_file_path,
                        width=150,
                        height=150,
                        fit=ft.ImageFit.COVER,
                        border_radius=10
                    )
                except:
                    pass
                
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        def upload_image(e):
            nonlocal uploaded_image_url
            if not selected_file_path:
                self.notification_manager.show_error("Lütfen önce bir resim seçin")
                return
            
            try:
                # Upload image
                with open(selected_file_path, 'rb') as f:
                    result = self.api_service.upload_image(f)
                    uploaded_image_url = result.get('url')
                    self.notification_manager.show_success("Resim başarıyla yüklendi")
                    file_name_text.value = f"✓ Yüklendi: {file_name_text.value}"
                    file_name_text.color = ft.Colors.BLUE
                    self.page.update()
            except Exception as ex:
                self.notification_manager.show_error(f"Resim yüklenemedi: {ex}")
        
        image_url_field = ft.TextField(
            label="Veya Görsel URL Girin",
            hint_text="https://...",
            helper_text="Bilgisayarınızdan resim seçin veya URL girin"
        )
        
        def save_product(e):
            # Validation
            if not name_field.value:
                self.notification_manager.show_error("Ürün adı gerekli")
                return
            
            if not price_field.value:
                self.notification_manager.show_error("Fiyat gerekli")
                return
            
            try:
                price = float(price_field.value)
                if price < 0:
                    self.notification_manager.show_error("Fiyat negatif olamaz")
                    return
            except ValueError:
                self.notification_manager.show_error("Geçersiz fiyat")
                return
            
            try:
                stock = int(stock_field.value) if stock_field.value else 0
                if stock < 0:
                    self.notification_manager.show_error("Stok negatif olamaz")
                    return
            except ValueError:
                self.notification_manager.show_error("Geçersiz stok miktarı")
                return
            
            # Determine image URL (uploaded image takes priority)
            final_image_url = uploaded_image_url or image_url_field.value or None
            
            # Prepare data
            product_data = {
                "name": name_field.value,
                "description": description_field.value or None,
                "price": price,
                "stock_quantity": stock,
                "unit": unit_field.value,
                "category_id": int(category_field.value) if category_field.value else None,
                "image_url": final_image_url
            }
            
            try:
                self.api_service.create_product(product_data)
                self.notification_manager.show_success("Ürün başarıyla eklendi")
                self.modal_manager.close_modal()
                self.load_data()
            except Exception as ex:
                self.notification_manager.show_error(f"Ürün eklenemedi: {ex}")
        
        form = ft.Column([
            name_field,
            description_field,
            ft.Row([price_field, stock_field], spacing=10),
            ft.Row([unit_field, category_field], spacing=10),
            ft.Divider(),
            ft.Text("Ürün Görseli", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([
                image_preview,
                ft.Column([
                    file_name_text,
                    ft.Container(height=5),
                    ft.ElevatedButton(
                        "Bilgisayardan Seç",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda e: file_picker.pick_files(
                            allowed_extensions=["jpg", "jpeg", "png", "gif", "webp"],
                            dialog_title="Ürün Resmi Seç"
                        )
                    ),
                    ft.ElevatedButton(
                        "Yükle",
                        icon=ft.Icons.CLOUD_UPLOAD,
                        on_click=upload_image,
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE
                    )
                ], spacing=5)
            ], spacing=15),
            image_url_field,
            ft.Container(height=20),
            ft.Row([
                ft.TextButton("İptal", on_click=lambda e: self.modal_manager.close_modal()),
                ft.ElevatedButton("Kaydet", on_click=save_product, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.END, spacing=10)
        ], spacing=10, scroll=ft.ScrollMode.AUTO, height=600)
        
        self.modal_manager.show_modal(form, title="Yeni Ürün Ekle", width=700)
    
    def edit_product(self, product):
        """Edit product"""
        name_field = ft.TextField(label="Ürün Adı *", value=product.get('name', ''))
        description_field = ft.TextField(
            label="Açıklama",
            value=product.get('description', ''),
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        price_field = ft.TextField(label="Fiyat *", value=str(product.get('price', 0)), keyboard_type=ft.KeyboardType.NUMBER)
        stock_field = ft.TextField(label="Stok Miktarı *", value=str(product.get('stock_quantity', 0)), keyboard_type=ft.KeyboardType.NUMBER)
        unit_field = ft.Dropdown(
            label="Birim *",
            options=[
                ft.dropdown.Option("adet", "Adet"),
                ft.dropdown.Option("kg", "Kilogram"),
                ft.dropdown.Option("gram", "Gram"),
                ft.dropdown.Option("litre", "Litre"),
                ft.dropdown.Option("ml", "Mililitre"),
            ],
            value=product.get('unit', 'adet')
        )
        
        category_options = [ft.dropdown.Option("", "Kategorisiz")]
        for cat in self.categories:
            category_options.append(ft.dropdown.Option(str(cat.get('id')), cat.get('name')))
        
        category_field = ft.Dropdown(
            label="Kategori",
            options=category_options,
            value=str(product.get('category_id', '')) if product.get('category_id') else ""
        )
        
        # Image upload components
        selected_file_path = None
        uploaded_image_url = None
        current_image_url = product.get('image_url', '')
        
        # Show current image or placeholder
        if current_image_url:
            image_preview = ft.Container(
                content=ft.Image(
                    src=current_image_url,
                    width=150,
                    height=150,
                    fit=ft.ImageFit.COVER,
                    border_radius=10
                ),
                width=150,
                height=150,
                border_radius=10
            )
        else:
            image_preview = ft.Container(
                content=ft.Icon(ft.Icons.IMAGE, size=80, color=ft.Colors.GREY_400),
                width=150,
                height=150,
                bgcolor=ft.Colors.GREY_200,
                border_radius=10,
                alignment=ft.alignment.center
            )
        
        file_name_text = ft.Text("Mevcut resim" if current_image_url else "Dosya seçilmedi", size=12, color=ft.Colors.GREY_600, italic=True)
        
        def on_file_picked(e: ft.FilePickerResultEvent):
            nonlocal selected_file_path
            if e.files and len(e.files) > 0:
                selected_file_path = e.files[0].path
                file_name_text.value = e.files[0].name
                file_name_text.color = ft.Colors.GREEN
                file_name_text.italic = False
                
                # Show preview
                try:
                    image_preview.content = ft.Image(
                        src=selected_file_path,
                        width=150,
                        height=150,
                        fit=ft.ImageFit.COVER,
                        border_radius=10
                    )
                except:
                    pass
                
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        def upload_image(e):
            nonlocal uploaded_image_url
            if not selected_file_path:
                self.notification_manager.show_error("Lütfen önce bir resim seçin")
                return
            
            try:
                # Upload image
                with open(selected_file_path, 'rb') as f:
                    result = self.api_service.upload_image(f)
                    uploaded_image_url = result.get('url')
                    self.notification_manager.show_success("Resim başarıyla yüklendi")
                    file_name_text.value = f"✓ Yüklendi: {file_name_text.value}"
                    file_name_text.color = ft.Colors.BLUE
                    self.page.update()
            except Exception as ex:
                self.notification_manager.show_error(f"Resim yüklenemedi: {ex}")
        
        image_url_field = ft.TextField(
            label="Veya Görsel URL Girin",
            value=current_image_url,
            hint_text="https://...",
            helper_text="Bilgisayarınızdan resim seçin veya URL girin"
        )
        
        def update_product(e):
            # Validation
            if not name_field.value:
                self.notification_manager.show_error("Ürün adı gerekli")
                return
            
            if not price_field.value:
                self.notification_manager.show_error("Fiyat gerekli")
                return
            
            try:
                price = float(price_field.value)
                if price < 0:
                    self.notification_manager.show_error("Fiyat negatif olamaz")
                    return
            except ValueError:
                self.notification_manager.show_error("Geçersiz fiyat")
                return
            
            try:
                stock = int(stock_field.value) if stock_field.value else 0
                if stock < 0:
                    self.notification_manager.show_error("Stok negatif olamaz")
                    return
            except ValueError:
                self.notification_manager.show_error("Geçersiz stok miktarı")
                return
            
            # Determine image URL (uploaded image takes priority, then URL field, then keep current)
            final_image_url = uploaded_image_url or image_url_field.value or current_image_url or None
            
            # Prepare data
            product_data = {
                "name": name_field.value,
                "description": description_field.value or None,
                "price": price,
                "stock_quantity": stock,
                "unit": unit_field.value,
                "category_id": int(category_field.value) if category_field.value else None,
                "image_url": final_image_url
            }
            
            try:
                self.api_service.update_product(product['id'], product_data)
                self.notification_manager.show_success("Ürün başarıyla güncellendi")
                self.modal_manager.close_modal()
                self.load_data()
            except Exception as ex:
                self.notification_manager.show_error(f"Ürün güncellenemedi: {ex}")
        
        form = ft.Column([
            name_field,
            description_field,
            ft.Row([price_field, stock_field], spacing=10),
            ft.Row([unit_field, category_field], spacing=10),
            ft.Divider(),
            ft.Text("Ürün Görseli", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([
                image_preview,
                ft.Column([
                    file_name_text,
                    ft.Container(height=5),
                    ft.ElevatedButton(
                        "Bilgisayardan Seç",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda e: file_picker.pick_files(
                            allowed_extensions=["jpg", "jpeg", "png", "gif", "webp"],
                            dialog_title="Ürün Resmi Seç"
                        )
                    ),
                    ft.ElevatedButton(
                        "Yükle",
                        icon=ft.Icons.CLOUD_UPLOAD,
                        on_click=upload_image,
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE
                    )
                ], spacing=5)
            ], spacing=15),
            image_url_field,
            ft.Container(height=20),
            ft.Row([
                ft.TextButton("İptal", on_click=lambda e: self.modal_manager.close_modal()),
                ft.ElevatedButton("Güncelle", on_click=update_product, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.END, spacing=10)
        ], spacing=10, scroll=ft.ScrollMode.AUTO, height=600)
        
        self.modal_manager.show_modal(form, title=f"Ürün Düzenle: {product.get('name')}", width=700)
    
    def delete_product(self, product):
        """Delete product"""
        def confirm_delete(e):
            try:
                self.api_service.delete_product(product['id'])
                self.notification_manager.show_success("Ürün başarıyla silindi")
                self.load_data()
            except Exception as ex:
                self.notification_manager.show_error(f"Ürün silinemedi: {ex}")
        
        self.modal_manager.show_confirmation(
            f"'{product.get('name')}' ürününü silmek istediğinizden emin misiniz?",
            confirm_delete
        )