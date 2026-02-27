"""
Fin AI – Risk & Optimization Engine
Fixed-income risk analysis, balance-sheet-aware valuation,
and integrated pricing / decision-impact assessment — all
framed for financial-inclusion use cases.
"""

import math


class RiskOptimizationEngine:
    """Provides three core analyses used on the Analytics page."""

    # ── 1. Fixed-Income Risk & Optimization ──────────────────────────────
    def analyze_fixed_income(self, data):
        """Score risk across the user's fixed-income holdings and suggest
        optimizations (duration, diversification, reinvestment)."""

        holdings = data.get('holdings', [])
        #  Each holding: {name, principal, rate, tenure_years}
        if not holdings:
            return {'error': 'Add at least one fixed-income holding.'}

        total_invested = 0
        weighted_rate = 0
        weighted_duration = 0
        results = []

        for h in holdings:
            p = float(h.get('principal', 0))
            r = float(h.get('rate', 0)) / 100
            t = float(h.get('tenure_years', 1))
            name = h.get('name', 'Unnamed')

            # Macaulay duration proxy for simple instruments
            if r > 0 and t > 0:
                coupon = p * r
                pv_coupons = sum(coupon / (1 + r) ** yr for yr in range(1, int(t) + 1))
                pv_face = p / (1 + r) ** t
                price = pv_coupons + pv_face
                mac_dur = sum(yr * (coupon / (1 + r) ** yr) for yr in range(1, int(t) + 1))
                mac_dur += t * (p / (1 + r) ** t)
                mac_dur /= price if price else 1
                mod_dur = mac_dur / (1 + r)
            else:
                price = p
                mac_dur = t
                mod_dur = t

            maturity_value = p * (1 + r) ** t
            total_return = maturity_value - p

            results.append({
                'name': name,
                'principal': p,
                'rate': float(h.get('rate', 0)),
                'tenure': t,
                'macaulay_duration': round(mac_dur, 2),
                'modified_duration': round(mod_dur, 2),
                'maturity_value': round(maturity_value, 2),
                'total_return': round(total_return, 2),
                'price_sensitivity': round(mod_dur * 0.01 * p, 2),  # Ksh  change per 1% rate move
            })

            total_invested += p
            weighted_rate += r * p
            weighted_duration += mac_dur * p

        avg_rate = (weighted_rate / total_invested * 100) if total_invested else 0
        avg_duration = (weighted_duration / total_invested) if total_invested else 0
        portfolio_return = sum(r['total_return'] for r in results)

        # Risk score (0-100, lower = safer)
        risk_score = min(100, max(0, int(avg_duration * 8 + (100 - avg_rate * 5))))

        # Recommendations
        recs = []
        if avg_duration > 5:
            recs.append('High duration exposure — consider shorter-tenure instruments to reduce interest-rate risk.')
        if avg_rate < 6:
            recs.append('Below-market yields detected. Explore government bonds or top-rated corporate FDs for better risk-adjusted returns.')
        if len(holdings) < 3:
            recs.append('Low diversification. Spread across at least 3 instruments with different maturities.')
        if avg_duration < 2 and avg_rate < 5:
            recs.append('Very conservative portfolio. For longer goals, consider balanced mutual funds for growth.')
        recs.append(f'Portfolio average yield: {avg_rate:.1f}% | Average duration: {avg_duration:.1f} years.')

        return {
            'holdings': results,
            'total_invested': round(total_invested, 2),
            'portfolio_return': round(portfolio_return, 2),
            'avg_rate': round(avg_rate, 2),
            'avg_duration': round(avg_duration, 2),
            'risk_score': risk_score,
            'recommendations': recs,
        }

    # ── 2. Balance-Sheet-Aware Valuation ─────────────────────────────────
    def balance_sheet_valuation(self, data):
        """Compute net worth, solvency metrics, and valuation ratios
        from a simplified personal balance sheet."""

        assets = data.get('assets', {})
        liabilities = data.get('liabilities', {})
        monthly_income = float(data.get('monthly_income', 0))

        # Assets
        cash = float(assets.get('cash_savings', 0))
        investments = float(assets.get('investments', 0))
        property_val = float(assets.get('property', 0))
        vehicles = float(assets.get('vehicles', 0))
        gold = float(assets.get('gold_jewelry', 0))
        other_assets = float(assets.get('other', 0))

        liquid_assets = cash + investments
        total_assets = liquid_assets + property_val + vehicles + gold + other_assets

        # Liabilities
        home_loan = float(liabilities.get('home_loan', 0))
        vehicle_loan = float(liabilities.get('vehicle_loan', 0))
        personal_loan = float(liabilities.get('personal_loan', 0))
        credit_card = float(liabilities.get('credit_card', 0))
        other_liab = float(liabilities.get('other', 0))

        total_liabilities = home_loan + vehicle_loan + personal_loan + credit_card + other_liab
        net_worth = total_assets - total_liabilities

        # Ratios
        solvency_ratio = (net_worth / total_assets * 100) if total_assets > 0 else 0
        debt_to_asset = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
        liquidity_ratio = (liquid_assets / total_liabilities) if total_liabilities > 0 else float('inf')
        months_runway = (liquid_assets / monthly_income) if monthly_income > 0 else 0

        # Score (0-100)
        score = 50
        if net_worth > 0:
            score += min(20, net_worth / (monthly_income * 12) * 5) if monthly_income > 0 else 10
        else:
            score -= 20
        if solvency_ratio > 60:
            score += 10
        if liquidity_ratio > 1:
            score += 10
        if months_runway >= 6:
            score += 10
        score = max(0, min(100, int(score)))

        # Insights
        insights = []
        if net_worth < 0:
            insights.append({'type': 'critical', 'text': f'Negative net worth (Ksh {net_worth:,.0f}). Focus on debt reduction urgently.'})
        elif net_worth > 0:
            insights.append({'type': 'success', 'text': f'Positive net worth of Ksh {net_worth:,.0f}. You\'re on the right track!'})
        if debt_to_asset > 50:
            insights.append({'type': 'warning', 'text': f'Debt-to-asset ratio is {debt_to_asset:.0f}% — aim for under 40%.'})
        if months_runway < 3:
            insights.append({'type': 'warning', 'text': f'Only {months_runway:.1f} months of liquid runway. Build to 6+ months.'})
        if credit_card > 0:
            insights.append({'type': 'critical', 'text': 'Outstanding credit-card debt carries 24-40% interest. Prioritize paying it off.'})
        if liquidity_ratio > 2:
            insights.append({'type': 'success', 'text': 'Strong liquidity position — your liquid assets comfortably cover debts.'})

        return {
            'total_assets': round(total_assets, 2),
            'total_liabilities': round(total_liabilities, 2),
            'net_worth': round(net_worth, 2),
            'liquid_assets': round(liquid_assets, 2),
            'solvency_ratio': round(solvency_ratio, 1),
            'debt_to_asset': round(debt_to_asset, 1),
            'liquidity_ratio': round(min(liquidity_ratio, 999), 2),
            'months_runway': round(months_runway, 1),
            'valuation_score': score,
            'insights': insights,
            'asset_breakdown': {
                'Cash & Savings': cash, 'Investments': investments,
                'Property': property_val, 'Vehicles': vehicles,
                'Gold & Jewelry': gold, 'Other': other_assets,
            },
            'liability_breakdown': {
                'Home Loan': home_loan, 'Vehicle Loan': vehicle_loan,
                'Personal Loan': personal_loan, 'Credit Card': credit_card,
                'Other': other_liab,
            },
        }

    # ── 3. Integrated Impact on Pricing & Decisions ──────────────────────
    def decision_impact(self, data):
        """Simulate the financial impact of a proposed decision (e.g. taking
        a loan, making an investment, quitting a job) on the user's overall
        balance sheet and cash-flow."""

        decision_type = data.get('decision_type', 'loan')  # loan | investment | expense
        amount = float(data.get('amount', 0))
        monthly_income = float(data.get('monthly_income', 0))
        monthly_expenses = float(data.get('monthly_expenses', 0))
        current_savings = float(data.get('current_savings', 0))
        current_debt = float(data.get('current_debt', 0))
        interest_rate = float(data.get('interest_rate', 10))
        tenure_months = max(1, int(data.get('tenure_months', 12)))

        before = {
            'monthly_surplus': monthly_income - monthly_expenses,
            'savings': current_savings,
            'debt': current_debt,
            'net_position': current_savings - current_debt,
            'debt_to_income': (current_debt / (monthly_income * 12) * 100) if monthly_income else 0,
        }

        after = dict(before)
        timeline = []
        monthly_impact = 0

        if decision_type == 'loan':
            r = interest_rate / 12 / 100
            if r > 0:
                emi = amount * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
            else:
                emi = amount / tenure_months
            total_repay = emi * tenure_months
            total_interest = total_repay - amount
            monthly_impact = -emi

            after['debt'] = current_debt + amount
            after['monthly_surplus'] = before['monthly_surplus'] - emi
            after['net_position'] = after['savings'] - after['debt']
            after['debt_to_income'] = (after['debt'] / (monthly_income * 12) * 100) if monthly_income else 0

            # Month-by-month projection
            bal = amount
            for m in range(1, min(tenure_months + 1, 25)):
                interest_part = bal * r
                principal_part = emi - interest_part
                bal -= principal_part
                timeline.append({
                    'month': m,
                    'emi': round(emi, 2),
                    'principal': round(principal_part, 2),
                    'interest': round(interest_part, 2),
                    'balance': round(max(0, bal), 2),
                })

        elif decision_type == 'investment':
            monthly_return = amount * (interest_rate / 100 / 12)
            monthly_impact = monthly_return

            after['savings'] = current_savings - amount
            after['monthly_surplus'] = before['monthly_surplus'] + monthly_return
            after['net_position'] = after['savings'] - after['debt']

            acc = amount
            for m in range(1, min(tenure_months + 1, 25)):
                acc *= (1 + interest_rate / 100 / 12)
                timeline.append({
                    'month': m,
                    'value': round(acc, 2),
                    'returns': round(acc - amount, 2),
                })

        elif decision_type == 'expense':
            monthly_impact = -amount / tenure_months if tenure_months > 0 else -amount

            after['savings'] = current_savings - amount
            after['monthly_surplus'] = before['monthly_surplus'] + monthly_impact
            after['net_position'] = after['savings'] - after['debt']

        # Impact assessment
        impact_score = 50  # neutral
        risk_indicatoKsh = []

        surplus_change = after['monthly_surplus'] - before['monthly_surplus']
        if surplus_change < 0:
            impact_score -= min(30, abs(surplus_change) / (monthly_income or 1) * 100)
        else:
            impact_score += min(20, surplus_change / (monthly_income or 1) * 100)

        if after['monthly_surplus'] < 0:
            risk_indicators.append({'type': 'critical', 'text': 'This decision will make your monthly expenses exceed income!'})
            impact_score -= 20
        if after['debt_to_income'] > 50:
            risk_indicators.append({'type': 'warning', 'text': f'Debt-to-income will rise to {after["debt_to_income"]:.0f}% — above safe levels.'})
            impact_score -= 10
        if after['savings'] < monthly_expenses * 3:
            risk_indicators.append({'type': 'warning', 'text': 'Savings will drop below 3-month emergency-fund level.'})
            impact_score -= 10
        if after['monthly_surplus'] > before['monthly_surplus']:
            risk_indicators.append({'type': 'success', 'text': 'This decision improves your monthly cash flow!'})
        if impact_score >= 60:
            risk_indicators.append({'type': 'success', 'text': 'Overall low-risk decision — proceed with confidence.'})

        impact_score = max(0, min(100, int(impact_score)))
        verdict = 'Recommended' if impact_score >= 60 else 'Proceed with Caution' if impact_score >= 40 else 'High Risk'

        return {
            'before': {k: round(v, 2) for k, v in before.items()},
            'after': {k: round(v, 2) for k, v in after.items()},
            'monthly_impact': round(monthly_impact, 2),
            'impact_score': impact_score,
            'verdict': verdict,
            'risk_indicators': risk_indicators,
            'timeline': timeline,
            'decision_type': decision_type,
        }
