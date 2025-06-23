"""
NeoFinX - Kişilik Profili Analizi
Harcama alışkanlıklarına göre kullanıcı kişilik etiketleri belirleme
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

class PersonalityAnalyzer:
    """Harcama verilerine göre kişilik profili analizi"""
    
    def __init__(self, db_path: str = 'data/neofinx.db'):
        self.db_path = db_path
        
        # Kişilik profilleri tanımları
        self.personality_profiles = {
            "alışveriş_bağımlısı": {
                "name": "🛍️ Alışveriş Bağımlısı",
                "description": "Alışverişte kendinizi kaybediyorsunuz! Mağazalar sizin için bir terapi alanı.",
                "emoji": "🛍️",
                "color": "#FF6B6B",
                "tips": [
                    "Alışveriş listesi yapın ve ona sadık kalın",
                    "24 saat kuralı uygulayın - hemen almayın",
                    "Bütçe limitleri belirleyin"
                ]
            },
            "yatırımcı_kafası": {
                "name": "📈 Yatırımcı Kafası", 
                "description": "Paranızı akıllıca değerlendiriyorsunuz. Geleceği düşünen bir yatırımcısınız!",
                "emoji": "📈",
                "color": "#4ECDC4",
                "tips": [
                    "Portföyünüzü çeşitlendirin",
                    "Düzenli yatırım yapın",
                    "Risk toleransınızı bilin"
                ]
            },
            "doğa_dostu_tüketici": {
                "name": "🌱 Doğa Dostu Tüketici",
                "description": "Çevre bilincli harcamalar yapıyorsunuz. Dünya sizin için önemli!",
                "emoji": "🌱", 
                "color": "#96CEB4",
                "tips": [
                    "Sürdürülebilir markaları tercih edin",
                    "Toplu taşıma kullanın",
                    "İkinci el alışverişi deneyin"
                ]
            },
            "sosyal_kelebek": {
                "name": "🦋 Sosyal Kelebek",
                "description": "Eğlence ve sosyalleşme odaklısınız. Hayat dolu bir karaktersiniz!",
                "emoji": "🦋",
                "color": "#FECA57",
                "tips": [
                    "Ev partileri düzenleyin",
                    "Eğlence bütçesi belirleyin", 
                    "Arkadaşlarla ortak aktiviteler planlayın"
                ]
            },
            "tutumluluk_ustası": {
                "name": "💎 Tutumluluk Ustası",
                "description": "Parayla aranız çok iyi! Dengeli ve bilinçli harcamalar yapıyorsunuz.",
                "emoji": "💎",
                "color": "#54A0FF",
                "tips": [
                    "Tasarruf hedeflerinizi artırın",
                    "Acil durum fonu oluşturun",
                    "Finansal planlama öğrenin"
                ]
            },
            "teknoloji_gurumsu": {
                "name": "🤖 Teknoloji Gurumsu", 
                "description": "Teknoloji ve innovation meraklısısınız. Geleceğin trendlerini takip ediyorsunuz!",
                "emoji": "🤖",
                "color": "#5F27CD",
                "tips": [
                    "Teknoloji bütçesi belirleyin",
                    "Eski cihazları satın",
                    "Gerçekten ihtiyacınızı değerlendirin"
                ]
            },
            "ev_hanımı_babası": {
                "name": "🏠 Ev Hanımı/Babası",
                "description": "Ev ve aile odaklı harcamalar yapıyorsunuz. Sevdikleriniz için yaşıyorsunuz!",
                "emoji": "🏠",
                "color": "#00D2D3",
                "tips": [
                    "Toplu alışveriş yapın",
                    "Ev yapımı yemekleri tercih edin",
                    "Çocuk aktiviteleri için bütçe ayırın"
                ]
            },
            "seyahat_aşığı": {
                "name": "✈️ Seyahat Aşığı",
                "description": "Dünyayı keşfetmek için yaşıyorsunuz! Deneyimler sizin için çok değerli.",
                "emoji": "✈️",
                "color": "#FF9FF3",
                "tips": [
                    "Seyahat fonu oluşturun",
                    "Erken rezervasyon yapın",
                    "Lokal deneyimleri tercih edin"
                ]
            },
            "gurme_aşçı": {
                "name": "👨‍🍳 Gurme Aşçı",
                "description": "Yemek sizin için bir tutku! İyi yemek için para harcamaktan çekinmiyorsunuz.",
                "emoji": "👨‍🍳",
                "color": "#FF6B9D",
                "tips": [
                    "Ev yemeği yapmayı öğrenin",
                    "Mevsimlik ürünler tercih edin",
                    "Yemek bütçesi belirleyin"
                ]
            },
            "minimalist_yaşam": {
                "name": "🕯️ Minimalist Yaşam",
                "description": "Az ama öz! Sadece gerçekten ihtiyacınız olan şeyleri alıyorsunuz.",
                "emoji": "🕯️",
                "color": "#C44569",
                "tips": [
                    "Kaliteli ürünler tercih edin",
                    "Çok amaçlı eşyalar alın",
                    "Düzenli temizlik yapın"
                ]
            }
        }
    
    def get_user_expenses(self, days: int = 90) -> List[Dict]:
        """Son N günün harcamalarını getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
            SELECT e.amount, e.date, e.description, c.name as category_name, e.created_at
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date >= ?
            ORDER BY e.date DESC
            ''', (since_date,))
            
            expenses = []
            for row in cursor.fetchall():
                expenses.append({
                    'amount': row[0],
                    'date': row[1],
                    'description': row[2],
                    'category': row[3],
                    'created_at': row[4]
                })
            
            conn.close()
            return expenses
            
        except Exception as e:
            print(f"Harcama verileri getirilemedi: {e}")
            return []
    
    def analyze_spending_patterns(self, expenses: List[Dict]) -> Dict:
        """Harcama desenlerini analiz et"""
        if not expenses:
            return {}
        
        # Kategori bazlı analiz
        category_spending = defaultdict(float)
        category_frequency = defaultdict(int)
        total_spending = 0
        
        # Zaman bazlı analiz
        weekend_spending = 0
        weekday_spending = 0
        
        # Miktar bazlı analiz
        high_amount_count = 0  # 1000₺ üzeri
        small_amount_count = 0  # 100₺ altı
        
        for expense in expenses:
            amount = expense['amount']
            category = expense['category'].lower()
            date = datetime.strptime(expense['date'], '%Y-%m-%d')
            
            # Kategori istatistikleri
            category_spending[category] += amount
            category_frequency[category] += 1
            total_spending += amount
            
            # Zaman analizi
            if date.weekday() >= 5:  # Cumartesi-Pazar
                weekend_spending += amount
            else:
                weekday_spending += amount
            
            # Miktar analizi
            if amount >= 1000:
                high_amount_count += 1
            elif amount <= 100:
                small_amount_count += 1
        
        # Yüzde hesaplamaları
        category_percentages = {}
        if total_spending > 0:
            for category, amount in category_spending.items():
                category_percentages[category] = (amount / total_spending) * 100
        
        return {
            'category_percentages': category_percentages,
            'category_spending': dict(category_spending),
            'category_frequency': dict(category_frequency),
            'total_spending': total_spending,
            'weekend_vs_weekday': {
                'weekend_percentage': (weekend_spending / total_spending * 100) if total_spending > 0 else 0,
                'weekday_percentage': (weekday_spending / total_spending * 100) if total_spending > 0 else 0
            },
            'spending_behavior': {
                'high_amount_ratio': (high_amount_count / len(expenses)) * 100,
                'small_amount_ratio': (small_amount_count / len(expenses)) * 100,
                'average_spending': total_spending / len(expenses) if expenses else 0
            },
            'expense_count': len(expenses)
        }
    
    def determine_personality_profile(self, patterns: Dict) -> Dict:
        """Harcama desenlerine göre kişilik profili belirle"""
        if not patterns or patterns.get('expense_count', 0) < 5:
            return {
                'profile': 'yeni_kullanıcı',
                'name': '🌟 Yeni Kullanıcı',
                'description': 'Henüz yeni başlıyorsunuz! Daha fazla veri toplandıkça kişiliğinizi keşfedeceğiz.',
                'emoji': '🌟',
                'color': '#A0A0A0',
                'confidence': 0,
                'tips': ['Düzenli harcama kayıtları tutun', 'Bütçe hedefleri belirleyin']
            }
        
        category_percentages = patterns.get('category_percentages', {})
        behavior = patterns.get('spending_behavior', {})
        weekend_data = patterns.get('weekend_vs_weekday', {})
        
        scores = {}
        
        # Alışveriş Bağımlısı
        shopping_score = 0
        shopping_categories = ['alışveriş', 'kişisel bakım', 'giyim']
        for cat in shopping_categories:
            shopping_score += category_percentages.get(cat, 0)
        if shopping_score > 35:
            scores['alışveriş_bağımlısı'] = shopping_score + 20
        
        # Yatırımcı Kafası  
        investment_score = 0
        if behavior.get('average_spending', 0) < 200:  # Düşük ortalama harcama
            investment_score += 30
        if patterns.get('total_spending', 0) < 5000:  # Düşük toplam harcama
            investment_score += 20
        scores['yatırımcı_kafası'] = investment_score
        
        # Doğa Dostu Tüketici
        eco_score = 0
        transport_pct = category_percentages.get('ulaşım', 0)
        if transport_pct < 10:  # Az ulaşım harcaması
            eco_score += 25
        if 'organik' in str(patterns.get('category_spending', {})).lower():
            eco_score += 30
        scores['doğa_dostu_tüketici'] = eco_score
        
        # Sosyal Kelebek
        social_score = 0
        social_categories = ['eğlence', 'yemek & içecek', 'dışarıda yemek']
        for cat in social_categories:
            social_score += category_percentages.get(cat, 0)
        if weekend_data.get('weekend_percentage', 0) > 40:
            social_score += 15
        scores['sosyal_kelebek'] = social_score
        
        # Tutumluluk Ustası
        frugal_score = 0
        if behavior.get('average_spending', 0) < 150:
            frugal_score += 30
        if behavior.get('small_amount_ratio', 0) > 60:
            frugal_score += 25
        # Dengeli harcama kontrolü
        max_category_pct = max(category_percentages.values()) if category_percentages else 0
        if max_category_pct < 40:  # Hiçbir kategoride aşırı harcama yok
            frugal_score += 20
        scores['tutumluluk_ustası'] = frugal_score
        
        # Teknoloji Gurumsu
        tech_score = 0
        tech_categories = ['teknoloji', 'elektronik', 'oyun']
        for cat in tech_categories:
            tech_score += category_percentages.get(cat, 0) * 2  # Teknoloji kategorileri daha ağırlıklı
        scores['teknoloji_gurumsu'] = tech_score
        
        # Ev Hanımı/Babası
        home_score = 0
        home_categories = ['market', 'ev', 'çocuk', 'temizlik']
        for cat in home_categories:
            home_score += category_percentages.get(cat, 0)
        if weekend_data.get('weekday_percentage', 0) > 60:
            home_score += 15
        scores['ev_hanımı_babası'] = home_score
        
        # Seyahat Aşığı
        travel_score = 0
        travel_categories = ['seyahat', 'tatil', 'ulaşım']
        for cat in travel_categories:
            travel_score += category_percentages.get(cat, 0)
        if behavior.get('high_amount_ratio', 0) > 20:  # Yüksek miktarlı harcamalar
            travel_score += 15
        scores['seyahat_aşığı'] = travel_score
        
        # Gurme Aşçı
        food_score = 0
        food_categories = ['yemek & içecek', 'restaurant', 'gurme', 'dışarıda yemek']
        for cat in food_categories:
            food_score += category_percentages.get(cat, 0)
        scores['gurme_aşçı'] = food_score
        
        # Minimalist Yaşam
        minimal_score = 0
        if patterns.get('expense_count', 0) < 30:  # Az sayıda harcama
            minimal_score += 25
        if behavior.get('average_spending', 0) > 300:  # Yüksek ortalama (az ama kaliteli)
            minimal_score += 20
        scores['minimalist_yaşam'] = minimal_score
        
        # En yüksek skoru bul
        if not scores:
            return self.determine_personality_profile({})  # Yeni kullanıcı döndür
        
        best_profile = max(scores.items(), key=lambda x: x[1])
        profile_key = best_profile[0]
        confidence = min(100, int(best_profile[1]))
        
        profile_data = self.personality_profiles[profile_key].copy()
        profile_data['profile'] = profile_key
        profile_data['confidence'] = confidence
        profile_data['scores'] = scores
        
        return profile_data
    
    def get_personality_insights(self, profile_data: Dict, patterns: Dict) -> List[Dict]:
        """Kişilik profiline göre içgörüler"""
        insights = []
        
        category_percentages = patterns.get('category_percentages', {})
        behavior = patterns.get('spending_behavior', {})
        
        # Dominant kategori
        if category_percentages:
            dominant_category = max(category_percentages.items(), key=lambda x: x[1])
            insights.append({
                'type': 'dominant_category',
                'title': f'Dominant Harcama Kategoriniz: {dominant_category[0].title()}',
                'description': f'Harcamalarınızın %{dominant_category[1]:.1f}\'i bu kategoride',
                'icon': '📊'
            })
        
        # Harcama davranışı
        avg_spending = behavior.get('average_spending', 0)
        if avg_spending > 500:
            insights.append({
                'type': 'spending_behavior',
                'title': 'Yüksek Ortalama Harcama',
                'description': f'Ortalama harcamanız {avg_spending:.0f}₺. Lüks tüketim eğiliminiz var.',
                'icon': '💎'
            })
        elif avg_spending < 100:
            insights.append({
                'type': 'spending_behavior', 
                'title': 'Düşük Ortalama Harcama',
                'description': f'Ortalama harcamanız {avg_spending:.0f}₺. Tutumlu bir yaklaşımınız var.',
                'icon': '💰'
            })
        
        # Hafta sonu davranışı
        weekend_data = patterns.get('weekend_vs_weekday', {})
        weekend_pct = weekend_data.get('weekend_percentage', 0)
        if weekend_pct > 50:
            insights.append({
                'type': 'weekend_behavior',
                'title': 'Hafta Sonu Harcama Eğilimi',
                'description': f'Harcamalarınızın %{weekend_pct:.1f}\'i hafta sonunda. Sosyal aktiviteler sizi cezbediyor!',
                'icon': '🎉'
            })
        
        return insights
    
    def analyze_user_personality(self, days: int = 90) -> Dict:
        """Kullanıcının kişilik analizini yap"""
        # Harcama verilerini al
        expenses = self.get_user_expenses(days)
        
        # Harcama desenlerini analiz et
        patterns = self.analyze_spending_patterns(expenses)
        
        # Kişilik profilini belirle
        profile = self.determine_personality_profile(patterns)
        
        # İçgörüleri üret
        insights = self.get_personality_insights(profile, patterns)
        
        return {
            'profile': profile,
            'patterns': patterns,
            'insights': insights,
            'analysis_date': datetime.now().isoformat(),
            'data_period_days': days
        }
    
    def get_personality_evolution(self, periods: List[int] = [30, 60, 90]) -> Dict:
        """Kişilik gelişimini takip et"""
        evolution = {}
        
        for period in periods:
            analysis = self.analyze_user_personality(period)
            evolution[f'{period}_days'] = {
                'profile_name': analysis['profile']['name'],
                'profile_key': analysis['profile']['profile'],
                'confidence': analysis['profile']['confidence'],
                'total_spending': analysis['patterns'].get('total_spending', 0)
            }
        
        return evolution 