import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import sqlite3
import os
import requests
import json

# Modern sayfa konfigürasyonu
st.set_page_config(
    page_title="NeoFinX - Akıllı Bütçe Asistanı",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode toggle - Prominente yerleştirme
st.sidebar.markdown("---")
dark_mode = st.sidebar.checkbox("🌙 **Dark Mode**", value=False, key="dark_mode_toggle", help="Karanlık tema ile göz yorgunluğunu azaltın")
st.sidebar.markdown("---")

# Dynamic CSS based on dark mode
if dark_mode:
    # Dark mode CSS
    st.markdown("""
    <style>
        /* Dark theme renkleri */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: #334155;
            --input-bg: #1e293b;
            --sidebar-bg: #0f172a;
        }
        
        /* Ana body ve container - güçlü selector'lar */
        .stApp {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Sidebar dark - güçlü selector'lar */
        .css-1d391kg, .css-1oe6wy4, .sidebar .sidebar-content {
            background: linear-gradient(180deg, var(--sidebar-bg), #1e293b) !important;
        }
        
        /* Streamlit'in varsayılan beyaz arka planını override et */
        [data-testid="stApp"] {
            background-color: var(--bg-color) !important;
        }
        
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* Tüm section'ları dark yap */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--sidebar-bg), #1e293b) !important;
        }
        
        section[data-testid="stSidebar"] > div {
            background: linear-gradient(180deg, var(--sidebar-bg), #1e293b) !important;
        }
        
        /* Main header dark */
        .main-header {
            background: linear-gradient(135deg, #4338ca, #6366f1);
            color: white;
        }
        
        /* Kartlar dark - güçlü selector'lar */
        [data-testid="metric-container"] {
            background: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        [data-testid="metric-container"] > div {
            color: var(--text-primary) !important;
        }
        
        [data-testid="metric-container"] label {
            color: var(--text-secondary) !important;
        }
        
        /* Tüm text elementleri dark */
        .stMarkdown, .stMarkdown p, .stMarkdown div {
            color: var(--text-primary) !important;
        }
        
        /* Form container dark */
        [data-testid="stForm"] {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Input field'lar dark - güçlü selector'lar */
        .stSelectbox > div > div, [data-testid="stSelectbox"] > div {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stSelectbox div[role="listbox"] {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
        }
        
        .stSelectbox div[role="option"] {
            background-color: var(--input-bg) !important;
            color: var(--text-primary) !important;
        }
        
        .stSelectbox div[role="option"]:hover {
            background-color: var(--border-color) !important;
        }
        
        .stNumberInput > div > div > input, [data-testid="stNumberInput"] input {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stTextInput > div > div > input, [data-testid="stTextInput"] input {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stDateInput > div > div > input, [data-testid="stDateInput"] input {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Checkbox dark */
        .stCheckbox > label {
            color: var(--text-primary) !important;
        }
        
        /* Buton dark - güçlü selector'lar */
        .stButton > button, [data-testid="stButton"] button {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border: 2px solid transparent !important;
        }
        
        /* Ekspander dark */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, var(--card-bg), #334155);
            color: var(--text-primary);
        }
        
        /* Grafik container dark */
        .js-plotly-plot {
            background: var(--card-bg);
        }
        
        /* Success/Error mesajları dark */
        .stSuccess {
            background: linear-gradient(90deg, #064e3b, #065f46);
            color: #d1fae5;
        }
        
        .stError {
            background: linear-gradient(90deg, #7f1d1d, #991b1b);
            color: #fecaca;
        }
        
        .stWarning {
            background: linear-gradient(90deg, #78350f, #92400e);
            color: #fed7aa;
        }
        
        .stInfo {
            background: linear-gradient(90deg, #1e3a8a, #1e40af);
            color: #dbeafe;
        }
        
        /* Global dark theme override - En güçlü selector'lar */
        html, body {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main > .block-container {
            background-color: var(--bg-color) !important;
        }
        
        /* Ekspander ve diğer widget'lar */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, var(--card-bg), var(--border-color)) !important;
            color: var(--text-primary) !important;
        }
        
        .streamlit-expanderContent {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Tablo dark */
        .stDataFrame {
            background-color: var(--card-bg) !important;
            color: var(--text-primary) !important;
        }
        
        /* Grafik container'ları dark */
        [data-testid="stPlotlyChart"] {
            background-color: var(--card-bg) !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Light mode CSS
    st.markdown("""
    <style>
        /* Light theme renkleri */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --bg-color: #ffffff;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --input-bg: #ffffff;
            --sidebar-bg: #f8fafc;
        }
        
        /* Ana container light - güçlü selector'lar */
        .stApp {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Sidebar light - güçlü selector'lar */
        .css-1d391kg, .css-1oe6wy4, .sidebar .sidebar-content {
            background: linear-gradient(180deg, var(--sidebar-bg), #ffffff) !important;
        }
        
        [data-testid="stApp"] {
            background-color: var(--bg-color) !important;
        }
        
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--sidebar-bg), #ffffff) !important;
        }
        
        section[data-testid="stSidebar"] > div {
            background: linear-gradient(180deg, var(--sidebar-bg), #ffffff) !important;
        }
    
    /* Genel görünüm */
    .main {
        padding-top: 1rem;
    }
    
    /* Başlık stilleri */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Buton stilleri */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        border: 2px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Sidebar stilleri */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc, #e2e8f0);
    }
    
    /* Metrik kartları */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    /* Form stilleri */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: border-color 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Ekspander stilleri */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #f8fafc, #e2e8f0);
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, #e2e8f0, #cbd5e1);
        transform: translateY(-1px);
    }
    
    /* Success/Error mesajları */
    .stSuccess {
        background: linear-gradient(90deg, #dcfce7, #bbf7d0);
        border-left: 4px solid var(--success-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    .stError {
        background: linear-gradient(90deg, #fef2f2, #fecaca);
        border-left: 4px solid var(--danger-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    .stWarning {
        background: linear-gradient(90deg, #fffbeb, #fed7aa);
        border-left: 4px solid var(--warning-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    .stInfo {
        background: linear-gradient(90deg, #eff6ff, #dbeafe);
        border-left: 4px solid var(--primary-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    /* Animasyonlar */
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Grafik konteyneri */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# Veritabanı bağlantısı
DB_PATH = "data/neofinx.db"

# Para birimi ve kur fonksiyonları
@st.cache_data(ttl=3600)  # 1 saat cache
def get_exchange_rates():
    """Güncel döviz kurlarını getir"""
    try:
        # Merkez Bankası API'si
        url = "https://api.exchangerate-api.com/v4/latest/TRY"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # TRY bazında kurlar, bize ters kurlar lazım (diğer para birimlerini TRY'ye çevirmek için)
            rates = data.get('rates', {})
            
            # Manuel olarak popüler kurları ekleyelim (fallback)
            exchange_rates = {
                'TRY': 1.0,
                'USD': 32.50,  # Fallback değerler
                'EUR': 35.20,
                'GBP': 41.80,
                'CHF': 36.40,
                'CAD': 24.10,
                'AUD': 21.30,
                'JPY': 0.22,
                'CNY': 4.52,
                'RUB': 0.35
            }
            
            # API'den gelen kurları kullan (eğer varsa)
            if rates:
                for currency in exchange_rates.keys():
                    if currency in rates and rates[currency] > 0:
                        # TRY bazından diğer para birimine ters kur hesapla
                        exchange_rates[currency] = 1.0 / rates[currency]
            
            return exchange_rates
            
        else:
            raise Exception("API yanıt vermedi")
            
    except Exception as e:
        st.warning(f"⚠️ Kur bilgileri alınamadı, manuel kurlar kullanılıyor: {str(e)}")
        # Manuel fallback kurlar
        return {
            'TRY': 1.0,
            'USD': 32.50,
            'EUR': 35.20,
            'GBP': 41.80,
            'CHF': 36.40,
            'CAD': 24.10,
            'AUD': 21.30,
            'JPY': 0.22,
            'CNY': 4.52,
            'RUB': 0.35
        }

def convert_to_try(amount, currency, exchange_rates):
    """Para birimini TRY'ye çevir"""
    if currency == 'TRY':
        return amount
    
    rate = exchange_rates.get(currency, 1.0)
    return amount * rate

def format_currency_display(amount, currency):
    """Para birimi ile görünüm formatı"""
    currency_symbols = {
        'TRY': '₺',
        'USD': '$',
        'EUR': '€', 
        'GBP': '£',
        'CHF': 'CHF',
        'CAD': 'C$',
        'AUD': 'A$',
        'JPY': '¥',
        'CNY': '¥',
        'RUB': '₽'
    }
    
    symbol = currency_symbols.get(currency, currency)
    if currency in ['JPY', 'CNY']:
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

def init_database():
    """Veritabanını başlat"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        cursor = conn.cursor()
        
        # Kategoriler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#3498db'
            )
        ''')
        
        # Harcamalar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                original_amount REAL,
                currency TEXT DEFAULT 'TRY',
                exchange_rate REAL DEFAULT 1.0,
                description TEXT,
                category_id INTEGER,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Mevcut verilere para birimi sütunları ekle (eğer yoksa)
        try:
            cursor.execute('ALTER TABLE expenses ADD COLUMN original_amount REAL')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE expenses ADD COLUMN currency TEXT DEFAULT "TRY"')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE expenses ADD COLUMN exchange_rate REAL DEFAULT 1.0')
        except:
            pass
        
        # Mevcut NULL değerleri düzelt
        cursor.execute('''
            UPDATE expenses 
            SET original_amount = amount, currency = 'TRY', exchange_rate = 1.0 
            WHERE original_amount IS NULL OR currency IS NULL OR exchange_rate IS NULL
        ''')
        
        # Test için örnek farklı para birimi verileri ekle (sadece bir kez)
        cursor.execute('SELECT COUNT(*) FROM expenses WHERE currency != "TRY"')
        foreign_count = cursor.fetchone()[0]
        
        if foreign_count == 0:
            # Test verileri ekle
            test_expenses = [
                (325.0, 10.0, 'USD', 32.5, 'Starbucks kahve', 1, '2024-01-20'),
                (704.0, 20.0, 'EUR', 35.2, 'Amazon alışveriş', 5, '2024-01-21'), 
                (418.0, 10.0, 'GBP', 41.8, 'Uber ride', 2, '2024-01-22'),
                (182.0, 5.0, 'USD', 36.4, 'Apple App Store', 3, '2024-01-23'),
                (1760.0, 50.0, 'EUR', 35.2, 'Hotel booking', 3, '2024-01-24')
            ]
            
            for tl_amount, orig_amount, currency, rate, desc, cat_id, date_str in test_expenses:
                cursor.execute('''
                    INSERT INTO expenses (amount, original_amount, currency, exchange_rate, description, category_id, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (tl_amount, orig_amount, currency, rate, desc, cat_id, date_str))
        
        # Varsayılan kategoriler ekle
        default_categories = [
            ('Yemek', '#e74c3c'),
            ('Ulaşım', '#3498db'),
            ('Eğlence', '#9b59b6'),
            ('Sağlık', '#2ecc71'),
            ('Alışveriş', '#f39c12'),
            ('Faturalar', '#34495e'),
            ('Diğer', '#95a5a6')
        ]
        
        for cat_name, color in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)
            ''', (cat_name, color))
        
        conn.commit()
        
    except Exception as e:
        st.error(f"Veritabanı başlatma hatası: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_expense(amount, description, category_id, date, currency='TRY', exchange_rate=1.0):
    """Yeni harcama ekle"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Original amount (girilen miktar)
        original_amount = amount
        
        # TL karşılığı hesaplama
        if currency != 'TRY':
            tl_amount = amount * exchange_rate
        else:
            tl_amount = amount
        
        cursor.execute('''
            INSERT INTO expenses (amount, original_amount, currency, exchange_rate, description, category_id, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tl_amount, original_amount, currency, exchange_rate, description, category_id, date))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Harcama ekleme hatası: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_categories():
    """Kategorileri getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, color FROM categories')
        categories = cursor.fetchall()
        return categories
    except Exception as e:
        st.error(f"Kategori getirme hatası: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_expenses(limit=None):
    """Harcamaları getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        query = '''
            SELECT e.amount, e.original_amount, e.currency, e.exchange_rate, 
                   e.description, c.name as category_name, e.date, c.color, e.created_at
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            ORDER BY e.created_at DESC, e.date DESC, e.id DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        expenses = cursor.fetchall()
        return expenses
    except Exception as e:
        st.error(f"Harcama getirme hatası: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_real_data():
    """Gerçek veritabanından veri getir"""
    expenses = get_expenses()
    data = []
    
    for row in expenses:
        try:
            # Yeni format: amount, original_amount, currency, exchange_rate, description, category_name, date, color, created_at
            if len(row) >= 9:
                amount, original_amount, currency, exchange_rate, description, category_name, date_str, color, created_at = row
                
                # NULL değerleri düzelt
                original_amount = original_amount if original_amount is not None else amount
                currency = currency if currency is not None else 'TRY'
                exchange_rate = exchange_rate if exchange_rate is not None else 1.0
                
            elif len(row) >= 8:
                amount, original_amount, currency, exchange_rate, description, category_name, date_str, color = row
                created_at = None
                
                # NULL değerleri düzelt
                original_amount = original_amount if original_amount is not None else amount
                currency = currency if currency is not None else 'TRY'
                exchange_rate = exchange_rate if exchange_rate is not None else 1.0
                
            else:
                # Eski format için uyumluluk
                amount, description, category_name, date_str, color = row
                original_amount = amount
                currency = 'TRY'
                exchange_rate = 1.0
                created_at = None
            
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                date_obj = datetime.now()
                
            try:
                if created_at:
                    created_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                else:
                    created_obj = date_obj
            except:
                created_obj = date_obj
            
            data.append({
                'date': date_obj,
                'created_at': created_obj,
                'amount': float(amount),  # TL cinsinden
                'original_amount': float(original_amount),
                'currency': str(currency),
                'exchange_rate': float(exchange_rate),
                'category_name': category_name.lower(),
                'description': description or 'Açıklama yok'
            })
            
        except Exception as e:
            print(f"Veri işleme hatası: {e}, Row: {row}")
            continue
    
    return data

@st.cache_data
def create_demo_data():
    """Demo veri oluştur (gerçek veri yoksa)"""
    random.seed(42)
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()
    current_date = start_date
    
    categories = ['yemek', 'ulasim', 'eglence', 'saglik', 'alisveris', 'faturalar']
    data = []
    
    while current_date <= end_date:
        num_expenses = random.randint(1, 4)
        for _ in range(num_expenses):
            category = random.choice(categories)
            
            if category == 'yemek':
                amount = random.gauss(50, 20)
            elif category == 'ulasim':
                amount = random.gauss(30, 10)
            elif category == 'eglence':
                amount = random.gauss(100, 40)
            else:
                amount = random.gauss(80, 30)
            
            amount = max(10, amount)
            
            data.append({
                'date': current_date,
                'amount': round(amount, 2),
                'category_name': category,
                'description': f"{category.title()} harcamasi"
            })
        
        current_date += timedelta(days=1)
    
    return data

# Veritabanını başlat
init_database()

# Modern ana başlık 
st.markdown("""
<div class="main-header">
    <h1>🏦 NeoFinX</h1>
    <p>Yapay Zeka Destekli Akıllı Bütçe ve Harcama Asistanı</p>
</div>
""", unsafe_allow_html=True)

# Sidebar menu
st.sidebar.title("📋 Menu")
page = st.sidebar.selectbox(
    "Sayfa Secin:",
    ["🏠 Ana Sayfa", "➕ Harcama Ekle", "📤 CSV Import", "📊 Harcama Analizi", "📈 Butce Planlama"]
)

# Veri kaynağı seçimi
data_source = st.sidebar.radio(
    "Veri Kaynagi:",
    ["📊 Gerçek Veriler", "🎭 Demo Veriler"]
)

# Güncel kur bilgileri
st.sidebar.markdown("---")
st.sidebar.markdown("### 💱 Güncel Kurlar")

# Kurları getir ve göster
try:
    exchange_rates = get_exchange_rates()
    
    # Popüler kurları göster
    popular_currencies = ['USD', 'EUR', 'GBP']
    
    for currency in popular_currencies:
        if currency in exchange_rates:
            rate = exchange_rates[currency]
            currency_symbols = {'USD': '🇺🇸 $', 'EUR': '🇪🇺 €', 'GBP': '🇬🇧 £'}
            symbol = currency_symbols.get(currency, currency)
            
            st.sidebar.metric(
                label=f"{symbol}",
                value=f"{rate:.4f} ₺",
                help=f"1 {currency} = {rate:.4f} TRY"
            )
    
    # Küçük yazı ile son güncelleme
    st.sidebar.caption("🕐 Kurlar saatlik güncellenir")
    
except Exception as e:
    st.sidebar.error("❌ Kur bilgileri alınamadı")

# Geliştirici bilgileri - Sidebar'da modern card
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 12px;
    border-radius: 10px;
    margin: 10px 0;
    text-align: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
">
    <div style="color: white; font-size: 13px; font-weight: 600; margin-bottom: 8px;">
        👨‍💻 Proje Geliştiricileri
    </div>
    <div style="color: rgba(255, 255, 255, 0.9); font-size: 12px; line-height: 1.4;">
        <div style="margin-bottom: 3px;">🎯 Erkan Tan</div>
        <div>🎯 Raziyegül Kahraman</div>
    </div>
</div>
""", unsafe_allow_html=True)

def import_csv_data(uploaded_file):
    """CSV dosyasından veri import et"""
    try:
        # CSV içeriğini oku
        content = uploaded_file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        imported_count = 0
        categories = get_categories()
        category_map = {cat[1].lower(): cat[0] for cat in categories}
        
        # Kategori eşleştirme haritası
        category_mapping = {
            'yemek & içecek': 'yemek',
            'yemek': 'yemek',
            'ulaşım': 'ulaşım',
            'ulasim': 'ulaşım',
            'eğlence': 'eğlence',
            'eglence': 'eğlence',
            'sağlık': 'sağlık',
            'saglik': 'sağlık',
            'alışveriş': 'alışveriş',
            'alisveris': 'alışveriş',
            'faturalar': 'faturalar',
            'eğitim': 'eğlence',  # Eğitim -> Eğlence
            'egitim': 'eğlence',
            'spor': 'eğlence',    # Spor -> Eğlence
            'kişisel bakım': 'alışveriş',  # Kişisel Bakım -> Alışveriş
            'kisisel bakim': 'alışveriş',
            'diğer': 'diğer',
            'diger': 'diğer'
        }
        
        # İlk satır başlık mı kontrol et
        header = lines[0].lower()
        start_line = 1 if 'date' in header or 'tarih' in header else 0
        
        for line in lines[start_line:]:
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    # Format 1: date,amount,category,description
                    # Format 2: tarih,tutar,aciklama,kategori
                    if len(parts) >= 4:
                        if 'date' in lines[0] or parts[0].count('-') == 2:
                            # Format 1: date,amount,category,description
                            date_str = parts[0].strip()
                            amount = float(parts[1].strip())
                            category_name = parts[2].strip().lower()
                            description = parts[3].strip()
                        else:
                            # Format 2: tarih,tutar,aciklama,kategori
                            date_str = parts[0].strip()
                            amount = float(parts[1].strip())
                            description = parts[2].strip()
                            category_name = parts[3].strip().lower()
                    else:
                        # Sadece 3 alan: date,amount,category
                        date_str = parts[0].strip()
                        amount = float(parts[1].strip())
                        category_name = parts[2].strip().lower()
                        description = f"{category_name.title()} harcaması"
                    
                    # Kategori eşleştir
                    mapped_category = category_mapping.get(category_name, category_name)
                    category_id = category_map.get(mapped_category, category_map.get('diğer', 1))
                    
                    # Tarihi parse et
                    try:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        try:
                            parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
                        except:
                            try:
                                parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
                            except:
                                parsed_date = datetime.now()
                    
                    add_expense(amount, description, category_id, parsed_date.strftime('%Y-%m-%d'))
                    imported_count += 1
                    
                except Exception as e:
                    st.warning(f"Satır atlandı: {line[:50]}... Hata: {str(e)}")
                    continue
        
        return imported_count
        
    except Exception as e:
        st.error(f"CSV işlenirken hata: {str(e)}")
        return 0

if page == "➕ Harcama Ekle":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">➕ Yeni Harcama Ekle</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Harcamalarınızı hızlı ve kolay bir şekilde kaydedin</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("expense_form"):
        # Form için özel stil
        st.markdown("""
        <style>
        .expense-form {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("### 💰 Finansal Bilgiler")
            
            # Para birimi seçimi ve kur gösterimi
            col_curr1, col_curr2 = st.columns([1, 1])
            
            with col_curr1:
                currencies = ['TRY', 'USD', 'EUR', 'GBP', 'CHF', 'CAD', 'AUD', 'JPY', 'CNY', 'RUB']
                selected_currency = st.selectbox(
                    "💱 Para Birimi",
                    currencies,
                    help="Harcama para birimini seçin"
                )
            
            with col_curr2:
                # Güncel kurları getir
                exchange_rates = get_exchange_rates()
                
                if selected_currency != 'TRY':
                    current_rate = exchange_rates.get(selected_currency, 1.0)
                    st.info(f"📊 {selected_currency}/TRY: {current_rate:.4f}")
                else:
                    st.info("🇹🇷 Türk Lirası seçildi")
            
            # Tutar girişi
            amount = st.number_input(
                f"Tutar ({selected_currency})", 
                min_value=0.01, 
                value=50.0 if selected_currency == 'TRY' else 10.0,
                step=0.01,
                help=f"Harcama tutarınızı {selected_currency} cinsinden girin"
            )
            
            # TL karşılığını göster
            if selected_currency != 'TRY':
                tl_equivalent = convert_to_try(amount, selected_currency, exchange_rates)
                st.caption(f"💰 TL Karşılığı: {tl_equivalent:,.2f} ₺")
            
            categories = get_categories()
            category_options = {cat[1]: cat[0] for cat in categories}  # name: id
            selected_category = st.selectbox(
                "📂 Kategori", 
                list(category_options.keys()),
                help="Harcamanın hangi kategoriye ait olduğunu seçin"
            )
            
        with col2:
            st.markdown("### 📝 Detay Bilgileri")
            description = st.text_input(
                "Açıklama", 
                placeholder="Örn: Akşam yemeği, Market alışverişi",
                help="Harcamanızla ilgili kısa bir açıklama yazın"
            )
            expense_date = st.date_input(
                "Tarih", 
                value=datetime.now().date(),
                help="Harcama tarihinizi seçin"
            )
        
        st.markdown("---")
        
        # Özelleştirilmiş submit butonu
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button(
                "🚀 Harcama Kaydet", 
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            if amount > 0:
                category_id = category_options[selected_category]
                
                # Kur hesaplama
                exchange_rate = exchange_rates.get(selected_currency, 1.0)
                
                success = add_expense(
                    amount=amount, 
                    description=description, 
                    category_id=category_id, 
                    date=expense_date.strftime('%Y-%m-%d'),
                    currency=selected_currency,
                    exchange_rate=exchange_rate
                )
                
                if success:
                    if selected_currency != 'TRY':
                        tl_amount = convert_to_try(amount, selected_currency, exchange_rates)
                        st.success(f"✅ {format_currency_display(amount, selected_currency)} ({tl_amount:,.2f} ₺) tutarında harcama başarıyla eklendi!")
                    else:
                        st.success(f"✅ {amount:,.2f} ₺ tutarında harcama başarıyla eklendi!")
                    
                    st.balloons()
                    # Balon efekti için kısa bir gecikme
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Harcama eklenirken bir hata oluştu!")
            else:
                st.error("❌ Lütfen geçerli bir tutar girin!")

elif page == "📤 CSV Import":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe, #00f2fe); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">📤 CSV Dosyası ile Toplu Veri İçe Aktarma</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Mevcut harcama verilerinizi toplu olarak sisteme aktarın</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mevcut sample CSV'yi import et
    st.markdown("### 🎯 Hızlı Başlangıç")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Örnek Verileri Yükle", type="primary"):
            if os.path.exists("data/sample_expenses.csv"):
                with open("data/sample_expenses.csv", 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Fake uploaded file object oluştur
                class FakeFile:
                    def __init__(self, content):
                        self.content = content.encode('utf-8')
                        self.pos = 0
                    
                    def read(self):
                        return self.content
                    
                    def seek(self, pos):
                        self.pos = pos
                
                fake_file = FakeFile(content)
                
                with st.spinner("Örnek veriler yükleniyor..."):
                    imported_count = import_csv_data(fake_file)
                
                if imported_count > 0:
                    st.success(f"✅ {imported_count} örnek harcama kaydı eklendi!")
                    st.balloons()
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Örnek veriler yüklenemedi!")
            else:
                st.error("❌ sample_expenses.csv dosyası bulunamadı!")
    
    with col2:
        # Mevcut veritabanı durumu
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM expenses')
            current_count = cursor.fetchone()[0]
            conn.close()
        except:
            current_count = 0
        
        st.info(f"""
        **📊 Mevcut Durum:**
        - Veritabanında {current_count} harcama kaydı var
        - Örnek dosyada ~400 kayıt var
        - Kategoriler: Yemek, Ulaşım, Eğlence, Sağlık, vb.
        """)
    
    st.markdown("---")
    
    st.info("""
    **📋 CSV Format Örneği:**
    ```
    tarih,tutar,aciklama,kategori
    2024-01-15,50.0,Akşam yemeği,yemek
    2024-01-16,25.0,Otobüs bileti,ulaşım
    2024-01-17,120.0,Market alışverişi,alışveriş
    ```
    
    **📌 Format Kuralları:**
    - Tarih formatı: YYYY-MM-DD veya DD.MM.YYYY
    - Tutar: Sayısal değer (nokta ile ondalık)
    - Kategori: yemek, ulaşım, eğlence, sağlık, alışveriş, faturalar, diğer
    """)
    
    # Örnek CSV dosyası oluştur
    if st.button("📋 Örnek CSV İndir"):
        sample_csv = """tarih,tutar,aciklama,kategori
2024-01-15,50.0,Akşam yemeği,yemek
2024-01-16,25.0,Otobüs bileti,ulaşım
2024-01-17,120.0,Market alışverişi,alışveriş
2024-01-18,75.0,Sinema bileti,eğlence
2024-01-19,200.0,Elektrik faturası,faturalar"""
        
        st.download_button(
            label="💾 orneg_harcamalar.csv",
            data=sample_csv,
            file_name="orneg_harcamalar.csv",
            mime="text/csv"
        )
    
    # CSV upload
    uploaded_file = st.file_uploader(
        "📁 CSV Dosyası Seçin",
        type=['csv'],
        help="Yukarıdaki formatta hazırlanmış CSV dosyasını yükleyin"
    )
    
    if uploaded_file is not None:
        st.write("📊 **Dosya Bilgileri:**")
        st.write(f"- Dosya adı: {uploaded_file.name}")
        st.write(f"- Dosya boyutu: {uploaded_file.size} bytes")
        
        # Dosya önizlemesi
        preview_content = uploaded_file.read().decode('utf-8')
        uploaded_file.seek(0)  # Reset file pointer
        
        lines = preview_content.strip().split('\n')
        st.write(f"- Toplam satır: {len(lines)}")
        st.write(f"- Veri satırı: {len(lines)-1}")
        
        st.subheader("🔍 Dosya Önizlemesi")
        preview_lines = lines[:6]  # İlk 5 satır + başlık
        for i, line in enumerate(preview_lines):
            if i == 0:
                st.write(f"**Başlık:** {line}")
            else:
                st.write(f"**{i}.** {line}")
        
        if len(lines) > 6:
            st.write(f"... ve {len(lines)-6} satır daha")
        
        # Import butonu
        if st.button("📤 Verileri İçe Aktar", type="primary"):
            with st.spinner("İçe aktarılıyor..."):
                imported_count = import_csv_data(uploaded_file)
                
            if imported_count > 0:
                st.success(f"✅ {imported_count} harcama kaydı başarıyla eklendi!")
                st.balloons()
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Hiçbir veri içe aktarılamadı. Format kontrolü yapın.")

# Veri kaynağına göre data seç
if data_source == "📊 Gerçek Veriler":
    data = get_real_data()
    if not data:
        st.sidebar.warning("⚠️ Henüz veri yok! Önce harcama ekleyin.")
        data = create_demo_data()
else:
    data = create_demo_data()

# Ana Sayfa
if page == "🏠 Ana Sayfa":
    col1, col2, col3 = st.columns(3)
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month_data = [
        item for item in data 
        if item['date'].month == current_month and item['date'].year == current_year
    ]
    
    total_spending = sum(item['amount'] for item in this_month_data)
    
    with col1:
        st.metric("💳 Bu Ay Toplam Harcama", f"{total_spending:.0f} TL")
    
    with col2:
        avg_daily = total_spending / 30 if total_spending > 0 else 0
        st.metric("📊 Gunluk Ortalama", f"{avg_daily:.0f} TL")
    
    with col3:
        expense_count = len(this_month_data)
        st.metric("📈 Bu Ay Harcama Sayısı", f"{expense_count}")
    
    # Veri kaynağı göstergesi
    if data_source == "📊 Gerçek Veriler":
        st.info("📊 Gerçek verileriniz gösteriliyor")
    else:
        st.warning("🎭 Demo veriler gösteriliyor - Gerçek veri için 'Harcama Ekle' sayfasını kullanın")
    
    # Son harcamalar - Dinamik güncelleme
    st.subheader("💳 Son 10 Harcama (Canlı)")
    
    # Her zaman en güncel verileri getir (cache yok)
    @st.cache_data(ttl=0)  # Cache'siz
    def get_latest_expenses():
        return get_expenses(limit=10)
    
    # Güncel verileri getir
    latest_expenses_raw = get_latest_expenses()
    
    if latest_expenses_raw:
        # Başlık satırı
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2.5, 1.5, 1.5, 1.5, 1])
        with col1:
            st.write("**📅 Tarih**")
        with col2:
            st.write("**📝 Açıklama**")
        with col3:
            st.write("**📁 Kategori**")
        with col4:
            st.write("**💱 Orijinal**")
        with col5:
            st.write("**💰 TL Karşılığı**")
        with col6:
            st.write("**🕐 Zaman**")
        
        st.markdown("---")
        
        # Son 10 harcamayı işle
        for i, row in enumerate(latest_expenses_raw[:10], 1):
            try:
                # Row parsing
                if len(row) >= 9:
                    amount, original_amount, currency, exchange_rate, description, category_name, date_str, color, created_at = row
                elif len(row) >= 8:
                    amount, original_amount, currency, exchange_rate, description, category_name, date_str, color = row
                    created_at = None
                else:
                    continue
                
                # NULL değer kontrolü
                original_amount = original_amount if original_amount is not None else amount
                currency = currency if currency is not None else 'TRY'
                description = description if description else 'Açıklama yok'
                
                # Tarih işleme
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    display_date = date_obj.strftime('%d.%m.%Y')
                except:
                    display_date = date_str
                
                # Zaman işleme
                try:
                    if created_at:
                        time_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        display_time = time_obj.strftime('%H:%M')
                    else:
                        display_time = "—"
                except:
                    display_time = "—"
                
                col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2.5, 1.5, 1.5, 1.5, 1])
                
                with col1:
                    st.write(f"**{i}.** {display_date}")
                
                with col2:
                    if description and description != f"{category_name.title()} harcaması":
                        st.write(f"📋 {description[:25]}..." if len(description) > 25 else f"📋 {description}")
                    else:
                        st.write("📝 *Genel harcama*")
                
                with col3:
                    # Kategori ikonları
                    category_icons = {
                        'yemek': '🍽️',
                        'ulaşım': '🚗', 
                        'eğlence': '🎮',
                        'sağlık': '🏥',
                        'alışveriş': '🛒',
                        'faturalar': '💡',
                        'diğer': '📦'
                    }
                    icon = category_icons.get(category_name.lower(), '📦')
                    st.write(f"{icon} {category_name.title()}")
                
                with col4:
                    # Orijinal para birimi
                    if currency != 'TRY':
                        st.write(f"**{format_currency_display(original_amount, currency)}**")
                    else:
                        st.write(f"**{original_amount:.0f} ₺**")
                
                with col5:
                    # TL karşılığı ve renk kodlaması
                    if currency != 'TRY':
                        if amount > 1000:
                            st.write(f"🔴 **{amount:.0f} ₺**")
                        elif amount > 500:
                            st.write(f"🟡 **{amount:.0f} ₺**")
                        else:
                            st.write(f"🟢 **{amount:.0f} ₺**")
                    else:
                        # TRY için de renk kodlaması
                        if amount > 1000:
                            st.write(f"🔴 **{amount:.0f} ₺**")
                        elif amount > 500:
                            st.write(f"🟡 **{amount:.0f} ₺**")
                        else:
                            st.write(f"🟢 **{amount:.0f} ₺**")
                
                with col6:
                    if display_time != "—":
                        st.write(f"🕐 {display_time}")
                    else:
                        st.write("—")
                        
            except Exception as e:
                continue
                
        # Güncelleme butonu
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Listeyi Yenile", key="refresh_recent", type="secondary"):
                st.cache_data.clear()
                st.rerun()
                
        st.caption("💡 Liste otomatik olarak en son eklenen 10 harcamayı gösterir")
        
    else:
        st.info("📝 Henüz harcama kaydı bulunmuyor. Harcama eklemek için ➕ Harcama Ekle sayfasını kullanın.")
    
    st.subheader("📈 İnteraktif Harcama Trendi")
    
    # Tarih aralığı seçimi
    col_period1, col_period2 = st.columns(2)
    with col_period1:
        period_options = {
            "Son 7 Gün": 7,
            "Son 15 Gün": 15,
            "Son 30 Gün": 30,
            "Son 60 Gün": 60,
            "Son 90 Gün": 90
        }
        selected_period = st.selectbox("📅 Zaman Aralığı:", list(period_options.keys()), index=2)
        days = period_options[selected_period]
    
    with col_period2:
        chart_type = st.selectbox("📊 Grafik Tipi:", ["Çizgi Grafik", "Alan Grafik", "Bar Grafik"])
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_data = [item for item in data if item['date'] >= cutoff_date]
    
    if recent_data:
        # Günlük toplam hesaplama
        daily_totals = {}
        daily_counts = {}
        daily_details = {}
        
        for item in recent_data:
            date_str = item['date'].strftime('%Y-%m-%d')
            daily_totals[date_str] = daily_totals.get(date_str, 0) + item['amount']
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            
            if date_str not in daily_details:
                daily_details[date_str] = []
            daily_details[date_str].append(item)
        
        # Eksik günleri sıfır ile doldur
        start_date = cutoff_date.date()
        end_date = datetime.now().date()
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in daily_totals:
                daily_totals[date_str] = 0
                daily_counts[date_str] = 0
            current_date += timedelta(days=1)
        
        # Sıralı liste oluştur
        sorted_dates = sorted(daily_totals.keys())
        sorted_amounts = [daily_totals[date] for date in sorted_dates]
        sorted_counts = [daily_counts[date] for date in sorted_dates]
        
        # Hover bilgileri hazırla
        hover_text = []
        for i, date in enumerate(sorted_dates):
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d %B %Y')
            count = sorted_counts[i]
            amount = sorted_amounts[i]
            
            hover_info = f"<b>{formatted_date}</b><br>"
            hover_info += f"💰 Toplam: {amount:,.0f} TL<br>"
            hover_info += f"📊 İşlem Sayısı: {count}<br>"
            
            if date in daily_details and daily_details[date]:
                hover_info += "<br><b>🏷️ Kategoriler:</b><br>"
                category_amounts = {}
                for item in daily_details[date]:
                    cat = item['category_name'].title()
                    category_amounts[cat] = category_amounts.get(cat, 0) + item['amount']
                
                for cat, cat_amount in sorted(category_amounts.items(), key=lambda x: x[1], reverse=True)[:3]:
                    hover_info += f"• {cat}: {cat_amount:,.0f} TL<br>"
            
            hover_text.append(hover_info)
        
        # Grafik oluştur
        if chart_type == "Çizgi Grafik":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sorted_dates,
                y=sorted_amounts,
                mode='lines+markers',
                name='Günlük Harcama',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#667eea'),
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.1)',
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            ))
        
        elif chart_type == "Alan Grafik":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sorted_dates,
                y=sorted_amounts,
                mode='lines',
                name='Günlük Harcama',
                line=dict(color='#667eea', width=2),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.3)',
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            ))
        
        else:  # Bar Grafik
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sorted_dates,
                y=sorted_amounts,
                name='Günlük Harcama',
                marker_color='#667eea',
                opacity=0.8,
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            ))
        
        # Dark mode'a göre grafik düzenleme
        title_color = '#f1f5f9' if dark_mode else '#1e293b'
        font_color = '#94a3b8' if dark_mode else '#64748b'
        grid_color = 'rgba(100,116,139,0.3)' if dark_mode else 'rgba(0,0,0,0.1)'
        
        fig.update_layout(
            title=dict(
                text=f"📈 {selected_period} Harcama Trendi ({chart_type})",
                font=dict(size=20, color=title_color),
                x=0.5
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=font_color),
            showlegend=False,
            margin=dict(l=0, r=0, t=60, b=0),
            hovermode='x unified'
        )
        
        fig.update_xaxes(
            title="📅 Tarih",
            gridcolor=grid_color,
            showgrid=True,
            zeroline=False,
            tickformat='%d.%m',
            title_font=dict(color=font_color),
            tickfont=dict(color=font_color)
        )
        
        fig.update_yaxes(
            title="💰 Tutar (TL)",
            gridcolor=grid_color,
            showgrid=True,
            zeroline=False,
            tickformat=',.0f',
            title_font=dict(color=font_color),
            tickfont=dict(color=font_color)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # İstatistik özeti
        col1, col2, col3, col4 = st.columns(4)
        
        total_amount = sum(sorted_amounts)
        avg_daily = total_amount / len(sorted_amounts) if sorted_amounts else 0
        max_day = max(sorted_amounts) if sorted_amounts else 0
        total_transactions = sum(sorted_counts)
        
        with col1:
            st.metric("💳 Toplam Harcama", f"{total_amount:,.0f} TL")
        with col2:
            st.metric("📊 Günlük Ortalama", f"{avg_daily:,.0f} TL")
        with col3:
            st.metric("🔝 En Yüksek Gün", f"{max_day:,.0f} TL")
        with col4:
            st.metric("🧾 Toplam İşlem", f"{total_transactions}")
    
    else:
        st.info(f"📅 Son {days} günde harcama kaydı bulunamadı.")
    
    # Akıllı Öneriler Bölümü
    st.markdown("---")
    st.subheader("🤖 Akıllı Finansal Öneriler")
    
    # Harcama pattern analizini çalıştır
    insights = analyze_spending_patterns()
    
    if insights:
        # Önerileri priority'ye göre grupla
        high_priority = [i for i in insights if i['priority'] == 'high']
        medium_priority = [i for i in insights if i['priority'] == 'medium']
        low_priority = [i for i in insights if i['priority'] == 'low']
        
        # Yüksek öncelikli uyarılar
        if high_priority:
            st.markdown("### ⚠️ Önemli Uyarılar")
            for insight in high_priority:
                with st.container():
                    # Dark mode'a göre alert renkleri
                    if insight['type'] == 'warning':
                        bg_color = 'linear-gradient(90deg, #dc2626, #ef4444)' if dark_mode else 'linear-gradient(90deg, #fef2f2, #fee2e2)'
                        text_color = '#fecaca' if dark_mode else '#dc2626'
                    else:
                        bg_color = 'linear-gradient(90deg, #1e40af, #3b82f6)' if dark_mode else 'linear-gradient(90deg, #eff6ff, #dbeafe)'
                        text_color = '#dbeafe' if dark_mode else '#1e40af'
                    
                    st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        padding: 1rem; 
                        border-radius: 12px; 
                        margin: 0.5rem 0;
                        border-left: 4px solid {text_color.replace('#', '').replace('fecaca', '#dc2626').replace('dbeafe', '#1e40af')};
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{insight['icon']}</span>
                            <strong style="color: {text_color}; font-size: 1.1rem;">{insight['title']}</strong>
                        </div>
                        <p style="color: {text_color}; margin: 0.3rem 0; font-size: 0.95rem;">{insight['message']}</p>
                        <p style="color: {text_color.replace('#dc2626', '#b91c1c').replace('#1e40af', '#1e3a8a')}; margin: 0; font-size: 0.85rem; font-style: italic;">
                            💡 {insight['suggestion']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Orta ve düşük öncelikli öneriler
        other_insights = medium_priority + low_priority
        if other_insights:
            st.markdown("### 💡 Diğer Öneriler")
            
            # 2 sütunlu layout
            col1, col2 = st.columns(2)
            
            for i, insight in enumerate(other_insights[:6]):  # En fazla 6 öneri göster
                target_col = col1 if i % 2 == 0 else col2
                
                with target_col:
                    # Öneri tipine göre renk seçimi
                    if insight['type'] == 'success':
                        bg_color = 'linear-gradient(90deg, #065f46, #10b981)' if dark_mode else 'linear-gradient(90deg, #f0fdf4, #dcfce7)'
                        text_color = '#d1fae5' if dark_mode else '#065f46'
                        border_color = '#10b981'
                    elif insight['type'] == 'warning':
                        bg_color = 'linear-gradient(90deg, #92400e, #f59e0b)' if dark_mode else 'linear-gradient(90deg, #fffbeb, #fef3c7)'
                        text_color = '#fed7aa' if dark_mode else '#92400e'
                        border_color = '#f59e0b'
                    else:  # info
                        bg_color = 'linear-gradient(90deg, #1e40af, #3b82f6)' if dark_mode else 'linear-gradient(90deg, #eff6ff, #dbeafe)'
                        text_color = '#dbeafe' if dark_mode else '#1e40af'
                        border_color = '#3b82f6'
                    
                    st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        padding: 1rem; 
                        border-radius: 10px; 
                        margin: 0.5rem 0;
                        border: 1px solid {border_color};
                        min-height: 120px;
                        transition: transform 0.2s ease;
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.1rem; margin-right: 0.5rem;">{insight['icon']}</span>
                            <strong style="color: {text_color}; font-size: 1rem;">{insight['title']}</strong>
                        </div>
                        <p style="color: {text_color}; margin: 0.3rem 0; font-size: 0.9rem; line-height: 1.3;">{insight['message']}</p>
                        <p style="color: {text_color}; margin: 0; font-size: 0.8rem; font-style: italic; opacity: 0.9;">
                            {insight['suggestion']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        # Veri yoksa genel öneriler göster
        st.info("📊 Detaylı analiz için daha fazla harcama verisi gerekiyor.")
        
        st.markdown("### 📚 Genel Finansal İpuçları")
        recommendations = get_spending_recommendations()
        
        col1, col2 = st.columns(2)
        for i, rec in enumerate(recommendations[:4]):  # İlk 4 öneriyi göster
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                bg_color = 'linear-gradient(90deg, #1e293b, #334155)' if dark_mode else 'linear-gradient(90deg, #f8fafc, #f1f5f9)'
                text_color = '#f1f5f9' if dark_mode else '#1e293b'
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    padding: 1rem; 
                    border-radius: 10px; 
                    margin: 0.5rem 0;
                    border: 1px solid {'#475569' if dark_mode else '#e2e8f0'};
                    min-height: 120px;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.1rem; margin-right: 0.5rem;">{rec['icon']}</span>
                        <strong style="color: {text_color}; font-size: 1rem;">{rec['title']}</strong>
                    </div>
                    <p style="color: {text_color}; margin: 0.3rem 0; font-size: 0.9rem; line-height: 1.3;">{rec['description']}</p>
                    <p style="color: {'#94a3b8' if dark_mode else '#64748b'}; margin: 0; font-size: 0.8rem; font-style: italic;">
                        ⚡ {rec['action']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

elif page == "📊 Harcama Analizi":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb, #f5576c); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">📊 Detaylı Harcama Analizi</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Harcama alışkanlıklarınızı detaylı analiz edin</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not data:
        st.warning("📊 Analiz için veri bulunamadı!")
        st.stop()
    
    category_totals = {}
    for item in data:
        cat = item['category_name']
        category_totals[cat] = category_totals.get(cat, 0) + item['amount']
    
    if category_totals:
        # İnteraktif kontroller
        col1, col2 = st.columns(2)
        with col1:
            pie_type = st.selectbox("📊 Grafik Türü:", ["Pasta Grafik", "Donut Grafik", "Bar Grafik"])
        with col2:
            show_values = st.checkbox("💰 Değerleri Göster", value=True)
        
        # Modern renk paleti
        modern_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#a8edea', '#fed6e3']
        
        # Veriyi hazırla
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        labels = [cat.title() for cat, _ in sorted_categories]
        values = [amount for _, amount in sorted_categories]
        
        # Detaylı hover bilgileri hazırla
        total_amount = sum(values)
        hover_text = []
        for i, (label, value) in enumerate(zip(labels, values)):
            percentage = (value / total_amount * 100) if total_amount > 0 else 0
            
            # Bu kategorideki işlem sayısını hesapla
            cat_transactions = len([item for item in data if item['category_name'].lower() == label.lower()])
            avg_transaction = value / cat_transactions if cat_transactions > 0 else 0
            
            hover_info = f"<b>{label}</b><br>"
            hover_info += f"💰 Tutar: {value:,.0f} TL<br>"
            hover_info += f"📊 Oran: {percentage:.1f}%<br>"
            hover_info += f"🧾 İşlem Sayısı: {cat_transactions}<br>"
            hover_info += f"💳 Ortalama İşlem: {avg_transaction:,.0f} TL"
            
            hover_text.append(hover_info)
        
        if pie_type == "Pasta Grafik":
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text,
                textinfo='label+percent' if show_values else 'label',
                textposition='inside',
                marker=dict(
                    colors=modern_colors[:len(labels)],
                    line=dict(color='#FFFFFF', width=2)
                ),
                pull=[0.05 if i == 0 else 0 for i in range(len(labels))]  # En büyük dilimi çıkar
            )])
            
        elif pie_type == "Donut Grafik":
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text,
                textinfo='label+percent' if show_values else 'label',
                textposition='inside',
                marker=dict(
                    colors=modern_colors[:len(labels)],
                    line=dict(color='#FFFFFF', width=2)
                )
            )])
            
        else:  # Bar Grafik
            fig_pie = go.Figure(data=[go.Bar(
                x=values,
                y=labels,
                orientation='h',
                marker=dict(
                    color=modern_colors[:len(labels)],
                    opacity=0.8
                ),
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            )])
        
        # Layout düzenlemesi - Dark mode desteği
        title_color = '#f1f5f9' if dark_mode else '#1e293b'
        font_color = '#94a3b8' if dark_mode else '#64748b'
        grid_color = 'rgba(100,116,139,0.3)' if dark_mode else 'rgba(0,0,0,0.1)'
        
        if pie_type in ["Pasta Grafik", "Donut Grafik"]:
            fig_pie.update_layout(
                title=dict(
                    text="🎯 Harcama Kategorileri Dağılımı",
                    font=dict(size=20, color=title_color),
                    x=0.5
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=font_color, size=12),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(color=font_color)
                ),
                margin=dict(l=0, r=0, t=60, b=0)
            )
            
            # Donut grafiği için merkez yazı
            if pie_type == "Donut Grafik":
                fig_pie.add_annotation(
                    text=f"<b>Toplam</b><br>{total_amount:,.0f} TL",
                    showarrow=False,
                    font_size=16,
                    font_color=title_color
                )
        else:
            fig_pie.update_layout(
                title=dict(
                    text="🎯 Harcama Kategorileri Dağılımı",
                    font=dict(size=20, color=title_color),
                    x=0.5
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=font_color),
                showlegend=False,
                margin=dict(l=0, r=0, t=60, b=0),
                xaxis_title="💰 Tutar (TL)",
                yaxis_title="📂 Kategoriler"
            )
            
            fig_pie.update_xaxes(
                gridcolor=grid_color,
                showgrid=True,
                tickformat=',.0f',
                title_font=dict(color=font_color),
                tickfont=dict(color=font_color)
            )
            
            fig_pie.update_yaxes(
                title_font=dict(color=font_color),
                tickfont=dict(color=font_color)
            )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # En çok harcama yapılan kategoriler detayları ile
        st.subheader("🏆 Top Kategoriler ve Harcama Detayları")
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        for i, (category, amount) in enumerate(sorted_categories[:5], 1):
            st.write(f"**{i}. {category.title()}: {amount:.0f} TL**")
            
            # Bu kategorideki harcamaları getir
            category_expenses = [
                item for item in data 
                if item['category_name'].lower() == category.lower()
            ]
            
            # Son 10 harcamayı göster
            recent_category_expenses = sorted(category_expenses, key=lambda x: x['date'], reverse=True)[:10]
            
            # Harcama detaylarını göster
            if recent_category_expenses:
                with st.expander(f"📋 {category.title()} kategorisindeki son harcamalar"):
                    # Başlık satırı
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                    with col1:
                        st.write("**📅 Tarih**")
                    with col2:
                        st.write("**📝 Açıklama**")
                    with col3:
                        st.write("**💱 Orijinal**")
                    with col4:
                        st.write("**💰 TL Karşılığı**")
                    
                    st.markdown("---")
                    
                    for expense in recent_category_expenses:
                        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                        with col1:
                            st.write(expense['date'].strftime('%d.%m.%Y'))
                        with col2:
                            description = expense.get('description', 'Açıklama yok')
                            if description and description != f"{category.title()} harcaması":
                                st.write(f"📝 {description}")
                            else:
                                st.write("📝 Açıklama yok")
                        with col3:
                            # Orijinal para birimi gösterimi
                            original_amount = expense.get('original_amount', expense['amount'])
                            currency = expense.get('currency', 'TRY')
                            
                            if currency != 'TRY':
                                st.write(f"**{format_currency_display(original_amount, currency)}**")
                            else:
                                st.write(f"**{original_amount:.0f} ₺**")
                        with col4:
                            # TL karşılığı
                            tl_amount = expense['amount']
                            if currency != 'TRY':
                                st.write(f"**{tl_amount:.0f} ₺**")
                            else:
                                st.write("—")
                    
                    # Kategori istatistikleri
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Toplam İşlem", f"{len(category_expenses)}")
                    with col2:
                        avg_amount = sum(exp['amount'] for exp in category_expenses) / len(category_expenses)
                        st.metric("💰 Ortalama (TL)", f"{avg_amount:.0f} ₺")
                    with col3:
                        max_expense = max(category_expenses, key=lambda x: x['amount'])
                        st.metric("🔝 En Yüksek (TL)", f"{max_expense['amount']:.0f} ₺")
                    with col4:
                        # Farklı para birimlerini say
                        currencies_used = set(exp.get('currency', 'TRY') for exp in category_expenses)
                        st.metric("💱 Para Birimi", f"{len(currencies_used)} çeşit")
                    
                    # Para birimi dağılımı
                    if len(currencies_used) > 1:
                        st.markdown("**💱 Para Birimi Dağılımı:**")
                        currency_breakdown = {}
                        for exp in category_expenses:
                            currency = exp.get('currency', 'TRY')
                            original_amount = exp.get('original_amount', exp['amount'])
                            currency_breakdown[currency] = currency_breakdown.get(currency, 0) + original_amount
                        
                        for curr, total in currency_breakdown.items():
                            if curr != 'TRY':
                                tl_equiv = sum(exp['amount'] for exp in category_expenses if exp.get('currency', 'TRY') == curr)
                                st.caption(f"• {curr}: {format_currency_display(total, curr)} = {tl_equiv:.0f} ₺")
                            else:
                                st.caption(f"• TRY: {total:.0f} ₺")
            
            st.markdown("---")

elif page == "📈 Butce Planlama":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea, #fed6e3); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: #1e293b; margin: 0; text-align: center;">📈 Akıllı Bütçe Planlama</h2>
        <p style="color: #64748b; margin: 0.5rem 0 0 0; text-align: center;">50/30/20 kuralı ile ideal bütçenizi oluşturun</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💰 50/30/20 Butce Kurali")
    monthly_income = st.number_input("Aylik Geliriniz (TL):", value=15000, step=500)
    
    if monthly_income > 0:
        needs = monthly_income * 0.5
        wants = monthly_income * 0.3
        savings = monthly_income * 0.2
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏠 Ihtiyaclar (50%)", f"{needs:.0f} TL")
            st.caption("Kira, faturalar, market")
        with col2:
            st.metric("🎮 Istekler (30%)", f"{wants:.0f} TL")
            st.caption("Eğlence, restoran")
        with col3:
            st.metric("💎 Tasarruf (20%)", f"{savings:.0f} TL")
            st.caption("Acil durum, yatırım")
        
        # Mevcut harcamalarla karşılaştırma
        if data:
            current_month = datetime.now().month
            current_year = datetime.now().year
            this_month_data = [
                item for item in data 
                if item['date'].month == current_month and item['date'].year == current_year
            ]
            
            total_spending = sum(item['amount'] for item in this_month_data)
            remaining_budget = monthly_income - total_spending
            
            st.subheader("📊 Bu Ay Durum")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💳 Bu Ay Harcama", f"{total_spending:.0f} TL")
            with col2:
                st.metric("💰 Kalan Bütçe", f"{remaining_budget:.0f} TL")
            with col3:
                usage_pct = (total_spending / monthly_income * 100) if monthly_income > 0 else 0
                st.metric("📈 Bütçe Kullanımı", f"{usage_pct:.1f}%")

# Footer
st.markdown("---")
st.markdown("*NeoFinX 2024 - Yapay zeka destekli akilli butce asistani*")

# Veritabanı durumu
def get_expense_count():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM expenses')
        return cursor.fetchone()[0]
    except:
        return 0
    finally:
        if conn:
            conn.close()



expense_count = get_expense_count()
st.sidebar.markdown("---")
st.sidebar.info(f"📊 Veritabanında {expense_count} harcama kaydı var")

# Akıllı öneriler fonksiyonları
def analyze_spending_patterns():
    """Harcama kalıplarını analiz et ve akıllı öneriler üret"""
    try:
        conn = sqlite3.connect('data/neofinx.db', timeout=30)
        conn.execute('PRAGMA journal_mode=WAL')
        cursor = conn.cursor()
        
        # Bu ay ve geçen ayın verilerini al
        current_month = datetime.now().strftime('%Y-%m')
        last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        
        # Bu ayın harcamaları
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY c.name
        """, (current_month,))
        current_month_data = cursor.fetchall()
        
        # Geçen ayın harcamaları
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY c.name
        """, (last_month,))
        last_month_data = cursor.fetchall()
        
        # Son 7 günün harcamaları
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count,
                   AVG(e.amount) as avg_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date >= ?
            GROUP BY c.name
            ORDER BY total DESC
        """, (week_ago,))
        week_data = cursor.fetchall()
        
        # Günlük ortalama harcamalar (son 30 gün)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT DATE(e.date) as expense_date, SUM(e.amount) as daily_total
            FROM expenses e
            WHERE e.date >= ?
            GROUP BY DATE(e.date)
            ORDER BY expense_date
        """, (thirty_days_ago,))
        daily_data = cursor.fetchall()
        
        # En sık harcama yapılan kategoriler
        cursor.execute("""
            SELECT c.name, COUNT(e.id) as frequency, AVG(e.amount) as avg_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date >= ?
            GROUP BY c.name
            ORDER BY frequency DESC
            LIMIT 5
        """, (thirty_days_ago,))
        frequent_categories = cursor.fetchall()
        
        conn.close()
        
        insights = []
        
        # 1. Aylık karşılaştırma analizi
        current_dict = {item[0]: item[1] for item in current_month_data}
        last_dict = {item[0]: item[1] for item in last_month_data}
        
        for category, current_amount in current_dict.items():
            if category in last_dict:
                last_amount = last_dict[category]
                if last_amount > 0:
                    change_percent = ((current_amount - last_amount) / last_amount) * 100
                    
                    if change_percent > 20:
                        insights.append({
                            'type': 'warning',
                            'icon': '📈',
                            'title': f'{category.title()} Harcaması Arttı',
                            'message': f'Bu ay {category} harcamanız geçen aya göre %{change_percent:.0f} arttı ({current_amount:,.0f} TL)',
                            'suggestion': f'{category} harcamalarınızı gözden geçirin ve gereksiz harcamaları belirleyin.',
                            'priority': 'high' if change_percent > 50 else 'medium'
                        })
                    elif change_percent < -15:
                        insights.append({
                            'type': 'success',
                            'icon': '💰',
                            'title': f'{category.title()} Tasarrufu',
                            'message': f'Bu ay {category} kategorisinde {abs(current_amount - last_amount):,.0f} TL tasarruf ettiniz!',
                            'suggestion': f'Harika! {category} harcamalarınızı kontrol altında tutmaya devam edin.',
                            'priority': 'low'
                        })
        
        # 2. Haftalık trend analizi
        if week_data:
            top_weekly_category = week_data[0]
            if top_weekly_category[1] > 1000:  # 1000 TL üzeri
                insights.append({
                    'type': 'info',
                    'icon': '🎯',
                    'title': 'Haftalık En Yüksek Harcama',
                    'message': f'Son 7 günde en çok {top_weekly_category[0]} kategorisinde harcama yaptınız ({top_weekly_category[1]:,.0f} TL)',
                    'suggestion': f'Ortalama işlem tutarınız {top_weekly_category[3]:,.0f} TL. Daha küçük tutarlarda alışveriş yapmayı düşünün.',
                    'priority': 'medium'
                })
        
        # 3. Günlük harcama pattern analizi
        if daily_data and len(daily_data) >= 7:
            daily_amounts = [item[1] for item in daily_data]
            avg_daily = sum(daily_amounts) / len(daily_amounts)
            recent_week_avg = sum(daily_amounts[-7:]) / 7
            
            if recent_week_avg > avg_daily * 1.3:
                insights.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'title': 'Günlük Harcama Artışı',
                    'message': f'Son 7 günlük ortalama harcamanız ({recent_week_avg:,.0f} TL) aylık ortalamanızdan %{((recent_week_avg/avg_daily)-1)*100:.0f} yüksek',
                    'suggestion': 'Günlük harcamalarınızı kontrol altına almak için bütçe limiti belirleyin.',
                    'priority': 'high'
                })
            elif recent_week_avg < avg_daily * 0.8:
                insights.append({
                    'type': 'success',
                    'icon': '🎉',
                    'title': 'Başarılı Tasarruf',
                    'message': f'Son hafta günlük ortalama {avg_daily - recent_week_avg:,.0f} TL daha az harcadınız!',
                    'suggestion': 'Bu tasarruf alışkanlığınızı sürdürmeye devam edin.',
                    'priority': 'low'
                })
        
        # 4. Sık harcama kategorileri analizi
        if frequent_categories:
            most_frequent = frequent_categories[0]
            if most_frequent[1] > 10:  # 10'dan fazla işlem
                insights.append({
                    'type': 'info',
                    'icon': '🔄',
                    'title': 'En Sık Harcama Kategorisi',
                    'message': f'{most_frequent[0]} kategorisinde son 30 günde {most_frequent[1]} işlem yaptınız',
                    'suggestion': f'Ortalama işlem tutarınız {most_frequent[2]:,.0f} TL. Daha az sıklıkta, daha planlı alışveriş yapabilirsiniz.',
                    'priority': 'low'
                })
        
        # 5. Genel bütçe önerileri
        if current_month_data:
            total_current = sum(item[1] for item in current_month_data)
            if total_current > 5000:
                insights.append({
                    'type': 'info',
                    'icon': '📊',
                    'title': 'Aylık Harcama Özeti',
                    'message': f'Bu ay toplam {total_current:,.0f} TL harcama yaptınız',
                    'suggestion': 'Ayın geri kalanı için günlük bütçe planlayarak harcamalarınızı optimize edebilirsiniz.',
                    'priority': 'medium'
                })
        
        # Önceliklere göre sırala
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        insights.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return insights[:8]  # En fazla 8 öneri göster
        
    except Exception as e:
        return []  # Hata durumunda boş liste döndür

