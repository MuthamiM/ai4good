/* 
   Fin AI — Main JavaScript
   Handles all page interactions, API calls, charting, and animations.
    */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initScrollAnimations();
  initDashboard();
  initBudget();
  initLoans();
  initSavings();
  initChat();
  initAnalytics();
});

//  HelpeKsh 
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);
const fmt = (n) => 'Ksh ' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });

async function api(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

function setRing(circleEl, valueEl, pct, label) {
  if (!circleEl) return;
  const circumference = 2 * Math.PI * 52; // r=52
  const offset = circumference - (Math.min(pct, 100) / 100) * circumference;
  circleEl.style.strokeDasharray = circumference;
  circleEl.style.strokeDashoffset = offset;
  if (valueEl) valueEl.textContent = label !== undefined ? label : Math.round(pct);
}

const CHART_COLOKsh = ['#6C63FF', '#00D9FF', '#FF6B9D', '#4ECB71', '#FFB74D', '#FF6B6B', '#9B59B6', '#1ABC9C', '#E74C3C', '#F39C12'];
const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#aaa', font: { family: 'Inter', size: 11 }, padding: 12 } },
  },
  scales: {
    x: { ticks: { color: '#666' }, grid: { color: 'rgba(255,255,255,0.04)' } },
    y: { ticks: { color: '#666' }, grid: { color: 'rgba(255,255,255,0.04)' } },
  },
};

function buildRecItem(rec) {
  const icon = { critical: '', warning: '🟠', success: '🟢', info: '' }[rec.type] || '';
  let html = `<div class="rec-item ${rec.type || ''}"><span class="rec-icon">${icon}</span><div class="rec-text">`;
  if (rec.category) html += `<strong>${rec.category}</strong>`;
  html += `<p>${rec.message || rec.text || rec}</p>`;
  if (rec.saving_potential > 0) html += `<span class="rec-saving">Potential saving: ${fmt(rec.saving_potential)}</span>`;
  html += '</div></div>';
  return html;
}

//  Navbar 
function initNavbar() {
  const toggle = $('#navToggle');
  const links = $('#navLinks');
  if (toggle) toggle.addEventListener('click', () => links.classList.toggle('open'));
  window.addEventListener('scroll', () => {
    const nav = $('#navbar');
    if (nav) nav.classList.toggle('scrolled', window.scrollY > 50);
  });
}

//  Scroll Animations 
function initScrollAnimations() {
  const observer = new IntersectionObserver(
    (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); }),
    { threshold: 0.1 }
  );
  $$('.animate-on-scroll').forEach((el) => observer.observe(el));
}

// 
// DASHBOARD (Tracker-style)
// 

// Demo monthly data (12 months) with slight randomisation
const DEMO_MONTHS = ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025', 'Jun 2025',
  'Jul 2025', 'Aug 2025', 'Sep 2025', 'Oct 2025', 'Nov 2025', 'Dec 2025'];
const DEMO_CATS = ['Housing', 'Utilities', 'Groceries', 'Transport', 'Health', 'Entertain', 'Dining', 'Shopping', 'Other'];
const BASE_VALS = [8000, 2000, 5000, 2000, 1000, 1500, 2000, 1500, 1000];

function genDemoData() {
  return DEMO_MONTHS.map(() =>
    BASE_VALS.map((v) => Math.round(v * (0.85 + Math.random() * 0.3)))
  );
}

function initDashboard() {
  const btn = $('#analyzeBtn');
  if (!btn) return;

  // Generate demo table on load
  const data = genDemoData();
  renderTrackerTable(data);
  runDashboardAnalysis();

  btn.addEventListener('click', () => runDashboardAnalysis());
}

