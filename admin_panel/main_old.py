import flet as ft
import requests
import base64

API_URL = "http://127.0.0.1:8000"
UPLOAD_URL = f"{API_URL}/upload-image/"


def main(page: ft.Page):
    page.title = "E-Ticaret Admin Paneli"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 800
    page.window_height = 800

    # --- DURUM YÖNETİMİ (STATE) ---
    # Hangi ürünün düzenlendiğini tutmak için. None ise ekleme modundayız.
    editing_product_id = ft.TextField(visible=False, value=None)

    # --- KONTROLLER ---
    product_name_input = ft.TextField(label="Ürün Adı", width=300)
    product_desc_input = ft.TextField(label="Açıklama", width=300)
    product_price_input = ft.TextField(label="Fiyat", width=150, prefix_text="TL")
    uploaded_image_url = ft.TextField(visible=False)

    def create_placeholder():
        return ft.Column([ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=40, color=ft.Colors.GREY_500),
                          ft.Text("Seçili Resim Yok.", color=ft.Colors.GREY_500)],
                         alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                         spacing=5)

    image_container = ft.Container(width=150, height=150, border=ft.border.all(2, ft.Colors.GREY_400),
                                   border_radius=ft.border_radius.all(10), content=create_placeholder(),
                                   alignment=ft.alignment.center)
    products_list = ft.ListView(expand=True, spacing=10, padding=20)

    # --- FONKSİYONLAR ---
    def load_products(e=None):
        try:
            response = requests.get(f"{API_URL}/products/", timeout=5)
            response.raise_for_status()
            products_data = response.json()
            products_list.controls.clear()
            if not products_data:
                products_list.controls.append(ft.Text("Henüz ürün eklenmemiş."))
            else:
                for product in products_data:
                    products_list.controls.append(
                        ft.Container(content=ft.Row(controls=[
                            ft.Image(src=product.get("image_url"), width=50, height=50, fit=ft.ImageFit.COVER,
                                     border_radius=ft.border_radius.all(5),
                                     error_content=ft.Icon(ft.Icons.NO_PHOTOGRAPHY)),
                            ft.Text(f"ID: {product['id']}", width=50, color=ft.Colors.WHITE),
                            ft.Text(product['name'], weight=ft.FontWeight.BOLD, expand=True, color=ft.Colors.WHITE),
                            ft.Text(f"{product['price']:.2f} TL", text_align=ft.TextAlign.RIGHT, width=100,
                                    color=ft.Colors.WHITE),
                            # --- YENİ: DÜZENLEME BUTONU ---
                            ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.BLUE_400, tooltip="Ürünü Düzenle",
                                          on_click=start_editing_product, data=product),
                            ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Ürünü Sil",
                                          on_click=open_delete_dialog, data=product['id'])
                        ]), padding=10, bgcolor=ft.Colors.ON_SURFACE_VARIANT, border_radius=5)
                    )
            page.update()
        except requests.exceptions.RequestException as ex:
            products_list.controls.clear()
            products_list.controls.append(ft.Text("API'ye bağlanılamadı.", color="red"))
            page.update()

    def delete_product(product_id: int):
        try:
            requests.delete(f"{API_URL}/products/{product_id}").raise_for_status()
            page.snack_bar = ft.SnackBar(ft.Text(f"ID {product_id} silindi."), bgcolor=ft.Colors.GREEN, open=True)
            load_products()
        except requests.exceptions.RequestException as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Hata: {ex}"), bgcolor=ft.Colors.RED, open=True)
        page.update()

    def open_delete_dialog(e):
        product_id = e.control.data

        def on_yes_click(e_inner): page.close(dlg_modal); delete_product(product_id)

        def on_no_click(e_inner): page.close(dlg_modal)

        dlg_modal = ft.AlertDialog(modal=True, title=ft.Text("Onay"),
                                   content=ft.Text(f"ID: {product_id} olan ürünü silmek istiyor musunuz?"),
                                   actions=[ft.TextButton("Evet", on_click=on_yes_click),
                                            ft.TextButton("No", on_click=on_no_click)],
                                   actions_alignment=ft.MainAxisAlignment.END)
        page.open(dlg_modal)

    def on_file_picker_result(e: ft.FilePickerResultEvent):
        if not e.files: return
        selected_file = e.files[0]
        try:
            with open(selected_file.path, "rb") as f:
                file_content_binary = f.read()
            preview_image = ft.Image(src_base64=base64.b64encode(file_content_binary).decode('utf-8'), width=150,
                                     height=150, fit=ft.ImageFit.CONTAIN, border_radius=ft.border_radius.all(8))
            image_container.content = preview_image
            page.update()
            files = {"file": (selected_file.name, file_content_binary, "image/jpeg")}
            response = requests.post(UPLOAD_URL, files=files)
            response.raise_for_status()
            url = response.json().get("url")
            uploaded_image_url.value = url
            preview_image.src = url
            preview_image.src_base64 = None
        except Exception as ex:
            image_container.content = create_placeholder()
            page.snack_bar = ft.SnackBar(ft.Text(f"Resim yüklenemedi: {ex}"), bgcolor=ft.Colors.RED, open=True)
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_picker_result)
    page.overlay.append(file_picker)

    def submit_form(e):
        if editing_product_id.value:
            # DÜZENLEME MODU
            update_product()
        else:
            # EKLEME MODU
            add_product()

    def add_product():
        try:
            price = float(product_price_input.value)
        except (ValueError, TypeError):
            page.snack_bar = ft.SnackBar(ft.Text("Geçerli fiyat girin."), bgcolor=ft.Colors.RED,
                                         open=True); page.update(); return
        if not product_name_input.value or not product_price_input.value: page.snack_bar = ft.SnackBar(
            ft.Text("Zorunlu alanları doldurun."), bgcolor=ft.Colors.RED, open=True); page.update(); return
        product_data = {"name": product_name_input.value, "description": product_desc_input.value, "price": price,
                        "image_url": uploaded_image_url.value}
        try:
            requests.post(f"{API_URL}/products/", json=product_data).raise_for_status()
            page.snack_bar = ft.SnackBar(ft.Text("Ürün başarıyla eklendi!"), bgcolor=ft.Colors.GREEN, open=True)
            reset_form()
            load_products()
        except requests.exceptions.RequestException as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"API hatası: {ex}"), bgcolor=ft.Colors.RED, open=True)
            page.update()

    # --- YENİ: GÜNCELLEME FONKSİYONLARI ---
    def update_product():
        product_id = editing_product_id.value
        try:
            price = float(product_price_input.value)
        except (ValueError, TypeError):
            page.snack_bar = ft.SnackBar(ft.Text("Geçerli fiyat girin."), bgcolor=ft.Colors.RED,
                                         open=True); page.update(); return
        if not product_name_input.value or not product_price_input.value: page.snack_bar = ft.SnackBar(
            ft.Text("Zorunlu alanları doldurun."), bgcolor=ft.Colors.RED, open=True); page.update(); return

        product_data = {"name": product_name_input.value, "description": product_desc_input.value, "price": price,
                        "image_url": uploaded_image_url.value}
        try:
            requests.put(f"{API_URL}/products/{product_id}", json=product_data).raise_for_status()
            page.snack_bar = ft.SnackBar(ft.Text("Ürün başarıyla güncellendi!"), bgcolor=ft.Colors.GREEN, open=True)
            reset_form()
            load_products()
        except requests.exceptions.RequestException as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"API hatası: {ex}"), bgcolor=ft.Colors.RED, open=True)
            page.update()

    def start_editing_product(e):
        product_data = e.control.data
        editing_product_id.value = product_data.get("id")

        # Formu doldur
        product_name_input.value = product_data.get("name")
        product_desc_input.value = product_data.get("description")
        product_price_input.value = str(product_data.get("price", ""))
        uploaded_image_url.value = product_data.get("image_url")

        # Resim önizlemesini güncelle
        if product_data.get("image_url"):
            image_container.content = ft.Image(src=product_data.get("image_url"), width=150, height=150,
                                               fit=ft.ImageFit.CONTAIN, border_radius=ft.border_radius.all(8))
        else:
            image_container.content = create_placeholder()

        # Butonları güncelle
        submit_button.text = "Değişiklikleri Kaydet"
        submit_button.icon = ft.Icons.SAVE_AS
        cancel_button.visible = True
        page.update()

    def reset_form(e=None):
        editing_product_id.value = None
        product_name_input.value = ""
        product_desc_input.value = ""
        product_price_input.value = ""
        uploaded_image_url.value = ""
        image_container.content = create_placeholder()
        submit_button.text = "Ürünü Kaydet"
        submit_button.icon = ft.Icons.SAVE
        cancel_button.visible = False
        page.update()

    # --- ARAYÜZ YERLEŞİMİ ---
    select_image_button = ft.ElevatedButton("Resim Seç", icon=ft.Icons.UPLOAD_FILE,
                                            on_click=lambda _: file_picker.pick_files(allow_multiple=False,
                                                                                      allowed_extensions=["png", "jpeg",
                                                                                                          "jpg"]))
    submit_button = ft.ElevatedButton(text="Ürünü Kaydet", on_click=submit_form, icon=ft.Icons.SAVE)
    cancel_button = ft.TextButton("İptal", on_click=reset_form, visible=False)  # Gizli iptal butonu

    add_product_form = ft.Container(content=ft.Column([
        ft.Text("Yeni Ürün Formu", size=20),
        ft.Row([
            ft.Column([product_name_input, product_desc_input, product_price_input]),
            ft.Column([image_container, select_image_button], alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ]),
        ft.Row([cancel_button, submit_button], alignment=ft.MainAxisAlignment.END)  # Butonları yan yana koy
    ]), padding=20, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=10, margin=ft.margin.only(bottom=20))

    page.add(add_product_form, ft.Row([ft.Text("Ürünler", size=30, weight=ft.FontWeight.BOLD),
                                       ft.IconButton(icon=ft.Icons.REFRESH, on_click=load_products)],
                                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Divider(), products_list)
    load_products()


ft.app(target=main)