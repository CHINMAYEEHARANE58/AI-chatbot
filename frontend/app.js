const merchants = [
  {
    id: "m_001_drmeera_dentist_delhi",
    category: "dentists",
    name: "Dr. Meera's Dental Clinic",
    owner: "Meera",
    city: "Delhi",
    locality: "Lajpat Nagar",
    verified: true,
    languages: ["en", "hi"],
    plan: "Pro",
    daysRemaining: 82,
    views: 2410,
    calls: 18,
    directions: 45,
    ctr: 2.1,
    leads: 9,
    responseRate: 64,
    engagement: 78,
    customers: "540 YTD",
    risk: "active",
    offers: ["Dental Cleaning @ ₹299", "Deep Cleaning @ ₹499 expired"],
    signals: ["stale_posts:22d", "ctr_below_peer_median", "high_risk_adult_cohort"],
    history: [
      {
        from: "vera",
        body: "Profile audit done. Your photos are 8/10, description is complete, but Google posts are stale: last post 22 days ago. Want me to draft 3 posts you can review?",
        time: "24 Apr, 10:12",
        engagement: "merchant_replied",
      },
      {
        from: "merchant",
        body: "Yes please, focus on whitening and aligners",
        time: "24 Apr, 10:18",
        engagement: "intent_action",
      },
    ],
    messages: [
      {
        from: "vera",
        body: "Dr. Meera, JIDA's Oct issue landed. One item is relevant to your 124 high-risk adult patients: a 2,100-patient trial showed 3-month fluoride recall cuts caries recurrence 38% better than 6-month. Want me to pull the abstract and draft a patient-ed WhatsApp?",
        time: "10:42",
      },
      {
        from: "merchant",
        body: "Yes, send me a short version first.",
        time: "10:45",
      },
    ],
  },
  {
    id: "m_003_studio11_salon_hyderabad",
    category: "salons",
    name: "Studio11 Family Salon",
    owner: "Lakshmi",
    city: "Hyderabad",
    locality: "Kapra",
    verified: true,
    languages: ["en", "hi", "te"],
    plan: "Pro",
    daysRemaining: 145,
    views: 4980,
    calls: 62,
    directions: 142,
    ctr: 4.8,
    leads: 38,
    responseRate: 41,
    engagement: 83,
    customers: "1,150 YTD",
    risk: "hot",
    offers: ["Haircut @ ₹99", "Hair Spa @ ₹499"],
    signals: ["high_engagement", "above_peer_median_calls", "growing_views_7d"],
    history: [
      {
        from: "vera",
        body: "Spotted: bridal-trial searches in Kapra +28% this week. Want me to push your bridal package as a GBP post?",
        time: "22 Apr, 15:00",
        engagement: "merchant_no_reply",
      },
    ],
    messages: [
      {
        from: "vera",
        body: "Lakshmi, Studio11's calls are up 20% this week and Hair Spa @ ₹499 is still active. Diwali prep is early this year. Want me to draft a Kapra bridal trial post using your Priya stylist reviews?",
        time: "12:08",
      },
    ],
  },
  {
    id: "m_005_pizzajunction_restaurant_delhi",
    category: "restaurants",
    name: "SK Pizza Junction",
    owner: "Suresh",
    city: "Delhi",
    locality: "Sant Nagar",
    verified: false,
    languages: ["en", "hi"],
    plan: "Trial",
    daysRemaining: 7,
    views: 2200,
    calls: 12,
    directions: 38,
    ctr: 2.0,
    leads: 4,
    responseRate: 36,
    engagement: 58,
    customers: "275 orders 30d",
    risk: "risk",
    offers: ["Buy 1 Pizza Get 1 Free Tue-Thu"],
    signals: ["new_merchant", "trial_ending_soon", "ipl_eligible_locality"],
    history: [
      {
        from: "vera",
        body: "Quick check: IPL match nights driving any extra footfall?",
        time: "25 Apr, 18:00",
        engagement: "merchant_no_reply",
      },
    ],
    messages: [
      {
        from: "vera",
        body: "Suresh ji, DC vs MI is at 7:30pm in Delhi today and your trial has 7 days left. Sant Nagar pizza searches usually convert fast on match nights. Want me to make a 2-line WhatsApp status for Buy 1 Pizza Get 1 Free?",
        time: "16:02",
      },
    ],
  },
  {
    id: "m_009_apollo_pharmacy_jaipur",
    category: "pharmacies",
    name: "Apollo Pharmacy",
    owner: "Nidhi",
    city: "Jaipur",
    locality: "Vaishali Nagar",
    verified: true,
    languages: ["en", "hi"],
    plan: "Pro",
    daysRemaining: 64,
    views: 8200,
    calls: 71,
    directions: 205,
    ctr: 3.4,
    leads: 58,
    responseRate: 72,
    engagement: 88,
    customers: "1,920 YTD",
    risk: "active",
    offers: ["BP Check @ ₹49", "Free home delivery above ₹499"],
    signals: ["supply_alert", "summer_demand_shift", "high_repeat_refill"],
    history: [],
    messages: [
      {
        from: "vera",
        body: "Nidhi, urgent supply alert: atorvastatin batches AT2024-1102 and AT2024-1108 from MfrZ are affected. Want me to draft a staff checklist for stock isolation and customer callbacks?",
        time: "09:18",
      },
    ],
  },
  {
    id: "m_007_powerhouse_gym_bangalore",
    category: "gyms",
    name: "PowerHouse Fitness",
    owner: "Karthik",
    city: "Bangalore",
    locality: "HSR Layout",
    verified: true,
    languages: ["en", "hi", "kn"],
    plan: "Pro",
    daysRemaining: 95,
    views: 1480,
    calls: 22,
    directions: 48,
    ctr: 5.2,
    leads: 14,
    responseRate: 49,
    engagement: 68,
    customers: "245 active",
    risk: "hot",
    offers: ["3 FREE Trial Classes"],
    signals: ["seasonal_dip_apr_may", "above_peer_ctr", "no_recent_post"],
    history: [],
    messages: [
      {
        from: "vera",
        body: "Karthik, HSR views are down 30% this week, but your CTR is still strong at 5.2%. This looks like the Apr-Jun post-resolution dip. Want me to turn 3 FREE Trial Classes into a summer comeback post?",
        time: "11:30",
      },
    ],
  },
];

