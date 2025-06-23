#!/usr/bin/env python3
"""
NeoFinX - Akıllı Bütçe ve Harcama Asistanı
Kurulum ve başlangıç scripti
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def create_database():
    """Veritabanını oluştur ve temel tabloları ekle"""
    print("📊 Veritabanı oluşturuluyor...")
    
    # SQLite veritabanı dosyası
    db_path = 'data/neofinx.db'
    
    # Data klasörü oluştur
    os.makedirs('data', exist_ok=True)
    
    # Veritabanı bağlantısı
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        monthly_income REAL DEFAULT 0.0,
        currency TEXT DEFAULT 'TRY',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Kategoriler tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '💰',
        color TEXT DEFAULT '#007bff',
        parent_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (parent_id) REFERENCES categories (id)
    )
    ''')
    
    # Harcamalar tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date DATE NOT NULL,
        location TEXT,
        payment_method TEXT DEFAULT 'cash',
        is_recurring BOOLEAN DEFAULT 0,
        recurring_frequency TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')
    
    # Bütçeler tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category_id INTEGER,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        period TEXT DEFAULT 'monthly',
        start_date DATE NOT NULL,
        end_date DATE,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')
    
    # Yatırım türleri tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investment_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        symbol TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        icon TEXT DEFAULT '📈',
        currency TEXT DEFAULT 'TRY',
        api_source TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Yatırımlar tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        investment_type_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        quantity REAL NOT NULL,
        purchase_price REAL NOT NULL,
        purchase_date DATE NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (investment_type_id) REFERENCES investment_types (id)
    )
    ''')
    
    # Yatırım fiyat geçmişi tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investment_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        investment_type_id INTEGER NOT NULL,
        price REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (investment_type_id) REFERENCES investment_types (id)
    )
    ''')
    
    # Varsayılan kategorileri ekle
    default_categories = [
        ('Yemek & İçecek', '🍽️', '#FF6B6B'),
        ('Ulaşım', '🚗', '#4ECDC4'),
        ('Eğlence', '🎬', '#45B7D1'),
        ('Sağlık', '🏥', '#96CEB4'),
        ('Alışveriş', '🛍️', '#FECA57'),
        ('Faturalar', '📋', '#FF9FF3'),
        ('Eğitim', '📚', '#54A0FF'),
        ('Kişisel Bakım', '💄', '#5F27CD'),
        ('Spor', '🏃', '#00D2D3'),
        ('Diğer', '📦', '#C44569')
    ]
    
    for name, icon, color in default_categories:
        cursor.execute('''
        INSERT OR IGNORE INTO categories (name, color)
        VALUES (?, ?)
        ''', (name, color))
    
    # Varsayılan yatırım türlerini ekle
    default_investments = [
        ('Dolar', 'USD', 'currency', '💵', 'USD'),
        ('Euro', 'EUR', 'currency', '💶', 'EUR'),
        ('Sterlin', 'GBP', 'currency', '💷', 'GBP'),
        ('Altın (Ons)', 'GOLD', 'precious_metal', '🥇', 'USD'),
        ('Gümüş (Ons)', 'SILVER', 'precious_metal', '🥈', 'USD'),
        ('Bitcoin', 'BTC', 'crypto', '₿', 'USD'),
        ('Ethereum', 'ETH', 'crypto', '⟠', 'USD'),
        ('BIST 100', 'XU100', 'stock_index', '📊', 'TRY'),
        ('S&P 500', 'SPX', 'stock_index', '📈', 'USD'),
        ('Nasdaq', 'IXIC', 'stock_index', '💻', 'USD')
    ]
    
    for name, symbol, inv_type, icon, currency in default_investments:
        cursor.execute('''
        INSERT OR IGNORE INTO investment_types (name, symbol, type, icon, currency)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, symbol, inv_type, icon, currency))
    
    # Finansal hedefler tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financial_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        goal_type TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0.0,
        target_date DATE NOT NULL,
        monthly_target REAL DEFAULT 0.0,
        description TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Hedef katkıları tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goal_contributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        contribution_date DATE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goal_id) REFERENCES financial_goals (id)
    )
    ''')
    
    # Vergi hesaplamaları tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tax_calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        calculation_type TEXT NOT NULL,
        tax_year INTEGER NOT NULL,
        income_amount REAL DEFAULT 0.0,
        investment_gains REAL DEFAULT 0.0,
        deductions REAL DEFAULT 0.0,
        calculated_tax REAL DEFAULT 0.0,
        effective_rate REAL DEFAULT 0.0,
        calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # KDV takip tablosu (freelancer'lar için)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vat_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        invoice_number TEXT,
        client_name TEXT NOT NULL,
        invoice_date DATE NOT NULL,
        invoice_amount REAL NOT NULL,
        vat_rate REAL DEFAULT 18.0,
        vat_amount REAL NOT NULL,
        payment_status TEXT DEFAULT 'pending',
        payment_date DATE,
        refund_eligible BOOLEAN DEFAULT 1,
        refund_requested BOOLEAN DEFAULT 0,
        refund_amount REAL DEFAULT 0.0,
        refund_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Yatırım kazançları vergi tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investment_tax (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        investment_id INTEGER,
        investment_type TEXT NOT NULL,
        purchase_amount REAL NOT NULL,
        sale_amount REAL DEFAULT 0.0,
        gain_loss REAL DEFAULT 0.0,
        holding_period_days INTEGER DEFAULT 0,
        tax_rate REAL DEFAULT 0.0,
        tax_amount REAL DEFAULT 0.0,
        purchase_date DATE NOT NULL,
        sale_date DATE,
        is_exempt BOOLEAN DEFAULT 0,
        exemption_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (investment_id) REFERENCES investments (id)
    )
    ''')
    
    # Vergi optimizasyon önerileri tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tax_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recommendation_type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        potential_savings REAL DEFAULT 0.0,
        priority_level INTEGER DEFAULT 1,
        is_applied BOOLEAN DEFAULT 0,
        applied_date DATE,
        valid_until DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Vergi dilim tablosu (Türkiye gelir vergisi dilimleri)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tax_brackets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tax_year INTEGER NOT NULL,
        bracket_min REAL NOT NULL,
        bracket_max REAL,
        tax_rate REAL NOT NULL,
        deduction_amount REAL DEFAULT 0.0,
        currency TEXT DEFAULT 'TRY',
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2024 Türkiye gelir vergisi dilimlerini ekle
    tax_brackets_2024 = [
        (0, 110000, 15.0, 0),
        (110000, 230000, 20.0, 5500),
        (230000, 580000, 27.0, 21600),
        (580000, 3000000, 35.0, 68000),
        (3000000, None, 40.0, 218000)
    ]
    
    for bracket_min, bracket_max, rate, deduction in tax_brackets_2024:
        cursor.execute('''
        INSERT OR IGNORE INTO tax_brackets (tax_year, bracket_min, bracket_max, tax_rate, deduction_amount)
        VALUES (?, ?, ?, ?, ?)
        ''', (2024, bracket_min, bracket_max, rate, deduction))
    
    # Varsayılan hedef şablonları
    default_goal_templates = [
        ('Ev Alma Hedefi', 'housing', '🏠', 'Ev peşinatı veya tam ödeme için tasarruf'),
        ('Emeklilik Planı', 'retirement', '👴', 'Rahat bir emeklilik için uzun vadeli tasarruf'),
        ('Acil Durum Fonu', 'emergency', '🛡️', 'Beklenmedik durumlar için güvenlik fonu'),
        ('Araç Alma Hedefi', 'vehicle', '🚗', 'Araba alımı için tasarruf'),
        ('Eğitim Fonu', 'education', '🎓', 'Kendiniz veya çocuklarınız için eğitim masrafları'),
        ('Tatil Fonu', 'vacation', '✈️', 'Hayal ettiğiniz tatil için tasarruf'),
        ('Yatırım Hedefi', 'investment', '📈', 'Yatırım yapmak için başlangıç sermayesi'),
        ('Düğün Hedefi', 'wedding', '💍', 'Düğün masrafları için tasarruf')
    ]
    
    # Hedef şablonları tablosu oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goal_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        icon TEXT DEFAULT '🎯',
        description TEXT,
        typical_duration_months INTEGER DEFAULT 24,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Varsayılan şablonları ekle
    for name, category, icon, description in default_goal_templates:
        cursor.execute('''
        INSERT OR IGNORE INTO goal_templates (name, category, description)
        VALUES (?, ?, ?)
        ''', (name, category, description))
    
    conn.commit()
    conn.close()
    print("✅ Veritabanı başarıyla oluşturuldu!")

def create_sample_data():
    """Örnek veriler oluştur"""
    print("📝 Örnek veriler oluşturuluyor...")
    
    import pandas as pd
    import numpy as np
    from datetime import date, timedelta
    
    # Kategoriler
    categories = [
        'Yemek & İçecek', 'Ulaşım', 'Eğlence', 'Sağlık', 
        'Alışveriş', 'Faturalar', 'Eğitim', 'Kişisel Bakım', 'Spor', 'Diğer'
    ]
    
    # Son 6 ay için örnek harcamalar
    np.random.seed(42)
    start_date = date.today() - timedelta(days=180)
    dates = [start_date + timedelta(days=x) for x in range(180)]
    
    sample_expenses = []
    for d in dates:
        # Günde 1-4 harcama
        num_expenses = np.random.randint(1, 5)
        for _ in range(num_expenses):
            category = np.random.choice(categories)
            
            # Kategori bazlı gerçekçi miktarlar
            if 'Yemek' in category:
                amount = np.random.normal(50, 20)
            elif 'Ulaşım' in category:
                amount = np.random.normal(30, 10)
            elif 'Eğlence' in category:
                amount = np.random.normal(100, 40)
            elif 'Sağlık' in category:
                amount = np.random.normal(80, 30)
            elif 'Alışveriş' in category:
                amount = np.random.normal(150, 60)
            elif 'Faturalar' in category:
                amount = np.random.normal(200, 50)
            else:
                amount = np.random.normal(70, 25)
            
            amount = max(10, round(amount, 2))
            
            sample_expenses.append({
                'date': d.isoformat(),
                'amount': amount,
                'category': category,
                'description': f"{category} harcaması"
            })
    
    # CSV dosyasına kaydet
    df = pd.DataFrame(sample_expenses)
    df.to_csv('data/sample_expenses.csv', index=False)
    
    print(f"✅ {len(sample_expenses)} örnek harcama kaydı oluşturuldu!")

def install_requirements():
    """Gerekli kütüphaneleri yükle"""
    print("📦 Gerekli kütüphaneler yükleniyor...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Kütüphaneler başarıyla yüklendi!")
    except subprocess.CalledProcessError:
        print("❌ Kütüphane yükleme hatası! requirements.txt dosyasını kontrol edin.")
        return False
    return True

def create_env_file():
    """Çevre değişkenleri dosyası oluştur"""
    print("🔧 Çevre değişkenleri dosyası oluşturuluyor...")
    
    env_content = """# NeoFinX Çevre Değişkenleri
