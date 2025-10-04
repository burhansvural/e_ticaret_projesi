"""
Categories View - Category list and management
"""

import flet as ft

from admin_panel.services import APIService


class CategoriesView:
    """Categories management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
        self.categories = []
    
    def build(self) -> ft.Control:
        """Build categories list UI"""
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
        
        # Categories table
        self.categories_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Kategori Adı")),
                ft.DataColumn(ft.Text("Açıklama")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=[]
        )
        
        table_container = ft.Container(
            content=ft.Column([self.categories_table], scroll=ft.ScrollMode.AUTO),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            header,
            ft.Container(height=20),
            table_container
        ], spacing=10, expand=True)
    
    def load_categories(self):
        """Load categories from API"""
        try:
            self.categories = self.api_service.get_categories()
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Kategoriler yüklenemedi: {e}")
    
    def _update_table(self):
        """Update categories table"""
        self.categories_table.rows.clear()
        
        for category in self.categories:
            self.categories_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(category.get('id', '')))),
                    ft.DataCell(ft.Text(category.get('name', ''))),
                    ft.DataCell(ft.Text(category.get('description', 'N/A'))),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e, c=category: self.edit_category(c)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, c=category: self.delete_category(c)
                            )
                        ], spacing=5)
                    )
                ])
            )
        
        self.page.update()
    
    def show_add_category_form(self):
        """Show add category form"""
        self.notification_manager.show_info("Kategori ekleme formu yakında eklenecek")
    
    def edit_category(self, category):
        """Edit category"""
        self.notification_manager.show_info(f"Kategori düzenleme: {category.get('name')}")
    
    def delete_category(self, category):
        """Delete category"""
        def confirm_delete(e):
            try:
                self.api_service.delete_category(category['id'])
                self.notification_manager.show_success("Kategori silindi")
                self.load_categories()
            except Exception as ex:
                self.notification_manager.show_error(f"Silme hatası: {ex}")
        
        self.modal_manager.show_confirmation(
            f"{category.get('name')} kategorisini silmek istediğinizden emin misiniz?",
            confirm_delete
        )