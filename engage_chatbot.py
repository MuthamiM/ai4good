import os
from dotenv import load_dotenv

# Load FIRST to ensure variables are available for module-level imports
load_dotenv()

from ai_engine.chatbot import FinancialChatbot

def test_engagement():
    print(f"DEBUG: OPENROUTER_API_KEY present: {bool(os.environ.get('OPENROUTER_API_KEY'))}")
    
    bot = FinancialChatbot()
    
    # Mix of General and Financial Questions
    questions = [
        "What is the capital of France?",
        "Explain quantum entanglement in 2 sentences.",
        "How can I improve my 13.3% savings rate?",
        "What is the meaning of life according to Douglas Adams?"
    ]
    
    print("\n--- STARTING CHATBOT ENGAGEMENT TEST ---")
    for q in questions:
        print(f"\n[USER]: {q}")
        res = bot.get_response(q)
        print(f"[FIN AI]: {res.get('response')}")
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    test_engagement()
