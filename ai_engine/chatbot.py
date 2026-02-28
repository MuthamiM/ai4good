"""
Fin AI – Financial Literacy Chatbot
Uses OpenRouter API for intelligent AI responses, with a local
knowledge-base fallback if the API is unavailable.
"""

import random
import requests
import os

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
        ]
        self.conversation_history = []

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

    #  Local fallback 
    def _local_response(self, message: str) -> dict:
        kb = {
            'budget': {
                'kw': ['budget', 'budgeting', 'spending', 'expense'],
                'ans': [
                    'Based on your data, you spend about Ksh 8,065 on rent and Ksh 5,101 on groceries. According to the 50/30/20 rule, your needs are well within the 50% limit of your Ksh 30,000 income. Try cutting back on dining out (Ksh 2,031) to reach a 20% savings rate.',
                    'Your current savings rate is 13.3% (Ksh 4,001). To hit the 20% goal (Ksh 6,000), consider reducing discretionary spending like entertainment and dining.',
                ],
            },
            'savings': {
                'kw': ['save', 'saving', 'savings', 'emergency fund'],
                'ans': [
                    'You are saving Ksh 4,001 per month. At this rate, building a 3-month emergency fund (approx Ksh 78,000) will take about 20 months. Increase savings to Ksh 6,000 to reach it in 13 months.',
                    'Your savings rate of 13.3% is good, but automating an extra Ksh 2,000 from your Ksh 30,000 income will significantly boost your wealth over time.',
                ],
            },
            'loan': {
                'kw': ['loan', 'borrow', 'credit', 'emi', 'microfinance'],
                'ans': [
                    'With an income of Ksh 30,000 and total expenses around Ksh 26,000, your free cash flow is limited to Ksh 4,000. Ensure any new EMI does not exceed this amount.',
                ],
            },
            'investment': {
                'kw': ['invest', 'sip', 'mutual fund', 'fd', 'stock'],
                'ans': [
                    'You are saving Ksh 4,001 monthly. Redirecting even half of this (Ksh 2,000) into a SIP in index funds can compound significantly over the next 10-15 years.',
                ],
            },
            'greeting': {
                'kw': ['hello', 'hi', 'hey', 'namaste'],
                'ans': ['Hello. I am Fin AI. I have analyzed your dashboard data (Income: Ksh 30,000, Savings: 13.3%). How can I help you optimize your finances today?'],
            },
        }

        msg = message.lower()
        best, best_n = None, 0
        for cat, info in kb.items():
            n = sum(1 for kw in info['kw'] if kw in msg)
            if n > best_n:
                best_n, best = n, cat

        if best:
            resp = random.choice(kb[best]['ans'])
        else:
            resp = "I have access to your budget data. Ask me how to improve your 13.3% savings rate or cut your expenses."

        return {
            'response': resp,
            'quick_replies': self.quick_replies[:4],
            'category': best or 'general',
        }
