import flet as ft
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

class OrdersView(ft.View):
    def __init__(self, app):
        self.app = app
        
        super().__init__(
            route="/orders",
            controls=[self.build()],
            padding=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    def build(self):
        # Kullanıcı giriş kontrolü
        if not self.app.current_user:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LOGIN, size=100, color=ft.Colors.GREY_400),
                    ft.Text("Siparişlerinizi Görüntülemek İçin Giriş Yapın", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    ft.Text("Sipariş geçmişinizi ve durumlarını takip etmek için hesabınıza giriş yapmanız gerekiyor.", size=16, color=ft.Colors.GREY_500),
                    ft.ElevatedButton(
                        text="Giriş Yap",
                        icon=ft.Icons.LOGIN,
                        on_click=lambda e: self.app.page.go("/auth"),
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
        
        # Sipariş listesi konteynerı
        self.orders_container = ft.Column([], spacing=15)
        
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
                        ft.Text("Siparişlerim", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            on_click=lambda e: self.load_orders(),
                            tooltip="Yenile"
                        ),
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Sipariş listesi
                self.orders_container
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def did_mount(self):
        """Sayfa yüklendiğinde çalışır"""
        self.load_orders()
    
    def load_orders(self):
        """Kullanıcının siparişlerini yükle"""
        if not self.app.current_user:
            return
        
        try:
            # Tüm siparişleri al ve kullanıcıya ait olanları filtrele
            response = requests.get(f"{API_URL}/orders/", timeout=10)
            response.raise_for_status()
            all_orders = response.json()
            
            # Kullanıcının siparişlerini filtrele
            user_orders = [order for order in all_orders if order.get('owner_id') == self.app.current_user['id']]
            
            # Siparişleri tarihe göre sırala (en yeni önce)
            user_orders.sort(key=lambda x: x.get('created_date', ''), reverse=True)
            
            self.orders_container.controls.clear()
            
            if not user_orders:
                self.orders_container.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.SHOPPING_BAG_OUTLINED, size=80, color=ft.Colors.GREY_400),
                            ft.Text("Henüz Siparişiniz Yok", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                            ft.Text("İlk siparişinizi vermek için alışverişe başlayın!", size=14, color=ft.Colors.GREY_500),
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
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                        alignment=ft.alignment.center,
                        padding=50
                    )
                )
            else:
                for order in user_orders:
                    self.orders_container.controls.append(self.create_order_card(order))
            
            self.update()
            
        except Exception as e:
            self.orders_container.controls.clear()
            self.orders_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=60, color=ft.Colors.RED_400),
                        ft.Text("Siparişler Yüklenemedi", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600),
                        ft.Text(f"Hata: {str(e)}", size=14, color=ft.Colors.GREY_600),
                        ft.ElevatedButton(
                            text="Tekrar Dene",
                            icon=ft.Icons.REFRESH,
                            on_click=lambda e: self.load_orders()
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center,
                    padding=30
                )
            )
            self.update()
    
    def create_order_card(self, order):
        """Sipariş kartı oluştur"""
        # Tarih formatla
        created_date = order.get('created_date', '')
        if created_date:
            try:
                date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
            except:
                formatted_date = created_date[:16]
        else:
            formatted_date = 'Bilinmiyor'
        
        # Durum rengi ve metni
        status = order.get('status', 'pending')
        status_color = self.get_status_color(status)
        status_text = self.get_status_text(status)
        status_icon = self.get_status_icon(status)
        
        # Ürün sayısı
        item_count = len(order.get('items', []))
        
        return ft.Container(
            content=ft.Column([
                # Üst kısım - Sipariş bilgileri
                ft.Row([
                    ft.Column([
                        ft.Text(f"Sipariş #{order['id']}", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Tarih: {formatted_date}", size=14, color=ft.Colors.GREY_600),
                        ft.Text(f"Ürün Sayısı: {item_count}", size=14, color=ft.Colors.GREY_600),
                    ], spacing=5),
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(status_icon, size=16, color=ft.Colors.WHITE),
                                ft.Text(status_text, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                            ], spacing=5),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=15, vertical=8),
                            border_radius=20
                        ),
                        ft.Text(f"{order.get('total_price', 0):.2f} TL", 
                               size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Durum açıklaması
                ft.Container(
                    content=ft.Text(
                        self.get_status_description(status),
                        size=13,
                        color=ft.Colors.GREY_700
                    ),
                    padding=ft.padding.only(top=10, bottom=10),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    margin=ft.margin.only(top=10)
                ),
                
                # Admin notları (varsa)
                *([ft.Container(
                    content=ft.Column([
                        ft.Text("Admin Notları:", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                        ft.Text(order.get('notes', ''), size=12, color=ft.Colors.BLUE_600)
                    ], spacing=5),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                    margin=ft.margin.only(top=5)
                )] if order.get('notes') else []),
                
                # Alt kısım - Butonlar
                ft.Row([
                    ft.ElevatedButton(
                        text="Detayları Görüntüle",
                        icon=ft.Icons.VISIBILITY,
                        on_click=lambda e, order_id=order['id']: self.show_order_details(order_id),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE
                        )
                    ),
                    ft.Container(expand=True),
                    *([ft.ElevatedButton(
                        text="İptal Et",
                        icon=ft.Icons.CANCEL,
                        on_click=lambda e, order_id=order['id']: self.cancel_order(order_id),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.RED_600,
                            color=ft.Colors.WHITE
                        )
                    )] if status in ['pending', 'preparing'] else [])
                ], spacing=10)
            ], spacing=15),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            )
        )
    
    def get_status_color(self, status):
        """Sipariş durumuna göre renk döndür"""
        status_colors = {
            'pending': ft.Colors.ORANGE_600,
            'preparing': ft.Colors.BLUE_600,
            'ready': ft.Colors.GREEN_600,
            'shipped': ft.Colors.PURPLE_600,
            'delivered': ft.Colors.GREEN_800,
            'cancelled': ft.Colors.RED_600
        }
        return status_colors.get(status, ft.Colors.GREY_600)
    
    def get_status_text(self, status):
        """Sipariş durumunu Türkçe'ye çevir"""
        status_texts = {
            'pending': 'Bekliyor',
            'preparing': 'Hazırlanıyor',
            'ready': 'Hazır',
            'shipped': 'Kargoda',
            'delivered': 'Teslim Edildi',
            'cancelled': 'İptal Edildi'
        }
        return status_texts.get(status, status)
    
    def get_status_icon(self, status):
        """Sipariş durumuna göre ikon döndür"""
        status_icons = {
            'pending': ft.Icons.PENDING,
            'preparing': ft.Icons.KITCHEN,
            'ready': ft.Icons.CHECK_CIRCLE,
            'shipped': ft.Icons.LOCAL_SHIPPING,
            'delivered': ft.Icons.DONE_ALL,
            'cancelled': ft.Icons.CANCEL
        }
        return status_icons.get(status, ft.Icons.HELP)
    
    def get_status_description(self, status):
        """Sipariş durumu açıklaması"""
        descriptions = {
            'pending': 'Siparişiniz alındı ve onay bekliyor.',
            'preparing': 'Siparişiniz hazırlanıyor.',
            'ready': 'Siparişiniz hazır ve kargoya verilmeyi bekliyor.',
            'shipped': 'Siparişiniz kargoya verildi ve yolda.',
            'delivered': 'Siparişiniz başarıyla teslim edildi.',
            'cancelled': 'Siparişiniz iptal edildi.'
        }
        return descriptions.get(status, 'Durum bilinmiyor.')
    
    def show_order_details(self, order_id):
        """Sipariş detaylarını göster"""
        try:
            response = requests.get(f"{API_URL}/orders/{order_id}", timeout=10)
            response.raise_for_status()
            order = response.json()
            
            # Ürün detaylarını oluştur
            items_content = []
            for item in order.get('items', []):
                # Ürün bilgilerini al
                try:
                    product_response = requests.get(f"{API_URL}/products/{item['product_id']}", timeout=5)
                    product = product_response.json() if product_response.status_code == 200 else None
                    product_name = product['name'] if product else f"Ürün #{item['product_id']}"
                    product_image = product.get('image_url', '/static/default_product.png') if product else '/static/default_product.png'
                except:
                    product_name = f"Ürün #{item['product_id']}"
                    product_image = '/static/default_product.png'
                
                # Ürün hazırlık durumu
                is_ready = item.get('preparation_status', False)
                cannot_prepare = item.get('cannot_prepare', False)
                preparation_note = item.get('preparation_note', '')
                cannot_prepare_reason = item.get('cannot_prepare_reason', '')
                
                # Durum belirleme
                if cannot_prepare:
                    status_text = "HAZIRLANAMAZ"
                    status_color = ft.Colors.RED
                    status_icon = ft.Icons.ERROR
                elif is_ready:
                    status_text = "HAZIR"
                    status_color = ft.Colors.GREEN
                    status_icon = ft.Icons.CHECK_CIRCLE
                else:
                    status_text = "HAZIRLANACAK"
                    status_color = ft.Colors.ORANGE
                    status_icon = ft.Icons.SCHEDULE
                
                # Ürün kartı
                item_card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Image(
                                    src=product_image,
                                    width=50,
                                    height=50,
                                    fit=ft.ImageFit.COVER,
                                    border_radius=5
                                ),
                                width=50,
                                height=50,
                                border_radius=5,
                                bgcolor=ft.Colors.GREY_100
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(product_name, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Miktar: {item['quantity']} adet", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(f"Birim Fiyat: {item.get('price', item.get('price_per_item', 0)):.2f} TL", size=12, color=ft.Colors.GREY_600)
                                ], spacing=2),
                                expand=True,
                                padding=ft.padding.only(left=10)
                            ),
                            ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(status_icon, size=14, color=ft.Colors.WHITE),
                                        ft.Text(status_text, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=11)
                                    ], spacing=3),
                                    bgcolor=status_color,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12
                                ),
                                ft.Text(f"{item['quantity'] * item.get('price', item.get('price_per_item', 0)):.2f} TL", 
                                       weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600, size=14)
                            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.END)
                        ]),
                        
                        # Notlar ve açıklamalar (varsa)
                        *([ft.Container(
                            content=ft.Column([
                                ft.Text(f"📝 Hazırlama Notu: {preparation_note}", 
                                       size=12, color=ft.Colors.BLUE_600, italic=True) if preparation_note else ft.Container(),
                                ft.Text(f"⚠️ Hazırlanamama Nedeni: {cannot_prepare_reason}", 
                                       size=12, color=ft.Colors.RED_600, italic=True) if cannot_prepare_reason else ft.Container()
                            ], spacing=3),
                            padding=ft.padding.only(top=8),
                            visible=bool(preparation_note or cannot_prepare_reason)
                        )] if (preparation_note or cannot_prepare_reason) else [])
                    ], spacing=5),
                    padding=12,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    border=ft.border.all(1, status_color if cannot_prepare else ft.Colors.GREY_200),
                    margin=ft.margin.only(bottom=8)
                )
                
                items_content.append(item_card)
            
            # Hazırlık durumu özeti
            ready_count = sum(1 for item in order.get('items', []) if item.get('preparation_status', False))
            cannot_prepare_count = sum(1 for item in order.get('items', []) if item.get('cannot_prepare', False))
            total_items = len(order.get('items', []))
            waiting_count = total_items - ready_count - cannot_prepare_count
            
            # Modal içeriği
            modal_content = ft.Container(
                width=600,
                height=650,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=20,
                content=ft.Column([
                    # Başlık
                    ft.Row([
                        ft.Text(f"Sipariş Detayları - #{order['id']}", 
                               size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e: self.close_modal()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(),
                    
                    # Sipariş durumu
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(self.get_status_icon(order.get('status', 'pending')), 
                                   color=ft.Colors.WHITE, size=20),
                            ft.Text(self.get_status_text(order.get('status', 'pending')), 
                                   color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16)
                        ], spacing=10),
                        bgcolor=self.get_status_color(order.get('status', 'pending')),
                        padding=15,
                        border_radius=10,
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # Hazırlık durumu özeti (sadece hazırlama aşamasındaysa)
                    *([ft.Container(
                        content=ft.Column([
                            ft.Text("Hazırlık Durumu Özeti", size=14, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"✅ Hazır: {ready_count}", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.GREEN,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=10
                                ),
                                ft.Container(
                                    content=ft.Text(f"⏳ Bekliyor: {waiting_count}", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.ORANGE,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=10
                                ),
                                ft.Container(
                                    content=ft.Text(f"❌ Hazırlanamaz: {cannot_prepare_count}", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.Colors.RED,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=10
                                ) if cannot_prepare_count > 0 else ft.Container()
                            ], spacing=8)
                        ], spacing=8),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=12,
                        border_radius=10,
                        margin=ft.margin.only(bottom=15)
                    )] if order.get('status') in ['preparing', 'ready'] else []),
                    
                    # Ürün listesi
                    ft.Text("Sipariş Edilen Ürünler", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.ListView(
                            controls=items_content,
                            spacing=0,
                            padding=ft.padding.all(5)
                        ),
                        height=300,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # Toplam tutar
                    ft.Container(
                        content=ft.Row([
                            ft.Text("TOPLAM TUTAR:", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{order.get('total_price', 0):.2f} TL", 
                                   size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10
                    ),
                    
                    # Kapat butonu
                    ft.Container(
                        content=ft.ElevatedButton(
                            "Kapat",
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e: self.close_modal()
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=15)
                    )
                ], spacing=10, scroll=ft.ScrollMode.AUTO)
            )
            
            self._show_overlay_modal(modal_content)
            
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Sipariş detayları yüklenirken hata: {e}"),
                open=True
            )
            self.page.update()
    
    def cancel_order(self, order_id):
        """Siparişi iptal et"""
        def confirm_cancel(e):
            try:
                update_data = {
                    "status": "cancelled",
                    "notes": "Müşteri tarafından iptal edildi"
                }
                
                response = requests.put(
                    f"{API_URL}/orders/{order_id}",
                    json=update_data,
                    timeout=10
                )
                response.raise_for_status()
                
                self.page.close(dialog)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Siparişiniz başarıyla iptal edildi."),
                    open=True
                )
                self.load_orders()  # Listeyi yenile
                
            except Exception as ex:
                self.page.close(dialog)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Sipariş iptal edilirken hata: {ex}"),
                    open=True
                )
                self.page.update()
        
        def cancel_action(e):
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Siparişi İptal Et"),
            content=ft.Text(f"#{order_id} numaralı siparişinizi iptal etmek istediğinizden emin misiniz?"),
            actions=[
                ft.TextButton("Hayır", on_click=cancel_action),
                ft.ElevatedButton("Evet, İptal Et", on_click=confirm_cancel, 
                                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dialog)
    
    def _show_overlay_modal(self, modal_content):
        """Custom modal overlay göster"""
        # Modal overlay oluştur
        modal_overlay = ft.Container(
            content=ft.Row([
                modal_content
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True,
            on_click=lambda e: self.close_modal()  # Arka plana tıklayınca kapat
        )
        
        # Overlay'i sayfaya ekle
        self.page.overlay.append(modal_overlay)
        self.page.update()
    
    def close_modal(self):
        """Modal'ı kapat"""
        if self.page.overlay:
            self.page.overlay.clear()
            self.page.update()