Bu, Flet'in iç odak mekanizmasıyla ilgili yaygın bir sorundur. Temel problem şu: Flet/Flutter, klavye olaylarını Page seviyesinde işler, ancak `TextField` gibi yerel (native) giriş bileşenleri, klavye olaylarını bazen çok erken yakalayıp tüketir ve bu, sizin özel `_handle_keyboard_event` işleyicinize ulaşmadan önce Tab navigasyonunun gerçekleşmesine neden olur.

Özellikle ilk `TextField`'a odaklanma ve Tab sızıntısı sorunlarını çözmek için aşağıdaki iki adımı uygulamalıyız:

1. **İlk Focus Gecikmesi:** Bazen Flet, modal eklendikten hemen sonra focus metodunu çağırdığımızda kontrolün render edilmesini beklemekte zorlanır. Bunu aşmak için ufak bir gecikme ekleyebiliriz.
2. **Konteyneri Odaklanabilir Hale Getirmek (Focus Scope):** Flet'te, bir odak döngüsünü belirli bir alana kilitlemenin en güvenilir yolu, **Focus Node** ve **Focus Scope** (Odak Kapsamı) kullanmaktır. Flet'te bu genellikle `ft.Container` veya özel bir kontrol içinde yapılır, ancak `TextField`'ların Tab olayını yakalamasını engellemek için doğrudan Page klavye işleyicisinin güvenilirliğini artırmalıyız.

### Yapılacak İyileştirmeler

Ana iyileştirmeyi, `_setup_keyboard_handling` metodu içinde gerçekleştireceğiz. Özellikle ilk odaklanma sorununu çözmek için `page.run_thread` veya eşdeğeri olan **asenkron** bir çağrı kullanmak faydalı olabilir.

Ancak, Flet'in Flet app (sync) yapısında `time.sleep` kullanmak UI'ı bloklayacağından, odaklanmayı modal açılışından hemen sonra Page'in kendi akışında zorlamayı deneyeceğiz.

#### 1. Odaklanma Sırasını Optimize Etme (Close Button ve İlk Form Alanı)

Siz `_setup_keyboard_handling` içinde Close Button'ı listenin başına alıyorsunuz. Eğer ilk odaklanmasını istediğiniz "Ürün Adı" (yani ilk form alanı) ise, Close Button'ı en başa değil, form alanlarından sonra ilk buton olarak koymanız gerekir.

**Düzeltme 1: Odak Sırası Mantığı**

Eğer amaç, modal açıldığında **doğrudan ilk form alanına (TextField) odaklanmak** ise, `_setup_keyboard_handling` metodunda Close Button'ın sırasını değiştirmeliyiz:

```python
    def _setup_keyboard_handling(self, modal_content_control: ft.Control):
        # ... (Önceki kodlar)
        
        # 1. Odaklanabilir kontrolleri topla
        form_fields, buttons = self._collect_focusable_controls(modal_content_control)
        
        # Close Button'ı belirle
        first_row = modal_content_control.controls[0]
        close_button = next((c for c in first_row.controls if isinstance(c, ft.IconButton)), None)

        # Close Button'ı butonlar listesinden çıkar (eğer oradaysa)
        if close_button and close_button in buttons:
            buttons.remove(close_button)

        # Odak sırası: [Tüm Form Alanları] + [Close Button] + [Diğer Butonlar]
        self.modal_focusable_controls = form_fields + ([close_button] if close_button else []) + buttons
        
        self.current_focus_index = 0
        
        # ... (Diğer kodlar)
        
        # 3. İlk kontrole odaklan (eğer varsa)
        if self.modal_focusable_controls:
            # Burası artık ilk TextField (Ürün Adı) olmalı
            self.modal_focusable_controls[0].focus()
            self.page.update() # Focus'u hemen tetikle
```

#### 2. Tab Sızıntısını Kesinlikle Engelleme Güçlendirmesi

Tab sızıntısını engellemek için Flet'in klavye olayını hemen işlediğinden emin olmalıyız.

Aşağıdaki kodu deneyerek, `show_modal` içerisinde odaklanma işlemini bir `self.page.after_update` veya benzeri bir mekanizma ile biraz geciktirebiliriz. Flet'te senkron çalışırken gecikme yaratmak zordur, bu yüzden `page.update()` sonrası hemen `focus()` çağrısının hemen arkasına bir kez daha `page.update()` eklemek bazen işe yarar.

**Not:** Flet'in focus yönetimi bazen stabil olmayabilir. Eğer aşağıdaki değişiklikler (özellikle sıralama değişikliği) işe yaramazsa, asenkron yapıyı kullanmanız gerekebilir. Basitlik açısından, sadece mevcut metodları optimize edelim.

### Son Düzeltilmiş `ModalManager` Kodu

Aşağıdaki kodda, `_setup_keyboard_handling` metodu, Close Button'ı form alanlarından hemen sonra yerleştirecek şekilde düzeltilmiştir (İlk focus ilk form alanına gitsin diye) ve `focus()` çağrıları güçlendirilmiştir.

