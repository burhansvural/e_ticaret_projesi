"""
Modal Manager Component
"""

import flet as ft


class ModalManager:
    """Manages modal dialogs"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_modal = None
        self.modal_focusable_controls = []  # Modal içindeki focusable kontroller
        self.current_focus_index = 0
        self.original_keyboard_handler = None
    
    def _handle_keyboard_event(self, e: ft.KeyboardEvent):
        """Tab tuşu basıldığında odak döngüsünü yönetir."""
        
        # Eğer modal açık değilse veya klavye olayı Tab değilse müdahale etme
        if not self.current_modal or e.key != "Tab":
            # Geri kalan olayların normal akışına izin ver
            return
            
        if not self.modal_focusable_controls:
            # Odaklanacak bir şey yoksa sadece varsayılan davranışı engelle
            e.handled = True 
            return
        
        # Odaklanma olayını yakaladık, Flet'in varsayılan davranışını durdur
        e.handled = True 
        
        num_controls = len(self.modal_focusable_controls)

        if e.shift:
            # Shift + Tab (Geriye doğru)
            self.current_focus_index = (self.current_focus_index - 1) % num_controls
        else:
            # Tab (İleriye doğru)
            self.current_focus_index = (self.current_focus_index + 1) % num_controls
        
        # Yeni kontrole odaklan
        control_to_focus = self.modal_focusable_controls[self.current_focus_index]
        
        try:
            # Eğer kontrolün focus metodu varsa odaklan
            if hasattr(control_to_focus, 'focus'):
                control_to_focus.focus()
            
            self.page.update()
        except Exception as ex:
            # Nadiren focus çağrısı sırasında Flet/Flutter hatası alınabilir
            print(f"Hata oluştu: Focuslama başarısız oldu: {ex}")
    
    def _setup_keyboard_handling(self, modal_content_control: ft.Control):
        """Klavye işleyicisini kurar ve odaklanabilir kontrolleri toplar."""
        
        # 1. Odaklanabilir kontrolleri topla
        form_fields, buttons = self._collect_focusable_controls(modal_content_control)
        
        # Close Button'ı belirle
        close_button = None
        try:
            # İlk row'daki IconButton'ı bulmaya çalış
            first_row = modal_content_control.controls[0]
            close_button = next((c for c in first_row.controls if isinstance(c, ft.IconButton)), None)
        except:
            pass  # Eğer ilk kontrol bir Row değilse
        
        # Close Button'ı butonlar listesinden çıkar (eğer oradaysa)
        if close_button and close_button in buttons:
            buttons.remove(close_button)
        
        # Odak sırası: [Tüm Form Alanları] + [Tüm Diğer Butonlar] + [Close Button (en son)]
        # İlk odaklanılacak eleman artık ilk TextField olacak
        self.modal_focusable_controls = form_fields + buttons
        
        # Close butonu varsa, onu döngüye dahil et (En sona)
        if close_button:
            self.modal_focusable_controls.append(close_button)

        self.current_focus_index = 0
        
        # 2. Klavye işleyicisini devral
        self.original_keyboard_handler = self.page.on_keyboard_event
        self.page.on_keyboard_event = self._handle_keyboard_event
        
        # 3. İlk kontrole odaklan (eğer varsa)
        if self.modal_focusable_controls:
            # İlk elemente focus al (artık ilk TextField olmalı)
            self.modal_focusable_controls[0].focus()
            # Gerekirse focus'un işlenmesi için hemen update çağrısı
            self.page.update()
    
    def show_modal(self, content: ft.Control, title: str = "", width: int = 600):
        """Show modal dialog"""
        def close_modal(e=None):
            # Tıklama olayı tetiklendiğinde emin olmak için
            self.close_modal()
        
        # Önemli: Close butonu, modalın içindeki ana sütun yapısında yer alıyor.
        modal_column_content = ft.Column([
            ft.Row([
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD) if title else ft.Container(),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    on_click=close_modal,
                    icon_color=ft.Colors.RED
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            content
        ], spacing=10, tight=True)

        modal_container = ft.Container(
            content=modal_column_content,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=20,
            width=width,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)
            )
        )
        
        overlay = ft.Container(
            content=ft.Stack([
                ft.GestureDetector(
                    content=ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                        expand=True
                    ),
                    on_tap=close_modal  # Arka plana tıklama ile kapatma
                ),
                ft.Container(
                    content=modal_container,
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]),
            expand=True
        )
        
        self.current_modal = overlay
        self.page.overlay.append(overlay)
        # Önce modalı ekle ve sayfayı güncelle
        self.page.update()
        
        # Ardından klavye işleyicisini kur ve odaklanmayı zorla
        self._setup_keyboard_handling(modal_column_content)
    
    def _collect_focusable_controls(self, control, form_fields=None, buttons=None):
        """Modal içindeki focusable kontrolleri topla (TextField, Dropdown, Button, vb.)"""
        # İlk çağrıda listeleri oluştur
        if form_fields is None:
            form_fields = []
        if buttons is None:
            buttons = []
        
        # Sadece focusable olan, görünür ve etkin kontrolleri al
        if hasattr(control, 'visible') and not control.visible:
            return form_fields, buttons
        
        # Form alanları (TextField, Dropdown) - öncelikli
        form_field_types = (ft.TextField, ft.Dropdown, ft.Checkbox, ft.Switch, ft.Radio)
        # Butonlar - sonra gelecek (IconButton da dahil)
        button_types = (ft.ElevatedButton, ft.TextButton, ft.IconButton, ft.OutlinedButton, ft.FilledButton)
        
        is_disabled = hasattr(control, 'disabled') and control.disabled
        has_focus_method = hasattr(control, 'focus')

        if not is_disabled and has_focus_method:
            if isinstance(control, form_field_types):
                form_fields.append(control)
            elif isinstance(control, button_types):
                buttons.append(control)
        
        # Kontrolün içeriği veya çocukları varsa özyinelemeli olarak kontrol et
        if hasattr(control, 'content') and control.content:
            self._collect_focusable_controls(control.content, form_fields, buttons)
        
        if hasattr(control, 'controls') and control.controls:
            for child in control.controls:
                self._collect_focusable_controls(child, form_fields, buttons)
        
        return form_fields, buttons
    
    def show_overlay_modal(self, content: ft.Control):
        """Show overlay modal (full screen)"""
        def close_modal(e):
            self.close_modal()
        
        overlay = ft.Container(
            content=ft.Stack([
                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                    expand=True,
                    on_click=close_modal
                ),
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]),
            expand=True
        )
        
        self.current_modal = overlay
        self.page.overlay.append(overlay)
        self.page.update()
    
    def close_modal(self):
        """Close current modal"""
        if self.current_modal:
            if self.current_modal in self.page.overlay:
                self.page.overlay.remove(self.current_modal)
            
            self.current_modal = None
            
            # Klavye handler'ını eski haline döndür
            self.page.on_keyboard_event = self.original_keyboard_handler
            self.original_keyboard_handler = None
            
            # Focusable kontrolleri temizle
            self.modal_focusable_controls = []
            self.current_focus_index = 0
            
            self.page.update()
    
    def show_confirmation(self, message: str, on_confirm, on_cancel=None, title: str = "Onay"):
        """Show confirmation dialog"""
        def handle_confirm(e):
            self.close_modal()
            if on_confirm:
                on_confirm(e)
        
        def handle_cancel(e):
            self.close_modal()
            if on_cancel:
                on_cancel(e)
        
        content = ft.Column([
            ft.Text(message, size=16),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "İptal",
                    on_click=handle_cancel,
                    bgcolor=ft.Colors.GREY,
                    color=ft.Colors.WHITE
                ),
                ft.ElevatedButton(
                    "Onayla",
                    on_click=handle_confirm,
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE
                )
            ], alignment=ft.MainAxisAlignment.END, spacing=10)
        ], spacing=10)
        
        self.show_modal(content, title, width=400)