function renderTrackerTable(data) {
  const tbody = $('#trackerBody');
  if (!tbody) return;
  const avgRow = $('#trackerAvg');

  let colTotals = new Array(DEMO_CATS.length).fill(0);
  let html = '';

  data.forEach((row, i) => {
    const total = row.reduce((s, v) => s + v, 0);
    html += `<tr><td>${DEMO_MONTHS[i]}</td>`;
    row.forEach((v, j) => { html += `<td>Ksh ${v.toLocaleString('en-IN')}</td>`; colTotals[j] += v; });
    html += `<td>Ksh ${total.toLocaleString('en-IN')}</td></tr>`;
  });
  tbody.innerHTML = html;

  // Averages footer
  let avgHtml = '<td><strong>Average</strong></td>';
  colTotals.forEach((t) => { avgHtml += `<td>Ksh ${Math.round(t / 12).toLocaleString('en-IN')}</td>`; });
  avgHtml += `<td>Ksh ${Math.round(colTotals.reduce((s, v) => s + v, 0) / 12).toLocaleString('en-IN')}</td>`;
  avgRow.innerHTML = avgHtml;
}

async function runDashboardAnalysis() {
  const data = {
    income: +(document.getElementById('ti-income')?.value || 30000),
    expenses: {
      housing: +(document.getElementById('ti-housing')?.value || 0),
      utilities: +(document.getElementById('ti-utilities')?.value || 0),
      groceries: +(document.getElementById('ti-groceries')?.value || 0),
      transportation: +(document.getElementById('ti-transport')?.value || 0),
      healthcare: +(document.getElementById('ti-healthcare')?.value || 0),
      entertainment: +(document.getElementById('ti-entertainment')?.value || 0),
      dining_out: +(document.getElementById('ti-dining')?.value || 0),
      shopping: +(document.getElementById('ti-shopping')?.value || 0),
      savings: +(document.getElementById('ti-savings')?.value || 0),
      debt_payment: +(document.getElementById('ti-debt')?.value || 0),
      insurance: +(document.getElementById('ti-insurance')?.value || 0),
    },
  };

  const r = await api('/api/budget/analyze', data);
  if (r.error) return;

  // Top metrics
  if ($('#tmIncome')) $('#tmIncome').textContent = fmt(r.income);
  if ($('#tmExpenses')) $('#tmExpenses').textContent = fmt(r.total_expenses);
  if ($('#tmSavings')) $('#tmSavings').textContent = fmt(r.remaining);
  if ($('#tmHealth')) $('#tmHealth').textContent = r.health_score + '/100';
  if ($('#tmSaveRate')) {
    const sr = r.budget_data.savings.percentage;
    $('#tmSaveRate').textContent = sr + '%';
  }

  // Category donut
  const catLabels = Object.keys(r.expense_breakdown).map((l) => l.replace(/_/g, ' '));
  const catValues = Object.values(r.expense_breakdown);
  const ctx1 = $('#catDonut');
  if (ctx1) {
    if (ctx1._chart) ctx1._chart.destroy();
    ctx1._chart = new Chart(ctx1, {
      type: 'doughnut',
      data: { labels: catLabels, datasets: [{ data: catValues, backgroundColor: ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#1abc9c', '#3498db', '#9b59b6', '#e91e63', '#00bcd4', '#ff5722', '#607d8b'], borderWidth: 0 }] },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '60%',
        plugins: { legend: { position: 'right', labels: { color: '#aaa', font: { family: 'Inter', size: 11 }, padding: 8 } } }
      },
    });
  }

  // Monthly trend bar
  const ctx2 = $('#monthBar');
  if (ctx2) {
    if (ctx2._chart) ctx2._chart.destroy();
    const monthTotals = DEMO_MONTHS.map(() => Math.round(r.total_expenses * (0.9 + Math.random() * 0.2)));
    ctx2._chart = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: DEMO_MONTHS.map((m) => m.slice(0, 3)),
        datasets: [{ label: 'Expenses', data: monthTotals, backgroundColor: '#6C63FF', borderRadius: 6 }],
      },
      options: { ...chartDefaults },
    });
  }

  // 50/30/20 rule chart
  const ctx3 = $('#ruleChart');
  if (ctx3) {
    if (ctx3._chart) ctx3._chart.destroy();
    const bd = r.budget_data;
    ctx3._chart = new Chart(ctx3, {
      type: 'bar',
      data: {
        labels: ['Needs', 'Wants', 'Savings'],
        datasets: [
          { label: 'Actual %', data: [bd.needs.percentage, bd.wants.percentage, bd.savings.percentage], backgroundColor: ['#e74c3c', '#3498db', '#2ecc71'], borderRadius: 6 },
          { label: 'Ideal %', data: [50, 30, 20], backgroundColor: ['rgba(231,76,60,0.2)', 'rgba(52,152,219,0.2)', 'rgba(46,204,113,0.2)'], borderRadius: 6 },
        ],
      },
      options: { ...chartDefaults },
    });
  }

  // Health gauge
  setRing($('#dashHealthCircle'), null, r.health_score);
  if ($('#dashHealthVal')) $('#dashHealthVal').textContent = r.health_score;

  // Recommendations
  if ($('#dashRecs') && r.recommendations.length) {
    $('#dashRecs').innerHTML = r.recommendations.map(buildRecItem).join('');
  }
}

