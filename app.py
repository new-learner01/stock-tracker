from flask import Flask, request, jsonify, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Universal Stock Screener with Interactive Chart</title>
<script src="https://unpkg.com/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js"></script>
<style>
  :root {
    --bg: #090d16;
    --card: #131d2e;
    --border: #24344d;
    --text: #f8fafc;
    --muted: #94a3b8;
    --blue: #38bdf8;
    --green: #4ade80;
    --rose: #f43f5e;
    --amber: #fbbf24;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: var(--bg); color: var(--text); padding: 20px; }
  .container { max-width: 1200px; margin: 0 auto; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; margin-bottom: 16px; }
  .search-box { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; justify-content: space-between; }
  .search-input { background: #090d16; border: 1px solid var(--border); color: #fff; padding: 10px 16px; border-radius: 8px; font-size: 1rem; width: 260px; text-transform: uppercase; font-weight: 700; outline: none; }
  .btn { background: var(--blue); color: #090d16; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; }
  .chips { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .chip { background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); color: var(--blue); padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; cursor: pointer; font-weight: 600; }
  .header-banner { display: flex; justify-content: space-between; align-items: center; }
  .price-large { font-size: 1.8rem; font-weight: 800; color: var(--blue); }
  
  /* Chart Controls */
  .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px; }
  .mode-switch { display: flex; background: #090d16; border: 1px solid var(--border); border-radius: 8px; padding: 3px; gap: 4px; }
  .mode-btn { background: transparent; border: none; color: var(--muted); padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 700; cursor: pointer; }
  .mode-btn.active { background: var(--blue); color: #090d16; }
  #chart-container { width: 100%; height: 420px; border-radius: 8px; overflow: hidden; background: #090d16; border: 1px solid var(--border); }
  
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .grid-8 { display: grid; grid-template-columns: repeat(8, 1fr); gap: 10px; }
  @media(max-width: 900px) { .grid-4 { grid-template-columns: repeat(2, 1fr); } .grid-8 { grid-template-columns: repeat(4, 1fr); } }
  @media(max-width: 550px) { .grid-8 { grid-template-columns: repeat(2, 1fr); } }
  
  .stat-card { background: rgba(9, 13, 22, 0.85); border: 1px solid var(--border); border-radius: 8px; padding: 12px; text-align: center; }
  .stat-title { font-size: 0.75rem; color: var(--muted); font-weight: 700; text-transform: uppercase; }
  .stat-val { font-size: 1.15rem; font-weight: 800; margin: 4px 0; }
  .pos { color: var(--green); } .neg { color: var(--rose); }
  .status-notice { padding: 10px 16px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 16px; display: none; }
  .notice-loading { background: rgba(56, 189, 248, 0.15); border: 1px solid var(--blue); color: var(--blue); display: block; }
  .notice-success { background: rgba(74, 222, 128, 0.15); border: 1px solid var(--green); color: var(--green); display: block; }
  .notice-error { background: rgba(244, 63, 94, 0.15); border: 1px solid var(--rose); color: var(--rose); display: block; }
</style>
</head>
<body>
<div class="container">
  <div class="card search-box">
    <div style="display:flex; gap:10px;">
      <input type="text" id="ticker" class="search-input" placeholder="e.g. KEC, RELIANCE, TCS" value="KEC" onkeydown="if(event.key==='Enter') loadStock()">
      <button class="btn" onclick="loadStock()">⚡ Search Any Stock</button>
    </div>
    <div class="chips">
      <span style="font-size:0.8rem; color:var(--muted);">Presets:</span>
      <span class="chip" onclick="quickSelect('KEC')">KEC</span>
      <span class="chip" onclick="quickSelect('TATAPOWER')">TATAPOWER</span>
      <span class="chip" onclick="quickSelect('RELIANCE')">RELIANCE</span>
      <span class="chip" onclick="quickSelect('TCS')">TCS</span>
      <span class="chip" onclick="quickSelect('ZOMATO')">ZOMATO</span>
      <span class="chip" onclick="quickSelect('SUZLON')">SUZLON</span>
      <span class="chip" onclick="quickSelect('GARUDA')">GARUDA</span>
      <span class="chip" onclick="quickSelect('OSWALPUMPS')">OSWALPUMPS</span>
    </div>
  </div>

  <div id="status-box" class="status-notice"></div>

  <div class="card header-banner">
    <div>
      <h2 id="name">Loading...</h2>
      <p id="symbol" style="color:var(--muted); font-size:0.9rem;">-</p>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.8rem; color:var(--muted);">Current Price</div>
      <div class="price-large" id="price">-</div>
    </div>
  </div>

  <!-- Interactive Chart -->
  <div class="card">
    <div class="chart-header">
      <div>
        <h4 style="color:var(--blue);" id="chart-title">📈 1-Year Interactive Candlestick Chart</h4>
        <p style="font-size:0.8rem; color:var(--muted);">Real daily price history directly from the exchange</p>
      </div>
      <div class="mode-switch">
        <button id="btn-candles" class="mode-btn active" onclick="setChartType('candles')">🕯️ Candlesticks</button>
        <button id="btn-area" class="mode-btn" onclick="setChartType('area')">📉 Area Line</button>
        <button id="btn-dma" class="mode-btn" onclick="toggleDMA()">📊 50/200 DMA</button>
      </div>
    </div>
    <div id="chart-container"></div>
  </div>

  <!-- DMAs -->
  <div class="card">
    <h4 style="color:var(--blue); margin-bottom:12px;">📊 Daily Moving Averages (DMAs)</h4>
    <div class="grid-4">
      <div class="stat-card"><div class="stat-title">10 DMA</div><div class="stat-val" id="dma10">-</div><div id="diff10" style="font-size:0.75rem; font-weight:700;">-</div></div>
      <div class="stat-card"><div class="stat-title">20 DMA</div><div class="stat-val" id="dma20">-</div><div id="diff20" style="font-size:0.75rem; font-weight:700;">-</div></div>
      <div class="stat-card"><div class="stat-title">50 DMA</div><div class="stat-val" id="dma50">-</div><div id="diff50" style="font-size:0.75rem; font-weight:700;">-</div></div>
      <div class="stat-card"><div class="stat-title">200 DMA</div><div class="stat-val" id="dma200">-</div><div id="diff200" style="font-size:0.75rem; font-weight:700;">-</div></div>
    </div>
  </div>

  <!-- Returns -->
  <div class="card">
    <h4 style="color:var(--blue); margin-bottom:12px;">📈 Multi-Period Price Returns</h4>
    <div class="grid-8">
      <div class="stat-card"><div class="stat-title">1D</div><div class="stat-val" id="r1d">-</div></div>
      <div class="stat-card"><div class="stat-title">1W</div><div class="stat-val" id="r1w">-</div></div>
      <div class="stat-card"><div class="stat-title">1M</div><div class="stat-val" id="r1m">-</div></div>
      <div class="stat-card"><div class="stat-title">3M</div><div class="stat-val" id="r3m">-</div></div>
      <div class="stat-card"><div class="stat-title">6M</div><div class="stat-val" id="r6m">-</div></div>
      <div class="stat-card"><div class="stat-title">1Y</div><div class="stat-val" id="r1y">-</div></div>
      <div class="stat-card"><div class="stat-title">3Y</div><div class="stat-val" id="r3y">-</div></div>
      <div class="stat-card"><div class="stat-title">5Y</div><div class="stat-val" id="r5y">-</div></div>
    </div>
  </div>

  <!-- Fundamentals -->
  <div class="card">
    <h4 style="color:var(--blue); margin-bottom:12px;">📑 Valuation Multiples</h4>
    <div class="grid-4">
      <div class="stat-card"><div class="stat-title">Trailing P/E</div><div class="stat-val" id="pe">-</div></div>
      <div class="stat-card"><div class="stat-title">P/B Ratio</div><div class="stat-val" id="pb">-</div></div>
      <div class="stat-card"><div class="stat-title">EPS</div><div class="stat-val" id="eps">-</div></div>
      <div class="stat-card"><div class="stat-title">Book Value</div><div class="stat-val" id="bvps">-</div></div>
    </div>
  </div>
</div>

<script>
let chart = null;
let mainSeries = null;
let dma50Series = null;
let dma200Series = null;
let currentChartMode = 'candles';
let showDMA = false;
let globalData = null;

function quickSelect(t) {
  document.getElementById('ticker').value = t;
  loadStock();
}

function showStatus(text, type) {
  const box = document.getElementById('status-box');
  box.className = 'status-notice ' + type;
  box.innerText = text;
}

function initChart() {
  const container = document.getElementById('chart-container');
  container.innerHTML = '';
  
  chart = LightweightCharts.createChart(container, {
    width: container.clientWidth,
    height: 420,
    layout: { background: { color: '#090d16' }, textColor: '#94a3b8' },
    grid: { vertLines: { color: 'rgba(36, 52, 77, 0.4)' }, horzLines: { color: 'rgba(36, 52, 77, 0.4)' } },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    rightPriceScale: { borderColor: '#24344d' },
    timeScale: { borderColor: '#24344d', timeVisible: false }
  });

  window.addEventListener('resize', () => {
    if (chart) chart.applyOptions({ width: container.clientWidth });
  });
}

function renderChart() {
  if (!globalData || !globalData.candles || globalData.candles.length === 0) return;
  initChart();

  if (currentChartMode === 'candles') {
    mainSeries = chart.addCandlestickSeries({
      upColor: '#4ade80', downColor: '#f43f5e',
      borderUpColor: '#4ade80', borderDownColor: '#f43f5e',
      wickUpColor: '#4ade80', wickDownColor: '#f43f5e'
    });
    mainSeries.setData(globalData.candles);
  } else {
    mainSeries = chart.addAreaSeries({
      topColor: 'rgba(56, 189, 248, 0.4)',
      bottomColor: 'rgba(56, 189, 248, 0.0)',
      lineColor: '#38bdf8',
      lineWidth: 2
    });
    mainSeries.setData(globalData.area);
  }

  if (showDMA) {
    dma50Series = chart.addLineSeries({ color: '#4ade80', lineWidth: 1.5, title: '50 DMA' });
    dma50Series.setData(globalData.dma50_line);

    dma200Series = chart.addLineSeries({ color: '#fbbf24', lineWidth: 2, title: '200 DMA' });
    dma200Series.setData(globalData.dma200_line);
  }

  chart.timeScale().fitContent();
}

function setChartType(type) {
  currentChartMode = type;
  document.getElementById('btn-candles').classList.toggle('active', type === 'candles');
  document.getElementById('btn-area').classList.toggle('active', type === 'area');
  renderChart();
}

function toggleDMA() {
  showDMA = !showDMA;
  document.getElementById('btn-dma').classList.toggle('active', showDMA);
  renderChart();
}

async function loadStock() {
  const sym = document.getElementById('ticker').value.trim().toUpperCase();
  showStatus(`Fetching live market data and historical price candles for ${sym}...`, 'notice-loading');

  try {
    const res = await fetch(`/api/stock?symbol=${encodeURIComponent(sym)}`);
    const data = await res.json();

    if (data.error) {
      showStatus(`❌ ${data.error}`, 'notice-error');
      return;
    }

    globalData = data;
    document.getElementById('name').innerText = data.name;
    document.getElementById('symbol').innerText = data.symbol;
    document.getElementById('price').innerText = `₹${data.price.toFixed(2)}`;

    setDmaCard('dma10', 'diff10', data.dma10, data.price);
    setDmaCard('dma20', 'diff20', data.dma20, data.price);
    setDmaCard('dma50', 'diff50', data.dma50, data.price);
    setDmaCard('dma200', 'diff200', data.dma200, data.price);

    setRet('r1d', data.ret['1d']);
    setRet('r1w', data.ret['1w']);
    setRet('r1m', data.ret['1m']);
    setRet('r3m', data.ret['3m']);
    setRet('r6m', data.ret['6m']);
    setRet('r1y', data.ret['1y']);
    setRet('r3y', data.ret['3y']);
    setRet('r5y', data.ret['5y']);

    document.getElementById('pe').innerText = data.pe ? `${data.pe.toFixed(2)}x` : 'N/A';
    document.getElementById('pb').innerText = data.pb ? `${data.pb.toFixed(2)}x` : 'N/A';
    document.getElementById('eps').innerText = data.eps ? `₹${data.eps.toFixed(2)}` : 'N/A';
    document.getElementById('bvps').innerText = data.bvps ? `₹${data.bvps.toFixed(2)}` : 'N/A';

    renderChart();
    showStatus(`✅ Live market data and candles loaded for ${data.name}.`, 'notice-success');
  } catch (e) {
    showStatus(`❌ Error connecting to server: ${e.message}`, 'notice-error');
  }
}

function setDmaCard(valId, diffId, dmaVal, curPrice) {
  const elV = document.getElementById(valId);
  const elD = document.getElementById(diffId);
  if (!dmaVal) {
    elV.innerText = 'N/A';
    elD.innerText = '-';
    elD.className = '';
    return;
  }
  elV.innerText = `₹${dmaVal.toFixed(2)}`;
  const diff = ((curPrice - dmaVal) / dmaVal) * 100;
  elD.innerText = (diff >= 0 ? '+' : '') + diff.toFixed(2) + '% ' + (diff >= 0 ? 'Above' : 'Below');
  elD.className = diff >= 0 ? 'pos' : 'neg';
}

function setRet(id, val) {
  const el = document.getElementById(id);
  if (val === null || val === undefined) {
    el.innerText = 'N/A';
    el.className = 'stat-val';
  } else {
    el.innerText = (val >= 0 ? '+' : '') + val.toFixed(2) + '%';
    el.className = 'stat-val ' + (val >= 0 ? 'pos' : 'neg');
  }
}

window.onload = loadStock;
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/stock')
def get_stock():
    raw_sym = request.args.get('symbol', 'KEC').strip().upper()
    clean = raw_sym.replace('.NS', '').replace('.BO', '')
    is_india = not any(clean.endswith(x) for x in ['AAPL', 'NVDA', 'MSFT', 'TSLA', 'AMZN', 'GOOGL', 'META'])
    
    candidates = [f"{clean}.NS", f"{clean}.BO", clean] if is_india else [clean]
    hist = pd.DataFrame()
    info = {}
    resolved = clean

    for cand in candidates:
        try:
            t = yf.Ticker(cand)
            h = t.history(period="5y", interval="1d")
            if not h.empty and len(h) > 5:
                hist = h
                info = t.info
                resolved = cand
                break
        except Exception:
            continue

    if hist.empty:
        return jsonify({"error": f"Stock '{raw_sym}' not found on NSE/BSE."}), 404

    hist = hist.dropna(subset=['Close', 'Open', 'High', 'Low'])
    prices = hist['Close']
    current_p = float(prices.iloc[-1])

    # Convert candles for lightweight-charts format (YYYY-MM-DD)
    candles = []
    area = []
    for idx, row in hist.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        candles.append({
            "time": date_str,
            "open": round(float(row['Open']), 2),
            "high": round(float(row['High']), 2),
            "low": round(float(row['Low']), 2),
            "close": round(float(row['Close']), 2)
        })
        area.append({
            "time": date_str,
            "value": round(float(row['Close']), 2)
        })

    # Rolling DMAs
    dma50_series = prices.rolling(50).mean()
    dma200_series = prices.rolling(200).mean()
    
    dma50_line = []
    dma200_line = []
    for idx in hist.index:
        date_str = idx.strftime('%Y-%m-%d')
        v50 = dma50_series.loc[idx]
        v200 = dma200_series.loc[idx]
        if not np.isnan(v50):
            dma50_line.append({"time": date_str, "value": round(float(v50), 2)})
        if not np.isnan(v200):
            dma200_line.append({"time": date_str, "value": round(float(v200), 2)})

    dma10 = float(prices.rolling(10).mean().iloc[-1]) if len(prices) >= 10 else None
    dma20 = float(prices.rolling(20).mean().iloc[-1]) if len(prices) >= 20 else None
    dma50 = float(prices.rolling(50).mean().iloc[-1]) if len(prices) >= 50 else None
    dma200 = float(prices.rolling(200).mean().iloc[-1]) if len(prices) >= 200 else None

    def calc_ret(days):
        if len(prices) > days:
            past_val = float(prices.iloc[-days-1])
            if past_val > 0:
                return round(((current_p - past_val) / past_val) * 100, 2)
        return None

    ret = {
        "1d": calc_ret(1), "1w": calc_ret(5), "1m": calc_ret(21),
        "3m": calc_ret(63), "6m": calc_ret(126), "1y": calc_ret(252),
        "3y": calc_ret(756), "5y": calc_ret(1260)
    }

    return jsonify({
        "name": info.get('longName') or clean,
        "symbol": f"{'BSE' if resolved.endswith('.BO') else 'NSE'}: {clean}",
        "price": current_p,
        "dma10": dma10, "dma20": dma20, "dma50": dma50, "dma200": dma200,
        "ret": ret,
        "pe": info.get('trailingPE'),
        "pb": info.get('priceToBook'),
        "eps": info.get('trailingEps'),
        "bvps": info.get('bookValue'),
        "candles": candles,
        "area": area,
        "dma50_line": dma50_line,
        "dma200_line": dma200_line
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
