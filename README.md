# NeoFinX - Akıllı Bütçe ve Harcama Asistanı 🏦

**NeoFinX**, yapay zeka destekli kişisel finans yönetim platformudur. Harcamalarınızı takip edin, bütçe planlayın, yatırımlarınızı yönetin ve akıllı finansal öneriler alın.

## 🚀 Özellikler

### 💰 Temel Finans Yönetimi
- **Harcama Takibi**: Günlük harcamalarınızı kategorilere ayırarak kaydedin
- **Çoklu Para Birimi**: TRY, USD, EUR, GBP ve daha fazla para birimi desteği
- **CSV Import/Export**: Mevcut verilerinizi kolayca aktarın
- **PDF Raporlama**: Aylık finansal raporlarınızı PDF olarak indirin

### 📊 Analiz ve İstatistikler
- **Harcama Analizi**: Kategorilere göre detaylı harcama analizleri
- **Trend Analizi**: Aylık/yıllık harcama trendleri
- **Anormal Harcama Tespiti**: Olağan dışı harcamalarınızı tespit edin
- **Görsel Raporlar**: İnteraktif grafikler ve çizelgeler

### 📈 Yatırım Takibi
- **Portföy Yönetimi**: Hisse, döviz, kripto, altın yatırımlarınızı takip edin
- **Canlı Fiyatlar**: Gerçek zamanlı piyasa verileri
- **Performans Analizi**: Yatırım kazanç/zarar hesaplamaları
- **Çeşitlendirme Önerileri**: Risk dağılımı için akıllı öneriler

### 🎯 Finansal Hedefler
- **Hedef Belirleme**: Ev, araba, tatil gibi finansal hedefler
- **İlerleme Takibi**: Hedefinize ne kadar yaklaştığınızı görün
- **Otomatik Hesaplama**: Aylık ne kadar biriktirmeniz gerektiğini öğrenin
- **Hedef Şablonları**: Hazır hedef kategorileri

### 🎭 Kişilik Profili ⭐ YENİ!
- **Harcama Kişiliği Analizi**: Alışkanlıklarınıza göre kişilik profili belirleme
- **10 Farklı Profil**: Alışveriş Bağımlısı, Yatırımcı Kafası, Sosyal Kelebek ve daha fazlası
- **Kişiselleştirilmiş İpuçları**: Profilinize özel finansal tavsiyeler
- **Profil Gelişimi**: Zaman içinde kişiliğinizin nasıl değiştiğini görün

### 📋 Vergi Hesaplamaları ⭐ YENİ!
- **Gelir Vergisi Hesaplama**: 2024 Türkiye vergi dilimlerine göre hesaplama
- **KDV İade Takibi**: Freelancer'lar için KDV iade yönetimi
- **Yatırım Kazançları Vergisi**: Hisse, gayrimenkul, döviz vergisi hesaplama
- **Vergi Optimizasyon Önerileri**: Kişiselleştirilmiş vergi tasarruf önerileri

### 🤖 AI Asistan
- **Akıllı Öneriler**: Harcama davranışlarınıza göre kişisel öneriler
- **Sohbet Botu**: Finansal sorularınızı sorun, akıllı yanıtlar alın
- **Bütçe Tavsiyeleri**: AI destekli bütçe optimizasyonu
- **Tasarruf İpuçları**: Kişiselleştirilmiş tasarruf önerileri

### 🔮 Tahmin ve Projeksiyonlar
- **Harcama Tahmini**: Gelecek ay harcamalarınızı önceden görün
- **Trend Analizi**: Mevsimsel harcama desenlerinizi keşfedin
- **Bütçe Projeksiyonu**: Yıllık bütçe planlaması

## 🛠️ Teknoloji Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Flask REST API
- **Veritabanı**: SQLite
- **Veri Analizi**: Pandas, NumPy, SciPy
- **Görselleştirme**: Plotly, Matplotlib
- **AI/ML**: OpenAI GPT, Statistical Models
- **PDF**: ReportLab
- **API**: Alpha Vantage, CoinGecko, TCMB

## 📦 Kurulum

### Gereksinimler
- Python 3.8+
- pip package manager

### Hızlı Başlangıç

1. **Projeyi İndirin**
```bash
git clone <repository-url>
cd neofinx
```

2. **Bağımlılıkları Yükleyin**
```bash
pip install -r requirements.txt
```

3. **Kurulum Scriptini Çalıştırın**
```bash
python setup.py
```

4. **Dashboard'u Başlatın**
```bash
streamlit run dashboard.py
```

5. **Tarayıcınızda Açın**
```
http://localhost:8501
```

### Manuel Kurulum

