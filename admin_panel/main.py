"""
E-Ticaret Admin Panel
Main Entry Point
"""
import sys
from pathlib import Path

# Add parent directory to path for proper imports
sys.path.insert(0, str(Path(__file__).parent))

import flet as ft
from core.app import AdminPanel


def main(page: ft.Page):
    """Main application entry point"""
    AdminPanel(page)


if __name__ == "__main__":
    ft.app(target=main)