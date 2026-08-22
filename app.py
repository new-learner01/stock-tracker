from flask import Flask, request, jsonify, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Universal Indian Stock Screener (NSE / BSE)</title>
<style>
  :root {
    --bg: #090d16;
    --card-bg: #131d2e;
    --border: #24344d;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --blue: #38bdf8;
    --green: #4ade80;
    --amber: #fbbf24;
    --rose: #f43f5e;
    --cyan: #22d3ee;
    --emerald: #10b981;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background-color: var(--bg); color: var(--text-main); padding: 24px; min-height: 100vh; }
  header { text-align: center; max-width: 950px; margin: 0 auto 20px auto; }
  header h1 { font-size: 2.2rem; background: linear-gradient(135deg, #38bdf8, #818cf8, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
  header p { color: var(--text-muted); font-size: 0.98rem; }

  .container { max-width: 1200px; margin: 0 auto; }

  .search-section {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 16px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
  }
  .search-group { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 320px; }
  .search-input {
    background: #090d16;
    border: 1px solid var(--border);
    color: #fff;
    padding: 11px 16px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    width: 260px;
    outline: none;
  }
  .search-input:focus { border-color: var(--blue); }
  .btn {
    background: var(--blue);
    color: #090d16;
    border: none;
    padding: 11px 22px;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 700;
    cursor: pointer;
    transition: 0.2s;
  }
  .btn:hover { opacity: 0.9; transform: translateY(-1px); }
  .quick-chips { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .chip {
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: var(--blue);
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    cursor: pointer;
    font-weight: 600;
  }
  .chip:hover { background: var(--blue); color: #090d16; }

  .profile-banner {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(52, 211, 153, 0.1));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }
  .profile-name { font-size: 1.4rem; font-weight: 800; }
  .profile-meta { color: var(--text-muted); font-size: 0.88rem; margin-top: 4px; }

  .dma-section, .returns-section {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 20px;
  }
  .dma-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 12px;
  }
  @media (max-width: 768px) { .dma-grid { grid-template-columns: repeat(2, 1fr); } }

  .dma-card {
    background: rgba(9, 13, 22, 0.85);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .dma-title { font-size: 0.8rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase; }
  .dma-val { font-size: 1.35rem; font-weight: 800; margin: 4px 0; }
  .dma-diff { font-size: 0.78rem; font-weight: 700; }

  .returns-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 10px;
    margin-top: 12px;
  }
  @media (max-width: 1000px) { .returns-grid { grid-template-columns: repeat(4, 1fr); } }
  @media (max-width: 550px) { .returns-grid { grid-template-columns: repeat(2, 1fr); } }

  .return-card {
    background: rgba(9, 13, 22, 0.85);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 10px;
    text-align: center;
  }
  .return-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
  .return-val { font-size: 1.05rem; font-weight: 800; }

  .pos { color: var(--green); }
  .neg { color: var(--rose); }
  .neutral { color: var(--text-muted); }

  .card { background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 20px; }
  .sim-layout { display: grid; grid-template-columns: 1fr 1.25fr; gap: 24px; margin-bottom: 24px; }
  @media (max-width: 900px) { .sim-layout { grid-template-columns: 1fr; } }

  .input-row { margin-bottom: 11px; }
  .input-row label { display: flex; justify-content: space-between; font-size: 0.83rem; color: var(--text-muted); margin-bottom: 4px; }
  .input-row span.val { color: var(--blue); font-weight: 700; }
  input[type="range"] { width: 100%; accent-color: var(--blue); cursor: pointer; }

  .section-title { font-size: 0.86rem; font-weight: 700; color: var(--emerald); text-transform: uppercase; letter-spacing: 0.05em; margin: 10px 0 5px 0; border-bottom: 1px solid var(--border); padding-bottom: 3px; }

  .results-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
  @media (max-width: 550px) { .results-grid { grid-template-columns: 1fr; } }
  
  .res-card { background: rgba(9, 13, 22, 0.85); border: 1px solid var(--border); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; }
  .res-card.highlight { border-color: rgba(52, 211, 153, 0.4); background: rgba(16, 185, 129, 0.05); }
  .res-title { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; }
  .res-formula { font-size: 0.7rem; color: var(--cyan); font-family: monospace; }
  .res-num { font-size: 1.25rem; font-weight: 800; margin: 4px 0; }
  .status-badge { font-size: 0.7rem; font-weight: 700; padding: 3px 6px; border-radius: 4px; display: inline-block; width: fit-content; }
  
  .good { background: rgba(74, 222, 128, 0.2); color: var(--green); }
  .mod { background: rgba(251, 191, 36, 0.2); color: var(--amber); }
  .warn { background: rgba(244, 63, 94, 0.2); color: var(--rose); }

  .status-notice {
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 0.85rem;
    margin-bottom: 16px;
    display: none;
  }
  .notice-loading { background: rgba(56, 189, 248, 0.15); border: 1px solid var(--blue); color: var(--blue); display: block; }
  .notice-success { background: rgba(74, 222, 128, 0.15); border: 1px solid var(--green); color: var(--green); display: block; }
  .notice-error { background: rgba(244, 63, 94, 0.15); border: 1px solid var(--rose); color: var(--rose); display: block; }
</style>
</head>
<body>

<header>
  <h1>Live NSE & BSE Universal Stock Screener</h1>
  <p>Real-Time Price Returns, Technical 10/20/50/200 DMA & Balance Sheet Diagnostics for ANY Indian Stock.</p>
</header>

<div class="container">

  <!-- Search Section -->
  <div class="search-section">
    <div class="search-group">
      <input type="text" id="ticker-input" class="search-input" placeholder="Enter ANY Ticker (e.g., SUZLON, TCS, ZOMATO, KEC)" value="KEC" onkeydown="if(event.key==='Enter') fetchLiveStock()">
      <button class="btn" onclick="fetchLiveStock()">⚡ Search Any Stock</button>
    </div>
    <div class="quick-chips">
      <span style="font-size:0.82rem; color:var(--text-muted);">Quick Presets:</span>
      <span class="chip" onclick="quickSelect('KEC')">KEC</span>
      <span class="chip" onclick="quickSelect('GARUDA')">GARUDA</span>
      <span class="chip" onclick="quickSelect('OSWALPUMPS')">OSWALPUMPS</span>
      <span class="chip" onclick="quickSelect('TATAPOWER')">TATAPOWER</span>
      <span class="chip" onclick="quickSelect('RELIANCE')">RELIANCE</span>
      <span class="chip" onclick="quickSelect('TCS')">TCS</span>
      <span class="chip" onclick="quickSelect('ZOMATO')">ZOMATO</span>
      <span class="chip" onclick="quickSelect('SUZLON')">SUZLON</span>
    </div>
  </div>

  <div id="status-box" class="status-notice"></div>

  <!-- Profile Banner -->
  <div class="profile-banner">
    <div>
      <div class="profile-name" id="comp-name">KEC International Ltd</div>
      <div class="profile-meta" id="comp-desc">Live Market Data Stream</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.8rem; color:var(--text-muted);">Live Market Price</div>
      <div style="font-size:1.75rem; font-weight:800; color:var(--blue);" id="comp-curr-price">₹-</div>
    </div>
  </div>

  <!-- Technical Daily Moving Averages (10, 20, 50, 200 DMA) -->
  <div class="dma-section">
    <h3 style="font-size:1.05rem; color:var(--blue);">📊 Live Daily Moving Averages (DMA Technicals)</h3>
    <div class="dma-grid">
      <div class="dma-card">
        <span class="dma-title">10 DMA</span>
        <span class="dma-val" id="val-dma10">-</span>
        <span class="dma-diff" id="diff-dma10">-</span>
      </div>
      <div class="dma-card">
        <span class="dma-title">20 DMA</span>
        <span class="dma-val" id="val-dma20">-</span>
        <span class="dma-diff" id="diff-dma20">-</span>
      </div>
      <div class="dma-card">
        <span class="dma-title">50 DMA</span>
        <span class="dma-val" id="val-dma50">-</span>
        <span class="dma-diff" id="diff-dma50">-</span>
      </div>
      <div class="dma-card">
        <span class="dma-title">200 DMA</span>
        <span class="dma-val" id="val-dma200">-</span>
        <span class="dma-diff" id="diff-dma200">-</span>
      </div>
    </div>
  </div>

  <!-- Multi-Period Historical Price Returns -->
  <div class="returns-section">
    <h3 style="font-size:1.05rem; color:var(--blue);">📈 Real-Time Multi-Period Price Returns</h3>
    <div class="returns-grid">
      <div class="return-card">
        <div class="return-label">1 Day</div>
        <div class="return-val" id="ret-1d">-</div>
      </div>
      <div class="return-card">
        <div class="return-label">1 Week</div>
        <div class="return-val" id="ret-1w">-</div>
      </div>
      <div class="return-card">
        <div class="return-label">1 Month</div>
        <div class="return-val" id="ret-1m">-</div>
      </div>
      <div class="return-card">
        <div class="return-label">3 Months</div>
        <div class="return-val" id="ret-3m">-</div>
      </div>
      <div class="return-card">
        <div class="return-label">6 Months</div>
        <div class="return-val" id="ret-6m">-</div>
      </div>
      <div class="return-card">
        <div class="return-label">1 Year</div>
        <div class="return-val" id="ret-1y">-</div>
      </div>
      <div class="return-card">
        <div class="return-label">3 Years</div>
        <div class="return-val" id="ret-3y">-</div>
      </div>
      <div class="return-card">
        <div class="return-label">5 Years</div>
        <div class="return-val" id="ret-5y">-</div>
      </div>
    </div>
  </div>

  <!-- Fundamentals & Ratio Calculation Section -->
  <div class="sim-layout">
    
    <!-- Sliders -->
    <div class="card">
      <h3 style="margin-bottom:10px;">Fundamental Parameters (Interactive Sliders)</h3>
      
      <div class="section-title">Valuation & Equity</div>
      <div class="input-row">
        <label>Share Price (<span id="unit-curr">₹</span>): <span class="val" id="disp-p">-</span></label>
        <input type="range" id="inp-p" min="1" max="2500" value="100" step="0.5" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Earnings Per Share (EPS): <span class="val" id="disp-eps">-</span></label>
        <input type="range" id="inp-eps" min="0.1" max="150" step="0.2" value="10" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Book Value Per Share (BVPS): <span class="val" id="disp-bvps">-</span></label>
        <input type="range" id="inp-bvps" min="0.5" max="500" step="0.5" value="50" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Expected EPS Growth (%): <span class="val" id="disp-g">15%</span></label>
        <input type="range" id="inp-g" min="2" max="60" value="15" oninput="recalc()">
      </div>

      <div class="section-title">Cash Flow & Liquidity</div>
      <div class="input-row">
        <label>Cash & Equivalents ($/₹ Cr): <span class="val" id="disp-cash">-</span></label>
        <input type="range" id="inp-cash" min="0" max="50000" step="10" value="100" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Operating Cash Flow - CFO ($/₹ Cr): <span class="val" id="disp-cfo">-</span></label>
        <input type="range" id="inp-cfo" min="-1000" max="50000" step="10" value="150" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Free Cash Flow - FCF ($/₹ Cr): <span class="val" id="disp-fcf">-</span></label>
        <input type="range" id="inp-fcf" min="-1000" max="50000" step="10" value="120" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Current Liabilities ($/₹ Cr): <span class="val" id="disp-cl">-</span></label>
        <input type="range" id="inp-cl" min="10" max="50000" step="20" value="200" oninput="recalc()">
      </div>

      <div class="section-title">Capital Structure & Debt</div>
      <div class="input-row">
        <label>Total Debt ($/₹ Cr): <span class="val" id="disp-debt">-</span></label>
        <input type="range" id="inp-debt" min="0" max="50000" step="20" value="100" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Shareholders' Equity ($/₹ Cr): <span class="val" id="disp-eq">-</span></label>
        <input type="range" id="inp-eq" min="10" max="100000" step="20" value="500" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Operating Profit - EBIT ($/₹ Cr): <span class="val" id="disp-ebit">-</span></label>
        <input type="range" id="inp-ebit" min="10" max="50000" step="10" value="200" oninput="recalc()">
      </div>
      <div class="input-row">
        <label>Annual Interest Expense ($/₹ Cr): <span class="val" id="disp-int">-</span></label>
        <input type="range" id="inp-int" min="1" max="10000" step="1" value="20" oninput="recalc()">
      </div>
    </div>

    <!-- Live Evaluated Dashboard -->
    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <h3 style="margin-bottom:14px; color:var(--blue);">Real-Time Computed Indicators</h3>
        <div class="results-grid">
          
          <div class="res-card highlight">
            <div class="res-title">Cash Ratio (Strict)</div>
            <div class="res-formula">Cash ÷ Current Liab.</div>
            <div class="res-num" id="res-cr">-</div>
            <span class="status-badge" id="badge-cr">-</span>
          </div>

          <div class="res-card highlight">
            <div class="res-title">CFO-to-Net Profit</div>
            <div class="res-formula">CFO ÷ Net Income</div>
            <div class="res-num" id="res-cfonp">-</div>
            <span class="status-badge" id="badge-cfonp">-</span>
          </div>

          <div class="res-card highlight">
            <div class="res-title">FCF Yield</div>
            <div class="res-formula">FCF ÷ Market Cap</div>
            <div class="res-num" id="res-fcfy">-</div>
            <span class="status-badge" id="badge-fcfy">-</span>
          </div>

          <div class="res-card highlight">
            <div class="res-title">Cash Debt Coverage</div>
            <div class="res-formula">CFO ÷ Total Debt</div>
            <div class="res-num" id="res-cdc">-</div>
            <span class="status-badge" id="badge-cdc">-</span>
          </div>

          <div class="res-card">
            <div class="res-title">P/E Ratio</div>
            <div class="res-formula">Price ÷ EPS</div>
            <div class="res-num" id="res-pe">-</div>
            <span class="status-badge" id="badge-pe">-</span>
          </div>

          <div class="res-card">
            <div class="res-title">P/B Ratio</div>
            <div class="res-formula">Price ÷ BVPS</div>
            <div class="res-num" id="res-pb">-</div>
            <span class="status-badge" id="badge-pb">-</span>
          </div>

          <div class="res-card">
            <div class="res-title">PEG Ratio</div>
            <div class="res-formula">P/E ÷ Growth Rate</div>
            <div class="res-num" id="res-peg">-</div>
            <span class="status-badge" id="badge-peg">-</span>
          </div>

          <div class="res-card">
            <div class="res-title">Debt-to-Equity</div>
            <div class="res-formula">Total Debt ÷ Equity</div>
            <div class="res-num" id="res-de">-</div>
            <span class="status-badge" id="badge-de">-</span>
          </div>

          <div class="res-card">
            <div class="res-title">ROCE</div>
            <div class="res-formula">EBIT ÷ Total Capital</div>
            <div class="res-num" id="res-roce">-</div>
            <span class="status-badge" id="badge-roce">-</span>
          </div>

          <div class="res-card">
            <div class="res-title">Interest Coverage Ratio</div>
            <div class="res-formula">EBIT ÷ Interest Exp</div>
            <div class="res-num" id="res-icr">-</div>
            <span class="status-badge" id="badge-icr">-</span>
          </div>

        </div>
      </div>
      <p style="font-size:0.8rem; color:var(--text-muted); margin-top:14px;">💡 <em>Calculated live for any Indian stock across 5-year historical exchange candles.</em></p>
    </div>
  </div>

</div>

<script>
function quickSelect(ticker) {
  document.getElementById('ticker-input').value = ticker;
  fetchLiveStock();
}

function showStatus(text, type) {
  const box = document.getElementById('status-box');
  box.className = 'status-notice ' + type;
  box.innerText = text;
}

function setDMARow(idVal, idDiff, dmaValue, currentPrice, currency) {
  const elVal = document.getElementById(idVal);
  const elDiff = document.getElementById(idDiff);
  
  if (dmaValue === null || dmaValue === undefined) {
    elVal.innerText = "N/A";
    elDiff.innerText = "Insufficient Data";
    elDiff.className = "dma-diff neutral";
    return;
  }
  
  elVal.innerText = `${currency}${dmaValue.toFixed(2)}`;
  const diff = ((currentPrice - dmaValue) / dmaValue) * 100;
  
  if (diff >= 0) {
    elDiff.innerText = `+${diff.toFixed(2)}% Above`;
    elDiff.className = "dma-diff pos";
  } else {
    elDiff.innerText = `${diff.toFixed(2)}% Below`;
    elDiff.className = "dma-diff neg";
  }
}

function setReturnCard(id, val) {
  const el = document.getElementById(id);
  if (val === null || val === undefined) {
    el.innerText = "N/A";
    el.className = "return-val neutral";
  } else if (val >= 0) {
    el.innerText = `+${val.toFixed(2)}%`;
    el.className = "return-val pos";
  } else {
    el.innerText = `${val.toFixed(2)}%`;
    el.className = "return-val neg";
  }
}

async function fetchLiveStock() {
  const sym = document.getElementById('ticker-input').value.trim().toUpperCase();
  showStatus(`Fetching live market data, returns & DMAs for ${sym}...`, "notice-loading");

  try {
    const res = await fetch(`/api/stock?symbol=${encodeURIComponent(sym)}`);
    const data = await res.json();

    if (data.error) {
      showStatus(`❌ ${data.error}`, "notice-error");
      return;
    }

    document.getElementById('comp-name').innerText = data.name;
    document.getElementById('comp-desc').innerText = `${data.sector} • ${data.symbol}`;
    document.getElementById('comp-curr-price').innerText = `${data.currency}${data.price.toFixed(2)}`;
    document.getElementById('unit-curr').innerText = data.currency;

    // Render DMAs
    setDMARow('val-dma10', 'diff-dma10', data.dma10, data.price, data.currency);
    setDMARow('val-dma20', 'diff-dma20', data.dma20, data.price, data.currency);
    setDMARow('val-dma50', 'diff-dma50', data.dma50, data.price, data.currency);
    setDMARow('val-dma200', 'diff-dma200', data.dma200, data.price, data.currency);

    // Render Returns
    setReturnCard('ret-1d', data.ret['1d']);
    setReturnCard('ret-1w', data.ret['1w']);
    setReturnCard('ret-1m', data.ret['1m']);
    setReturnCard('ret-3m', data.ret['3m']);
    setReturnCard('ret-6m', data.ret['6m']);
    setReturnCard('ret-1y', data.ret['1y']);
    setReturnCard('ret-3y', data.ret['3y']);
    setReturnCard('ret-5y', data.ret['5y']);

    // Set Sliders
    setSlider('inp-p', data.price, Math.max(1, data.price * 0.2), data.price * 3);
    setSlider('inp-eps', data.eps, Math.max(0.1, data.eps * 0.2), Math.max(10, data.eps * 3));
    setSlider('inp-bvps', data.bvps, Math.max(0.5, data.bvps * 0.2), Math.max(10, data.bvps * 3));
    setSlider('inp-cash', data.cash / 1e7, 0, Math.max(100, (data.cash / 1e7) * 3));
    setSlider('inp-cfo', data.cfo / 1e7, Math.min(-100, (data.cfo / 1e7) * 2), Math.max(100, (data.cfo / 1e7) * 3));
    setSlider('inp-fcf', data.fcf / 1e7, Math.min(-100, (data.fcf / 1e7) * 2), Math.max(100, (data.fcf / 1e7) * 3));
    setSlider('inp-cl', data.currentLiab / 1e7, 10, Math.max(100, (data.currentLiab / 1e7) * 3));
    setSlider('inp-debt', data.totalDebt / 1e7, 0, Math.max(50, (data.totalDebt / 1e7) * 3));
    setSlider('inp-eq', data.equity / 1e7, 10, Math.max(100, (data.equity / 1e7) * 3));
    setSlider('inp-ebit', data.ebit / 1e7, 10, Math.max(50, (data.ebit / 1e7) * 3));
    setSlider('inp-int', data.intExp / 1e7, 1, Math.max(10, (data.intExp / 1e7) * 3));

    recalc();
    showStatus(`✅ Successfully fetched live data for ${data.name} (${data.symbol})`, "notice-success");
  } catch (err) {
    showStatus(`❌ Server Connection Failed: ${err.message}`, "notice-error");
  }
}

function setSlider(id, val, min, max) {
  const el = document.getElementById(id);
  el.min = Math.floor(min);
  el.max = Math.ceil(max);
  el.value = val;
}

function recalc() {
  const p = parseFloat(document.getElementById('inp-p').value);
  const eps = parseFloat(document.getElementById('inp-eps').value);
  const bvps = parseFloat(document.getElementById('inp-bvps').value);
  const g = parseFloat(document.getElementById('inp-g').value);
  
  const cash = parseFloat(document.getElementById('inp-cash').value);
  const cfo = parseFloat(document.getElementById('inp-cfo').value);
  const fcf = parseFloat(document.getElementById('inp-fcf').value);
  const cl = parseFloat(document.getElementById('inp-cl').value);

  const debt = parseFloat(document.getElementById('inp-debt').value);
  const eq = parseFloat(document.getElementById('inp-eq').value);
  const ebit = parseFloat(document.getElementById('inp-ebit').value);
  const intExp = parseFloat(document.getElementById('inp-int').value);

  document.getElementById('disp-p').innerText = p.toFixed(2);
  document.getElementById('disp-eps').innerText = eps.toFixed(2);
  document.getElementById('disp-bvps').innerText = bvps.toFixed(2);
  document.getElementById('disp-g').innerText = g + '%';

  document.getElementById('disp-cash').innerText = cash.toLocaleString();
  document.getElementById('disp-cfo').innerText = cfo.toLocaleString();
  document.getElementById('disp-fcf').innerText = fcf.toLocaleString();
  document.getElementById('disp-cl').innerText = cl.toLocaleString();

  document.getElementById('disp-debt').innerText = debt.toLocaleString();
  document.getElementById('disp-eq').innerText = eq.toLocaleString();
  document.getElementById('disp-ebit').innerText = ebit.toLocaleString();
  document.getElementById('disp-int').innerText = intExp.toLocaleString();

  // Metrics
  const cashRatio = cl > 0 ? (cash / cl) : 0;
  const estNetProfit = Math.max(1, (ebit - intExp) * 0.75);
  const cfoToNet = estNetProfit > 0 ? (cfo / estNetProfit) : 0;
  const estShares = eq / bvps;
  const mcap = estShares * p;
  const fcfYield = mcap > 0 ? (fcf / mcap) * 100 : 0;
  const cashDebtCoverage = debt > 0 ? (cfo / debt) * 100 : 100;

  const pe = p / eps;
  const pb = p / bvps;
  const peg = pe / g;
  const de = eq > 0 ? debt / eq : 0;
  const roce = ((debt + eq) > 0) ? (ebit / (debt + eq)) * 100 : 0;
  const icr = intExp > 0 ? ebit / intExp : 99;

  // Badges
  document.getElementById('res-cr').innerText = cashRatio.toFixed(2) + 'x';
  setB('badge-cr', cashRatio >= 0.5 ? 'good' : (cashRatio >= 0.2 ? 'mod' : 'warn'), cashRatio >= 0.5 ? 'Cash Fortress' : (cashRatio >= 0.2 ? 'Moderate Buffer' : 'Low Buffer'));

  document.getElementById('res-cfonp').innerText = cfoToNet.toFixed(2) + 'x';
  setB('badge-cfonp', cfoToNet >= 1.0 ? 'good' : (cfoToNet >= 0.7 ? 'mod' : 'warn'), cfoToNet >= 1.0 ? 'Real Cash Profit' : (cfoToNet >= 0.7 ? 'Moderate Quality' : 'Paper Profit Alert'));

  document.getElementById('res-fcfy').innerText = (isFinite(fcfYield) ? fcfYield.toFixed(1) : '0.0') + '%';
  setB('badge-fcfy', fcfYield >= 5.0 ? 'good' : (fcfYield >= 2.0 ? 'mod' : 'warn'), fcfYield >= 5.0 ? 'High Cash Yield' : (fcfYield >= 2.0 ? 'Moderate Yield' : 'CapEx Intensive'));

  document.getElementById('res-cdc').innerText = (debt === 0 ? 'Debt Free' : cashDebtCoverage.toFixed(1) + '%');
  setB('badge-cdc', debt === 0 || cashDebtCoverage >= 35 ? 'good' : (cashDebtCoverage >= 15 ? 'mod' : 'warn'), debt === 0 ? 'Negligible Debt' : (cashDebtCoverage >= 35 ? 'Rapid Payoff' : (cashDebtCoverage >= 15 ? 'Manageable' : 'Slow Payoff Risk')));

  document.getElementById('res-pe').innerText = pe.toFixed(2) + 'x';
  setB('badge-pe', pe < 18 ? 'good' : (pe <= 35 ? 'mod' : 'warn'), pe < 18 ? 'Attractive' : (pe <= 35 ? 'Fair' : 'Premium'));

  document.getElementById('res-pb').innerText = pb.toFixed(2) + 'x';
  setB('badge-pb', pb < 2.5 ? 'good' : (pb <= 5.0 ? 'mod' : 'warn'), pb < 2.5 ? 'Low Multiple' : (pb <= 5.0 ? 'Normal Multiple' : 'High Multiple'));

  document.getElementById('res-peg').innerText = peg.toFixed(2);
  setB('badge-peg', peg <= 1.2 ? 'good' : (peg <= 2.0 ? 'mod' : 'warn'), peg <= 1.2 ? 'Undervalued Growth' : (peg <= 2.0 ? 'Fair Growth' : 'Priced In'));

  document.getElementById('res-de').innerText = de.toFixed(2);
  setB('badge-de', de <= 0.6 ? 'good' : (de <= 1.5 ? 'mod' : 'warn'), de <= 0.6 ? 'Safe Leverage' : (de <= 1.5 ? 'Moderate Debt' : 'High Debt'));

  document.getElementById('res-roce').innerText = roce.toFixed(1) + '%';
  setB('badge-roce', roce >= 15 ? 'good' : (roce >= 9 ? 'mod' : 'warn'), roce >= 15 ? 'Elite Compounding' : (roce >= 9 ? 'Moderate Compounding' : 'Low Return'));

  document.getElementById('res-icr').innerText = (icr > 50 ? '>50' : icr.toFixed(1)) + 'x';
  setB('badge-icr', icr >= 4.0 ? 'good' : (icr >= 2.0 ? 'mod' : 'warn'), icr >= 4.0 ? 'Fortress Solvency' : (icr >= 2.0 ? 'Adequate' : 'Vulnerable'));
}

function setB(id, cls, text) {
  const el = document.getElementById(id);
  el.className = 'status-badge ' + cls;
  el.innerText = text;
}

window.onload = function() {
  fetchLiveStock();
};
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
    
    # Try NSE first (.NS), then BSE (.BO), then raw symbol
    candidates = [f"{clean}.NS", f"{clean}.BO", clean] if is_india else [clean]
    
    hist = pd.DataFrame()
    info = {}
    resolved_ticker = clean
    
    for candidate in candidates:
        try:
            t = yf.Ticker(candidate)
            h = t.history(period="5y", interval="1d")
            if not h.empty and len(h) > 5:
                hist = h
                info = t.info
                resolved_ticker = candidate
                break
        except Exception:
            continue
            
    if hist.empty:
        return jsonify({"error": f"Symbol '{raw_sym}' not found on NSE or BSE. Please verify the ticker."}), 404
        
    prices = hist['Close'].dropna()
    current_p = float(prices.iloc[-1])
    
    # Calculate exact DMA levels
    dma10 = float(prices.rolling(10).mean().iloc[-1]) if len(prices) >= 10 else None
    dma20 = float(prices.rolling(20).mean().iloc[-1]) if len(prices) >= 20 else None
    dma50 = float(prices.rolling(50).mean().iloc[-1]) if len(prices) >= 50 else None
    dma200 = float(prices.rolling(200).mean().iloc[-1]) if len(prices) >= 200 else None
    
    # Returns helper function based on trading sessions (approx: 1w=5, 1m=21, 3m=63, 6m=126, 1y=252, 3y=756, 5y=1260)
    def calc_ret(days):
        if len(prices) > days:
            past_val = float(prices.iloc[-days-1])
            if past_val > 0:
                return round(((current_p - past_val) / past_val) * 100, 2)
        return None

    ret = {
        "1d": calc_ret(1),
        "1w": calc_ret(5),
        "1m": calc_ret(21),
        "3m": calc_ret(63),
        "6m": calc_ret(126),
        "1y": calc_ret(252),
        "3y": calc_ret(756),
        "5y": calc_ret(1260)
    }

    # Financial Fundamentals
    try:
        t = yf.Ticker(resolved_ticker)
        bs = t.balance_sheet
        cf = t.cashflow
        inc = t.income_stmt
        
        eps = info.get('trailingEps') or (current_p / 25.0)
        bvps = info.get('bookValue') or (current_p / 3.5)
        mcap = info.get('marketCap') or (current_p * 1e7)
        
        cfo = info.get('operatingCashflow') or (cf.loc['Operating Cash Flow'].iloc[0] if not cf.empty and 'Operating Cash Flow' in cf.index else (mcap * 0.08))
        fcf = info.get('freeCashflow') or (cfo - abs(info.get('capitalExpenditure', cfo * 0.2)))
        cash = info.get('totalCash') or (bs.loc['Cash And Cash Equivalents'].iloc[0] if not bs.empty and 'Cash And Cash Equivalents' in bs.index else (mcap * 0.05))
        debt = info.get('totalDebt') or (bs.loc['Total Debt'].iloc[0] if not bs.empty and 'Total Debt' in bs.index else (mcap * 0.02))
        currentLiab = (bs.loc['Current Liabilities'].iloc[0] if not bs.empty and 'Current Liabilities' in bs.index else (mcap * 0.06))
        equity = (bs.loc['Stockholders Equity'].iloc[0] if not bs.empty and 'Stockholders Equity' in bs.index else (mcap * 0.4))
        ebit = info.get('ebitda') or (inc.loc['EBIT'].iloc[0] if not inc.empty and 'EBIT' in inc.index else (mcap * 0.12))
        intExp = (inc.loc['Interest Expense'].iloc[0] if not inc.empty and 'Interest Expense' in inc.index else (debt * 0.08))
    except Exception:
        eps, bvps, mcap, cfo, fcf, cash, debt, currentLiab, equity, ebit, intExp = (
            current_p/25.0, current_p/3.5, current_p*1e7, current_p*1e6, current_p*7e5, 
            current_p*5e5, current_p*3e5, current_p*6e5, current_p*4e6, current_p*1.2e6, current_p*1e5
        )

    exchange_label = "BSE" if resolved_ticker.endswith('.BO') else "NSE"
    if not is_india:
        exchange_label = "NASDAQ"

    payload = {
        "name": info.get('longName') or clean,
        "symbol": f"{exchange_label}: {clean}",
        "sector": info.get('sector') or "Equity",
        "currency": "₹" if is_india else "$",
        "price": round(current_p, 2),
        "eps": round(float(eps), 2),
        "bvps": round(float(bvps), 2),
        "cfo": float(cfo),
        "fcf": float(fcf),
        "cash": float(cash),
        "totalDebt": float(debt),
        "currentLiab": float(currentLiab),
        "equity": float(equity),
        "ebit": float(ebit),
        "intExp": float(abs(intExp)),
        "dma10": round(dma10, 2) if dma10 else None,
        "dma20": round(dma20, 2) if dma20 else None,
        "dma50": round(dma50, 2) if dma50 else None,
        "dma200": round(dma200, 2) if dma200 else None,
        "ret": ret
    }
    return jsonify(payload)

if __name__ == '__main__':
    print("🚀 Universal Indian Stock Screener running at http://localhost:5000")
    app.run(port=5000, debug=True)
