"""
Categories View - Category list and management
"""

import flet as ft

from admin_panel.services import APIService


class CategoriesView:
    """Categories management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.categories_table = None
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
        self.categories = []
        self.filtered_categories = []
        
        # UI Components
        self.search_field = None
        self.total_categories_text = None
        self.loading_indicator = None
    
    def build(self) -> ft.Control:
        """Build categories list UI"""
        # Header
        header = ft.Row([
            ft.Text("Kategoriler", size=32, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Yeni Kategori Ekle",
                icon=ft.Icons.ADD,
                on_click=lambda e: self.show_add_category_form(),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Search bar
        self.search_field = ft.TextField(
            label="Kategori Ara",
            hint_text="Kategori adı veya açıklama...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.apply_filters(),
            expand=True
        )
        
        search_row = ft.Row([
            self.search_field,
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Yenile",
                on_click=lambda e: self.load_data()
            )
        ], spacing=10)
        
        # Stats
        self.total_categories_text = ft.Text("Toplam: 0 kategori", size=14, color=ft.Colors.GREY_700)
        
        # Categories table
        self.categories_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Kategori Adı", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Açıklama", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Oluşturma Tarihi", weight=ft.FontWeight.BOLD)),
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
                ft.Row([self.total_categories_text, self.loading_indicator], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Column([self.categories_table], scroll=ft.ScrollMode.AUTO, expand=True),
            ], expand=True),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            header,
            ft.Container(height=10),
            search_row,
            ft.Container(height=10),
            table_container
        ], spacing=0, expand=True)
    
    def load_data(self):
        """Load categories from API"""
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            response = self.api_service.get_categories()
            self.categories = response if isinstance(response, list) else []
            self.filtered_categories = self.categories.copy()
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Kategoriler yüklenemedi: {e}")
            self.categories = []
            self.filtered_categories = []
        finally:
            self.loading_indicator.visible = False
            self.page.update()
    
    # Backward compatibility
    def load_categories(self):
        """Load categories from API (legacy method)"""
        self.load_data()
    
    def apply_filters(self):
        """Apply search filter"""
        search_text = self.search_field.value.lower() if self.search_field.value else ""
        
        self.filtered_categories = []
        
        for category in self.categories:
            # Search filter
            if search_text:
                name = category.get('name', '').lower()
                desc = category.get('description', '').lower() if category.get('description') else ''
                if search_text not in name and search_text not in desc:
                    continue
            
            self.filtered_categories.append(category)
        
        self._update_table()
    
    def _update_table(self):
        """Update categories table"""
        self.categories_table.rows.clear()
        
        for category in self.filtered_categories:
            # Format date
            created_at = category.get('created_at', '')
            if created_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime('%d.%m.%Y %H:%M')
                except:
                    date_str = created_at[:10] if len(created_at) >= 10 else created_at
            else:
                date_str = '-'
            
            self.categories_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(category.get('name', ''), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(category.get('description', '-'), max_lines=2)),
                    ft.DataCell(ft.Text(date_str, size=12)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                icon_color=ft.Colors.GREEN,
                                tooltip="Görüntüle",
                                on_click=lambda e, c=category: self.view_category(c)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Düzenle",
                                on_click=lambda e, c=category: self.edit_category(c)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Sil",
                                on_click=lambda e, c=category: self.delete_category(c)
                            )
                        ], spacing=0)
                    )
                ])
            )
        
        # Update stats
        self.total_categories_text.value = f"Toplam: {len(self.filtered_categories)} kategori"
        self.page.update()
    
    def view_category(self, category):
        """View category details"""
        # Format date
        created_at = category.get('created_at', '')
        if created_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = dt.strftime('%d.%m.%Y %H:%M')
            except:
                date_str = created_at[:10] if len(created_at) >= 10 else created_at
        else:
            date_str = '-'
        
        details = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CATEGORY, color=ft.Colors.BLUE),
                ft.Text("Kategori Detayları", size=20, weight=ft.FontWeight.BOLD)
            ]),
            ft.Divider(),
            ft.Container(height=10),
            ft.Text(f"ID: {category.get('id')}", size=14, color=ft.Colors.GREY_700),
            ft.Text(f"Kategori Adı: {category.get('name')}", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text("Açıklama:", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(category.get('description', 'Açıklama yok'), size=14, color=ft.Colors.GREY_700),
            ft.Container(height=10),
            ft.Text(f"Oluşturma Tarihi: {date_str}", size=12, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            ft.Row([
                ft.TextButton("Kapat", on_click=lambda e: self.modal_manager.close_modal())
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
        
        self.modal_manager.show_modal(details, title="Kategori Detayları")
    
    def show_add_category_form(self):
        """Show add category form"""
        name_field = ft.TextField(
            label="Kategori Adı *",
            hint_text="Kategori adını girin",
            autofocus=True
        )
        description_field = ft.TextField(
            label="Açıklama",
            hint_text="Kategori açıklaması (opsiyonel)",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        def save_category(e):
            # Validation
            if not name_field.value or not name_field.value.strip():
                self.notification_manager.show_error("Kategori adı gerekli")
                return
            
            # Prepare data
            category_data = {
                "name": name_field.value.strip(),
                "description": description_field.value.strip() if description_field.value else None
            }
            
            try:
                self.api_service.create_category(category_data)
                self.notification_manager.show_success("Kategori başarıyla eklendi")
                self.modal_manager.close_modal()
                self.load_data()
            except Exception as ex:
                self.notification_manager.show_error(f"Kategori eklenemedi: {ex}")
        
        form = ft.Column([
            name_field,
            description_field,
            ft.Container(height=20),
            ft.Row([
                ft.TextButton("İptal", on_click=lambda e: self.modal_manager.close_modal()),
                ft.ElevatedButton("Kaydet", on_click=save_category, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.END, spacing=10)
        ], spacing=10, scroll=ft.ScrollMode.AUTO, height=300)
        
        self.modal_manager.show_modal(form, title="Yeni Kategori Ekle")
    
    def edit_category(self, category):
        """Edit category"""
        name_field = ft.TextField(
            label="Kategori Adı *",
            value=category.get('name', ''),
            autofocus=True
        )
        description_field = ft.TextField(
            label="Açıklama",
            value=category.get('description', ''),
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        def update_category(e):
            # Validation
            if not name_field.value or not name_field.value.strip():
                self.notification_manager.show_error("Kategori adı gerekli")
                return
            
            # Prepare data
            category_data = {
                "name": name_field.value.strip(),
                "description": description_field.value.strip() if description_field.value else None
            }
            
            try:
                self.api_service.update_category(category['id'], category_data)
                self.notification_manager.show_success("Kategori başarıyla güncellendi")
                self.modal_manager.close_modal()
                self.load_data()
            except Exception as ex:
                self.notification_manager.show_error(f"Kategori güncellenemedi: {ex}")
        
        form = ft.Column([
            name_field,
            description_field,
            ft.Container(height=20),
            ft.Row([
                ft.TextButton("İptal", on_click=lambda e: self.modal_manager.close_modal()),
                ft.ElevatedButton("Güncelle", on_click=update_category, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.END, spacing=10)
        ], spacing=10, scroll=ft.ScrollMode.AUTO, height=300)
        
        self.modal_manager.show_modal(form, title=f"Kategori Düzenle: {category.get('name')}")
    
    def delete_category(self, category):
        """Delete category"""
        def confirm_delete(e):
            try:
                self.api_service.delete_category(category['id'])
                self.notification_manager.show_success("Kategori başarıyla silindi")
                self.load_data()
            except Exception as ex:
                self.notification_manager.show_error(f"Kategori silinemedi: {ex}")
        
        self.modal_manager.show_confirmation(
            f"'{category.get('name')}' kategorisini silmek istediğinizden emin misiniz?\n\nBu kategoriye ait ürünler kategorisiz olarak işaretlenecektir.",
            confirm_delete,
            title="Kategori Sil"
        )