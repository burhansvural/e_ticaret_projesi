# frontend/src/views/main_view.py
import flet as ft


def MainView(app):
    """Ana ürün vitrini sayfasını oluşturur."""

    app.products_container.controls = [
        ft.Row([ft.ProgressRing(), ft.Text("Ürünler yükleniyor")], alignment=ft.MainAxisAlignment.CENTER)]

    # Kullanıcı durumuna göre buton metni
    if app.current_user:
        # Kullanıcı adını güvenli şekilde al
        full_name = app.current_user.get('full_name', '')
        first_name = full_name.split()[0] if full_name else app.current_user.get('email', 'Kullanıcı')
        
        user_button = ft.PopupMenuButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE),
                ft.Text(f"Merhaba, {first_name}", color=ft.Colors.WHITE)
            ], spacing=5),
            items=[
                ft.PopupMenuItem(text="Profilim", icon=ft.Icons.PERSON),
                ft.PopupMenuItem(
                    text="Siparişlerim", 
                    icon=ft.Icons.SHOPPING_BAG,
                    on_click=lambda _: app.page.go("/orders")
                ),
                ft.PopupMenuItem(),  # Ayırıcı
                ft.PopupMenuItem(
                    text="Çıkış Yap", 
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda _: logout_user(app)
                ),
            ]
        )
        
        # Ek logout icon button (daha görünür)
        logout_icon_button = ft.IconButton(
            ft.Icons.LOGOUT,
            icon_color=ft.Colors.WHITE,
            tooltip="Çıkış Yap",
            on_click=lambda _: logout_user(app)
        )
    else:
        user_button = ft.TextButton(
            "Giriş Yap / Kayıt Ol", 
            icon=ft.Icons.PERSON_OUTLINED, 
            icon_color=ft.Colors.WHITE,
            on_click=lambda _: app.page.go("/auth"),
            style=ft.ButtonStyle(color=ft.Colors.WHITE)
        )
        logout_icon_button = None

    # AppBar actions listesini oluştur
    appbar_actions = [user_button]
    
    # Kullanıcı giriş yapmışsa logout icon button ekle
    if logout_icon_button:
        appbar_actions.append(logout_icon_button)
    
    # Sepet butonu ve sayacını ekle
    appbar_actions.extend([
        ft.IconButton(ft.Icons.SHOPPING_CART_OUTLINED, icon_color=ft.Colors.WHITE,
                      on_click=lambda _: app.page.go("/checkout")),
        app.cart_item_count_text,
        ft.Container(width=10)
    ])

    # Bu View'i döndür
    return ft.View(
        "/",
        [
            ft.AppBar(
                title=ft.Text("Flet Mağaza", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_GREY_800,
                actions=appbar_actions
            ),
            ft.Row([ft.Text("Popüler Ürünler", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                   alignment=ft.MainAxisAlignment.CENTER),
            app.products_container,
        ]
    )

def logout_user(app):
    """Kullanıcı çıkışı yap"""
    from ..api import logout_user_api
    
    # Backend'e logout isteği gönder
    if app.current_user and app.current_user.get('access_token'):
        result = logout_user_api(
            access_token=app.current_user.get('access_token'),
            refresh_token=app.current_user.get('refresh_token')
        )
        
        if result["success"]:
            # Başarılı çıkış
            app.current_user = None
            app.page.snack_bar.content = ft.Text("Başarıyla çıkış yaptınız.", color=ft.Colors.WHITE)
            app.page.snack_bar.bgcolor = ft.Colors.GREEN
        else:
            # Hata durumunda da kullanıcıyı çıkart (güvenlik için)
            app.current_user = None
            app.page.snack_bar.content = ft.Text("Çıkış yapıldı (bağlantı hatası).", color=ft.Colors.WHITE)
            app.page.snack_bar.bgcolor = ft.Colors.ORANGE
    else:
        # Token yoksa sadece local çıkış yap
        app.current_user = None
        app.page.snack_bar.content = ft.Text("Çıkış yapıldı.", color=ft.Colors.WHITE)
        app.page.snack_bar.bgcolor = ft.Colors.GREEN
    
    app.page.snack_bar.open = True
    app.page.update()
    app.page.go("/")  # Ana sayfayı yenile
    app.route_change("/")  # Ana sayfayı yeniden yükle