const triggers = {
  m_001_drmeera_dentist_delhi: {
    kind: "research_digest",
    source: "external",
    urgency: 2,
    whyNow: "Weekly dentistry digest released; last Vera touch got a reply 2 days ago.",
    suppressionKey: "research:dentists:2026-W17",
    payload: "JIDA Oct: 2,100-patient trial, 38% better recurrence reduction for 3-month fluoride recall.",
    expires: "3 May 2026",
    scope: "merchant",
  },
  m_003_studio11_salon_hyderabad: {
    kind: "festival_upcoming",
    source: "external",
    urgency: 1,
    whyNow: "Early Diwali grooming planning is open; merchant ignored the last bridal-search nudge.",
    suppressionKey: "festival:diwali:2026:m_003",
    payload: "Diwali 2026, Kapra salon demand, active Hair Spa @ ₹499.",
    expires: "2 Nov 2026",
    scope: "merchant",
  },
  m_005_pizzajunction_restaurant_delhi: {
    kind: "ipl_match_today",
    source: "external",
    urgency: 3,
    whyNow: "DC vs MI plays in Delhi at 7:30pm today; match-night demand is time boxed.",
    suppressionKey: "ipl:m_005:2026-04-26",
    payload: "DC vs MI, Arun Jaitley Stadium, Delhi, active BOGO offer.",
    expires: "26 Apr 2026, 23:59",
    scope: "merchant",
  },
  m_009_apollo_pharmacy_jaipur: {
    kind: "supply_alert",
    source: "external",
    urgency: 5,
    whyNow: "Affected atorvastatin batches need stock isolation before more refills go out.",
    suppressionKey: "alert:atorvastatin:2026-04",
    payload: "Batches AT2024-1102 and AT2024-1108, manufacturer MfrZ.",
    expires: "30 May 2026",
    scope: "merchant",
  },
  m_007_powerhouse_gym_bangalore: {
    kind: "seasonal_perf_dip",
    source: "internal",
    urgency: 1,
    whyNow: "Views fell 30% in 7 days during the expected Apr-Jun fitness acquisition dip.",
    suppressionKey: "seasonal_dip:m_007:2026-Q2",
    payload: "7-day views -30%, CTR 5.2%, active 3 FREE Trial Classes.",
    expires: "30 Jun 2026",
    scope: "merchant",
  },
};