1. **Veritabanını Oluşturun**
```bash
python -c "from setup import create_database; create_database()"
```

2. **Backend API'yi Başlatın** (Opsiyonel)
```bash
python backend/app.py
```

3. **Dashboard'u Çalıştırın**
```bash
streamlit run dashboard.py
```

## 🎮 Kullanım Kılavuzu

### 📱 Dashboard Navigasyonu

**Ana Sayfa**: Finansal özetinizi ve KPI'larınızı görün
- Toplam harcama, gelir, tasarruf metrikleri
- Son harcamalar listesi
- Hızlı eylem butonları

**Harcama Ekle**: Yeni harcamalarınızı kaydedin
- Kategori seçimi (Yemek, Ulaşım, Eğlence, vb.)
- Çoklu para birimi desteği
- Tarih ve açıklama ekleme

**Kişilik Profili**: Harcama kişiliğinizi keşfedin
- Harcama alışkanlıklarına göre 10 farklı profil
- Kişiselleştirilmiş finansal tavsiyeleri
- Zaman içinde profil gelişimi takibi

**Vergi Hesaplamaları**: Vergi planlamanızı yapın
- Gelir vergisi hesaplama ve simülasyon
- KDV iade takibi ve optimizasyon
- Yatırım kazançları vergi hesaplama
- Kişiselleştirilmiş vergi tasarruf önerileri

**Harcama Analizi**: Detaylı finansal analizler
- Kategorilere göre harcama dağılımı
- Aylık/yıllık trend grafikleri
- Karşılaştırmalı analizler

**Bütçe Planlama**: Aylık bütçenizi yönetin
- Kategori bazlı bütçe hedefleri
- Gerçekleşme oranları
- Aşım uyarıları

**Yatırım Takibi**: Portföyünüzü yönetin
- Hisse senedi, döviz, kripto takibi
- Canlı fiyat güncellemeleri
- Performans raporları

### 💡 Pro İpuçları

1. **Düzenli Kayıt**: Harcamalarınızı günlük kaydetmek daha doğru analizler sağlar
2. **Kategori Tutarlılığı**: Benzer harcamaları aynı kategoride tutun
3. **Bütçe Hedefleri**: Gerçekçi bütçe hedefleri belirleyin
4. **Düzenli İnceleme**: Aylık raporlarınızı düzenli inceleyin
5. **Vergi Planlaması**: Yıl sonu vergi hesaplamalarını önceden planlayın

## 🔧 Yapılandırma

### Çevre Değişkenleri (.env)
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///data/neofinx.db
OPENAI_API_KEY=your-openai-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
```

### API Anahtarları
- **OpenAI API**: AI asistan için gerekli
- **Alpha Vantage**: Hisse senedi fiyatları için
- **CoinGecko**: Kripto para fiyatları için (ücretsiz)

## 📊 Veri Modeli

### Temel Tablolar
- `users`: Kullanıcı bilgileri
- `expenses`: Harcama kayıtları
- `categories`: Harcama kategorileri
- `budgets`: Bütçe planları
- `investments`: Yatırım portföyü

### Vergi Tabloları
- `tax_calculations`: Vergi hesaplama sonuçları
- `vat_tracking`: KDV fatura takibi
- `investment_tax`: Yatırım kazanç vergileri
- `tax_recommendations`: Vergi optimizasyon önerileri
- `tax_brackets`: Vergi dilim bilgileri

## 🌐 API Endpoints

### Vergi API'leri
```
POST /api/tax/income-tax        # Gelir vergisi hesaplama
POST /api/tax/investment-tax    # Yatırım vergisi hesaplama
POST /api/tax/vat-tracking      # KDV fatura ekleme
GET  /api/tax/vat-tracking      # KDV fatura listesi
POST /api/tax/recommendations   # Vergi optimizasyon önerileri
GET  /api/tax/brackets/{year}   # Vergi dilim bilgileri
GET  /api/tax/history          # Vergi hesaplama geçmişi
```

### Temel API'ler
```
POST /api/expenses              # Harcama ekleme
GET  /api/expenses             # Harcama listesi
POST /api/analytics/spending   # Harcama analizi
GET  /api/investments         # Yatırım portföyü
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasını inceleyin.

## 👥 Geliştirici Ekibi

- **Erkan Tan** - Backend & AI Development
- **Raziyegül Kahraman** - Frontend & UX Design

## 📞 Destek

Sorularınız için:
- 📧 Email: support@neofinx.app
- 🐛 Bug Reports: GitHub Issues
- 💡 Feature Requests: GitHub Discussions

---

**NeoFinX** ile finansal geleceğinizi kontrol altına alın! 💰✨ 