SECRET_KEY=neofinx-secret-key-2024-dev
JWT_SECRET_KEY=jwt-secret-string-dev
DATABASE_URL=sqlite:///data/neofinx.db
FLASK_ENV=development
FLASK_APP=backend/app.py
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env dosyası oluşturuldu!")

def run_streamlit_app():
    """Streamlit uygulamasını başlat"""
    print("🚀 NeoFinX Dashboard başlatılıyor...")
    print("📱 Tarayıcınızda http://localhost:8501 adresini açın")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    except KeyboardInterrupt:
        print("\n👋 NeoFinX kapatılıyor...")

def main():
    """Ana setup fonksiyonu"""
    print("🏦 NeoFinX - Akıllı Bütçe ve Harcama Asistanı")
    print("=" * 50)
    print("🚀 Kurulum başlatılıyor...\n")
    
    # 1. Çevre değişkenleri dosyası oluştur
    create_env_file()
    
    # 2. Veritabanını oluştur
    create_database()
    
    # 3. Örnek veri oluştur
    create_sample_data()
    
    print("\n" + "=" * 50)
    print("✅ NeoFinX kurulumu tamamlandı!")
    print("\n📋 Kullanım Talimatları:")
    print("1. Dashboard: python -m streamlit run dashboard.py")
    print("2. Backend API: python backend/app.py")
    print("3. ML Model Test: python ml_models/expense_classifier.py")
    print("\n💡 İpucu: Önce Python kütüphanelerini yükleyin:")
    print("   pip install -r requirements.txt")
    
    # Streamlit'i başlatmayı sor
    response = input("\n🚀 Dashboard'u şimdi başlatmak ister misiniz? (y/N): ")
    if response.lower() in ['y', 'yes', 'evet']:
        run_streamlit_app()

if __name__ == "__main__":
    main() 