/* ============================================
   FOREXPRO — SHARED SCRIPT
   ============================================ */

// ── THEME ──────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('fpTheme') || 'dark';
  applyTheme(saved);
}

function applyTheme(theme) {
  const html = document.documentElement;
  if (theme === 'light') {
    html.classList.add('light');
    html.classList.remove('dark');
  } else {
    html.classList.remove('light');
    html.classList.add('dark');
  }
  localStorage.setItem('fpTheme', theme);
  // sync icons
  document.querySelectorAll('.icon-sun').forEach(el => el.classList.toggle('hidden', theme !== 'dark'));
  document.querySelectorAll('.icon-moon').forEach(el => el.classList.toggle('hidden', theme === 'dark'));
}

function toggleTheme() {
  const current = localStorage.getItem('fpTheme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

// ── MOBILE MENU ─────────────────────────────
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  const iconOpen = document.getElementById('icon-menu');
  const iconClose = document.getElementById('icon-close');
  if (!menu) return;
  menu.classList.toggle('open');
  if (iconOpen) iconOpen.classList.toggle('hidden');
  if (iconClose) iconClose.classList.toggle('hidden');
}

function closeMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  const iconOpen = document.getElementById('icon-menu');
  const iconClose = document.getElementById('icon-close');
  if (!menu) return;
  menu.classList.remove('open');
  if (iconOpen) iconOpen.classList.remove('hidden');
  if (iconClose) iconClose.classList.add('hidden');
}

// ── SMOOTH SCROLL ───────────────────────────
function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  closeMobileMenu();
}

// ── LIVE PRICE TICKER ────────────────────────
const PAIRS = [
  { pair: 'EUR/USD', bid: 1.08542, ask: 1.08559, spread: 1.7,  change: 0.42,  trend: 'up'   },
  { pair: 'GBP/USD', bid: 1.26381, ask: 1.26402, spread: 2.1,  change: -0.18, trend: 'down' },
  { pair: 'USD/JPY', bid: 149.821, ask: 149.843, spread: 2.2,  change: 0.31,  trend: 'up'   },
  { pair: 'AUD/USD', bid: 0.64712, ask: 0.64729, spread: 1.7,  change: -0.09, trend: 'down' },
  { pair: 'USD/CAD', bid: 1.35621, ask: 1.35644, spread: 2.3,  change: 0.14,  trend: 'up'   },
];

let prices = JSON.parse(JSON.stringify(PAIRS));

function formatPrice(pair, price) {
  return pair.includes('JPY') ? price.toFixed(3) : price.toFixed(5);
}

function renderPrices() {
  const tbody = document.getElementById('price-table-body');
  if (!tbody) return;
  tbody.innerHTML = prices.map(p => `
    <tr>
      <td><span class="pair-name">${p.pair}</span></td>
      <td><span class="price-val">${formatPrice(p.pair, p.bid)}</span></td>
      <td><span class="price-val">${formatPrice(p.pair, p.ask)}</span></td>
      <td class="col-spread"><span class="spread-val">${p.spread.toFixed(1)}</span></td>
      <td><span class="${p.change >= 0 ? 'change-up' : 'change-down'}">${p.change >= 0 ? '+' : ''}${p.change.toFixed(2)}%</span></td>
      <td><span class="trend-badge ${p.trend === 'up' ? 'trend-up' : 'trend-down'}">${p.trend === 'up' ? '↑' : '↓'}</span></td>
    </tr>
  `).join('');
}

function updatePrices() {
  prices = prices.map(p => {
    const isPip = p.pair.includes('JPY') ? 0.01 : 0.0001;
    const delta  = (Math.random() - 0.5) * isPip * 4;
    const newBid = Math.max(0.0001, p.bid + delta);
    const newAsk = newBid + p.spread * isPip;
    const newChange = parseFloat((p.change + (Math.random() - 0.5) * 0.025).toFixed(2));
    return { ...p, bid: newBid, ask: newAsk, change: newChange, trend: newChange >= 0 ? 'up' : 'down' };
  });
  renderPrices();
}

function startTicker() {
  renderPrices();
  setInterval(updatePrices, 1800);
}

