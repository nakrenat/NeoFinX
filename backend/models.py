from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """Kullanıcı modeli"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    monthly_income = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='TRY')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Şifreyi hashle ve kaydet"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifreyi kontrol et"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'monthly_income': self.monthly_income,
            'currency': self.currency,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    """Harcama kategorileri"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), default='💰')
    color = db.Column(db.String(7), default='#007bff')
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Self-referential relationship for subcategories
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    expenses = db.relationship('Expense', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'parent_id': self.parent_id,
            'is_active': self.is_active
        }

class Expense(db.Model):
    """Harcama kayıtları"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    location = db.Column(db.String(100))
    payment_method = db.Column(db.String(20), default='cash')  # cash, card, transfer
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    tags = db.Column(db.Text)  # JSON string for tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_tags(self):
        """Tag listesini döndür"""
        return json.loads(self.tags) if self.tags else []
    
    def set_tags(self, tag_list):
        """Tag listesini JSON olarak kaydet"""
        self.tags = json.dumps(tag_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'amount': self.amount,
            'description': self.description,
            'date': self.date.isoformat(),
            'location': self.location,
            'payment_method': self.payment_method,
            'is_recurring': self.is_recurring,
            'recurring_frequency': self.recurring_frequency,
            'tags': self.get_tags(),
            'created_at': self.created_at.isoformat()
        }

class Budget(db.Model):
    """Bütçe planları"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20), default='monthly')  # weekly, monthly, yearly
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Genel Bütçe',
            'name': self.name,
            'amount': self.amount,
            'period': self.period,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Prediction(db.Model):
    """AI tahmin sonuçları"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    prediction_type = db.Column(db.String(50), nullable=False)  # monthly_expense, category_spending, etc.
    predicted_amount = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, default=0.0)
    prediction_date = db.Column(db.Date, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    model_version = db.Column(db.String(20), default='1.0')
    features_used = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'prediction_type': self.prediction_type,
            'predicted_amount': self.predicted_amount,
            'confidence_score': self.confidence_score,
            'prediction_date': self.prediction_date.isoformat(),
            'target_date': self.target_date.isoformat(),
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat()
        }

class TaxCalculation(db.Model):
    """Vergi hesaplamaları"""
    __tablename__ = 'tax_calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    calculation_type = db.Column(db.String(50), nullable=False)  # income_tax, investment_tax, etc.
    tax_year = db.Column(db.Integer, nullable=False)
    income_amount = db.Column(db.Float, default=0.0)
    investment_gains = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    calculated_tax = db.Column(db.Float, default=0.0)
    effective_rate = db.Column(db.Float, default=0.0)
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'calculation_type': self.calculation_type,
            'tax_year': self.tax_year,
            'income_amount': self.income_amount,
            'investment_gains': self.investment_gains,
            'deductions': self.deductions,
            'calculated_tax': self.calculated_tax,
            'effective_rate': self.effective_rate,
            'calculation_date': self.calculation_date.isoformat(),
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class VATTracking(db.Model):
    """KDV takip (freelancer'lar için)"""
    __tablename__ = 'vat_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invoice_number = db.Column(db.String(50))
    client_name = db.Column(db.String(100), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    invoice_amount = db.Column(db.Float, nullable=False)
    vat_rate = db.Column(db.Float, default=18.0)
    vat_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    payment_date = db.Column(db.Date)
    refund_eligible = db.Column(db.Boolean, default=True)
    refund_requested = db.Column(db.Boolean, default=False)
    refund_amount = db.Column(db.Float, default=0.0)
    refund_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'invoice_number': self.invoice_number,
            'client_name': self.client_name,
            'invoice_date': self.invoice_date.isoformat(),
            'invoice_amount': self.invoice_amount,
            'vat_rate': self.vat_rate,
            'vat_amount': self.vat_amount,
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'refund_eligible': self.refund_eligible,
            'refund_requested': self.refund_requested,
            'refund_amount': self.refund_amount,
            'refund_date': self.refund_date.isoformat() if self.refund_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class InvestmentTax(db.Model):
    """Yatırım kazançları vergi hesabı"""
    __tablename__ = 'investment_tax'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id'), nullable=True)
    investment_type = db.Column(db.String(50), nullable=False)
    purchase_amount = db.Column(db.Float, nullable=False)
    sale_amount = db.Column(db.Float, default=0.0)
    gain_loss = db.Column(db.Float, default=0.0)
    holding_period_days = db.Column(db.Integer, default=0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    purchase_date = db.Column(db.Date, nullable=False)
    sale_date = db.Column(db.Date)
    is_exempt = db.Column(db.Boolean, default=False)
    exemption_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'investment_id': self.investment_id,
            'investment_type': self.investment_type,
            'purchase_amount': self.purchase_amount,
            'sale_amount': self.sale_amount,
            'gain_loss': self.gain_loss,
            'holding_period_days': self.holding_period_days,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'purchase_date': self.purchase_date.isoformat(),
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'is_exempt': self.is_exempt,
            'exemption_reason': self.exemption_reason,
            'created_at': self.created_at.isoformat()
        }

class TaxRecommendation(db.Model):
    """Vergi optimizasyon önerileri"""
    __tablename__ = 'tax_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    potential_savings = db.Column(db.Float, default=0.0)
    priority_level = db.Column(db.Integer, default=1)  # 1=high, 2=medium, 3=low
    is_applied = db.Column(db.Boolean, default=False)
    applied_date = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recommendation_type': self.recommendation_type,
            'title': self.title,
            'description': self.description,
            'potential_savings': self.potential_savings,
            'priority_level': self.priority_level,
            'is_applied': self.is_applied,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'created_at': self.created_at.isoformat()
        }

class TaxBracket(db.Model):
    """Vergi dilimleri"""
    __tablename__ = 'tax_brackets'
    
    id = db.Column(db.Integer, primary_key=True)
    tax_year = db.Column(db.Integer, nullable=False)
    bracket_min = db.Column(db.Float, nullable=False)
    bracket_max = db.Column(db.Float)
    tax_rate = db.Column(db.Float, nullable=False)
    deduction_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='TRY')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tax_year': self.tax_year,
            'bracket_min': self.bracket_min,
            'bracket_max': self.bracket_max,
            'tax_rate': self.tax_rate,
            'deduction_amount': self.deduction_amount,
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        } 