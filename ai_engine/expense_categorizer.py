"""
Fin AI – Expense Categorizer
Keyword-based AI categorizer that classifies transactions,
computes totals per category, and generates spending insights.
"""


class ExpenseCategorizer:

    CATEGORIES = {
        'housing':        ['rent', 'mortgage', 'property', 'house', 'apartment', 'flat', 'home loan'],
        'utilities':      ['electricity', 'water', 'gas', 'internet', 'wifi', 'phone', 'mobile', 'broadband', 'bill'],
        'groceries':      ['grocery', 'food', 'vegetables', 'fruits', 'supermarket', 'kirana', 'ration'],
        'transportation': ['fuel', 'petrol', 'diesel', 'bus', 'train', 'metro', 'uber', 'ola', 'auto', 'cab', 'taxi'],
        'healthcare':     ['medicine', 'doctor', 'hospital', 'pharmacy', 'medical', 'health', 'clinic', 'dental'],
        'insurance':      ['insurance', 'premium', 'lic', 'policy'],
        'entertainment':  ['movie', 'netflix', 'spotify', 'games', 'concert', 'theatre', 'streaming'],
        'dining_out':     ['restaurant', 'cafe', 'coffee', 'zomato', 'swiggy', 'dining', 'pizza', 'burger'],
        'shopping':       ['clothes', 'shoes', 'amazon', 'flipkart', 'shopping', 'mall', 'fashion'],
        'education':      ['school', 'college', 'tuition', 'course', 'books', 'training', 'fees'],
        'savings':        ['savings', 'fixed deposit', 'fd', 'rd', 'mutual fund', 'sip', 'investment'],
        'debt_payment':   ['loan', 'emi', 'credit card', 'repayment', 'installment'],
    }

    ICONS = {
        'housing': '', 'utilities': '', 'groceries': '',
        'transportation': '', 'healthcare': '', 'insurance': '',
        'entertainment': '', 'dining_out': '', 'shopping': '',
        'education': '', 'savings': '', 'debt_payment': '',
        'other': '',
    }

    def categorize(self, data):
        transactions = data.get('transactions', [])
        results = []
        totals: dict[str, float] = {}

        for txn in transactions:
            desc = txn.get('description', '')
            amount = float(txn.get('amount', 0))
            cat = self._match(desc)
            results.append({
                'description': desc,
                'amount': amount,
                'category': cat,
                'icon': self.ICONS.get(cat, ''),
            })
            totals[cat] = totals.get(cat, 0) + amount

        total = sum(float(t.get('amount', 0)) for t in transactions)

        # Insights
        insights = []
        ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)

        if ranked:
            top = ranked[0]
            insights.append(
                f'Highest spending: {top[0].replace("_", " ").title()} '
                f'at Ksh {top[1]:,.2f} ({top[1] / total * 100:.1f}%).'
            )

        dining = totals.get('dining_out', 0)
        groceries = totals.get('groceries', 0)
        if dining > groceries > 0:
            insights.append(
                f'Dining out (Ksh {dining:,.2f}) exceeds groceries (Ksh {groceries:,.2f}). '
                f'Cooking at home could save ~Ksh {(dining - groceries) * 0.5:,.2f}/month.'
            )

        discretionary = totals.get('entertainment', 0) + totals.get('shopping', 0)
        if total > 0 and discretionary / total > 0.30:
            insights.append(
                f'Discretionary spending is {discretionary / total * 100:.1f}% of total — '
                f'aim for under 30%.'
            )

        return {
            'transactions': results,
            'category_totals': totals,
            'total': total,
            'insights': insights,
            'num_transactions': len(transactions),
            'categories_found': len(totals),
        }

    def _match(self, description: str) -> str:
        desc = description.lower()
        for cat, keywords in self.CATEGORIES.items():
            if any(kw in desc for kw in keywords):
                return cat
        return 'other'
