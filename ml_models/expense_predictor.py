import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class ExpensePredictor:
    """
    Zaman serisi analizi ile harcama tahminleri yapan model
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        
    def prepare_data(self, expenses_df):
        """
        Harcama verilerini Prophet formatına çevir
        """
        # Tarih ve miktar sütunlarını al
        df = expenses_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Günlük toplam harcamaları hesapla
        daily_expenses = df.groupby('date')['amount'].sum().reset_index()
        daily_expenses.columns = ['ds', 'y']
        
        # Eksik günleri doldur
        date_range = pd.date_range(
            start=daily_expenses['ds'].min(),
            end=daily_expenses['ds'].max(),
            freq='D'
        )
        
        complete_df = pd.DataFrame({'ds': date_range})
        complete_df = complete_df.merge(daily_expenses, on='ds', how='left')
        complete_df['y'] = complete_df['y'].fillna(0)
        
        return complete_df
    
    def train_model(self, expenses_df, category=None):
        """
        Modeli eğit
        """
        if category:
            # Belirli kategori için filtrele
            filtered_df = expenses_df[expenses_df['category_name'] == category]
        else:
            filtered_df = expenses_df
            
        # Veriyi hazırla
        prophet_data = self.prepare_data(filtered_df)
        
        if len(prophet_data) < 10:
            raise ValueError("Yeterli veri yok! En az 10 gün veri gerekli.")
        
        # Prophet modeli oluştur
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        
        # Modeli eğit
        self.model.fit(prophet_data)
        self.is_trained = True
        
        return self.model
    
    def predict_future(self, days_ahead=30):
        """
        Gelecek için tahmin yap
        """
        if not self.is_trained:
            raise ValueError("Model henüz eğitilmemiş!")
        
        # Gelecek tarihler oluştur
        future = self.model.make_future_dataframe(periods=days_ahead)
        
        # Tahmin yap
        forecast = self.model.predict(future)
        
        # Son tahminleri al
        future_predictions = forecast.tail(days_ahead)
        
        return {
            'dates': future_predictions['ds'].tolist(),
            'predictions': future_predictions['yhat'].tolist(),
            'lower_bound': future_predictions['yhat_lower'].tolist(),
            'upper_bound': future_predictions['yhat_upper'].tolist()
        }
    
    def predict_monthly_total(self, month=None, year=None):
        """
        Belirli bir ay için toplam harcama tahmini
        """
        if not month or not year:
            # Sonraki ay
            from datetime import datetime, timedelta
            next_month = datetime.now().replace(day=1) + timedelta(days=32)
            month = next_month.month
            year = next_month.year
        
        # O ay için günlük tahminler
        start_date = pd.Timestamp(year=year, month=month, day=1)
        if month == 12:
            end_date = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
        else:
            end_date = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
        
        # Tahmin için dataframe oluştur
        future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        future_df = pd.DataFrame({'ds': future_dates})
        
        # Tahmin yap
        forecast = self.model.predict(future_df)
        
        # Aylık toplam
        monthly_total = forecast['yhat'].sum()
        monthly_lower = forecast['yhat_lower'].sum()
        monthly_upper = forecast['yhat_upper'].sum()
        
        return {
            'month': month,
            'year': year,
            'predicted_total': max(0, monthly_total),
            'lower_bound': max(0, monthly_lower),
            'upper_bound': max(0, monthly_upper),
            'daily_average': max(0, monthly_total / len(future_dates))
        }
    
    def get_spending_insights(self, expenses_df):
        """
        Harcama davranışları hakkında içgörüler
        """
        df = expenses_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month_name()
        
        insights = {}
        
        # Günlük ortalamalar
        daily_avg = df.groupby('weekday')['amount'].mean().to_dict()
        insights['daily_patterns'] = daily_avg
        
        # Aylık ortalamalar
        monthly_avg = df.groupby('month')['amount'].mean().to_dict()
        insights['monthly_patterns'] = monthly_avg
        
        # Kategori dağılımı
        category_spending = df.groupby('category_name')['amount'].sum().to_dict()
        insights['category_distribution'] = category_spending
        
        # Trend analizi
        recent_data = df[df['date'] >= df['date'].max() - pd.Timedelta(days=30)]
        previous_data = df[(df['date'] >= df['date'].max() - pd.Timedelta(days=60)) & 
                          (df['date'] < df['date'].max() - pd.Timedelta(days=30))]
        
        recent_avg = recent_data['amount'].mean() if len(recent_data) > 0 else 0
        previous_avg = previous_data['amount'].mean() if len(previous_data) > 0 else 0
        
        if previous_avg > 0:
            trend_change = ((recent_avg - previous_avg) / previous_avg) * 100
        else:
            trend_change = 0
        
        insights['trend_analysis'] = {
            'recent_daily_average': recent_avg,
            'previous_daily_average': previous_avg,
            'change_percentage': trend_change
        }
        
        return insights
    
    def detect_anomalies(self, expenses_df, threshold=2):
        """
        Anormal harcamaları tespit et
        """
        df = expenses_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Günlük toplamlar
        daily_totals = df.groupby('date')['amount'].sum()
        
        # Z-score ile anomali tespiti
        mean_spending = daily_totals.mean()
        std_spending = daily_totals.std()
        
        anomalies = []
        for date, amount in daily_totals.items():
            z_score = abs((amount - mean_spending) / std_spending) if std_spending > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': amount,
                    'z_score': z_score,
                    'deviation_from_mean': amount - mean_spending
                })
        
        return {
            'anomalies': anomalies,
            'total_anomalies': len(anomalies),
            'mean_daily_spending': mean_spending,
            'std_daily_spending': std_spending
        }

# Test fonksiyonu
def test_predictor():
    """
    Predictor'ı test et
    """
    # Örnek veri oluştur
    dates = pd.date_range('2024-01-01', '2024-06-01', freq='D')
    np.random.seed(42)
    
    # Gerçekçi harcama verileri simüle et
    base_amount = 100
    trend = np.linspace(0, 20, len(dates))
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)  # Haftalık döngü
    noise = np.random.normal(0, 15, len(dates))
    amounts = base_amount + trend + seasonal + noise
    amounts = np.maximum(amounts, 0)  # Negatif değerleri sıfırla
    
    test_data = pd.DataFrame({
        'date': dates,
        'amount': amounts,
        'category_name': np.random.choice(['yemek', 'ulaşım', 'eğlence'], len(dates))
    })
    
    # Predictor test et
    predictor = ExpensePredictor()
    predictor.train_model(test_data)
    
    # Gelecek tahminleri
    future_predictions = predictor.predict_future(30)
    monthly_prediction = predictor.predict_monthly_total()
    insights = predictor.get_spending_insights(test_data)
    anomalies = predictor.detect_anomalies(test_data)
    
    print("=== ExpensePredictor Test Sonuçları ===")
    print(f"Gelecek 30 gün ortalama günlük harcama: {np.mean(future_predictions['predictions']):.2f} TL")
    print(f"Sonraki ay tahmini toplam: {monthly_prediction['predicted_total']:.2f} TL")
    print(f"Tespit edilen anomali sayısı: {anomalies['total_anomalies']}")
    print(f"Ortalama günlük harcama: {anomalies['mean_daily_spending']:.2f} TL")
    
    return predictor

if __name__ == "__main__":
    test_predictor() 