// 
// BUDGET PLANNER
// 
function initBudget() {
  const form = $('#budgetForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      income: +$('#bIncome').value,
      expenses: {
        housing: +$('#bHousing').value, utilities: +$('#bUtilities').value,
        groceries: +$('#bGroceries').value, transportation: +$('#bTransport').value,
        insurance: +$('#bInsurance').value, healthcare: +$('#bHealthcare').value,
        entertainment: +$('#bEntertain').value, dining_out: +$('#bDining').value,
        shopping: +$('#bShopping').value, subscriptions: +$('#bSubscriptions').value,
        savings: +$('#bSavings').value, debt_payment: +$('#bDebt').value,
      },
    };

    const r = await api('/api/budget/analyze', data);
    if (r.error) return alert(r.error);

    $('#budgetResults').classList.remove('hidden');

    // Metrics
    setRing($('#healthCircle'), $('#healthScore'), r.health_score);
    $('#metricRemaining').textContent = fmt(r.remaining);
    $('#metricRisk').textContent = r.risk_level.toUpperCase();
    $('#metricRisk').style.color = { low: '#4ECB71', medium: '#FFB74D', high: '#FF6B6B' }[r.risk_level] || '#fff';
    const saveRate = r.budget_data.savings.percentage;
    $('#metricSaveRate').textContent = saveRate + '%';
    $('#metricSaveRate').style.color = saveRate >= 20 ? '#4ECB71' : saveRate >= 10 ? '#FFB74D' : '#FF6B6B';

    // Charts
    renderBudgetCharts(r);

    // Recommendations
    $('#budgetRecs').innerHTML = r.recommendations.map(buildRecItem).join('');

    // Optimized budget
    const og = $('#optimizedBudget');
    const bd = r.budget_data;
    const opt = r.optimized_budget;
    og.innerHTML = ['needs', 'wants', 'savings'].map((k) => {
      const label = k.charAt(0).toUpperCase() + k.slice(1);
      const actual = bd[k].amount;
      const ideal = opt[k];
      const diff = ideal - actual;
      return `<div class="optimized-item">
        <div class="opt-label">${label}</div>
        <div class="opt-value">${fmt(ideal)}</div>
        <div class="opt-diff ${diff >= 0 ? 'positive' : 'negative'}">${diff >= 0 ? '↑' : '↓'} ${fmt(Math.abs(diff))} vs current</div>
      </div>`;
    }).join('');

    // Scroll to results
    $('#budgetResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function renderBudgetCharts(r) {
  const labels = Object.keys(r.expense_breakdown).map((l) => l.replace(/_/g, ' '));
  const values = Object.values(r.expense_breakdown);

  const ctx1 = $('#budgetDonut');
  if (ctx1) {
    if (ctx1._chart) ctx1._chart.destroy();
    ctx1._chart = new Chart(ctx1, {
      type: 'doughnut',
      data: { labels, datasets: [{ data: values, backgroundColor: CHART_COLORS, borderWidth: 0 }] },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '65%',
        plugins: { legend: { position: 'right', labels: { color: '#aaa', font: { family: 'Inter', size: 11 }, padding: 8 } } }
      },
    });
  }

  const ctx2 = $('#budgetBar');
  if (ctx2) {
    if (ctx2._chart) ctx2._chart.destroy();
    const bd = r.budget_data;
    ctx2._chart = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: ['Needs', 'Wants', 'Savings'],
        datasets: [
          { label: 'Actual %', data: [bd.needs.percentage, bd.wants.percentage, bd.savings.percentage], backgroundColor: ['#6C63FF', '#FF6B9D', '#4ECB71'], borderRadius: 6 },
          { label: 'Ideal %', data: [50, 30, 20], backgroundColor: ['rgba(108,99,255,0.2)', 'rgba(255,107,157,0.2)', 'rgba(78,203,113,0.2)'], borderRadius: 6 },
        ],
      },
      options: { ...chartDefaults },
    });
  }
}

