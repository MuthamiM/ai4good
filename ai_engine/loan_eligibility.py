"""
Fin AI – Loan Eligibility Checker
Scores useKsh on multiple financial-health factoKsh and matches them
with suitable microfinance products.
"""


class LoanEligibilityChecker:

    PRODUCTS = [
        {
            'name': 'Community Starter Loan',
            'min_score': 30, 'max_amount': 25_000,
            'interest_rate': 12, 'tenure_months': 12,
            'description': 'Entry-level microfinance for first-time borrowers.',
        },
        {
            'name': 'Growth Accelerator Loan',
            'min_score': 50, 'max_amount': 75_000,
            'interest_rate': 10, 'tenure_months': 24,
            'description': 'For small-business owneKsh looking to expand.',
        },
        {
            'name': 'Enterprise Builder Loan',
            'min_score': 70, 'max_amount': 200_000,
            'interest_rate': 8, 'tenure_months': 36,
            'description': 'Premium product for high-potential entrepreneurs.',
        },
        {
            'name': 'Women Empowerment Fund',
            'min_score': 25, 'max_amount': 50_000,
            'interest_rate': 7, 'tenure_months': 18,
            'description': 'Low-interest fund for women entrepreneurs.',
        },
        {
            'name': 'Agricultural Support Loan',
            'min_score': 35, 'max_amount': 100_000,
            'interest_rate': 9, 'tenure_months': 12,
            'description': 'Seasonal funding for farmeKsh and agri-workers.',
        },
    ]

    # 
    def check_eligibility(self, data):
        monthly_income   = float(data.get('monthly_income', 0))
        monthly_expenses = float(data.get('monthly_expenses', 0))
        existing_debt    = float(data.get('existing_debt', 0))
        savings          = float(data.get('savings', 0))
        employment_months = int(data.get('employment_months', 0))
        dependents       = int(data.get('dependents', 0))
        has_bank_account = data.get('has_bank_account', False)
        requested_amount = float(data.get('requested_amount', 0))

        score = 0
        factoKsh = []

        # Income level  (0-25)
        if monthly_income > 0:
            s = min(25, (monthly_income / 1000) * 2)
            score += s
            factors.append({'name': 'Income Level', 'score': round(s, 1), 'max': 25,
                            'status': 'good' if s > 15 else 'fair'})

        # Debt-to-income  (0-20)
        if monthly_income > 0:
            dti = existing_debt / monthly_income * 100
            s = max(0, 20 - dti * 0.4)
            score += s
            factors.append({'name': 'Debt-to-Income', 'score': round(s, 1), 'max': 20,
                            'status': 'good' if dti < 30 else 'warning'})

        # Savings buffer  (0-20)
        if monthly_income > 0:
            ratio = savings / (monthly_income * 6) * 100
            s = min(20, ratio * 0.2)
            score += s
            factors.append({'name': 'Savings Buffer', 'score': round(s, 1), 'max': 20,
                            'status': 'good' if s > 10 else 'fair'})

        # Employment stability  (0-15)
        s = min(15, employment_months / 12 * 5)
        score += s
        factors.append({'name': 'Employment Stability', 'score': round(s, 1), 'max': 15,
                        'status': 'good' if s > 10 else 'fair'})

        # Financial inclusion  (0-10)
        s = 5 if has_bank_account else 0
        s += max(0, min(5, 5 - dependents))
        score += s
        factors.append({'name': 'Financial Inclusion', 'score': round(s, 1), 'max': 10,
                        'status': 'good' if has_bank_account else 'warning'})

        # Disposable income  (0-10)
        if monthly_income > 0:
            disp_pct = (monthly_income - monthly_expenses) / monthly_income * 100
            s = min(10, max(0, disp_pct * 0.3))
            score += s
            factors.append({'name': 'Disposable Income', 'score': round(s, 1), 'max': 10,
                            'status': 'good' if disp_pct > 20 else 'warning'})

        score = min(100, max(0, round(score)))

        # Eligible products
        eligible = []
        for p in self.PRODUCTS:
            if score >= p['min_score']:
                max_eligible = min(p['max_amount'],
                                   monthly_income * p['tenure_months'] * 0.3)
                emi = self._emi(min(requested_amount, max_eligible),
                                p['interest_rate'], p['tenure_months'])
                eligible.append({
                    **p,
                    'max_eligible_amount': round(max_eligible),
                    'monthly_emi': round(emi),
                    'affordable': emi < (monthly_income - monthly_expenses) * 0.5,
                })

        # Improvement tips
        tips = []
        if not has_bank_account:
            tips.append('Open a bank account to improve your financial-inclusion score.')
        if existing_debt > monthly_income * 3:
            tips.append('Reduce existing debt before taking on new loans.')
        if savings < monthly_income * 3:
            tips.append(f'Build an emergency fund of at least Ksh {monthly_income * 3:,.0f} (3 months).')
        if employment_months < 12:
            tips.append('Maintain stable employment for 12+ months.')
        if score >= 60:
            tips.append('Strong profile — you qualify for premium low-interest products!')

        if score >= 70:
            risk, verdict = 'low', 'Excellent'
        elif score >= 50:
            risk, verdict = 'moderate', 'Good'
        elif score >= 30:
            risk, verdict = 'elevated', 'Fair'
        else:
            risk, verdict = 'high', 'Needs Improvement'

        # Qualifying Countries based on score
        countries = ['Kenya']
        if score >= 30: countries.append('Uganda')
        if score >= 50: countries.append('Tanzania')
        if score >= 70: 
            countries.extend(['Rwanda', 'Burundi', 'South Sudan'])

        return {
            'score': score,
            'verdict': verdict,
            'risk_level': risk,
            'factors': factors,
            'eligible_products': eligible,
            'eligible_countries': countries,
            'improvement_tips': tips,
            'monthly_disposable': round(monthly_income - monthly_expenses, 2),
            'safe_emi': round((monthly_income - monthly_expenses) * 0.4),
        }

    @staticmethod
    def _emi(principal, annual_rate, months):
        if principal <= 0 or months <= 0:
            return 0
        r = annual_rate / 12 / 100
        if r == 0:
            return principal / months
        return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
