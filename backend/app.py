from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'neofinx-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///neofinx.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')

# Initialize extensions
db = SQLAlchemy(app)
cors = CORS(app)
jwt = JWTManager(app)

# Import models and routes
from models import User, Expense, Category, Budget, TaxCalculation, VATTracking, InvestmentTax, TaxRecommendation, TaxBracket
from routes import auth_bp, expense_bp, analytics_bp, budget_bp
from routes.tax import tax_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(expense_bp, url_prefix='/api/expenses')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(budget_bp, url_prefix='/api/budget')
app.register_blueprint(tax_bp, url_prefix='/api/tax')

@app.route('/')
def home():
    return jsonify({
        'message': 'NeoFinX API - Akıllı Bütçe ve Harcama Asistanı',
        'version': '1.0.0',
        'status': 'active'
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 