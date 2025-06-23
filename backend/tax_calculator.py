"""
NeoFinX - Vergi Hesaplama Modülü
Gelir vergisi, KDV, yatırım kazançları vergisi hesaplama işlemleri
"""

from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import sqlite3

class TaxCalculator:
    """Türkiye vergi sistemine göre vergi hesaplama sınıfı"""
    
    def __init__(self, db_path: str = 'data/neofinx.db'):
        self.db_path = db_path
        
    def get_tax_brackets(self, tax_year: int = 2024) -> List[Dict]:
        """Vergi dilimlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT bracket_min, bracket_max, tax_rate, deduction_amount 
        FROM tax_brackets 
        WHERE tax_year = ? AND is_active = 1
        ORDER BY bracket_min
        ''', (tax_year,))
        
        brackets = []
        for row in cursor.fetchall():
            brackets.append({
                'min': row[0],
                'max': row[1],
                'rate': row[2],
                'deduction': row[3]
            })
        
        conn.close()
        return brackets
    
    def calculate_income_tax(self, annual_income: float, tax_year: int = 2024) -> Dict:
        """Gelir vergisi hesaplama"""
        brackets = self.get_tax_brackets(tax_year)
        
        if not brackets:
            return {
                'error': 'Vergi dilimleri bulunamadı',
                'total_tax': 0,
                'net_income': annual_income,
                'effective_rate': 0,
                'breakdown': []
            }
        
        total_tax = 0
        breakdown = []
        remaining_income = annual_income
        
        for bracket in brackets:
            if remaining_income <= 0:
                break
                
            bracket_min = bracket['min']
            bracket_max = bracket['max'] if bracket['max'] else float('inf')
            tax_rate = bracket['rate'] / 100
            deduction = bracket['deduction']
            
            # Bu dilimde vergilendirilecek miktar
            if annual_income > bracket_min:
                taxable_in_bracket = min(remaining_income, bracket_max - bracket_min)
                if annual_income <= bracket_max or bracket_max == float('inf'):
                    # Bu dilimde kalıyoruz
                    tax_in_bracket = (annual_income - bracket_min) * tax_rate - deduction
                    total_tax = max(0, tax_in_bracket)
                    
                    breakdown.append({
                        'bracket': f"{bracket_min:,.0f} - {bracket_max if bracket_max != float('inf') else '∞'}",
                        'rate': bracket['rate'],
                        'taxable_amount': annual_income - bracket_min,
                        'tax_amount': total_tax,
                        'deduction': deduction
                    })
                    break
        
        net_income = annual_income - total_tax
        effective_rate = (total_tax / annual_income * 100) if annual_income > 0 else 0
        
        return {
            'annual_income': annual_income,
            'total_tax': total_tax,
            'net_income': net_income,
            'effective_rate': effective_rate,
            'marginal_rate': brackets[-1]['rate'] if brackets else 0,
            'breakdown': breakdown,
            'tax_year': tax_year
        }
    
    def calculate_investment_tax(self, purchase_amount: float, sale_amount: float, 
                               purchase_date: date, sale_date: date, 
                               investment_type: str = 'stock') -> Dict:
        """Yatırım kazançları vergisi hesaplama"""
        
        # Elde tutma süresi
        holding_period = (sale_date - purchase_date).days
        gain_loss = sale_amount - purchase_amount
        
        # Vergi oranları (Türkiye mevzuatına göre)
        tax_rates = {
            'stock': 0.0,  # Hisse senetleri vergisiz (2 yıl üzeri)
            'bond': 0.10,  # Tahviller %10
            'currency': 0.0,  # Döviz vergisiz
            'crypto': 0.0,  # Kripto vergisiz (henüz düzenlenmedi)
            'real_estate': 0.20,  # Gayrimenkul %20
            'gold': 0.0  # Altın vergisiz
        }
        
        # Muafiyet koşulları
        is_exempt = False
        exemption_reason = ""
        
        if investment_type == 'stock' and holding_period >= 730:  # 2 yıl
            is_exempt = True
            exemption_reason = "Hisse senedi 2 yıl üzeri elde tutulma muafiyeti"
        
        elif investment_type == 'real_estate' and holding_period >= 1825:  # 5 yıl
            is_exempt = True
            exemption_reason = "Gayrimenkul 5 yıl üzeri elde tutulma muafiyeti"
        
        elif gain_loss <= 0:
            is_exempt = True
            exemption_reason = "Zarar nedeniyle vergi yükümlülüğü yok"
        
        # Vergi hesaplama
        tax_rate = 0 if is_exempt else tax_rates.get(investment_type, 0)
        tax_amount = max(0, gain_loss * tax_rate) if gain_loss > 0 and not is_exempt else 0
        net_gain = gain_loss - tax_amount
        
        return {
            'purchase_amount': purchase_amount,
            'sale_amount': sale_amount,
            'gain_loss': gain_loss,
            'holding_period_days': holding_period,
            'investment_type': investment_type,
            'tax_rate': tax_rate * 100,
            'tax_amount': tax_amount,
            'net_gain': net_gain,
            'is_exempt': is_exempt,
            'exemption_reason': exemption_reason,
            'purchase_date': purchase_date.isoformat(),
            'sale_date': sale_date.isoformat()
        }
    
    def calculate_vat_refund(self, vat_records: List[Dict]) -> Dict:
        """KDV iade hesaplama (freelancer'lar için)"""
        
        total_vat_paid = 0
        total_invoice_amount = 0
        eligible_refund = 0
        pending_payments = 0
        
        detailed_records = []
        
        for record in vat_records:
            vat_amount = record.get('vat_amount', 0)
            invoice_amount = record.get('invoice_amount', 0)
            payment_status = record.get('payment_status', 'pending')
            refund_eligible = record.get('refund_eligible', True)
            
            total_vat_paid += vat_amount
            total_invoice_amount += invoice_amount
            
            if payment_status == 'paid' and refund_eligible:
                eligible_refund += vat_amount
            elif payment_status == 'pending':
                pending_payments += vat_amount
            
            detailed_records.append({
                'invoice_number': record.get('invoice_number', ''),
                'client_name': record.get('client_name', ''),
                'invoice_amount': invoice_amount,
                'vat_amount': vat_amount,
                'payment_status': payment_status,
                'refund_eligible': refund_eligible,
                'refund_amount': vat_amount if payment_status == 'paid' and refund_eligible else 0
            })
        
        # KDV iade koşulları kontrolü
        min_refund_amount = 200  # Minimum iade tutarı
        can_request_refund = eligible_refund >= min_refund_amount
        
        return {
            'total_vat_paid': total_vat_paid,
            'total_invoice_amount': total_invoice_amount,
            'eligible_refund': eligible_refund,
            'pending_payments': pending_payments,
            'can_request_refund': can_request_refund,
            'min_refund_amount': min_refund_amount,
            'refund_percentage': (eligible_refund / total_vat_paid * 100) if total_vat_paid > 0 else 0,
            'detailed_records': detailed_records,
            'record_count': len(vat_records)
        }
    
    def generate_tax_recommendations(self, user_data: Dict) -> List[Dict]:
        """Vergi optimizasyon önerileri üret"""
        
        recommendations = []
        annual_income = user_data.get('annual_income', 0)
        investment_portfolio = user_data.get('investments', [])
        is_freelancer = user_data.get('is_freelancer', False)
        
        # Gelir vergisi optimizasyonu
        if annual_income > 100000:
            recommendations.append({
                'type': 'income_tax_optimization',
                'title': 'Emeklilik Planı Vergi Avantajı',
                'description': 'Bireysel emeklilik sistemine katkı payı ödeyerek gelir vergisinden indirim sağlayabilirsiniz. Yıllık gelirin %10\'u kadar katkı payı vergiden düşülebilir.',
                'potential_savings': min(annual_income * 0.1 * 0.2, 6000),  # %20 vergi dilimi varsayımı
                'priority': 1,
                'action_items': [
                    'Bireysel emeklilik planı araştırın',
                    'Uygun fon seçimi yapın',
                    'Otomatik ödeme talimatı verin'
                ]
            })
        
        # Yatırım vergisi optimizasyonu
        if investment_portfolio:
            short_term_investments = [inv for inv in investment_portfolio if inv.get('holding_period', 0) < 730]
            if short_term_investments:
                recommendations.append({
                    'type': 'investment_tax_optimization',
                    'title': 'Hisse Senedi Elde Tutma Süresi',
                    'description': 'Hisse senetlerinizi 2 yıl süre ile elde tutarsanız satış kazançları vergiden muaf olur. Mevcut kısa vadeli yatırımlarınızı gözden geçirin.',
                    'potential_savings': sum([inv.get('potential_gain', 0) * 0.15 for inv in short_term_investments]),
                    'priority': 2,
                    'action_items': [
                        'Kısa vadeli yatırımları gözden geçirin',
                        'Satış zamanlamasını planlayın',
                        'Portföy çeşitliliğini koruyun'
                    ]
                })
        
        # KDV iadesi (freelancer'lar için)
        if is_freelancer:
            recommendations.append({
                'type': 'vat_refund_optimization',
                'title': 'KDV İade Takibi',
                'description': 'Freelancer olarak ödediğiniz KDV\'leri takip ederek düzenli iade talep edebilirsiniz. Bu, nakit akışınızı önemli ölçüde iyileştirecektir.',
                'potential_savings': 0,  # Kullanıcı verisine göre hesaplanacak
                'priority': 1,
                'action_items': [
                    'Tüm faturalarınızı kayıt altına alın',
                    'KDV hesaplarınızı düzenli takip edin',
                    'Aylık iade başvurusu yapın'
                ]
            })
        
        # Gider optimizasyonu
        recommendations.append({
            'type': 'deduction_optimization',
            'title': 'Vergi İndirimleri',
            'description': 'Eğitim, sağlık, bağış gibi harcamalarınızı belgelendirerek gelir vergisi matrahından indirim sağlayabilirsiniz.',
            'potential_savings': 2000,  # Ortalama tasarruf
            'priority': 3,
            'action_items': [
                'Eğitim harcama belgelerini saklayın',
                'Sağlık giderlerini kayıt altına alın',
                'Bağış ve yardım makbuzlarını muhafaza edin'
            ]
        })
        
        return sorted(recommendations, key=lambda x: x['priority'])
    
    def save_calculation(self, user_id: int, calculation_data: Dict) -> bool:
        """Vergi hesaplama sonucunu kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO tax_calculations 
            (user_id, calculation_type, tax_year, income_amount, investment_gains, 
             deductions, calculated_tax, effective_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                calculation_data.get('calculation_type', 'income_tax'),
                calculation_data.get('tax_year', 2024),
                calculation_data.get('income_amount', 0),
                calculation_data.get('investment_gains', 0),
                calculation_data.get('deductions', 0),
                calculation_data.get('calculated_tax', 0),
                calculation_data.get('effective_rate', 0),
                calculation_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Hesaplama kaydetme hatası: {e}")
            return False 