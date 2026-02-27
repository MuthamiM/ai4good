"""
Fin AI – Savings Advisor
Creates personalised savings plans with investment strategy
recommendations and projected growth scenarios.
"""


class SavingsAdvisor:

    STRATEGIES = {
        'conservative': [
            {'name': 'Fixed Deposit', 'allocation': 50, 'expected_return': '6-7%',
             'risk': 'Very Low', 'description': 'Safe bank deposits with guaranteed returns.'},
            {'name': 'Recurring Deposit', 'allocation': 30, 'expected_return': '5.5-6.5%',
             'risk': 'Very Low', 'description': 'Monthly deposits with fixed returns.'},
            {'name': 'Government Bonds', 'allocation': 20, 'expected_return': '7-8%',
             'risk': 'Low', 'description': 'Sovereign-backed securities.'},
        ],
        'moderate': [
            {'name': 'Balanced Mutual Funds', 'allocation': 40, 'expected_return': '10-12%',
             'risk': 'Medium', 'description': 'Equity + debt mix for balanced growth.'},
            {'name': 'Fixed Deposit', 'allocation': 30, 'expected_return': '6-7%',
             'risk': 'Very Low', 'description': 'Safety net for stability.'},
            {'name': 'SIP (Index Funds)', 'allocation': 30, 'expected_return': '12-15%',
             'risk': 'Medium', 'description': 'Systematic market-index investment.'},
        ],
        'aggressive': [
            {'name': 'Equity Mutual Funds', 'allocation': 50, 'expected_return': '14-18%',
             'risk': 'High', 'description': 'High-growth equity investments.'},
            {'name': 'SIP (Small Cap)', 'allocation': 30, 'expected_return': '15-20%',
             'risk': 'High', 'description': 'Small-cap funds for maximum growth.'},
            {'name': 'Balanced Funds', 'allocation': 20, 'expected_return': '10-12%',
             'risk': 'Medium', 'description': 'Stability anchor for portfolio.'},
        ],
    }

    RATES = {'conservative': 0.06, 'moderate': 0.10, 'aggressive': 0.14}

    def create_plan(self, data):
        income   = float(data.get('monthly_income', 0))
        expenses = float(data.get('monthly_expenses', 0))
        current  = float(data.get('current_savings', 0))
        target   = float(data.get('target_amount', 0))
        months   = max(1, int(data.get('target_months', 12)))
        goal     = data.get('goal_name', 'My Goal')
        risk     = data.get('risk_tolerance', 'moderate')

        disposable = income - expenses
        remaining  = max(0, target - current)
        monthly_needed = remaining / months if months > 0 else 0
        feasible = monthly_needed <= disposable * 0.8
        progress = min(100, current / target * 100) if target > 0 else 0

        # Growth scenarios
        scenarios = []
        for label, r in [('Conservative (6%)', 0.06),
                         ('Moderate (10%)', 0.10),
                         ('Aggressive (14%)', 0.14)]:
            mr = r / 12
            fv = current * (1 + mr) ** months
            for m in range(months):
                fv += monthly_needed * (1 + mr) ** (months - m - 1)
            scenarios.append({
                'label': label,
                'projected_value': round(fv, 2),
                'returns': round(fv - current - monthly_needed * months, 2),
                'meets_goal': fv >= target,
            })

        # Monthly milestones (first 12)
        rate = self.RATES.get(risk, 0.10)
        mr = rate / 12
        milestones, acc = [], current
        for m in range(1, min(months + 1, 13)):
            acc = acc * (1 + mr) + monthly_needed
            milestones.append({
                'month': m,
                'amount': round(acc, 2),
                'percentage': round(min(100, acc / target * 100), 1) if target > 0 else 0,
            })

        # Tips
        tips = []
        if not feasible:
            safe_months = int(remaining / (disposable * 0.6)) if disposable > 0 else 0
            tips.append(
                f'Goal requires Ksh {monthly_needed:,.0f}/month but you have '
                f'Ksh {disposable:,.0f} disposable. Consider extending to ~{safe_months} months.'
            )
        if disposable > monthly_needed * 1.5:
            tips.append(
                f'Room to save extra! Adding Ksh {(disposable - monthly_needed) * 0.3:,.0f}/month '
                f'could accelerate your goal.'
            )
        if months > 24 and risk == 'conservative':
            tips.append('Consider moderate-risk investments for long-term goals.')
        if current > 0:
            tips.append(f'Great start — {progress:.1f}% of your goal is already saved!')
        tips.append('Set up automatic transfeKsh on payday to make saving effortless.')

        return {
            'goal_name': goal,
            'target_amount': target,
            'current_savings': current,
            'remaining': remaining,
            'monthly_required': round(monthly_needed, 2),
            'progress': round(progress, 1),
            'feasible': feasible,
            'disposable_income': disposable,
            'scenarios': scenarios,
            'strategies': self.STRATEGIES.get(risk, self.STRATEGIES['moderate']),
            'milestones': milestones,
            'tips': tips,
            'target_months': months,
            'recommended_monthly': round(min(monthly_needed, disposable * 0.6), 2),
        }