// ── POSITION CALCULATOR ──────────────────────
function calculatePosition() {
  const balance = parseFloat(document.getElementById('balance')?.value) || 0;
  const risk    = parseFloat(document.getElementById('risk-percent')?.value) || 0;
  const sl      = parseFloat(document.getElementById('stop-loss')?.value) || 0;
  const goal    = parseFloat(document.getElementById('daily-goal')?.value) || 0;

  const summary = document.getElementById('position-summary');
  if (!summary) return;

  if (balance <= 0 || risk <= 0 || sl <= 0) {
    summary.classList.add('hidden');
    return;
  }

  // Calculate position size correctly
  const riskAmount = (balance * risk) / 100;
  
  // Standard lot calculation: 1 lot = $10 per pip for standard lots
  const pipValuePerLot = 10; // $10 per pip for 1 standard lot
  const pipValuePerUnit = pipValuePerLot / 100000; // $0.0001 per pip per unit
  const lotSize = riskAmount / (sl * pipValuePerUnit * 100000); // Convert to standard lots
  
  // Calculate risk multiple
  const rMultiple = goal > 0 ? goal / riskAmount : 0;

  // Display results
  document.getElementById('result-lots').textContent = lotSize.toFixed(2);
  document.getElementById('result-risk').textContent = '$' + riskAmount.toFixed(2);
  document.getElementById('result-rmultiple').textContent = rMultiple.toFixed(1) + 'R';

  summary.classList.remove('hidden');
}

// ── MODALS ──────────────────────────────────
function openModal(id) {
  const backdrop = document.getElementById('modal-backdrop');
  const box      = document.getElementById(id);
  if (!backdrop || !box) return;
  backdrop.classList.add('show');
  box.classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeAllModals() {
  document.getElementById('modal-backdrop')?.classList.remove('show');
  document.querySelectorAll('.modal-box').forEach(el => el.classList.remove('show'));
  document.body.style.overflow = '';
}

// close on Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeAllModals(); });

// ── INIT ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  if (document.getElementById('price-table-body')) startTicker();
  if (document.getElementById('forex-chart')) initLiveChart();
});

// ── LIVE CHART ───────────────────────────────
let chartInstance = null;
let chartData = [];
let currentPair = 'EUR/USD';
let currentTimeframe = '1h';

// Base prices for realistic simulation
const basePrices = {
  'EUR/USD': 1.0850,
  'GBP/USD': 1.2750,
  'USD/JPY': 148.50,
  'USD/CHF': 0.8750,
  'AUD/USD': 0.6550
};

function initLiveChart() {
  const chartSelect = document.getElementById('chart-pair');
  const timeframeSelect = document.getElementById('chart-timeframe');
  
  if (chartSelect) {
    chartSelect.addEventListener('change', (e) => {
      currentPair = e.target.value;
      generateChartData();
      updateChart();
    });
  }
  
  if (timeframeSelect) {
    timeframeSelect.addEventListener('change', (e) => {
      currentTimeframe = e.target.value;
      generateChartData();
      updateChart();
    });
  }
  
  // Initialize chart with data
  generateChartData();
  setTimeout(() => {
    document.getElementById('chart-loading').style.display = 'none';
    document.getElementById('chart-wrapper').style.display = 'block';
    createChart();
    updateChart();
    
    // Start live updates
    setInterval(updateLiveData, 3000);
  }, 1500);
}

function generateChartData() {
  chartData = [];
  const basePrice = basePrices[currentPair];
  const now = Date.now();
  let candles = 50; // Number of candles to show
  
  // Adjust candles based on timeframe
  switch(currentTimeframe) {
    case '1m': candles = 60; break;
    case '5m': candles = 48; break;
    case '15m': candles = 32; break;
    case '1h': candles = 48; break;
    case '4h': candles = 48; break;
    case '1d': candles = 30; break;
  }
  
  let currentPrice = basePrice;
  const intervalMs = getTimeframeMs(currentTimeframe);
  
  for (let i = candles; i >= 0; i--) {
    const timestamp = now - (i * intervalMs);
    const volatility = basePrice * 0.002; // 0.2% volatility
    const change = (Math.random() - 0.5) * volatility;
    
    const open = currentPrice;
    const close = currentPrice + change;
    const high = Math.max(open, close) + Math.random() * volatility * 0.5;
    const low = Math.min(open, close) - Math.random() * volatility * 0.5;
    
    chartData.push({
      time: timestamp,
      open: open,
      high: high,
      low: low,
      close: close,
      volume: Math.floor(Math.random() * 1000000) + 500000
    });
    
    currentPrice = close;
  }
}

function getTimeframeMs(timeframe) {
  const multipliers = {
    '1m': 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000
  };
  return multipliers[timeframe] || 60 * 60 * 1000;
}

function createChart() {
  const canvas = document.getElementById('forex-chart');
  const ctx = canvas.getContext('2d');
  
  // Set canvas size
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;
  
  // Simple candlestick chart implementation
  chartInstance = {
    ctx: ctx,
    canvas: canvas,
    width: canvas.width,
    height: canvas.height
  };
}

