import os
from dotenv import load_dotenv
load_dotenv()

from ai_engine.chatbot import FinancialChatbot

def test_focused():
    bot = FinancialChatbot()
    questions = [
        "How to cut wants?",
        "Show top expenses"
    ]
    
    for q in questions:
        print(f"\n[USER]: {q}")
        res = bot.get_response(q)
        print(f"[FIN AI]: {res.get('response')}")

if __name__ == "__main__":
    test_focused()
