from ai_engine.loan_eligibility import LoanEligibilityChecker

def test_loan_logic():
    checker = LoanEligibilityChecker()
    data = {
        'monthly_income': 30000,
        'monthly_expenses': 20000,
        'existing_debt': 5000,
        'savings': 10000,
        'employment_months': 24,
        'dependents': 2,
        'has_bank_account': True,
        'requested_amount': 50000
    }
    
    try:
        print("Testing Loan Eligibility Logic...")
        result = checker.check_eligibility(data)
        print("Result:", result)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_loan_logic()
