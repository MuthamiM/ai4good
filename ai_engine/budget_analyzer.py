"""
Fin AI – Budget Analyzer
Uses the 50/30/20 rule to analyze income vs expenses and provide
AI-powered recommendations for healthier spending patterns.
"""


class BudgetAnalyzer:
    NEEDS = ['housing', 'utilities', 'groceries', 'transportation', 'insurance', 'healthcare']
    WANTS = ['entertainment', 'dining_out', 'shopping', 'subscriptions', 'hobbies']
    SAVINGS = ['savings', 'investments', 'debt_payment', 'emergency_fund']

    def analyze(self, data):
        income = float(data.get('income', 0))
        expenses = data.get('expenses', {})

        if income <= 0:
            return {'error': 'Please provide a valid income amount.'}

        # Totals by bucket
        needs_total = sum(float(expenses.get(c, 0)) for c in self.NEEDS)
        wants_total = sum(float(expenses.get(c, 0)) for c in self.WANTS)
        savings_total = sum(float(expenses.get(c, 0)) for c in self.SAVINGS)
        total_expenses = needs_total + wants_total + savings_total

        needs_pct = needs_total / income * 100
        wants_pct = wants_total / income * 100
        savings_pct = savings_total / income * 100

        ideal_needs = income * 0.50
        ideal_wants = income * 0.30
        ideal_savings = income * 0.20

        #  Recommendations & health score 
        recommendations = []
        health_score = 100
        risk_level = 'low'

        if needs_pct > 55:
            recommendations.append({
                'type': 'warning',
                'category': 'Needs',
                'message': (f'Essential expenses are {needs_pct:.1f}% of income '
                            f'(recommended ≤ 50%). Consider reducing housing or utility costs.'),
                'saving_potential': round(needs_total - ideal_needs, 2),
            })
            health_score -= 15

        if wants_pct > 35:
            recommendations.append({
                'type': 'warning',
                'category': 'Wants',
                'message': (f'Discretionary spending is {wants_pct:.1f}% '
                            f'(recommended ≤ 30%). Look for areas to cut back.'),
                'saving_potential': round(wants_total - ideal_wants, 2),
            })
            health_score -= 10

        if savings_pct < 15:
            recommendations.append({
                'type': 'critical',
                'category': 'Savings',
                'message': (f'Savings rate is {savings_pct:.1f}% '
                            f'(recommended ≥ 20%). Increase your savings contributions.'),
                'saving_potential': round(ideal_savings - savings_total, 2),
            })
            health_score -= 20
            risk_level = 'medium'

        if savings_pct < 5:
            risk_level = 'high'
            health_score -= 15

        if total_expenses > income:
            recommendations.append({
                'type': 'critical',
                'category': 'Overall',
                'message': (f'You are spending Ksh {total_expenses - income:,.2f} '
                            f'more than you earn!'),
                'saving_potential': round(total_expenses - income, 2),
            })
            risk_level = 'high'
            health_score -= 30

        remaining = income - total_expenses
        if remaining > 0 and savings_pct >= 20:
            recommendations.append({
                'type': 'success',
                'category': 'Overall',
                'message': (f'Great job! Ksh {remaining:,.2f} remaining and '
                            f'you meet the 20% savings target.'),
                'saving_potential': 0,
            })

        #  Expense breakdown 
        all_expenses = {k: float(v) for k, v in expenses.items() if float(v) > 0}
        sorted_expenses = sorted(all_expenses.items(), key=lambda x: x[1], reverse=True)

        budget_data = {
            'needs': {'amount': needs_total, 'percentage': round(needs_pct, 1),
                      'ideal': 50, 'status': 'good' if needs_pct <= 50 else 'warning'},
            'wants': {'amount': wants_total, 'percentage': round(wants_pct, 1),
                      'ideal': 30, 'status': 'good' if wants_pct <= 30 else 'warning'},
            'savings': {'amount': savings_total, 'percentage': round(savings_pct, 1),
                        'ideal': 20, 'status': 'good' if savings_pct >= 20 else 'warning'},
        }

        optimized = {
            'needs': round(min(needs_total, ideal_needs), 2),
            'wants': round(min(wants_total, ideal_wants), 2),
            'savings': round(max(savings_total, ideal_savings), 2),
        }

        health_score = max(0, min(100, health_score))

        return {
            'income': income,
            'total_expenses': round(total_expenses, 2),
            'remaining': round(remaining, 2),
            'health_score': health_score,
            'risk_level': risk_level,
            'budget_data': budget_data,
            'recommendations': recommendations,
            'top_expenses': sorted_expenses[:5],
            'optimized_budget': optimized,
            'expense_breakdown': all_expenses,
        }
