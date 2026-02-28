from flask import Flask, render_template, request, jsonify
import os
import sqlite3
import random
from werkzeug.utils import secure_filename

from ai_engine.budget_analyzer import BudgetAnalyzer
from ai_engine.loan_eligibility import LoanEligibilityChecker
from ai_engine.expense_categorizer import ExpenseCategorizer
from ai_engine.savings_advisor import SavingsAdvisor
from ai_engine.chatbot import FinancialChatbot
from ai_engine.risk_optimization import RiskOptimizationEngine

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize AI engines
budget_analyzer = BudgetAnalyzer()
loan_checker = LoanEligibilityChecker()
expense_categorizer = ExpenseCategorizer()
savings_advisor = SavingsAdvisor()
chatbot = FinancialChatbot()
risk_engine = RiskOptimizationEngine()

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('finai.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS kyc_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            crb_score INTEGER
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS linked_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT NOT NULL,
            card_last4 TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()


#  Page Routes 

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/budget')
def budget():
    return render_template('budget.html')


@app.route('/loans')
def loans():
    return render_template('loans.html')


@app.route('/savings')
def savings():
    return render_template('savings.html')


@app.route('/chat')
def chat_page():
    return render_template('chatbot.html')


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')


#  API Routes 

@app.route('/api/budget/analyze', methods=['POST'])
def analyze_budget():
    data = request.json
    result = budget_analyzer.analyze(data)
    return jsonify(result)


@app.route('/api/loan/check', methods=['POST'])
def check_loan():
    data = request.json
    result = loan_checker.check_eligibility(data)
    return jsonify(result)


@app.route('/api/expense/categorize', methods=['POST'])
def categorize_expense():
    data = request.json
    result = expense_categorizer.categorize(data)
    return jsonify(result)


@app.route('/api/savings/plan', methods=['POST'])
def plan_savings():
    data = request.json
    result = savings_advisor.create_plan(data)
    return jsonify(result)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    response = chatbot.get_response(data.get('message', ''))
    return jsonify(response)


@app.route('/api/risk/fixed-income', methods=['POST'])
def fixed_income():
    data = request.json
    result = risk_engine.analyze_fixed_income(data)
    return jsonify(result)


@app.route('/api/risk/balance-sheet', methods=['POST'])
def balance_sheet():
    data = request.json
    result = risk_engine.balance_sheet_valuation(data)
    return jsonify(result)


@app.route('/api/risk/decision-impact', methods=['POST'])
def decision_impact():
    data = request.json
    result = risk_engine.decision_impact(data)
    return jsonify(result)


@app.route('/api/onboarding/kyc', methods=['POST'])
def upload_kyc():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Simulate CRB check
        crb_score = random.randint(300, 850)
        status = 'Approved' if crb_score > 500 else 'Manual Review'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO kyc_documents (filename, status, crb_score) VALUES (?, ?, ?)', (filename, status, crb_score))
        doc_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'id': doc_id, 
            'status': status, 
            'crb_score': crb_score, 
            'message': f'Document processed & checked. CRB Status: {status} (Score: {crb_score})'
        })


@app.route('/api/onboarding/card', methods=['POST'])
def link_card():
    data = request.json
    name = data.get('name')
    number = data.get('number', '')
    
    last4 = number[-4:] if len(number) >= 4 else '0000'
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO linked_cards (card_name, card_last4) VALUES (?, ?)', (name, last4))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Card ending in {last4} securely linked and stored.'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
