import smtplib
import secrets
import hashlib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from . import models
from dotenv import load_dotenv

load_dotenv()


# E-mail yapılandırması (environment variables'dan al)
EMAIL_CONFIG = {
    "SMTP_SERVER": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
    "EMAIL_ADDRESS": os.getenv("SMTP_USERNAME") or os.getenv("SMTP_FROM_EMAIL"),
    "EMAIL_PASSWORD": os.getenv("SMTP_PASSWORD"),
    "FROM_NAME": os.getenv("SMTP_FROM_NAME", "E-Ticaret Sistemi"),
    "USE_TLS": True
}

class EmailService:
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG["SMTP_SERVER"]
        self.smtp_port = EMAIL_CONFIG["SMTP_PORT"]
        self.email_address = EMAIL_CONFIG["EMAIL_ADDRESS"]
        self.email_password = EMAIL_CONFIG["EMAIL_PASSWORD"]
        self.from_name = EMAIL_CONFIG["FROM_NAME"]
        self.use_tls = EMAIL_CONFIG["USE_TLS"]
        
        # Email yapılandırması kontrolü
        if not self.email_address or not self.email_password:
            print("⚠️  UYARI: Email yapılandırması eksik!")
            print("SMTP_USERNAME ve SMTP_PASSWORD .env dosyasında ayarlanmalı.")
            print("Gmail için App Password oluşturmanız gerekiyor.")
            self.is_configured = False
        else:
            self.is_configured = True
            print(f"✅ Email servisi yapılandırıldı: {self.email_address}")
    
    def generate_verification_token(self, email: str) -> str:
        """E-mail doğrulama token'ı oluştur (6 haneli kod)"""
        # 6 haneli rastgele kod oluştur
        verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        return verification_code
    
    def create_verification_html(self, user_name: str, verification_code: str) -> str:
        """E-mail doğrulama HTML şablonu"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>E-mail Doğrulama</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2196F3;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .verification-code {{
                    background-color: #4CAF50;
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px;
                    margin: 20px 0;
                    letter-spacing: 8px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛒 E-Ticaret Platformu</h1>
                <h2>E-mail Adresinizi Doğrulayın</h2>
            </div>
            <div class="content">
                <p>Merhaba <strong>{user_name}</strong>,</p>
                
                <p>E-Ticaret platformumuza hoş geldiniz! Hesabınızı aktifleştirmek için e-mail adresinizi doğrulamanız gerekmektedir.</p>
                
                <p>Aşağıdaki 6 haneli doğrulama kodunu uygulamaya girin:</p>
                
                <div class="verification-code">
                    {verification_code}
                </div>
                
                <p><strong>Önemli:</strong> Bu doğrulama kodu 24 saat geçerlidir. Süre dolmadan önce doğrulama işlemini tamamlayınız.</p>
                
                <p>Eğer bu hesabı siz oluşturmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
                
                <p>Teşekkürler,<br>
                E-Ticaret Ekibi</p>
            </div>
            <div class="footer">
                <p>Bu e-posta otomatik olarak gönderilmiştir. Lütfen yanıtlamayınız.</p>
                <p>© 2024 E-Ticaret Platformu. Tüm hakları saklıdır.</p>
            </div>
        </body>
        </html>
        """
        return html_template
    
    def send_verification_email(self, to_email: str, user_name: str, verification_code: str) -> bool:
        """E-mail doğrulama e-postası gönder"""
        # Email yapılandırması kontrolü
        if not self.is_configured:
            print(f"❌ Email yapılandırması eksik - {to_email} adresine mail gönderilemedi")
            print("🔧 Çözüm için aşağıdaki adımları takip edin:")
            print("1. Gmail hesabınızda 2-Factor Authentication'ı aktifleştirin")
            print("2. Gmail App Password oluşturun: https://myaccount.google.com/apppasswords")
            print("3. Environment variables'ları ayarlayın:")
            print(f"   export EMAIL_ADDRESS='your-gmail@gmail.com'")
            print(f"   export EMAIL_PASSWORD='your-16-digit-app-password'")
            return False
            
        try:
            # E-posta içeriği oluştur
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "E-mail Doğrulama Kodu - E-Ticaret Platformu"
            msg['From'] = self.email_address
            msg['To'] = to_email
            
            # HTML içerik
            html_content = self.create_verification_html(user_name, verification_code)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            # Metin içerik (HTML desteklemeyen e-posta istemcileri için)
            text_content = f"""
            Merhaba {user_name},
            
            E-Ticaret platformumuza hoş geldiniz!
            
            Hesabınızı aktifleştirmek için aşağıdaki 6 haneli doğrulama kodunu uygulamaya girin:
            
            {verification_code}
            
            Bu doğrulama kodu 24 saat geçerlidir.
            
            Teşekkürler,
            E-Ticaret Ekibi
            """
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # SMTP bağlantısı ve e-posta gönderimi
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Doğrulama kodu gönderildi: {to_email} - Kod: {verification_code}")
            return True
            
        except Exception as e:
            print(f"E-posta gönderme hatası: {e}")
            return False
    
    def verify_code(self, code: str, email: str, db: Session) -> bool:
        """Doğrulama kodunu kontrol et"""
        try:
            # Veritabanından kullanıcıyı bul
            user = db.query(models.User).filter(models.User.email == email).first()
            if not user:
                print(f"❌ Kullanıcı bulunamadı: {email}")
                return False
            
            # Kod kontrolü
            if user.verification_token != code:
                print(f"❌ Kod eşleşmiyor. Beklenen: {user.verification_token}, Gelen: {code}")
                return False
            
            # Kod süresini kontrol et (24 saat)
            if user.verification_token_expires and user.verification_token_expires < datetime.now():
                print(f"❌ Kod süresi dolmuş: {email}")
                return False
            
            # Kullanıcıyı doğrulanmış olarak işaretle
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            user.is_active = True
            
            db.commit()
            print(f"✅ Kullanıcı doğrulandı: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Kod doğrulama hatası: {e}")
            return False

# EmailService sınıfı kullanıma hazır