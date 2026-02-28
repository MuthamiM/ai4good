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

    #  Local fallback 
    def _local_response(self, message):
        """Conversational fallback when API is down."""
        msg_low = message.lower()
        
        # Identity / General Greetings
        if any(w in msg_low for w in ['who are you', 'what are you', 'how are you', 'your name']):
            return {
                'response': "I am Fin AI, your intelligent financial coach. I can help you with budgeting, savings analysis, or general questions you may have. How can I assist you today?",
                'quick_replies': self.quick_replies[:4],
                'category': 'general',
            }
        
        if any(w in msg_low for w in ['hello', 'hi', 'hey']):
            return {
                'response': "Hello! I am Fin AI. I have analyzed your dashboard data and I am ready to help you optimize your finances or answer any general questions. What is on your mind?",
                'quick_replies': self.quick_replies[:4],
                'category': 'greeting',
            }

        # Mission / SDG
        if any(w in msg_low for w in ['sdg', 'mission', 'good', 'hackathon']):
            return {
                'response': "Our mission is to empower financial inclusion through AI. We align with SDG 1 (No Poverty) by providing tools to manage debt and SDG 17 (Partnerships) by building community-driven financial literacy for the AI for Good Hackathon 2026.",
                'quick_replies': self.quick_replies[:4],
                'category': 'general',
            }

        # Analysis Fallback
        if any(w in msg_low for w in ['budget', 'income', 'save', 'money', 'rent', 'expense']):
            return {
                'response': "Based on your dashboard, your current savings rate is 13.3% (Ksh 4,000). I recommend trying to cut your Dining Out or Entertainment expenses to reach a 20% savings goal. Would you like a breakdown of those categories?",
                'quick_replies': ['How to cut dining out?', 'What is 20% savings goal?', 'Show my expenses'],
                'category': 'financial',
            }

        # General Catch-all
        return {
            'response': "I am currently in high-performance mode. While I am waiting for my full neural uplink (OpenRouter API), I can still discuss your budget, our AI mission, or basic financial concepts. What would you like to explore?",
            'quick_replies': self.quick_replies[:4],
            'category': 'general',
        }
