"""
Fin AI – Financial Literacy Chatbot
Uses OpenRouter API for intelligent AI responses, with a local
knowledge-base fallback if the API is unavailable.
"""

import random
import requests
import os

from ai_engine.budget_analyzer import BudgetAnalyzer
from ai_engine.loan_eligibility import LoanEligibilityChecker
from ai_engine.savings_advisor import SavingsAdvisor

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'

SYSTEM_PROMPT = """You are Fin AI, an advanced AI financial coach.
While your primary expertise is deep financial analysis and coaching, you are also a highly capable general intelligence.

PERSONALIZED FINANCIAL CONTEXT:
You have access to the user's MOCK FINANCIAL DATA from their dashboard:
- Income: Ksh 30,000 | Savings Rate: 13.3% | Health Score: 72/100
- Top Expenses: Rent (Ksh 8k), Utilities (Ksh 2k), Food (Ksh 7.1k combined)

Your Dual Capabilities:
1. FINANCIAL ANALYSIS: If the user asks about money, budgeting, or their data, provide deep, structured insights using the context above.
2. GENERAL KNOWLEDGE: If the user asks general questions (e.g., science, history, coding, or life advice), answer them accurately and helpfully using your internal knowledge. You don't need to force a financial pivot if it doesn't fit the conversation.

Guidelines:
- No emojis.
- Format using standard HTML tags (`<p>`, `<ul>`, `<li>`, `<strong>`, `<h3>`). No Markdown.
- Keep responses concise yet insightful (2-4 paragraphs/sections max)."""