// 
// LOANS
// 
function initLoans() {
  const form = $('#loanForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      monthly_income: +$('#lIncome').value,
      monthly_expenses: +$('#lExpenses').value,
      existing_debt: +$('#lDebt').value,
      savings: +$('#lSavings').value,
      employment_months: +$('#lEmployment').value,
      dependents: +$('#lDependents').value,
      has_bank_account: $('#lBank').checked,
      requested_amount: +$('#lAmount').value,
    };

    const r = await api('/api/loan/check', data);

    $('#loanResults').classList.remove('hidden');

    // Metrics
    setRing($('#loanCircle'), null, r.score);
    $('#loanScore').textContent = r.score;
    $('#loanVerdict').textContent = r.verdict;
    $('#loanVerdict').style.color = { Excellent: '#4ECB71', Good: '#00D9FF', Fair: '#FFB74D', 'Needs Improvement': '#FF6B6B' }[r.verdict] || '#fff';
    $('#loanRisk').textContent = r.risk_level.toUpperCase();
    $('#loanSafeEmi').textContent = fmt(r.safe_emi);

    // Score factors
    $('#loanFactors').innerHTML = r.factors.map((f) => `
      <div class="factor-item">
        <span class="factor-name">${f.name}</span>
        <div class="factor-bar-bg"><div class="factor-bar" style="width:${(f.score / f.max * 100)}%"></div></div>
        <span class="factor-score">${f.score}/${f.max}</span>
      </div>`).join('');

    // Countries
    if (r.eligible_countries && r.eligible_countries.length) {
      $('#loanCountries').innerHTML = r.eligible_countries.map(c =>
        `<span class="product-tag" style="font-size: 1.05rem; padding: 0.6rem 1.2rem; background: rgba(108,99,255,0.1); border: 1px solid rgba(108,99,255,0.2);"><i class="fas fa-map-marker-alt" style="color:var(--accent-purple); margin-right: 6px;"></i> <strong>${c}</strong></span>`
      ).join('');
    } else {
      $('#loanCountries').innerHTML = '<span class="text-muted">No countries currently qualified.</span>';
    }

    // Products
    $('#loanProducts').innerHTML = r.eligible_products.length
      ? r.eligible_products.map((p) => `
          <div class="product-card">
            <h4>${p.name}</h4>
            <p>${p.description}</p>
            <div class="product-meta">
              <span class="product-tag">Rate: ${p.interest_rate}%</span>
              <span class="product-tag">Max: ${fmt(p.max_eligible_amount)}</span>
              <span class="product-tag">EMI: ${fmt(p.monthly_emi)}/mo</span>
              <span class="product-tag ${p.affordable ? 'affordable' : 'not-affordable'}">${p.affordable ? ' Affordable' : ' Tight'}</span>
            </div>
          </div>`).join('')
      : '<p style="color:var(--text-muted)">No products match your current profile. Follow the tips below to improve.</p>';

    // Tips
    $('#loanTips').innerHTML = r.improvement_tips.map((t) => buildRecItem({ type: 'info', message: t })).join('');

    $('#loanResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

// 
// SAVINGS
// 
function initSavings() {
  const form = $('#savingsForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const risk = document.querySelector('input[name="risk"]:checked')?.value || 'moderate';
    const data = {
      goal_name: $('#sGoal').value || 'My Goal',
      target_amount: +$('#sTarget').value,
      current_savings: +$('#sCurrent').value,
      target_months: +$('#sMonths').value,
      monthly_income: +$('#sIncome').value,
      monthly_expenses: +$('#sExpenses').value,
      risk_tolerance: risk,
    };

    const r = await api('/api/savings/plan', data);

    $('#savingsResults').classList.remove('hidden');

    // Metrics
    setRing($('#savingsCircle'), null, r.progress);
    $('#savingsProgress').textContent = r.progress + '%';
    $('#savingsRequired').textContent = fmt(r.monthly_required);
    $('#savingsRemaining').textContent = fmt(r.remaining);
    const feasEl = $('#savingsFeasible');
    feasEl.textContent = r.feasible ? ' Feasible' : ' Stretch';
    feasEl.style.color = r.feasible ? '#4ECB71' : '#FF6B6B';

    // Growth chart
    renderGrowthChart(r);

    // Strategies
    $('#strategyGrid').innerHTML = r.strategies.map((s) => `
      <div class="strategy-card">
        <h4>${s.name}</h4>
        <div class="strategy-alloc">${s.allocation}%</div>
        <p>${s.description}</p>
        <div class="strategy-meta">
          <span>Return: ${s.expected_return}</span>
          <span>Risk: ${s.risk}</span>
        </div>
      </div>`).join('');

    // Milestones
    $('#milestones').innerHTML = r.milestones.map((m) => `
      <div class="milestone">
        <div class="milestone-month">Month ${m.month}</div>
        <div class="milestone-amount">${fmt(m.amount)}</div>
        <div class="milestone-bar"><div class="milestone-bar-fill" style="width:${m.percentage}%"></div></div>
      </div>`).join('');

    // Tips
    $('#savingsTips').innerHTML = r.tips.map((t) => buildRecItem({ type: 'info', message: t })).join('');

    $('#savingsResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function renderGrowthChart(r) {
  const ctx = $('#growthChart');
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  const labels = r.milestones.map((m) => 'M' + m.month);
  const target = r.milestones.map(() => r.target_amount);
  const actual = r.milestones.map((m) => m.amount);

  ctx._chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Projected Savings', data: actual, borderColor: '#6C63FF', backgroundColor: 'rgba(108,99,255,0.1)', fill: true, tension: 0.3, pointRadius: 4 },
        { label: 'Target', data: target, borderColor: '#FF6B6B', borderDash: [6, 4], pointRadius: 0, fill: false },
      ],
    },
    options: { ...chartDefaults },
  });
}

