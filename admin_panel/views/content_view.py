"""
Content Management Views
"""

import flet as ft
from admin_panel.services import APIService


class BlogPostsView:
    """Blog posts management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build blog posts UI"""
        # Posts table
        posts_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Başlık", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Yazar", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Kategori", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tarih", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Blog Yazıları", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Yazı",
                    icon=ft.Icons.ADD,
                    on_click=self.create_post
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=posts_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load blog posts data"""
        pass
    
    def create_post(self, e):
        """Create new blog post"""
        self.notification_manager.show_info("Blog yazısı oluşturma özelliği yakında eklenecek")


class PagesView:
    """Pages management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build pages UI"""
        # Pages list
        pages_list = ft.ListView(
            spacing=10,
            controls=[
                self._create_page_card("Hakkımızda", "/about", "Yayında"),
                self._create_page_card("İletişim", "/contact", "Yayında"),
                self._create_page_card("Gizlilik Politikası", "/privacy", "Yayında"),
                self._create_page_card("Kullanım Koşulları", "/terms", "Yayında"),
            ]
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Sayfalar", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Sayfa",
                    icon=ft.Icons.ADD,
                    on_click=self.create_page
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=pages_list,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_page_card(self, title: str, url: str, status: str) -> ft.Container:
        """Create page card"""
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(url, size=12, color=ft.Colors.GREY_600),
                ], spacing=5),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(status, color=ft.Colors.WHITE, size=12),
                    bgcolor=ft.Colors.GREEN,
                    padding=5,
                    border_radius=5
                ),
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Düzenle"),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="Sil", icon_color=ft.Colors.RED),
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
        )
    
    def load_data(self):
        """Load pages data"""
        pass
    
    def create_page(self, e):
        """Create new page"""
        self.notification_manager.show_info("Sayfa oluşturma özelliği yakında eklenecek")


class FAQView:
    """FAQ management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build FAQ UI"""
        # FAQ list
        faq_list = ft.ListView(spacing=10)
        
        return ft.Column([
            ft.Row([
                ft.Text("Sık Sorulan Sorular", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Soru Ekle",
                    icon=ft.Icons.ADD,
                    on_click=self.add_faq
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=faq_list,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load FAQ data"""
        pass
    
    def add_faq(self, e):
        """Add new FAQ"""
        self.notification_manager.show_info("Soru ekleme özelliği yakında eklenecek")


class MediaLibraryView:
    """Media library view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build media library UI"""
        # Media grid
        media_grid = ft.GridView(
            expand=True,
            runs_count=4,
            max_extent=200,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Medya Kütüphanesi", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Dosya Yükle",
                    icon=ft.Icons.UPLOAD,
                    on_click=self.upload_file
                ),
            ]),
            ft.Container(height=20),
            ft.Row([
                ft.TextField(label="Ara", prefix_icon=ft.Icons.SEARCH, width=300),
                ft.Dropdown(
                    label="Tür",
                    width=150,
                    options=[
                        ft.dropdown.Option("all", "Tümü"),
                        ft.dropdown.Option("image", "Resim"),
                        ft.dropdown.Option("video", "Video"),
                        ft.dropdown.Option("document", "Doküman"),
                    ],
                    value="all"
                ),
            ], spacing=10),
            ft.Container(height=20),
            ft.Container(
                content=media_grid,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load media library data"""
        pass
    
    def upload_file(self, e):
        """Upload new file"""
        self.notification_manager.show_info("Dosya yükleme özelliği yakında eklenecek")