def get_spending_recommendations():
    """Harcama önerileri ve ipuçları"""
    recommendations = [
        {
            'icon': '🎯',
            'title': 'Bütçe Hedefi Belirleyin',
            'description': 'Her kategori için aylık bütçe limiti belirleyerek harcamalarınızı kontrol altında tutun.',
            'action': 'Bütçe Planlama sayfasından kategori limitlerini ayarlayın.'
        },
        {
            'icon': '📱',
            'title': 'Düzenli Takip',
            'description': 'Harcamalarınızı günlük olarak kaydetme alışkanlığı edinin.',
            'action': 'Her gün en az bir kez uygulamayı kontrol edin.'
        },
        {
            'icon': '💡',
            'title': 'Analiz Yapın',
            'description': 'Haftalık ve aylık harcama trendlerinizi düzenli olarak inceleyin.',
            'action': 'Harcama Analizi sayfasından raporlarınızı gözden geçirin.'
        },
        {
            'icon': '🛒',
            'title': 'Planlı Alışveriş',
            'description': 'Alışveriş öncesi liste hazırlayarak gereksiz harcamaları önleyin.',
            'action': 'Büyük harcamalar öncesi bütçenizi kontrol edin.'
        },
        {
            'icon': '📈',
            'title': 'Trend Takibi',
            'description': 'Aylık harcama artış/azalışlarınızı takip ederek finansal hedefinize odaklanın.',
            'action': 'Ana sayfadaki trend grafiklerini düzenli inceleyin.'
        }
    ]
    
    return recommendations

 