```python
"""
Modal Manager Component
"""

import flet as ft

class ModalManager:
    """Manages modal dialogs"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_modal = None
        self.modal_focusable_controls = []
        self.current_focus_index = 0
        self.original_keyboard_handler = None

    # --- Klavye İşleyici ve Odak Döngüsü ---

    def _handle_keyboard_event(self, e: ft.KeyboardEvent):
        """Tab tuşu basıldığında odak döngüsünü yönetir."""
        
        # Modal açık değilse veya Tab tuşu değilse varsayılan akışı sürdür
        if not self.current_modal or e.key != "Tab":
            return
            
        if not self.modal_focusable_controls:
            e.handled = True 
            return
        
        # **KRİTİK**: Tab sızıntısını engellemek için olayı hemen tüket.
        e.handled = True 
        
        num_controls = len(self.modal_focusable_controls)

        if e.shift:
            # Shift + Tab (Geriye doğru)
            self.current_focus_index = (self.current_focus_index - 1) % num_controls
        else:
            # Tab (İleriye doğru)
            self.current_focus_index = (self.current_focus_index + 1) % num_controls
        
        control_to_focus = self.modal_focusable_controls[self.current_focus_index]
        
        try:
            if hasattr(control_to_focus, 'focus'):
                control_to_focus.focus()
            
            # Odak değişikliğini zorlamak için update çağrısı
            self.page.update()
        except Exception as ex:
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
            pass # Eğer ilk kontrol bir Row değilse

        # Close Button'ı butonlar listesinden çıkar (eğer oradaysa ve karışıklık yaratıyorsa)
        if close_button and close_button in buttons:
            buttons.remove(close_button)

        # Odak sırası: [Tüm Form Alanları] + [Tüm Diğer Butonlar] + [Close Button (genellikle son)]
        # NOT: Eğer ilk odaklanılacak eleman Close Button değilse, onu form alanlarından sonraki butonlar grubunun sonuna koymak daha mantıklıdır.
        self.modal_focusable_controls = form_fields + buttons
        
        # Close butonu varsa, onu döngüye dahil et (Genellikle en sona)
        if close_button:
            self.modal_focusable_controls.append(close_button)

        self.current_focus_index = 0
        
        # 2. Klavye işleyicisini devral
        self.original_keyboard_handler = self.page.on_keyboard_event
        self.page.on_keyboard_event = self._handle_keyboard_event
        
        # 3. İlk kontrole odaklan (eğer varsa)
        if self.modal_focusable_controls:
            # İlk elemente focus al
            self.modal_focusable_controls[0].focus()
            # Gerekirse focus'un işlenmesi için hemen update çağrısı
            self.page.update()
            
    # --- Kontrol Toplama ---
    
    def _collect_focusable_controls(self, control, form_fields=None, buttons=None):
        """Modal içindeki focusable kontrolleri topla (TextField, Dropdown, Button, vb.)"""
        # (Bu metot önceki versiyonda zaten doğruydu, sadece tamlık için burada tutuluyor)
        if form_fields is None:
            form_fields = []
        if buttons is None:
            buttons = []
        
        if hasattr(control, 'visible') and not control.visible:
            return form_fields, buttons
        
        form_field_types = (ft.TextField, ft.Dropdown, ft.Checkbox, ft.Switch, ft.Radio)
        button_types = (ft.ElevatedButton, ft.TextButton, ft.IconButton, ft.OutlinedButton, ft.FilledButton)
        
        is_disabled = hasattr(control, 'disabled') and control.disabled
        has_focus_method = hasattr(control, 'focus')

        if not is_disabled and has_focus_method:
            if isinstance(control, form_field_types):
                form_fields.append(control)
            elif isinstance(control, button_types):
                buttons.append(control)
        
        if hasattr(control, 'content') and control.content:
            self._collect_focusable_controls(control.content, form_fields, buttons)
        
        if hasattr(control, 'controls') and control.controls:
            for child in control.controls:
                self._collect_focusable_controls(child, form_fields, buttons)
        
        return form_fields, buttons

    # --- Modal Gösterme ve Kapatma ---
    
    def show_modal(self, content: ft.Control, title: str = "", width: int = 600):
        """Show modal dialog"""
        def close_modal(e=None):
            self.close_modal()
        
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
            # ... (stil ayarları)
        )
        
        overlay = ft.Container(
            content=ft.Stack([
                ft.GestureDetector(
                    content=ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                        expand=True
                    ),
                    on_tap=close_modal
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
    
    def close_modal(self):
        """Close current modal"""
        if self.current_modal:
            if self.current_modal in self.page.overlay:
                self.page.overlay.remove(self.current_modal)
            
            self.current_modal = None
            
            # Klavye handler'ını eski haline döndür
            self.page.on_keyboard_event = self.original_keyboard_handler
            self.original_keyboard_handler = None
            
            # Temizlik
            self.modal_focusable_controls = []
            self.current_focus_index = 0
            
            self.page.update()

    # ... (show_overlay_modal ve show_confirmation metotları buraya dahil edilmeli)
```

Bu son haliyle, `_setup_keyboard_handling` metodu önce tüm form alanlarını listeye ekleyecek, böylece ilk form alanı listenin ilk elemanı olacaktır ve `self.modal_focusable_controls[0].focus()` çağrısı ona odaklanmayı zorlayacaktır.

Ayrıca `_handle_keyboard_event` içindeki `e.handled = True` ifadesi, Tab tuşu olayını Page seviyesinde kesinlikle tüketerek, olayın alt katmanlara (arka plandaki kontrole) sızmasını engellemelidir.