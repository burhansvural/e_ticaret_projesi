"""
Notification Manager Component
"""

import flet as ft


class NotificationManager:
    """Manages notifications (success, error, info, warning)"""
    
    def __init__(self, page: ft.Page):
        self.page = page
    
    def show_snackbar(self, message: str, bgcolor: str):
        """Show snackbar notification"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=bgcolor,
            duration=3000
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()
    
    def show_success(self, message: str):
        """Show success notification"""
        self.show_snackbar(message, ft.Colors.GREEN)
    
    def show_error(self, message: str):
        """Show error notification"""
        self.show_snackbar(message, ft.Colors.RED)
    
    def show_info(self, message: str):
        """Show info notification"""
        self.show_snackbar(message, ft.Colors.BLUE)
    
    def show_warning(self, message: str):
        """Show warning notification"""
        self.show_snackbar(message, ft.Colors.ORANGE)