const customerContexts = {
  m_001_drmeera_dentist_delhi: {
    name: "Priya",
    state: "lapsed_soft",
    language: "hi-en mix",
    lastVisit: "12 May 2026",
    preference: "Weekday evening slots",
    consent: "Opted in on 4 Nov 2025",
  },
};

const categoryVoice = {
  dentists: "Clinical, technical, calm. Avoid cure, guaranteed, hype.",
  salons: "Trend-led, visual, energetic. Prefer service + price offers.",
  restaurants: "Local, timely, practical. Lean on events and cravings.",
  pharmacies: "Compliance-first, clear, non-promotional for health alerts.",
  gyms: "Motivating, direct, seasonal. Focus on trials and habit restarts.",
};

const state = {
  selectedId: merchants[0].id,
  category: "all",
  query: "",
  loading: true,
  apiReady: false,
  conversationIds: {},
  expanded: {
    stats: false,
    context: false,
  },
};

const elements = {
  body: document.body,
  search: document.querySelector("#conversation-search"),
  filters: document.querySelector("#category-filters"),
  conversations: document.querySelector("#conversation-list"),
  metrics: document.querySelector("#metrics-grid"),
  merchantCard: document.querySelector("#merchant-card"),
  triggerCard: document.querySelector("#trigger-card"),
  suggestions: document.querySelector("#suggestions-card"),
  chatTitle: document.querySelector("#chat-title"),
  statusBadge: document.querySelector("#status-badge"),
  messages: document.querySelector("#message-list"),
  typing: document.querySelector("#typing-row"),
  form: document.querySelector("#composer-form"),
  input: document.querySelector("#composer-input"),
  magicCompose: document.querySelector("#magic-compose"),
  themeToggle: document.querySelector("#theme-toggle"),
  simulateTrigger: document.querySelector("#simulate-trigger"),
  stats: document.querySelector("#stats-panel"),
  context: document.querySelector("#context-panel"),
  customer: document.querySelector("#customer-panel"),
  customerScopeBadge: document.querySelector("#customer-scope-badge"),
  history: document.querySelector("#history-panel"),
  chart: document.querySelector("#trend-chart"),
  toastHost: document.querySelector("#toast-host"),
};

function formatNumber(value) {
  return new Intl.NumberFormat("en-IN").format(value);
}

function currentMerchant() {
  return merchants.find((merchant) => merchant.id === state.selectedId) || merchants[0];
}

function currentTrigger() {
  return triggers[state.selectedId];
}

async function postJson(path, payload = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.details || data.error || `Request failed: ${response.status}`);
  }
  return data;
}

async function bootstrapBackend() {
  const data = await postJson("/v1/demo/bootstrap");
  state.apiReady = true;
  return data;
}

async function getBackendAction(merchantId) {
  const data = await postJson("/v1/demo/action", { merchant_id: merchantId });
  const action = data.action;
  if (action?.conversation_id) {
    state.conversationIds[merchantId] = action.conversation_id;
  }
  return action;
}

async function getBackendReply(merchantId, message) {
  const data = await postJson("/v1/demo/reply", {
    merchant_id: merchantId,
    conversation_id: state.conversationIds[merchantId],
    message,
  });
  if (data.conversation_id) {
    state.conversationIds[merchantId] = data.conversation_id;
  }
  return data.response;
}