// 
// CHATBOT
// 
function initChat() {
  const form = $('#chatForm');
  if (!form) return;

  let msgCount = 0;
  const topicsSet = new Set();

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    // User bubble
    appendMsg('user', message);
    msgCount++;
    if ($('#msgCount')) $('#msgCount').textContent = msgCount;

    // Typing indicator
    const typing = appendMsg('bot', '<span class="spinner"></span> Thinking…');

    const r = await api('/api/chat', { message });

    // Replace typing with response
    typing.querySelector('.chat-bubble').innerHTML = formatResponse(r.response);
    if (r.category && r.category !== 'general') topicsSet.add(r.category);
    if ($('#topicCount')) $('#topicCount').textContent = topicsSet.size;

    // Update quick replies
    if (r.quick_replies) {
      const qr = $('#quickReplies');
      qr.innerHTML = r.quick_replies.map((q) => `<button class="quick-reply" data-msg="${q}">${q}</button>`).join('');
      qr.querySelectorAll('.quick-reply').forEach((btn) => btn.addEventListener('click', () => sendMessage(btn.dataset.msg)));
    }
  };

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = $('#chatInput');
    sendMessage(input.value);
    input.value = '';
  });

  $$('.quick-reply').forEach((btn) => btn.addEventListener('click', () => sendMessage(btn.dataset.msg)));

  function appendMsg(who, html) {
    const div = document.createElement('div');
    div.className = `chat-msg ${who}`;
    div.innerHTML = `<div class="chat-avatar"><i class="fas fa-${who === 'bot' ? 'robot' : 'user'}"></i></div><div class="chat-bubble">${html}</div>`;
    const msgs = $('#chatMessages');
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
  }

  function formatResponse(text) {
    return text.replace(/\n/g, '<br>').replace(/•/g, '<br>•');
  }
}

// 
// ANALYTICS (Risk, Balance Sheet, Decision Impact)
// 
function initAnalytics() {
  // Tab switching
  $$('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      $$('.tab-btn').forEach((b) => b.classList.remove('active'));
      $$('.tab-panel').forEach((p) => p.classList.remove('active'));
      btn.classList.add('active');
      const panel = $('#tab-' + btn.dataset.tab);
      if (panel) {
        panel.classList.add('active');
        // Re-trigger scroll animations
        panel.querySelectorAll('.animate-on-scroll').forEach((el) => {
          el.classList.remove('visible');
          setTimeout(() => el.classList.add('visible'), 50);
        });
      }
    });
  });

  initFixedIncome();
  initBalanceSheet();
  initDecisionImpact();
}