function updateChart() {
  if (!chartInstance) return;
  
  const { ctx, width, height } = chartInstance;
  const padding = { top: 20, right: 60, bottom: 40, left: 10 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  
  // Clear canvas
  ctx.clearRect(0, 0, width, height);
  
  if (chartData.length === 0) return;
  
  // Calculate price range
  const prices = chartData.flatMap(d => [d.high, d.low]);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;
  
  // Draw grid lines
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--border');
  ctx.lineWidth = 1;
  ctx.setLineDash([2, 2]);
  
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (chartHeight / 5) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
    
    // Price labels
    const price = maxPrice - (priceRange / 5) * i;
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-muted');
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(price.toFixed(4), width - padding.right + 5, y + 4);
  }
  
  ctx.setLineDash([]);
  
  // Draw candlesticks
  const candleWidth = Math.max(1, chartWidth / chartData.length - 2);
  
  chartData.forEach((candle, index) => {
    const x = padding.left + (index / chartData.length) * chartWidth + candleWidth / 2;
    
    const yHigh = padding.top + ((maxPrice - candle.high) / priceRange) * chartHeight;
    const yLow = padding.top + ((maxPrice - candle.low) / priceRange) * chartHeight;
    const yOpen = padding.top + ((maxPrice - candle.open) / priceRange) * chartHeight;
    const yClose = padding.top + ((maxPrice - candle.close) / priceRange) * chartHeight;
    
    // Determine color
    const isGreen = candle.close >= candle.open;
    ctx.strokeStyle = isGreen ? '#10b981' : '#ef4444';
    ctx.fillStyle = isGreen ? '#10b981' : '#ef4444';
    
    // Draw wick
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, yHigh);
    ctx.lineTo(x, yLow);
    ctx.stroke();
    
    // Draw body
    const bodyHeight = Math.abs(yClose - yOpen);
    const bodyY = Math.min(yOpen, yClose);
    
    if (isGreen) {
      ctx.fillRect(x - candleWidth / 2, bodyY, candleWidth, bodyHeight);
    } else {
      ctx.fillRect(x - candleWidth / 2, bodyY, candleWidth, bodyHeight);
    }
  });
  
  // Update stats
  updateChartStats();
}

function updateLiveData() {
  if (chartData.length === 0) return;
  
  // Add new candle or update last one
  const lastCandle = chartData[chartData.length - 1];
  const now = Date.now();
  const intervalMs = getTimeframeMs(currentTimeframe);
  
  if (now - lastCandle.time >= intervalMs) {
    // Create new candle
    const basePrice = basePrices[currentPair];
    const volatility = basePrice * 0.002;
    const change = (Math.random() - 0.5) * volatility;
    
    chartData.push({
      time: now,
      open: lastCandle.close,
      high: lastCandle.close + Math.random() * volatility * 0.5,
      low: lastCandle.close - Math.random() * volatility * 0.5,
      close: lastCandle.close + change,
      volume: Math.floor(Math.random() * 1000000) + 500000
    });
    
    // Keep only recent candles
    const maxCandles = 50;
    if (chartData.length > maxCandles) {
      chartData.shift();
    }
  } else {
    // Update current candle
    const volatility = basePrices[currentPair] * 0.001;
    const change = (Math.random() - 0.5) * volatility;
    
    lastCandle.close = lastCandle.close + change;
    lastCandle.high = Math.max(lastCandle.high, lastCandle.close);
    lastCandle.low = Math.min(lastCandle.low, lastCandle.close);
    lastCandle.volume += Math.floor(Math.random() * 10000);
  }
  
  updateChart();
}

function updateChartStats() {
  if (chartData.length === 0) return;
  
  const currentPrice = chartData[chartData.length - 1].close;
  const previousPrice = chartData.length > 1 ? chartData[chartData.length - 2].close : currentPrice;
  const change = currentPrice - previousPrice;
  const changePercent = (change / previousPrice) * 100;
  const volume = chartData[chartData.length - 1].volume;
  
  document.getElementById('current-price').textContent = currentPrice.toFixed(4);
  
  const changeElement = document.getElementById('price-change');
  changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(4)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
  changeElement.className = `stat-value ${change >= 0 ? 'positive' : 'negative'}`;
  
  document.getElementById('volume').textContent = formatVolume(volume);
}

function formatVolume(volume) {
  if (volume >= 1000000) {
    return (volume / 1000000).toFixed(1) + 'M';
  } else if (volume >= 1000) {
    return (volume / 1000).toFixed(1) + 'K';
  }
  return volume.toString();
}