function html(strings, ...values) {
  return strings.reduce((result, string, index) => {
    const value = values[index] ?? "";
    return result + string + value;
  }, "");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderFilters() {
  const categories = ["all", ...new Set(merchants.map((merchant) => merchant.category))];
  elements.filters.innerHTML = categories
    .map(
      (category) => html`
        <button class="filter-chip ${state.category === category ? "active" : ""}" type="button" data-category="${category}">
          ${category}
        </button>
      `,
    )
    .join("");
}

function filteredMerchants() {
  const query = state.query.trim().toLowerCase();
  return merchants.filter((merchant) => {
    const matchesCategory = state.category === "all" || merchant.category === state.category;
    const blob = `${merchant.name} ${merchant.city} ${merchant.locality} ${merchant.category} ${triggers[merchant.id].kind}`.toLowerCase();
    return matchesCategory && (!query || blob.includes(query));
  });
}

function renderConversations() {
  const list = filteredMerchants();
  if (!list.length) {
    elements.conversations.innerHTML = `<div class="empty-state">No conversations match this view.</div>`;
    return;
  }

  elements.conversations.innerHTML = list
    .map((merchant) => {
      const trigger = triggers[merchant.id];
      return html`
        <button class="conversation-item ${merchant.id === state.selectedId ? "active" : ""}" type="button" data-merchant="${merchant.id}">
          <div class="avatar">${escapeHtml(merchant.owner[0])}</div>
          <div class="conversation-copy">
            <strong>${escapeHtml(merchant.name)}</strong>
            <span>${escapeHtml(merchant.locality)}, ${escapeHtml(merchant.city)} · ${escapeHtml(trigger.kind)}</span>
          </div>
          <span class="mini-badge">${trigger.urgency}/5</span>
        </button>
      `;
    })
    .join("");
}

function renderMetrics() {
  const totalViews = merchants.reduce((sum, merchant) => sum + merchant.views, 0);
  const active = merchants.filter((merchant) => merchant.risk !== "risk").length;
  const avgResponse = Math.round(merchants.reduce((sum, merchant) => sum + merchant.responseRate, 0) / merchants.length);
  const avgEngagement = Math.round(merchants.reduce((sum, merchant) => sum + merchant.engagement, 0) / merchants.length);
  const metrics = [
    ["Total merchants", formatNumber(merchants.length * 20000), "+8.5%"],
    ["Active conversations", formatNumber(active * 1274), "+12.1%"],
    ["Trigger count", formatNumber(Object.keys(triggers).length * 20), "+34 today"],
    ["Response rate", `${avgResponse}%`, "+5.4%"],
    ["Engagement score", `${avgEngagement}/100`, "+7 pts"],
  ];

  elements.metrics.innerHTML = metrics
    .map(
      ([label, value, delta], index) => html`
        <article class="metric-card" style="animation-delay: ${index * 45}ms">
          <div>
            <p>${label}</p>
            <strong>${value}</strong>
          </div>
          <span>${delta}</span>
        </article>
      `,
    )
    .join("");
}

function renderMerchantCard(merchant) {
  elements.merchantCard.innerHTML = html`
    <div class="merchant-identity">
      <div class="avatar">${escapeHtml(merchant.owner[0])}</div>
      <div>
        <p class="section-label">Merchant profile</p>
        <h3>${escapeHtml(merchant.name)}</h3>
      </div>
      <span class="mini-badge">${merchant.verified ? "Verified" : "Unverified"}</span>
    </div>
    <div class="meta-grid">
      <div class="meta-tile"><span>Location</span><strong>${escapeHtml(merchant.locality)}, ${escapeHtml(merchant.city)}</strong></div>
      <div class="meta-tile"><span>Plan</span><strong>${escapeHtml(merchant.plan)} · ${merchant.daysRemaining}d left</strong></div>
      <div class="meta-tile"><span>Languages</span><strong>${merchant.languages.join(", ")}</strong></div>
      <div class="meta-tile"><span>Active offer</span><strong>${escapeHtml(merchant.offers[0])}</strong></div>
    </div>
  `;
}

function renderTriggerCard(trigger) {
  const dots = Array.from({ length: 5 }, (_, index) => `<span class="${index < trigger.urgency ? "on" : ""}"></span>`).join("");
  elements.triggerCard.innerHTML = html`
    <div class="trigger-title">
      <div>
        <p class="section-label">Trigger information</p>
        <h3>${escapeHtml(trigger.kind.replaceAll("_", " "))}</h3>
      </div>
      <div class="urgency-dots" aria-label="Urgency ${trigger.urgency} of 5">${dots}</div>
    </div>
    <p class="body-copy">${escapeHtml(trigger.whyNow)}</p>
    <div class="meta-grid">
      <div class="meta-tile"><span>Source</span><strong>${escapeHtml(trigger.source)}</strong></div>
      <div class="meta-tile"><span>Expires</span><strong>${escapeHtml(trigger.expires)}</strong></div>
    </div>
  `;
}

function renderSuggestions(merchant, trigger) {
  const suggestions = [
    {
      title: "Generate JSON draft",
      body: "Strict Vera format with one CTA",
      text: makeVeraDraft(merchant, trigger),
    },
    {
      title: "Ask for approval",
      body: "Short binary CTA",
      text: `Can I send this as ${merchant.name}'s next WhatsApp nudge? Reply YES and I will queue it.`,
    },
    {
      title: "Summarize context",
      body: "Useful before handoff",
      text: `${merchant.name}: ${trigger.kind} triggered now because ${trigger.whyNow} Main signals: ${merchant.signals.join(", ")}.`,
    },
  ];

  elements.suggestions.innerHTML = suggestions
    .map(
      (suggestion) => html`
        <button class="suggestion-row" type="button" data-suggestion="${escapeHtml(suggestion.text)}">
          <div>
            <strong>${escapeHtml(suggestion.title)}</strong>
            <span>${escapeHtml(suggestion.body)}</span>
          </div>
          <span class="mini-badge">Use</span>
        </button>
      `,
    )
    .join("");
}

function renderMessages(merchant) {
  elements.chatTitle.textContent = merchant.name;
  elements.statusBadge.textContent = merchant.risk === "risk" ? "Needs action" : merchant.risk === "hot" ? "High intent" : "Active";
  elements.statusBadge.className = `status-badge ${merchant.risk}`;

  if (state.loading) {
    return;
  }

  elements.messages.innerHTML = merchant.messages
    .map((message) => {
      const isVera = message.from === "vera";
      return html`
        <article class="message ${isVera ? "outbound" : "merchant"}">
          <p>${escapeHtml(message.body)}</p>
          <div class="message-meta">
            <span>${isVera ? "Vera" : merchant.owner}</span>
            <span>${escapeHtml(message.time)}</span>
          </div>
        </article>
      `;
    })
    .join("");
  requestAnimationFrame(() => {
    elements.messages.scrollTop = elements.messages.scrollHeight;
  });
}

function renderStats(merchant) {
  const rows = [
    ["30d views", formatNumber(merchant.views), Math.min(100, merchant.views / 125)],
    ["Calls", formatNumber(merchant.calls), Math.min(100, merchant.calls)],
    ["Directions", formatNumber(merchant.directions), Math.min(100, merchant.directions / 3.2)],
    ["CTR", `${merchant.ctr.toFixed(1)}%`, Math.min(100, merchant.ctr * 16)],
    ["Leads", formatNumber(merchant.leads), Math.min(100, merchant.leads * 2.5)],
  ];
  const visibleRows = state.expanded.stats ? rows : rows.slice(0, 3);

  elements.stats.innerHTML = visibleRows
    .map(
      ([label, value, width]) => html`
        <div class="stat-row">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
        <div class="bar-track"><div class="bar-fill" style="--value: ${width}%"></div></div>
      `,
    )
    .join("");
}

function renderContext(merchant, trigger) {
  const contextRows = [
    ["Category", `${merchant.category}: ${categoryVoice[merchant.category]}`],
    ["Merchant", `${merchant.name}, ${merchant.locality}, ${merchant.city}`],
    ["Trigger", `${trigger.kind}, urgency ${trigger.urgency}/5`],
    ["Suppression", trigger.suppressionKey],
    ["Payload", trigger.payload],
  ];
  const visibleRows = state.expanded.context ? contextRows : contextRows.slice(0, 4);

  elements.context.innerHTML = visibleRows
    .map(
      ([label, value]) => html`
        <div class="context-pill">
          <span>${label}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>
      `,
    )
    .join("");
}

function renderCustomer(merchant) {
  const customer = customerContexts[merchant.id];
  elements.customerScopeBadge.textContent = customer ? "Available" : "Not provided";

  if (!customer) {
    elements.customer.innerHTML = `<div class="empty-state">No customer context for this merchant-facing trigger.</div>`;
    return;
  }

  elements.customer.innerHTML = html`
    <div class="context-pill"><span>Name</span><strong>${escapeHtml(customer.name)}</strong></div>
    <div class="context-pill"><span>State</span><strong>${escapeHtml(customer.state)}</strong></div>
    <div class="context-pill"><span>Last visit</span><strong>${escapeHtml(customer.lastVisit)}</strong></div>
    <div class="context-pill"><span>Preference</span><strong>${escapeHtml(customer.preference)}</strong></div>
    <div class="context-pill"><span>Consent</span><strong>${escapeHtml(customer.consent)}</strong></div>
  `;
}

function renderHistory(merchant) {
  if (!merchant.history.length) {
    elements.history.innerHTML = `<div class="empty-state">No prior Vera turns in this sample.</div>`;
    return;
  }

  elements.history.innerHTML = merchant.history
    .map(
      (item) => html`
        <div class="timeline-item">
          <span>${escapeHtml(item.time)} · ${escapeHtml(item.from)}</span>
          <strong>${escapeHtml(item.engagement)}</strong>
          <p>${escapeHtml(item.body)}</p>
        </div>
      `,
    )
    .join("");
}

function renderChart(merchant) {
  const seed = merchant.responseRate;
  const values = [seed - 11, seed - 7, seed - 3, seed + 2, seed - 1, seed + 4, seed + 8].map((value) =>
    Math.max(18, Math.min(92, value)),
  );
  const points = values.map((value, index) => {
    const x = 18 + index * 47;
    const y = 132 - value * 1.18;
    return [x, y];
  });
  const path = points.map(([x, y], index) => `${index === 0 ? "M" : "L"} ${x} ${y}`).join(" ");
  const area = `${path} L ${points.at(-1)[0]} 136 L ${points[0][0]} 136 Z`;

  elements.chart.innerHTML = `
    <defs>
      <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#635bff" stop-opacity="0.24" />
        <stop offset="100%" stop-color="#0ea5e9" stop-opacity="0.02" />
      </linearGradient>
    </defs>
    <path class="trend-area" d="${area}" fill="url(#chartFill)"></path>
    <path class="trend-line" d="${path}" fill="none" stroke="#635bff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
    ${points.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4" fill="#0ea5e9"></circle>`).join("")}
  `;
}

function makeVeraDraft(merchant, trigger) {
  const sendAs = trigger.scope === "customer" ? "merchant_on_behalf" : "vera";
  const bodyByCategory = {
    dentists: `Dr. ${merchant.owner}, ${trigger.payload} Your CTR is ${merchant.ctr.toFixed(1)}% vs South Delhi peer median 3.0%, so this is a good moment to turn it into a patient-ed WhatsApp. Want me to draft it?`,
    salons: `${merchant.owner}, ${merchant.name}'s calls are ${merchant.calls} in 30d and ${merchant.offers[0]} is active. ${trigger.whyNow} Want me to create one Diwali-ready post?`,
    restaurants: `${merchant.owner} ji, ${trigger.payload}. Your trial has ${merchant.daysRemaining} days left, so tonight is a useful test. Want me to draft a 2-line WhatsApp status?`,
    pharmacies: `${merchant.owner}, ${trigger.payload}. This needs action now so affected stock does not go into more refills. Want me to draft a staff checklist?`,
    gyms: `${merchant.owner}, views are down 30% in 7 days but CTR is still ${merchant.ctr.toFixed(1)}%. Want me to draft a summer comeback post for ${merchant.offers[0]}?`,
  };

  return JSON.stringify(
    {
      body: bodyByCategory[merchant.category],
      cta: "Reply YES to draft",
      send_as: sendAs,
      suppression_key: trigger.suppressionKey,
      rationale: `Sent now because ${trigger.whyNow}`,
    },
    null,
    2,
  );
}

