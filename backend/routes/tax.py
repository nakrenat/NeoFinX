"""
NeoFinX - Vergi API Rotaları
Vergi hesaplamaları için REST API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from ..models import db, TaxCalculation, VATTracking, InvestmentTax, TaxRecommendation, TaxBracket
from ..tax_calculator import TaxCalculator

tax_bp = Blueprint('tax', __name__)
tax_calc = TaxCalculator()

@tax_bp.route('/income-tax', methods=['POST'])
@jwt_required()
def calculate_income_tax():
    """Gelir vergisi hesaplama"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        annual_income = float(data.get('annual_income', 0))
        tax_year = int(data.get('tax_year', 2024))
        deductions = float(data.get('deductions', 0))
        
        # Vergi hesaplama
        result = tax_calc.calculate_income_tax(annual_income, tax_year)
        
        # Sonucu veritabanına kaydet
        tax_calc_record = TaxCalculation(
            user_id=user_id,
            calculation_type='income_tax',
            tax_year=tax_year,
            income_amount=annual_income,
            deductions=deductions,
            calculated_tax=result['total_tax'],
            effective_rate=result['effective_rate'],
            notes=f"Vergi dilimi hesaplama - {len(result['breakdown'])} dilim"
        )
        
        db.session.add(tax_calc_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Gelir vergisi başarıyla hesaplandı'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@tax_bp.route('/investment-tax', methods=['POST'])
@jwt_required()
def calculate_investment_tax():
    """Yatırım kazançları vergisi hesaplama"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        purchase_amount = float(data.get('purchase_amount', 0))
        sale_amount = float(data.get('sale_amount', 0))
        investment_type = data.get('investment_type', 'stock')
        purchase_date = datetime.strptime(data.get('purchase_date'), '%Y-%m-%d').date()
        sale_date = datetime.strptime(data.get('sale_date'), '%Y-%m-%d').date()
        
        # Vergi hesaplama
        result = tax_calc.calculate_investment_tax(
            purchase_amount, sale_amount, purchase_date, sale_date, investment_type
        )
        
        # Sonucu veritabanına kaydet
        investment_tax = InvestmentTax(
            user_id=user_id,
            investment_type=investment_type,
            purchase_amount=purchase_amount,
            sale_amount=sale_amount,
            gain_loss=result['gain_loss'],
            holding_period_days=result['holding_period_days'],
            tax_rate=result['tax_rate'],
            tax_amount=result['tax_amount'],
            purchase_date=purchase_date,
            sale_date=sale_date,
            is_exempt=result['is_exempt'],
            exemption_reason=result['exemption_reason']
        )
        
        db.session.add(investment_tax)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Yatırım vergisi başarıyla hesaplandı'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@tax_bp.route('/vat-tracking', methods=['POST'])
@jwt_required()
def add_vat_invoice():
    """KDV faturası ekleme"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        vat_invoice = VATTracking(
            user_id=user_id,
            invoice_number=data.get('invoice_number'),
            client_name=data.get('client_name'),
            invoice_date=datetime.strptime(data.get('invoice_date'), '%Y-%m-%d').date(),
            invoice_amount=float(data.get('invoice_amount')),
            vat_rate=float(data.get('vat_rate', 18.0)),
            vat_amount=float(data.get('vat_amount')),
            payment_status=data.get('payment_status', 'pending'),
            notes=data.get('notes', '')
        )
        
        db.session.add(vat_invoice)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': vat_invoice.to_dict(),
            'message': 'KDV faturası başarıyla eklendi'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@tax_bp.route('/vat-tracking', methods=['GET'])
@jwt_required()
def get_vat_invoices():
    """KDV faturalarını listeleme"""
    try:
        user_id = get_jwt_identity()
        
        invoices = VATTracking.query.filter_by(user_id=user_id).order_by(
            VATTracking.invoice_date.desc()
        ).all()
        
        invoice_list = [invoice.to_dict() for invoice in invoices]
        
        # KDV iade hesaplama
        vat_records = [
            {
                'vat_amount': inv['vat_amount'],
                'invoice_amount': inv['invoice_amount'],
                'payment_status': inv['payment_status'],
                'refund_eligible': inv['refund_eligible']
            }
            for inv in invoice_list
        ]
        
        refund_analysis = tax_calc.calculate_vat_refund(vat_records)
        
        return jsonify({
            'success': True,
            'data': {
                'invoices': invoice_list,
                'refund_analysis': refund_analysis
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@tax_bp.route('/recommendations', methods=['POST'])
@jwt_required()
def get_tax_recommendations():
    """Vergi optimizasyon önerileri"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_data = {
            'annual_income': data.get('annual_income', 0),
            'investments': data.get('investments', []),
            'is_freelancer': data.get('is_freelancer', False)
        }
        
        # Önerileri üret
        recommendations = tax_calc.generate_tax_recommendations(user_data)
        
        # Önerileri veritabanına kaydet
        for rec in recommendations:
            existing = TaxRecommendation.query.filter_by(
                user_id=user_id,
                title=rec['title']
            ).first()
            
            if not existing:
                tax_rec = TaxRecommendation(
                    user_id=user_id,
                    recommendation_type=rec['type'],
                    title=rec['title'],
                    description=rec['description'],
                    potential_savings=rec['potential_savings'],
                    priority_level=rec['priority']
                )
                db.session.add(tax_rec)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': recommendations,
            'message': 'Vergi optimizasyon önerileri hazırlandı'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@tax_bp.route('/brackets/<int:tax_year>', methods=['GET'])
def get_tax_brackets(tax_year):
    """Vergi dilimlerini getirme"""
    try:
        brackets = TaxBracket.query.filter_by(
            tax_year=tax_year,
            is_active=True
        ).order_by(TaxBracket.bracket_min).all()
        
        bracket_list = [bracket.to_dict() for bracket in brackets]
        
        return jsonify({
            'success': True,
            'data': bracket_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@tax_bp.route('/history', methods=['GET'])
@jwt_required()
def get_tax_history():
    """Kullanıcının vergi hesaplama geçmişi"""
    try:
        user_id = get_jwt_identity()
        
        calculations = TaxCalculation.query.filter_by(user_id=user_id).order_by(
            TaxCalculation.created_at.desc()
        ).limit(20).all()
        
        calc_list = [calc.to_dict() for calc in calculations]
        
        return jsonify({
            'success': True,
            'data': calc_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400 