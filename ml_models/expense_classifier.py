import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import re
import string

class ExpenseClassifier:
    """
    Harcama açıklamalarını otomatik olarak kategorilere ayıran NLP modeli
    """
    
    def __init__(self):
        self.model = None
        self.categories = {
            'yemek': ['market', 'restoran', 'yemek', 'cafe', 'kahve', 'pizza', 'burger', 'starbucks', 'migros', 'bim', 'a101', 'şok'],
            'ulaşım': ['benzin', 'otobüs', 'metro', 'taksi', 'uber', 'bitaksi', 'otopark', 'köprü', 'otoyol'],
            'eğlence': ['sinema', 'konser', 'tiyatro', 'oyun', 'netflix', 'spotify', 'eğlence', 'bar', 'pub'],
            'sağlık': ['eczane', 'doktor', 'hastane', 'diş', 'göz', 'sağlık', 'ilaç', 'vitamin'],
            'alışveriş': ['kıyafet', 'ayakkabı', 'çanta', 'elektronik', 'telefon', 'bilgisayar', 'zara', 'hm', 'lcw'],
            'faturalar': ['elektrik', 'su', 'gaz', 'internet', 'telefon', 'kira', 'aidat', 'vergi'],
            'eğitim': ['kitap', 'kurs', 'ders', 'okul', 'üniversite', 'eğitim', 'kalem'],
            'kişisel_bakım': ['kuaför', 'berber', 'kozmetik', 'parfüm', 'şampuan', 'diş fırçası'],
            'spor': ['spor', 'fitness', 'gym', 'futbol', 'basketbol', 'yüzme', 'koşu'],
            'diğer': ['hediye', 'bağış', 'çeşitli', 'diğer']
        }
        
    def preprocess_text(self, text):
        """Metni temizle ve normalize et"""
        if pd.isna(text) or text == '':
            return ''
        
        text = str(text).lower()
        
        # Türkçe karakterleri normalize et
        turkish_chars = {'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c'}
        for char, replacement in turkish_chars.items():
            text = text.replace(char, replacement)
        
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def predict_category(self, description):
        """Harcama açıklaması için kategori tahmin et"""
        if self.model is None:
            raise ValueError("Model henüz eğitilmemiş!")
        
        processed_text = self.preprocess_text(description)
        
        if processed_text == '':
            return 'diğer', 0.0
        
        prediction = self.model.predict([processed_text])[0]
        probabilities = self.model.predict_proba([processed_text])[0]
        confidence = max(probabilities)
        
        return prediction, confidence