function renderAll() {
  const merchant = currentMerchant();
  const trigger = currentTrigger();
  renderFilters();
  renderConversations();
  renderMetrics();
  renderMerchantCard(merchant);
  renderTriggerCard(trigger);
  renderSuggestions(merchant, trigger);
  renderMessages(merchant);
  renderStats(merchant);
  renderContext(merchant, trigger);
  renderCustomer(merchant);
  renderHistory(merchant);
  renderChart(merchant);
}

function showToast(title, body) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<strong>${escapeHtml(title)}</strong><p>${escapeHtml(body)}</p>`;
  elements.toastHost.append(toast);
  setTimeout(() => toast.remove(), 3600);
}

function selectMerchant(id) {
  state.selectedId = id;
  state.loading = true;
  elements.messages.innerHTML = `
    <div class="skeleton-line"></div>
    <div class="skeleton-bubble"></div>
    <div class="skeleton-line small"></div>
  `;
  renderAll();
  setTimeout(() => {
    state.loading = false;
    renderAll();
  }, 420);
}

function addMessage(body, from = "vera") {
  const merchant = currentMerchant();
  merchant.messages.push({
    from,
    body,
    time: new Date().toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    }),
  });
  renderMessages(merchant);
}

async function simulateReply(message = "Yes, make it simple for patients.") {
  const merchant = currentMerchant();
  elements.typing.hidden = false;
  try {
    const response = await getBackendReply(merchant.id, message);
    elements.typing.hidden = true;
    if (response.action === "send") {
      addMessage(response.body, "vera");
      showToast("Vera replied", response.rationale || "Backend composer responded.");
      return;
    }
    if (response.action === "wait") {
      showToast("Vera is waiting", `Backoff: ${response.wait_seconds}s. ${response.rationale}`);
      return;
    }
    if (response.action === "end") {
      showToast("Conversation ended", response.rationale || "Vera closed the thread.");
      return;
    }
  } catch (error) {
    elements.typing.hidden = true;
    showToast("Backend unavailable", error.message);
  }
}

function initEvents() {
  elements.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderConversations();
  });

  elements.filters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) return;
    state.category = button.dataset.category;
    const firstMatch = filteredMerchants()[0];
    if (firstMatch) state.selectedId = firstMatch.id;
    renderAll();
  });

  elements.conversations.addEventListener("click", (event) => {
    const button = event.target.closest("[data-merchant]");
    if (!button) return;
    selectMerchant(button.dataset.merchant);
  });

  elements.suggestions.addEventListener("click", (event) => {
    const button = event.target.closest("[data-suggestion]");
    if (!button) return;
    elements.input.value = button.dataset.suggestion;
    elements.input.focus();
    autoSizeComposer();
  });

  elements.form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = elements.input.value.trim();
    if (!body) return;
    addMessage(body, "merchant");
    elements.input.value = "";
    autoSizeComposer();
    showToast("Merchant reply sent", "Asking Vera backend for the next response.");
    await simulateReply(body);
  });

  elements.magicCompose.addEventListener("click", async () => {
    try {
      const action = await getBackendAction(currentMerchant().id);
      elements.input.value = action.body;
      autoSizeComposer();
      elements.input.focus();
      showToast("Backend draft generated", action.rationale);
    } catch (error) {
      elements.input.value = makeVeraDraft(currentMerchant(), currentTrigger());
      autoSizeComposer();
      elements.input.focus();
      showToast("Fallback draft generated", error.message);
    }
  });

  elements.input.addEventListener("input", autoSizeComposer);

  elements.themeToggle.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem("vera-theme", nextTheme);
    showToast("Theme updated", `${nextTheme === "dark" ? "Dark" : "Light"} mode is active.`);
  });

  elements.simulateTrigger.addEventListener("click", async () => {
    const merchant = currentMerchant();
    try {
      const action = await getBackendAction(merchant.id);
      addMessage(action.body, "vera");
      showToast("Backend trigger sent", `${action.trigger_id} · ${action.cta}`);
    } catch (error) {
      const trigger = currentTrigger();
      addMessage(makeVeraDraft(merchant, trigger), "vera");
      showToast("Fallback trigger simulated", error.message);
    }
  });

  document.querySelectorAll("[data-expand]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.expand;
      state.expanded[key] = !state.expanded[key];
      button.textContent = state.expanded[key] ? "Collapse" : "Expand";
      renderStats(currentMerchant());
      renderContext(currentMerchant(), currentTrigger());
    });
  });
}

function autoSizeComposer() {
  elements.input.style.height = "auto";
  elements.input.style.height = `${Math.min(elements.input.scrollHeight, 116)}px`;
}

async function boot() {
  const savedTheme = localStorage.getItem("vera-theme");
  if (savedTheme) {
    document.documentElement.dataset.theme = savedTheme;
  }

  initEvents();
  renderAll();
  try {
    const data = await bootstrapBackend();
    showToast("Backend connected", `${data.contexts_loaded.trigger} demo triggers loaded.`);
  } catch (error) {
    showToast("UI-only mode", `Backend demo bootstrap failed: ${error.message}`);
  }
  setTimeout(() => {
    state.loading = false;
    renderAll();
    showToast("Live queue ready", state.apiReady ? "Chat uses Vera backend responses." : "Using local UI fallback only.");
  }, 700);
}

boot();
