from ai_engine.risk_optimization import RiskOptimizationEngine

def test_risk_logic():
    engine = RiskOptimizationEngine()
    
    # Test Decision Impact
    data = {
        'decision_type': 'loan',
        'amount': 50000,
        'monthly_income': 30000,
        'monthly_expenses': 20000,
        'current_savings': 10000,
        'current_debt': 5000,
        'interest_rate': 10,
        'tenure_months': 12
    }
    
    try:
        print("Testing Risk Optimization Decision Impact...")
        result = engine.decision_impact(data)
        print("Verdict:", result.get('verdict'))
        print("Risk Indicators:", result.get('risk_indicators'))
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_risk_logic()
