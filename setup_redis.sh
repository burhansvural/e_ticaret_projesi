#!/bin/bash
# Redis kurulum ve başlatma scripti

echo "🔧 Redis Kurulum ve Yapılandırma"
echo "=================================="
echo ""

# Redis kurulu mu kontrol et
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis kurulu değil. Kurulum başlatılıyor..."
    echo ""
    
    # İşletim sistemini tespit et
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🐧 Linux tespit edildi"
        
        # Debian/Ubuntu
        if command -v apt-get &> /dev/null; then
            echo "📦 apt-get ile kurulum yapılıyor..."
            sudo apt-get update
            sudo apt-get install -y redis-server
        
        # RedHat/CentOS/Fedora
        elif command -v yum &> /dev/null; then
            echo "📦 yum ile kurulum yapılıyor..."
            sudo yum install -y redis
        
        # Arch Linux
        elif command -v pacman &> /dev/null; then
            echo "📦 pacman ile kurulum yapılıyor..."
            sudo pacman -S --noconfirm redis
        
        else
            echo "❌ Desteklenmeyen Linux dağıtımı"
            exit 1
        fi
    
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 macOS tespit edildi"
        
        if command -v brew &> /dev/null; then
            echo "📦 Homebrew ile kurulum yapılıyor..."
            brew install redis
        else
            echo "❌ Homebrew kurulu değil. Lütfen önce Homebrew kurun:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    
    else
        echo "❌ Desteklenmeyen işletim sistemi: $OSTYPE"
        exit 1
    fi
    
    echo ""
    echo "✅ Redis kurulumu tamamlandı!"
else
    echo "✅ Redis zaten kurulu"
fi

echo ""
echo "🚀 Redis başlatılıyor..."
echo ""

# Redis'i başlat
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - systemd kullan
    if command -v systemctl &> /dev/null; then
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
        echo "✅ Redis systemd ile başlatıldı"
    else
        # systemd yoksa manuel başlat
        redis-server --daemonize yes
        echo "✅ Redis daemon olarak başlatıldı"
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - brew services kullan
    brew services start redis
    echo "✅ Redis brew services ile başlatıldı"
fi

echo ""
echo "🔍 Redis durumu kontrol ediliyor..."
sleep 2

# Redis'e bağlanabilir miyiz test et
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis çalışıyor ve erişilebilir!"
    echo ""
    echo "📊 Redis Bilgileri:"
    echo "-------------------"
    redis-cli INFO server | grep "redis_version"
    redis-cli INFO server | grep "os"
    redis-cli INFO server | grep "uptime_in_seconds"
    echo ""
    echo "🎉 Kurulum başarıyla tamamlandı!"
    echo ""
    echo "📝 Kullanışlı Komutlar:"
    echo "  - Redis durumu: redis-cli ping"
    echo "  - Redis durdur: sudo systemctl stop redis-server (Linux) veya brew services stop redis (macOS)"
    echo "  - Redis başlat: sudo systemctl start redis-server (Linux) veya brew services start redis (macOS)"
    echo "  - Redis CLI: redis-cli"
    echo ""
else
    echo "❌ Redis başlatılamadı veya erişilemiyor"
    echo "   Lütfen manuel olarak başlatmayı deneyin: redis-server"
    exit 1
fi