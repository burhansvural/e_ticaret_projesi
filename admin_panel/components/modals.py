"""
Modal Manager Component
"""

import flet as ft


class ModalManager:
    """Manages modal dialogs"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_modal = None
    
    def show_modal(self, content: ft.Control, title: str = "", width: int = 600):
        """Show modal dialog"""
        def close_modal(e):
            self.close_modal()
        
        modal_content = ft.Container(
            content=ft.Column([
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
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            width=width,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10
        )
        
        overlay = ft.Container(
            content=modal_content,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True,
            on_click=lambda e: self.close_modal() if e.control == overlay else None
        )
        
        self.current_modal = overlay
        self.page.overlay.append(overlay)
        self.page.update()
    
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
        if self.current_modal and self.current_modal in self.page.overlay:
            self.page.overlay.remove(self.current_modal)
            self.current_modal = None
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