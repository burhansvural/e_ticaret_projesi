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

    # --- KONTROLLER ---
    product_name_input = ft.TextField(label="Ürün Adı", width=300)
    product_desc_input = ft.TextField(label="Açıklama", width=300)
    product_price_input = ft.TextField(label="Fiyat", width=150, prefix_text="TL")
    uploaded_image_url = ft.TextField(visible=False)

    def create_placeholder():
        return ft.Column(
            [ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=40, color=ft.Colors.GREY_500),
             ft.Text("Seçili Resim Yok.", color=ft.Colors.GREY_500)],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5
        )

    image_container = ft.Container(
        width=150, height=150, border=ft.border.all(2, ft.Colors.GREY_400),
        border_radius=ft.border_radius.all(10), content=create_placeholder(), alignment=ft.alignment.center
    )
    products_list = ft.ListView(expand=True, spacing=10, padding=20)

    # --- DİYALOG KONTROLÜ ---
    # Diyaloğu en başta bir kere tanımla
    delete_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Onay"),
        content=ft.Text("Bu ürünü silmek istediğinize emin misiniz?"),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # --- FONKSİYONLAR ---
    def close_dialog(e):
        # e.control, tıklanan butondur ("Evet" veya "Hayır").
        # e.control.page, o butonun ait olduğu sayfadır.
        # page.close() metodu, kendisine verilen diyaloğu kapatır.
        # Hangi diyaloğun kapatılacağını bilmek için onu bir şekilde referans almalıyız.
        # En temizi, `page.dialog` özelliğini kullanmaktır.
        page.dialog.open = False
        page.update()

    def delete_confirmed(e):
        product_id = e.control.data  # ID'yi tıklanan "Evet" butonunun datasından al
        print(f"delete_confirmed çalıştı! ID: {product_id}")
        try:
            response = requests.delete(f"{API_URL}/products/{product_id}")
            response.raise_for_status()
            page.snack_bar = ft.SnackBar(content=ft.Text(f"ID: {product_id} olan ürün silindi."),
                                         bgcolor=ft.Colors.GREEN, open=True)
            load_products()
        except requests.exceptions.RequestException as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Hata: {ex}"), bgcolor=ft.Colors.RED, open=True)

        close_dialog(e)

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
            response_data = response.json()
            url = response_data.get("url")
            uploaded_image_url.value = url
            preview_image.src = url
            preview_image.src_base64 = None
        except Exception as ex:
            print(f"RESİM YÜKLEME HATASI: {ex}")
            image_container.content = create_placeholder()
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Resim yüklenemedi: {ex}"), bgcolor=ft.Colors.RED, open=True)
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_picker_result)
    page.overlay.append(file_picker)

    def add_product(e):
        try:
            price = float(product_price_input.value)
        except (ValueError, TypeError):
            page.snack_bar = ft.SnackBar(content=ft.Text("Geçerli bir fiyat girin."), bgcolor=ft.Colors.RED,
                                         open=True); page.update(); return
        if not product_name_input.value or not product_price_input.value: page.snack_bar = ft.SnackBar(
            content=ft.Text("Ürün Adı ve Fiyat zorunludur."), bgcolor=ft.Colors.RED, open=True); page.update(); return
        product_data = {"name": product_name_input.value, "description": product_desc_input.value, "price": price,
                        "image_url": uploaded_image_url.value}
        try:
            response = requests.post(f"{API_URL}/products/", json=product_data)
            response.raise_for_status()
            product_name_input.value = ""
            product_desc_input.value = ""
            product_price_input.value = ""
            uploaded_image_url.value = ""
            image_container.content = create_placeholder()
            page.snack_bar = ft.SnackBar(content=ft.Text("Ürün başarıyla eklendi!"), bgcolor=ft.Colors.GREEN, open=True)
            load_products()
        except requests.exceptions.RequestException as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"API hatası: {ex}"), bgcolor=ft.Colors.RED, open=True)
            page.update()
            pass
        pass

    def show_delete_dialog(e):
        product_id = e.control.data

        def delete_confirmed(e_inner):
            try:
                response = requests.delete(f"{API_URL}/products/{product_id}")
                response.raise_for_status()
                page.snack_bar = ft.SnackBar(ft.Text(f"ID {product_id} silindi."), bgcolor=ft.Colors.GREEN, open=True)
                load_products()
            except requests.exceptions.RequestException as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Hata: {ex}"), bgcolor=ft.Colors.RED, open=True)

            # İşlem sonrası diyaloğu kapat
            close_dialog(e_inner)

        # Diyalog nesnesini burada oluştur
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Lütfen Onaylayın"),
            content=ft.Text(f"ID: {product_id} olan ürünü gerçekten silmek istiyor musunuz?"),
            actions=[
                ft.TextButton("Evet", on_click=delete_confirmed),
                ft.TextButton("Hayır", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Diyaloğu page.open() ile AÇ!
        page.dialog = dlg_modal  # Kapatabilmek için referansı atamamız hala gerekli
        page.open(dlg_modal)

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
                        ft.Container(
                            content=ft.Row(controls=[
                                ft.Image(src=product.get("image_url"), width=50, height=50, fit=ft.ImageFit.COVER,
                                         border_radius=ft.border_radius.all(5),
                                         error_content=ft.Icon(ft.Icons.NO_PHOTOGRAPHY)),
                                ft.Text(f"ID: {product['id']}", width=50, color=ft.Colors.WHITE),
                                ft.Text(product['name'], weight=ft.FontWeight.BOLD, expand=True, color=ft.Colors.WHITE),
                                ft.Text(f"{product['price']:.2f} TL", text_align=ft.TextAlign.RIGHT, width=100,
                                        color=ft.Colors.WHITE),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Ürünü Sil",
                                    on_click=show_delete_dialog,  # Artık yeni fonksiyonu çağırıyor
                                    data=product['id']
                                )
                            ]),
                            padding=10, bgcolor=ft.Colors.ON_SURFACE_VARIANT, border_radius=5
                        )
                    )
            page.update()
        except requests.exceptions.RequestException as ex:
            print(f"API BAĞLANTI HATASI DETAYI: {ex}")
            products_list.controls.clear()
            products_list.controls.append(
                ft.Text("API'ye bağlanılamadı. Backend'in çalıştığından emin olun.", color="red"))
            page.update()

    # --- ARAYÜZ YERLEŞİMİ ---
    select_image_button = ft.ElevatedButton("Resim Seç", icon=ft.Icons.UPLOAD_FILE,
                                            on_click=lambda _: file_picker.pick_files(allow_multiple=False,
                                                                                      allowed_extensions=["png", "jpeg",
                                                                                                          "jpg"]))
    add_button = ft.ElevatedButton(text="Ürünü Kaydet", on_click=add_product, icon=ft.Icons.SAVE)
    add_product_form = ft.Container(
        content=ft.Column([
            ft.Text("Yeni Ürün Formu", size=20),
            ft.Row([
                ft.Column([product_name_input, product_desc_input, product_price_input]),
                ft.Column([image_container, select_image_button], alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ]),
            ft.Row([add_button], alignment=ft.MainAxisAlignment.END)
        ]),
        padding=20, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=10, margin=ft.margin.only(bottom=20)
    )
    page.add(
        add_product_form,
        ft.Row([ft.Text("Ürünler", size=30, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.Icons.REFRESH, on_click=load_products)],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(), products_list
    )
    load_products()


ft.app(target=main)