# frontend/main.py
import flet as ft
from src.app import ECommerceApp

def main(page: ft.Page):
    ECommerceApp(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP, assets_dir="assets")