//  Fixed Income 
function initFixedIncome() {
  const addBtn = $('#addHolding');
  const analyzeBtn = $('#analyzeFixedIncome');
  if (!addBtn) return;

  addBtn.addEventListener('click', () => {
    const row = document.createElement('div');
    row.className = 'holding-row form-grid-2';
    row.innerHTML = `
      <div class="form-group"><label>Name</label><input type="text" class="h-name" placeholder="e.g. HDFC FD" /></div>
      <div class="form-group"><label>Principal (Ksh )</label><input type="number" class="h-principal" placeholder="50000" /></div>
      <div class="form-group"><label>Interest Rate (%)</label><input type="number" class="h-rate" placeholder="7" step="0.1" /></div>
      <div class="form-group"><label>Tenure (years)</label><input type="number" class="h-tenure" placeholder="3" step="0.5" /></div>`;
    $('#holdingsList').appendChild(row);
  });

  analyzeBtn.addEventListener('click', async () => {
    const rows = $$('.holding-row');
    const holdings = [];
    rows.forEach((row) => {
      const name = row.querySelector('.h-name')?.value;
      const principal = +row.querySelector('.h-principal')?.value;
      const rate = +row.querySelector('.h-rate')?.value;
      const tenure = +row.querySelector('.h-tenure')?.value;
      if (principal > 0) holdings.push({ name: name || 'Unnamed', principal, rate, tenure_years: tenure });
    });

    if (!holdings.length) return alert('Add at least one holding.');
    const r = await api('/api/risk/fixed-income', { holdings });
    if (r.error) return alert(r.error);

    $('#fiResults').classList.remove('hidden');
    setRing($('#fiRiskCircle'), null, r.risk_score);
    $('#fiRiskScore').textContent = r.risk_score;
    $('#fiTotal').textContent = fmt(r.total_invested);
    $('#fiReturn').textContent = fmt(r.portfolio_return);
    $('#fiAvgRate').textContent = r.avg_rate + '%';

    // Table
    const tbody = $('#fiTable tbody');
    tbody.innerHTML = r.holdings.map((h) => `<tr>
      <td>${h.name}</td><td>${fmt(h.principal)}</td><td>${h.rate}%</td>
      <td>${h.macaulay_duration}y</td><td>${fmt(h.price_sensitivity)}/1%</td>
      <td>${fmt(h.maturity_value)}</td></tr>`).join('');

    // Recs
    $('#fiRecs').innerHTML = r.recommendations.map((t) => buildRecItem({ type: 'info', message: t })).join('');

    $('#fiResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

//  Balance Sheet 
function initBalanceSheet() {
  const form = $('#bsForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      assets: {
        cash_savings: +$('#bsCash').value,
        investments: +$('#bsInvest').value,
        property: +$('#bsProperty').value,
        vehicles: +$('#bsVehicles').value,
        gold_jewelry: +$('#bsGold').value,
        other: +$('#bsOtherA').value,
      },
      liabilities: {
        home_loan: +$('#bsHomeLoan').value,
        vehicle_loan: +$('#bsVehicleLoan').value,
        personal_loan: +$('#bsPersonalLoan').value,
        credit_card: +$('#bsCreditCard').value,
        other: +$('#bsOtherL').value,
      },
      monthly_income: +$('#bsIncome').value,
    };

    const r = await api('/api/risk/balance-sheet', data);
    $('#bsResults').classList.remove('hidden');

    setRing($('#bsScoreCircle'), null, r.valuation_score);
    $('#bsScore').textContent = r.valuation_score;
    $('#bsNetWorth').textContent = fmt(r.net_worth);
    $('#bsNetWorth').style.color = r.net_worth >= 0 ? '#4ECB71' : '#FF6B6B';
    $('#bsSolvency').textContent = r.solvency_ratio + '%';
    $('#bsRunway').textContent = r.months_runway + ' mo';

    // Asset pie
    renderPie('assetChart', r.asset_breakdown);
    renderPie('liabilityChart', r.liability_breakdown);

    // Insights
    $('#bsInsights').innerHTML = r.insights.map(buildRecItem).join('');
    $('#bsResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function renderPie(canvasId, dataObj) {
  const ctx = $('#' + canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();
  const entries = Object.entries(dataObj).filter(([, v]) => v > 0);
  ctx._chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: entries.map(([k]) => k),
      datasets: [{ data: entries.map(([, v]) => v), backgroundColor: CHART_COLORS, borderWidth: 0 }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '60%',
      plugins: { legend: { position: 'right', labels: { color: '#aaa', font: { family: 'Inter', size: 11 }, padding: 8 } } }
    },
  });
}

//  Decision Impact 
function initDecisionImpact() {
  const form = $('#diForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const decisionType = document.querySelector('input[name="diType"]:checked')?.value || 'loan';
    const data = {
      decision_type: decisionType,
      amount: +$('#diAmount').value,
      interest_rate: +$('#diRate').value,
      tenure_months: +$('#diTenure').value,
      monthly_income: +$('#diIncome').value,
      monthly_expenses: +$('#diExpenses').value,
      current_savings: +$('#diSavings').value,
      current_debt: +$('#diDebt').value,
    };

    const r = await api('/api/risk/decision-impact', data);
    $('#diResults').classList.remove('hidden');

    setRing($('#diScoreCircle'), null, r.impact_score);
    $('#diScore').textContent = r.impact_score;
    const verdictEl = $('#diVerdict');
    verdictEl.textContent = r.verdict;
    verdictEl.style.color = { Recommended: '#4ECB71', 'Proceed with Caution': '#FFB74D', 'High Risk': '#FF6B6B' }[r.verdict] || '#fff';
    $('#diMonthly').textContent = (r.monthly_impact >= 0 ? '+' : '') + fmt(r.monthly_impact);
    $('#diMonthly').style.color = r.monthly_impact >= 0 ? '#4ECB71' : '#FF6B6B';
    $('#diSurplus').textContent = fmt(r.after.monthly_surplus);
    $('#diSurplus').style.color = r.after.monthly_surplus >= 0 ? '#4ECB71' : '#FF6B6B';

    // Before vs After bar chart
    renderBeforeAfter(r);
    renderTimeline(r);

    // Risk indicators
    $('#diRisks').innerHTML = r.risk_indicators.map(buildRecItem).join('');
    $('#diResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function renderBeforeAfter(r) {
  const ctx = $('#beforeAfterChart');
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();

  ctx._chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Monthly Surplus', 'Savings', 'Debt'],
      datasets: [
        { label: 'Before', data: [r.before.monthly_surplus, r.before.savings, r.before.debt], backgroundColor: 'rgba(108,99,255,0.6)', borderRadius: 6 },
        { label: 'After', data: [r.after.monthly_surplus, r.after.savings, r.after.debt], backgroundColor: 'rgba(0,217,255,0.6)', borderRadius: 6 },
      ],
    },
    options: { ...chartDefaults },
  });
}

function renderTimeline(r) {
  const ctx = $('#timelineChart');
  if (!ctx || !r.timeline.length) return;
  if (ctx._chart) ctx._chart.destroy();

  const labels = r.timeline.map((t) => 'M' + t.month);
  let dataset;

  if (r.decision_type === 'loan') {
    dataset = [
      { label: 'Remaining Balance', data: r.timeline.map((t) => t.balance), borderColor: '#FF6B6B', fill: false, tension: 0.3 },
      { label: 'Principal Paid', data: r.timeline.map((t) => t.principal), borderColor: '#4ECB71', fill: false, tension: 0.3 },
    ];
  } else if (r.decision_type === 'investment') {
    dataset = [
      { label: 'Portfolio Value', data: r.timeline.map((t) => t.value), borderColor: '#4ECB71', backgroundColor: 'rgba(78,203,113,0.1)', fill: true, tension: 0.3 },
    ];
  } else {
    return; // no timeline for plain expense
  }

  ctx._chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: dataset },
    options: { ...chartDefaults },
  });
}