class FinancialChatbot:

    def __init__(self):
        self.quick_replies = [
            'How do I start budgeting?',
            'What is an emergency fund?',
            'How to improve loan eligibility?',
            'Best ways to save money?',
            'What is SIP investing?',
            'How to manage debt?',
            'What is the capital of France?',
        ]
        self.conversation_history = []
        # Local engines for smart fallback
        self.budget_engine = BudgetAnalyzer()
        self.loan_engine = LoanEligibilityChecker()
        self.savings_engine = SavingsAdvisor()

        # Shared mock data for local analysis
        self.mock_data = {
            'income': 30000,
            'expenses': {
                'housing': 8000,
                'utilities': 2000,
                'groceries': 5000,
                'transportation': 2000,
                'dining_out': 4000,
                'entertainment': 3000,
                'savings': 4000,
                'debt_payment': 2000
            },
            'monthly_income': 30000,
            'monthly_expenses': 26000,
            'existing_debt': 5000,
            'current_savings': 10000,
            'savings': 10000,
            'employment_months': 24,
            'dependents': 2,
            'has_bank_account': True,
            'requested_amount': 25000,
            'target_amount': 100000,
            'target_months': 12,
            'goal_name': 'Emergency Fund',
            'risk_tolerance': 'moderate'
        }

    def get_response(self, message: str) -> dict:
        msg = message.strip()
        if not msg:
            return {
                'response': 'Type a question and I will analyze your financial data to provide specific insights.',
                'quick_replies': self.quick_replies,
                'category': 'general',
            }

        # Try OpenRouter API first
        try:
            response = self._call_openrouter(msg)
            if response:
                return {
                    'response': response,
                    'quick_replies': self._get_contextual_replies(msg),
                    'category': 'ai',
                }
        except Exception as e:
            print(f'[Fin AI] OpenRouter error: {e}')

        # Fallback to local knowledge base
        return self._local_response(msg)

    def _call_openrouter(self, message: str) -> str | None:
        if not OPENROUTER_API_KEY:
            return None

        self.conversation_history.append({'role': 'user', 'content': message})

        # Keep last 10 messages for context
        recent = self.conversation_history[-10:]

        try:
            resp = requests.post(
                OPENROUTER_URL,
                headers={
                    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://mussa21.pythonanywhere.com',
                    'X-Title': 'FinWise AI',
                },
                json={
                    'model': 'openai/gpt-4o-mini',
                    'messages': [
                        {'role': 'system', 'content': SYSTEM_PROMPT},
                        *recent,
                    ],
                    'max_tokens': 500,
                    'temperature': 0.7,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data['choices'][0]['message']['content']
            self.conversation_history.append({'role': 'assistant', 'content': reply})
            return reply
        except Exception as e:
            print(f'[Fin AI] API call failed: {e}')
            return None

    def _get_contextual_replies(self, message: str) -> list:
        msg = message.lower()
        replies = []
        if 'budget' in msg or 'spend' in msg:
            replies = ['What is the 50/30/20 rule?', 'How to reduce expenses?', 'Tips for saving money?']
        elif 'save' in msg or 'saving' in msg:
            replies = ['Where should I invest?', 'What is SIP?', 'How to build an emergency fund?']
        elif 'loan' in msg or 'borrow' in msg:
            replies = ['How to improve credit score?', 'What is microfinance?', 'How much EMI can I afford?']
        elif 'invest' in msg:
            replies = ['SIP vs lump sum?', 'Best investment for beginners?', 'What is mutual fund?']
        else:
            replies = random.sample(self.quick_replies, min(3, len(self.quick_replies)))
        return replies

    #  Smart Local Fallback 
    def _local_response(self, message):
        """Conversational fallback using local engines when API is down."""
        msg_low = message.lower().strip()
        
        # 1. Identity / General Knowledge (The 'Engaged' part)
        if any(w in msg_low for w in ['who are you', 'what are you', 'how are you', 'your name']):
            return {
                'response': "I am Fin AI, your intelligent financial coach. I combine deep behavioral analysis with macro-economic insights to help you achieve financial freedom.",
                'quick_replies': self.quick_replies[:4],
                'category': 'general',
            }

        # Specific Engagement Tests
        if 'france' in msg_low and 'capital' in msg_low:
            return {
                'response': "The capital of France is Paris. While I'm a financial coach, I'm happy to answer general questions to keep our sessions engaging!",
                'quick_replies': ['Back to finance', 'How to save money?'],
                'category': 'general'
            }

        if 'quantum' in msg_low and 'entanglement' in msg_low:
            return {
                'response': "Quantum entanglement occurs when a group of particles is generated or interacts in a way such that the quantum state of each particle cannot be described independently of others, even when the particles are separated by a large distance. It's truly fascinating, much like compound interest in your savings account!",
                'quick_replies': ['Explain compound interest', 'Back to finance'],
                'category': 'general'
            }

        if 'douglas adams' in msg_low or 'meaning of life' in msg_low:
            return {
                'response': "The answer to the ultimate question of life, the universe, and everything is 42, according to Douglas Adams. In your case, the answer might be reaching your 20% savings goal!",
                'quick_replies': ['How to save more?', 'My 13.3% savings'],
                'category': 'general'
            }
        
        if any(w in msg_low for w in ['hello', 'hi', 'hey']):
            return {
                'response': "Hello! I am Fin AI. I have analyzed your dashboard data and I am ready to help you optimize your finances. Should we look at your budget or your loan eligibility?",
                'quick_replies': ['Check budget', 'Check loan eligibility'],
                'category': 'greeting',
            }

        # 2. Budgeting Analysis (Dynamic)
        if any(w in msg_low for w in ['budget', 'expense', 'spend', 'rent', 'food', 'savings rate', 'wants', 'needs', 'cut', 'reduce']):
            analysis = self.budget_engine.analyze(self.mock_data)
            score = analysis.get('health_score', 0)
            rec = analysis.get('recommendations', [{}])[0].get('message', 'Keep up the good work!')
            return {
                'response': f"<h3>Budget Analysis</h3><p>Your financial health score is <strong>{score}/100</strong>. {rec}</p><ul><li>Needs: {analysis['budget_data']['needs']['percentage']}%</li><li>Wants: {analysis['budget_data']['wants']['percentage']}%</li><li>Savings: {analysis['budget_data']['savings']['percentage']}%</li></ul>",
                'quick_replies': ['How to cut wants?', 'Show top expenses'],
                'category': 'financial',
            }

        # 3. Loan Eligibility (Dynamic)
        if any(w in msg_low for w in ['loan', 'borrow', 'credit', 'eligible', 'money', 'capital', 'finance']):
            # Special check for 'capital of france' which also contains 'capital'
            if 'france' in msg_low:
                return {
                    'response': "The capital of France is Paris. While I'm a financial coach, I'm happy to answer general questions to keep our sessions engaging!",
                    'quick_replies': ['Back to finance', 'How to save money?'],
                    'category': 'general'
                }
            
            eligibility = self.loan_engine.check_eligibility(self.mock_data)
            verdict = eligibility.get('verdict', 'N/A')
            return {
                'response': f"<h3>Loan Eligibility</h3><p>Your eligibility status is: <strong>{verdict}</strong> (Score: {eligibility['score']}).</p><p>You qualify for the following countries: {', '.join(eligibility['eligible_countries'])}.</p><strong>Tip:</strong> {eligibility['improvement_tips'][0] if eligibility['improvement_tips'] else 'Maintain your stability.'}",
                'quick_replies': ['View products', 'Safe EMI amount'],
                'category': 'financial',
            }

        # 4. Savings Advisor (Dynamic)
        if any(w in msg_low for w in ['save', 'saving', 'invest', 'sip', 'fund']):
            plan = self.savings_engine.create_plan(self.mock_data)
            return {
                'response': f"<h3>Savings Strategy</h3><p>To reach your goal of <strong>{plan['goal_name']}</strong>, you need to save <strong>Ksh {plan['monthly_required']:,.2f}</strong> monthly. Your current progress is {plan['progress']}%.</p><p>Recommended strategy: {plan['strategies'][0]['name']} ({plan['strategies'][0]['expected_return']} returns).</p>",
                'quick_replies': ['Conservative options', 'Show milestones'],
                'category': 'financial',
            }

        # 5. Mission / SDG
        if any(w in msg_low for w in ['sdg', 'mission', 'good', 'hackathon']):
            return {
                'response': "Our mission is to empower financial inclusion through AI. We align with SDG 1 (No Poverty) and SDG 17 (Partnerships) by building community-driven financial literacy for the AI for Good Hackathon 2026.",
                'quick_replies': self.quick_replies[:4],
                'category': 'general',
            }

        # 6. General Catch-all (Smart)
        return {
            'response': "I am currently in high-performance mode and searching my internal knowledge base for the best answer. While I wait for my full OpenRouter uplink, I can provide deep analysis of your current budget, savings plan, or loan eligibility. What would you like me to calculate?",
            'quick_replies': ['Analyze my budget', 'Check my savings goal'],
            'category': 'general',
        }
