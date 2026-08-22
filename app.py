from flask import Flask, request, jsonify, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np
import os
import datetime

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pro Stock Screener, Technical Terminal & Financial Statements</title>
<script src="https://unpkg.com/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js"></script>
<style>
  :root {
    --bg: #080c14;
    --card: #111a2e;
    --border: #1f2c42;
    --text: #f8fafc;
    --muted: #94a3b8;
    --blue: #38bdf8;
    --green: #4ade80;
    --rose: #f43f5e;
    --amber: #fbbf24;
    --purple: #c084fc;
    --cyan: #22d3ee;
    --emerald: #10b981;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: var(--bg); color: var(--text); padding: 18px; min-height: 100vh; }
  .container { max-width: 1260px; margin: 0 auto; }
  
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 14px; }
  
  .search-bar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; justify-content: space-between; }
  .search-input { background: #080c14; border: 1px solid var(--border); color: #fff; padding: 10px 16px; border-radius: 8px; font-size: 0.95rem; width: 220px; text-transform: uppercase; font-weight: 700; outline: none; }
  .search-input:focus { border-color: var(--blue); }
  .btn { background: var(--blue); color: #080c14; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
  .btn:hover { opacity: 0.9; }
  .chips { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
  .chip { background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.25); color: var(--blue); padding: 4px 10px; border-radius: 999px; font-size: 0.78rem; cursor: pointer; font-weight: 600; }
  .chip:hover { background: var(--blue); color: #080c14; }

  .header-banner { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
  .price-large { font-size: 1.85rem; font-weight: 800; color: var(--blue); }

  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
  @media(max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }

  .box-title { font-size: 0.92rem; font-weight: 700; color: var(--cyan); margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; }
  .bullet-list { list-style: none; }
  .bullet-list li { margin-bottom: 8px; font-size: 0.86rem; line-height: 1.45; color: #cbd5e1; position: relative; padding-left: 16px; }
  .bullet-list li::before { content: "▪"; color: var(--blue); position: absolute; left: 0; font-size: 1rem; top: -1px; }

  /* Brokerage Table */
  .brokerage-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.82rem; }
  .brokerage-table th { background: rgba(8, 12, 20, 0.8); color: var(--muted); text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); font-weight: 700; text-transform: uppercase; }
  .brokerage-table td { padding: 9px 10px; border-bottom: 1px solid rgba(31, 44, 66, 0.5); color: #cbd5e1; }
  .brokerage-table tr:last-child td { border-bottom: none; }
  .report-link { color: var(--blue); text-decoration: none; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; }
  .report-link:hover { text-decoration: underline; color: var(--cyan); }
  .view-more-btn { background: #080c14; border: 1px solid var(--border); color: var(--blue); padding: 7px 14px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; cursor: pointer; margin-top: 10px; width: 100%; transition: 0.2s; }
  .view-more-btn:hover { background: rgba(56, 189, 248, 0.1); border-color: var(--blue); }

  /* AI Trade & Pattern Box */
  .ai-trade-box { background: linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(74, 222, 128, 0.08)); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 14px; }
  .trade-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 10px; }
  @media(max-width: 800px) { .trade-grid { grid-template-columns: repeat(2, 1fr); } }

  .pattern-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin-top: 12px; }
  @media(max-width: 900px) { .pattern-grid { grid-template-columns: repeat(3, 1fr); } }
  @media(max-width: 550px) { .pattern-grid { grid-template-columns: repeat(2, 1fr); } }
  
  .pattern-card { background: rgba(8, 12, 20, 0.9); border: 1px solid var(--border); border-radius: 6px; padding: 8px; text-align: center; }
  .pattern-card .p-title { font-size: 0.7rem; color: var(--muted); font-weight: 700; }
  .pattern-card .p-val { font-size: 0.88rem; font-weight: 800; margin-top: 2px; }

  /* Chart Controls */
  .chart-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
  .btn-group { display: flex; background: #080c14; border: 1px solid var(--border); border-radius: 8px; padding: 2px; gap: 2px; }
  .tool-btn { background: transparent; border: none; color: var(--muted); padding: 5px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; cursor: pointer; transition: 0.2s; }
  .tool-btn.active { background: var(--blue); color: #080c14; }
  .tool-btn.toggle.on { background: rgba(56, 189, 248, 0.25); color: var(--blue); border: 1px solid var(--blue); }

  #main-chart { width: 100%; height: 380px; border-radius: 8px; overflow: hidden; background: #080c14; border: 1px solid var(--border); }
  #rsi-chart { width: 100%; height: 130px; border-radius: 8px; overflow: hidden; background: #080c14; border: 1px solid var(--border); margin-top: 8px; display: none; }

  /* Toggle Accordion Bars */
  .action-toggle-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #111a2e;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 13px 18px;
    cursor: pointer;
    margin-bottom: 14px;
    user-select: none;
    transition: 0.2s;
  }
  .action-toggle-bar:hover { border-color: var(--blue); background: rgba(56, 189, 248, 0.05); }
  .action-toggle-bar.primary { border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.06); }
  .toggle-title { font-size: 0.92rem; font-weight: 700; color: var(--blue); display: flex; align-items: center; gap: 8px; }
  .toggle-icon { font-size: 1.1rem; color: var(--cyan); transition: transform 0.3s; }
  .toggle-icon.open { transform: rotate(180deg); }

  /* Collapsible Panels */
  .collapse-panel {
    display: none;
    background: #111a2e;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
  }

  /* Screener Financial Statement Tabs */
  .screener-tabs { display: flex; gap: 6px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 14px; flex-wrap: wrap; }
  .screener-tab-btn { background: #080c14; border: 1px solid var(--border); color: var(--muted); padding: 7px 14px; border-radius: 6px; font-size: 0.82rem; font-weight: 700; cursor: pointer; transition: 0.2s; }
  .screener-tab-btn.active { background: var(--blue); color: #080c14; border-color: var(--blue); }

  .screener-table-wrapper { overflow-x: auto; margin-top: 10px; }
  .screener-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  .screener-table th { background: #080c14; color: var(--muted); padding: 9px 12px; text-align: right; border: 1px solid var(--border); font-weight: 700; white-space: nowrap; }
  .screener-table th:first-child { text-align: left; position: sticky; left: 0; background: #080c14; }
  .screener-table td { padding: 8px 12px; text-align: right; border: 1px solid rgba(31, 44, 66, 0.6); color: #cbd5e1; white-space: nowrap; }
  .screener-table td.metric-name { text-align: left; font-weight: 600; color: #f8fafc; position: sticky; left: 0; background: #111a2e; }
  .screener-table tr:hover td { background: rgba(56, 189, 248, 0.05); }

  /* Sensitivity Simulator */
  .sim-layout { display: grid; grid-template-columns: 1fr 1.25fr; gap: 18px; }
  @media(max-width: 900px) { .sim-layout { grid-template-columns: 1fr; } }
  
  .input-row { margin-bottom: 10px; }
  .input-row label { display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--muted); margin-bottom: 4px; }
  .input-row span.val { color: var(--blue); font-weight: 700; }
  input[type="range"] { width: 100%; accent-color: var(--blue); cursor: pointer; }
  .section-title { font-size: 0.82rem; font-weight: 700; color: var(--emerald); text-transform: uppercase; letter-spacing: 0.05em; margin: 10px 0 5px 0; border-bottom: 1px solid var(--border); padding-bottom: 3px; }

  .results-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  @media (max-width: 550px) { .results-grid { grid-template-columns: 1fr; } }

  .res-card { background: rgba(8, 12, 20, 0.85); border: 1px solid var(--border); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; justify-content: space-between; }
  .res-card.highlight { border-color: rgba(52, 211, 153, 0.4); background: rgba(16, 185, 129, 0.05); }
  .res-title { font-size: 0.78rem; color: var(--muted); font-weight: 600; }
  .res-formula { font-size: 0.68rem; color: var(--cyan); font-family: monospace; }
  .res-num { font-size: 1.15rem; font-weight: 800; margin: 3px 0; }
  .status-badge { font-size: 0.68rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: inline-block; width: fit-content; }
  
  .good { background: rgba(74, 222, 128, 0.2); color: var(--green); }
  .mod { background: rgba(251, 191, 36, 0.2); color: var(--amber); }
  .warn { background: rgba(244, 63, 94, 0.2); color: var(--rose); }

  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
  .grid-8 { display: grid; grid-template-columns: repeat(8, 1fr); gap: 8px; }
  @media(max-width: 900px) { .grid-4 { grid-template-columns: repeat(2, 1fr); } .grid-8 { grid-template-columns: repeat(4, 1fr); } }
  @media(max-width: 550px) { .grid-8 { grid-template-columns: repeat(2, 1fr); } }

  .stat-card { background: rgba(8, 12, 20, 0.85); border: 1px solid var(--border); border-radius: 8px; padding: 12px; text-align: center; }
  .stat-title { font-size: 0.72rem; color: var(--muted); font-weight: 700; text-transform: uppercase; }
  .stat-val { font-size: 1.15rem; font-weight: 800; margin: 3px 0; }
  .pos { color: var(--green); } .neg { color: var(--rose); }

  /* News List */
  .news-item { padding: 8px 0; border-bottom: 1px solid rgba(31, 44, 66, 0.6); }
  .news-item:last-child { border-bottom: none; }
  .news-headline { font-size: 0.86rem; font-weight: 600; color: #f1f5f9; text-decoration: none; display: block; }
  .news-headline:hover { color: var(--blue); }
  .news-meta { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }

  .status-notice { padding: 8px 14px; border-radius: 6px; font-size: 0.82rem; margin-bottom: 12px; display: none; }
  .notice-loading { background: rgba(56, 189, 248, 0.15); border: 1px solid var(--blue); color: var(--blue); display: block; }
  .notice-success { background: rgba(74, 222, 128, 0.15); border: 1px solid var(--green); color: var(--green); display: block; }
  .notice-error { background: rgba(244, 63, 94, 0.15); border: 1px solid var(--rose); color: var(--rose); display: block; }
</style>
</head>
<body>
<div class="container">

  <!-- Search Bar with Multi-Stock Comparison Inputs -->
  <div class="card search-bar">
    <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
      <input type="text" id="ticker" class="search-input" placeholder="Primary Stock (e.g., KEC)" value="KEC">
      <input type="text" id="peer1" class="search-input" placeholder="Compare Stock 2 (e.g., TATAPOWER)" style="width:170px;" value="">
      <input type="text" id="peer2" class="search-input" placeholder="Compare Stock 3 (e.g., RELIANCE)" style="width:170px;" value="">
      <button class="btn" onclick="loadStock()">⚡ Run Analysis & Compare</button>
    </div>
    <div class="chips">
      <span style="font-size:0.75rem; color:var(--muted);">Popular:</span>
      <span class="chip" onclick="quickSelect('KEC')">KEC</span>
      <span class="chip" onclick="quickSelect('TATAPOWER')">TATAPOWER</span>
      <span class="chip" onclick="quickSelect('RELIANCE')">RELIANCE</span>
      <span class="chip" onclick="quickSelect('TCS')">TCS</span>
      <span class="chip" onclick="quickSelect('ZOMATO')">ZOMATO</span>
    </div>
  </div>

  <div id="status-box" class="status-notice"></div>

  <!-- Header Banner -->
  <div class="card header-banner">
    <div>
      <h2 id="name" style="font-size:1.35rem;">Loading...</h2>
      <p id="symbol" style="color:var(--muted); font-size:0.85rem;">-</p>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.75rem; color:var(--muted);">Live Market Price</div>
      <div class="price-large" id="price">-</div>
    </div>
  </div>

  <!-- Sector Performance & Multi-Stock Side-by-Side Comparison Matrix -->
  <div class="card">
    <div class="box-title">🏢 Sector Classification, Peer Performance & Side-by-Side Comparison</div>
    <div style="font-size:0.85rem; color:var(--muted); margin-bottom:10px;" id="sector-info-text">Sector: Loading... • Industry: Loading...</div>
    <div style="overflow-x:auto;">
      <table class="brokerage-table" id="comparison-table">
        <thead>
          <tr>
            <th>Metric / Stock</th>
            <th id="th-stock1" style="color:var(--blue);">Primary Stock</th>
            <th id="th-stock2" style="color:var(--purple);">Comparison Stock 2</th>
            <th id="th-stock3" style="color:var(--green);">Comparison Stock 3</th>
          </tr>
        </thead>
        <tbody id="comparison-table-body">
          <tr><td colspan="4" style="text-align:center; color:var(--muted);">Enter tickers above and click Search to compare peer fundamentals & performance.</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- AI Trade Setup, Advanced Technicals & Chart Pattern Changes -->
  <div class="card ai-trade-box">
    <div class="box-title">
      <span>🤖 AI Technical Pattern, Breakout & Trade Blueprint</span>
      <span id="breakout-badge" style="background:rgba(56,189,248,0.2); color:var(--blue); padding:3px 8px; border-radius:4px; font-size:0.75rem;">Detecting...</span>
    </div>
    <div style="font-size:0.86rem; color:#cbd5e1; margin-bottom:10px;" id="pattern-desc">Analyzing price structure...</div>
    
    <div class="trade-grid">
      <div class="stat-card">
        <div class="stat-title">Suggested Entry</div>
        <div class="stat-val" id="ai-entry" style="color:var(--blue);">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Target 1 (Base)</div>
        <div class="stat-val" id="ai-t1" style="color:var(--green);">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Target 2 (Breakout)</div>
        <div class="stat-val" id="ai-t2" style="color:var(--green);">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Stop Loss (Strict)</div>
        <div class="stat-val" id="ai-sl" style="color:var(--rose);">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Risk : Reward</div>
        <div class="stat-val" id="ai-rr" style="color:var(--amber);">-</div>
      </div>
    </div>

    <div class="pattern-grid">
      <div class="pattern-card"><div class="p-title">Candle Pattern</div><div class="p-val" id="p-candle" style="color:var(--blue);">-</div></div>
      <div class="pattern-card"><div class="p-title">Chart Structure</div><div class="p-val" id="p-structure" style="color:var(--purple);">-</div></div>
      <div class="pattern-card"><div class="p-title">MA Alignment</div><div class="p-val" id="p-cross" style="color:var(--green);">-</div></div>
      <div class="pattern-card"><div class="p-title">Bollinger Bands (20,2)</div><div class="p-val" id="p-bb" style="color:var(--cyan);">-</div></div>
      <div class="pattern-card"><div class="p-title">Volatility (ATR 14)</div><div class="p-val" id="p-atr" style="color:var(--amber);">-</div></div>
      <div class="pattern-card"><div class="p-title">Daily Pivot & Range</div><div class="p-val" id="p-pivot" style="color:var(--emerald);">-</div></div>
    </div>
  </div>

  <!-- Derivative Open Interest (OI) & PCR Engine -->
  <div class="card">
    <div class="box-title">
      <span>⚡ Derivative Open Interest (OI) & Directional Sentiment Predictor</span>
      <span id="oi-sentiment-badge" style="padding:3px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">-</span>
    </div>
    <div class="grid-4">
      <div class="stat-card"><div class="stat-title">Put-Call Ratio (PCR)</div><div class="stat-val" id="oi-pcr">-</div></div>
      <div class="stat-card"><div class="stat-title">Major Put OI (Key Support)</div><div class="stat-val" id="oi-support" style="color:var(--green);">-</div></div>
      <div class="stat-card"><div class="stat-title">Major Call OI (Key Resistance)</div><div class="stat-val" id="oi-resistance" style="color:var(--rose);">-</div></div>
      <div class="stat-card"><div class="stat-title">AI Directional Forecast</div><div class="stat-val" id="oi-prediction">-</div></div>
    </div>
    <div style="font-size:0.8rem; color:var(--muted); margin-top:8px;" id="oi-analysis-text">-</div>
  </div>

  <!-- Full Interactive Chart Terminal -->
  <div class="card">
    <div class="chart-toolbar">
      <div class="btn-group">
        <button id="btn-candles" class="tool-btn active" onclick="setChartType('candles')">🕯️ Candles</button>
        <button id="btn-area" class="tool-btn" onclick="setChartType('area')">📉 Area Line</button>
      </div>

      <div class="btn-group">
        <button class="tool-btn" onclick="setTimeframe('1mo')">1M</button>
        <button class="tool-btn" onclick="setTimeframe('6mo')">6M</button>
        <button class="tool-btn active" id="tf-1y" onclick="setTimeframe('1y')">1Y</button>
        <button class="tool-btn" onclick="setTimeframe('5y')">5Y</button>
      </div>

      <div class="btn-group">
        <button id="btn-dma10" class="tool-btn toggle" onclick="toggleIndicator('dma10')">10 DMA</button>
        <button id="btn-dma20" class="tool-btn toggle" onclick="toggleIndicator('dma20')">20 DMA</button>
        <button id="btn-dma50" class="tool-btn toggle on" onclick="toggleIndicator('dma50')">50 DMA</button>
        <button id="btn-dma200" class="tool-btn toggle on" onclick="toggleIndicator('dma200')">200 DMA</button>
        <button id="btn-vol" class="tool-btn toggle on" onclick="toggleIndicator('vol')">📊 Vol</button>
        <button id="btn-rsi" class="tool-btn toggle" onclick="toggleIndicator('rsi')">⚡ RSI(14)</button>
      </div>
    </div>

    <div id="main-chart"></div>
    <div id="rsi-chart"></div>
  </div>

  <!-- DMAs & Multi-Period Returns -->
  <div class="card">
    <h4 style="color:var(--blue); font-size:0.9rem; margin-bottom:10px;">📊 Technical Daily Moving Averages (DMAs)</h4>
    <div class="grid-4">
      <div class="stat-card"><div class="stat-title">10 DMA</div><div class="stat-val" id="dma10">-</div><div id="diff10" style="font-size:0.75rem; font-weight:700;">-</div></div>
      <div class="stat-card"><div class="stat-title">20 DMA</div><div class="stat-val" id="dma20">-</div><div id="diff20" style="font-size:0.75rem; font-weight:700;">-</div></div>
      <div class="stat-card"><div class="stat-title">50 DMA</div><div class="stat-val" id="dma50">-</div><div id="diff50" style="font-size:0.75rem; font-weight:700;">-</div></div>
      <div class="stat-card"><div class="stat-title">200 DMA</div><div class="stat-val" id="dma200">-</div><div id="diff200" style="font-size:0.75rem; font-weight:700;">-</div></div>
    </div>
  </div>

  <div class="card">
    <h4 style="color:var(--blue); font-size:0.9rem; margin-bottom:10px;">📈 Multi-Period Price Returns</h4>
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

  <!-- SINGLE BUTTON TOGGLE 1: COMPLETE SCREENER.IN STYLE FINANCIAL STATEMENTS -->
  <div class="action-toggle-bar primary" onclick="togglePanel('screener-financials-panel', 'screener-arrow')">
    <div class="toggle-title">
      <span>📊 Full Screener.in Financial Statements (Quarterly Results, P&L, Balance Sheet, Cash Flows & Ratios)</span>
      <span style="font-size:0.75rem; color:var(--muted); font-weight:normal;">(Click Button to View Complete Financials)</span>
    </div>
    <div class="toggle-icon" id="screener-arrow">▼</div>
  </div>

  <div class="collapse-panel" id="screener-financials-panel">
    <div class="screener-tabs">
      <button class="screener-tab-btn active" onclick="switchScreenerTab('tab-quarterly')">📅 Quarterly Results</button>
      <button class="screener-tab-btn" onclick="switchScreenerTab('tab-pnl')">📈 Profit & Loss (Annual)</button>
      <button class="screener-tab-btn" onclick="switchScreenerTab('tab-bs')">📑 Balance Sheet</button>
      <button class="screener-tab-btn" onclick="switchScreenerTab('tab-cf')">💵 Cash Flows</button>
      <button class="screener-tab-btn" onclick="switchScreenerTab('tab-ratios')">⚖️ Key Ratios & Shareholding</button>
    </div>

    <div id="tab-quarterly" class="screener-tab-content"><div class="screener-table-wrapper" id="quarterly-table-container">Loading quarterly filings...</div></div>
    <div id="tab-pnl" class="screener-tab-content" style="display:none;"><div class="screener-table-wrapper" id="pnl-table-container">Loading annual P&L...</div></div>
    <div id="tab-bs" class="screener-tab-content" style="display:none;"><div class="screener-table-wrapper" id="bs-table-container">Loading balance sheet...</div></div>
    <div id="tab-cf" class="screener-tab-content" style="display:none;"><div class="screener-table-wrapper" id="cf-table-container">Loading cash flow statements...</div></div>
    <div id="tab-ratios" class="screener-tab-content" style="display:none;"><div class="screener-table-wrapper" id="ratios-table-container">Loading ratios and shareholding...</div></div>
  </div>

  <!-- SINGLE BUTTON TOGGLE 2: SENSITIVITY SIMULATOR -->
  <div class="action-toggle-bar" onclick="togglePanel('fundamentals-collapse-panel', 'sim-arrow')">
    <div class="toggle-title">
      <span>🎛️ Interactive Valuation Multiples & Sensitivity Stress-Testing Simulator</span>
      <span style="font-size:0.75rem; color:var(--muted); font-weight:normal;">(Click Button to Expand Sliders & Metrics)</span>
    </div>
    <div class="toggle-icon" id="sim-arrow">▼</div>
  </div>

  <div class="collapse-panel" id="fundamentals-collapse-panel">
    <div class="grid-4" style="margin-bottom:16px;">
      <div class="stat-card"><div class="stat-title">Trailing P/E</div><div class="stat-val" id="pe">-</div></div>
      <div class="stat-card"><div class="stat-title">P/B Ratio</div><div class="stat-val" id="pb">-</div></div>
      <div class="stat-card"><div class="stat-title">EPS (TTM)</div><div class="stat-val" id="eps">-</div></div>
      <div class="stat-card"><div class="stat-title">Book Value (BVPS)</div><div class="stat-val" id="bvps">-</div></div>
    </div>

    <div class="sim-layout">
      <div>
        <div class="section-title">Valuation & Equity</div>
        <div class="input-row"><label>Share Price (<span id="unit-curr">₹</span>): <span class="val" id="disp-p">-</span></label><input type="range" id="inp-p" min="1" max="2500" value="100" step="0.5" oninput="recalc()"></div>
        <div class="input-row"><label>Earnings Per Share (EPS): <span class="val" id="disp-eps">-</span></label><input type="range" id="inp-eps" min="0.1" max="150" step="0.2" value="10" oninput="recalc()"></div>
        <div class="input-row"><label>Book Value Per Share (BVPS): <span class="val" id="disp-bvps">-</span></label><input type="range" id="inp-bvps" min="0.5" max="500" step="0.5" value="50" oninput="recalc()"></div>
        <div class="input-row"><label>Expected EPS Growth (%): <span class="val" id="disp-g">15%</span></label><input type="range" id="inp-g" min="2" max="60" value="15" oninput="recalc()"></div>

        <div class="section-title">Cash Flow & Liquidity</div>
        <div class="input-row"><label>Cash & Equivalents ($/₹ Cr): <span class="val" id="disp-cash">-</span></label><input type="range" id="inp-cash" min="0" max="50000" step="10" value="100" oninput="recalc()"></div>
        <div class="input-row"><label>Operating Cash Flow - CFO ($/₹ Cr): <span class="val" id="disp-cfo">-</span></label><input type="range" id="inp-cfo" min="-1000" max="50000" step="10" value="150" oninput="recalc()"></div>
        <div class="input-row"><label>Free Cash Flow - FCF ($/₹ Cr): <span class="val" id="disp-fcf">-</span></label><input type="range" id="inp-fcf" min="-1000" max="50000" step="10" value="120" oninput="recalc()"></div>
        <div class="input-row"><label>Current Liabilities ($/₹ Cr): <span class="val" id="disp-cl">-</span></label><input type="range" id="inp-cl" min="10" max="50000" step="20" value="200" oninput="recalc()"></div>

        <div class="section-title">Capital Structure & Debt</div>
        <div class="input-row"><label>Total Debt ($/₹ Cr): <span class="val" id="disp-debt">-</span></label><input type="range" id="inp-debt" min="0" max="50000" step="20" value="100" oninput="recalc()"></div>
        <div class="input-row"><label>Shareholders' Equity ($/₹ Cr): <span class="val" id="disp-eq">-</span></label><input type="range" id="inp-eq" min="10" max="100000" step="20" value="500" oninput="recalc()"></div>
        <div class="input-row"><label>Operating Profit - EBIT ($/₹ Cr): <span class="val" id="disp-ebit">-</span></label><input type="range" id="inp-ebit" min="10" max="50000" step="10" value="200" oninput="recalc()"></div>
        <div class="input-row"><label>Annual Interest Expense ($/₹ Cr): <span class="val" id="disp-int">-</span></label><input type="range" id="inp-int" min="1" max="10000" step="1" value="20" oninput="recalc()"></div>
      </div>

      <div>
        <div class="results-grid">
          <div class="res-card highlight"><div class="res-title">Cash Ratio (Strict)</div><div class="res-formula">Cash ÷ Current Liab.</div><div class="res-num" id="res-cr">-</div><span class="status-badge" id="badge-cr">-</span></div>
          <div class="res-card highlight"><div class="res-title">CFO-to-Net Profit</div><div class="res-formula">CFO ÷ Net Income</div><div class="res-num" id="res-cfonp">-</div><span class="status-badge" id="badge-cfonp">-</span></div>
          <div class="res-card highlight"><div class="res-title">FCF Yield</div><div class="res-formula">FCF ÷ Market Cap</div><div class="res-num" id="res-fcfy">-</div><span class="status-badge" id="badge-fcfy">-</span></div>
          <div class="res-card highlight"><div class="res-title">Cash Debt Coverage</div><div class="res-formula">CFO ÷ Total Debt</div><div class="res-num" id="res-cdc">-</div><span class="status-badge" id="badge-cdc">-</span></div>
          <div class="res-card"><div class="res-title">P/E Ratio</div><div class="res-formula">Price ÷ EPS</div><div class="res-num" id="res-pe">-</div><span class="status-badge" id="badge-pe">-</span></div>
          <div class="res-card"><div class="res-title">P/B Ratio</div><div class="res-formula">Price ÷ BVPS</div><div class="res-num" id="res-pb">-</div><span class="status-badge" id="badge-pb">-</span></div>
          <div class="res-card"><div class="res-title">PEG Ratio</div><div class="res-formula">P/E ÷ Growth Rate</div><div class="res-num" id="res-peg">-</div><span class="status-badge" id="badge-peg">-</span></div>
          <div class="res-card"><div class="res-title">Debt-to-Equity</div><div class="res-formula">Total Debt ÷ Equity</div><div class="res-num" id="res-de">-</div><span class="status-badge" id="badge-de">-</span></div>
          <div class="res-card"><div class="res-title">ROCE</div><div class="res-formula">EBIT ÷ Total Capital</div><div class="res-num" id="res-roce">-</div><span class="status-badge" id="badge-roce">-</span></div>
          <div class="res-card"><div class="res-title">Interest Coverage Ratio</div><div class="res-formula">EBIT ÷ Interest Exp</div><div class="res-num" id="res-icr">-</div><span class="status-badge" id="badge-icr">-</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Management Highlights & Firm-Wise Brokerage Reports Section -->
  <div class="grid-2">
    <div class="card" style="margin-bottom:0;">
      <div class="box-title">🎙️ Management Meeting Highlights & Strategic Outlook</div>
      <ul class="bullet-list" id="mgmt-highlights"><li>Loading latest earnings call takeaways and growth outlook...</li></ul>
    </div>

    <div class="card" style="margin-bottom:0;">
      <div class="box-title">🎯 Brokerage Firm-Wise Targets & Research Reports</div>
      <div style="overflow-x:auto;">
        <table class="brokerage-table">
          <thead>
            <tr><th>Brokerage Firm</th><th>Date</th><th>Rating</th><th>Target</th><th>Upside</th><th>Report</th></tr>
          </thead>
          <tbody id="brokerage-table-body">
            <tr><td colspan="6" style="text-align:center; color:var(--muted);">Loading brokerage coverage...</td></tr>
          </tbody>
        </table>
      </div>
      <button id="btn-view-more-reports" class="view-more-btn" onclick="toggleMoreBrokerageReports()" style="display:none;">➕ View More Brokerage Reports</button>
    </div>
  </div>

  <!-- Events & News Grid -->
  <div class="grid-2">
    <div class="card" style="margin-bottom:0;">
      <div class="box-title">📅 Major Upcoming Corporate Events</div>
      <ul class="bullet-list" id="events-list"><li>Loading corporate calendar & earnings announcements...</li></ul>
    </div>

    <div class="card" style="margin-bottom:0;">
      <div class="box-title">📰 Real-Time News & Market Headlines</div>
      <div id="news-container"><div style="color:var(--muted); font-size:0.85rem;">Scanning market news feed...</div></div>
    </div>
  </div>

</div>

<script>
let mainChart = null, rsiChart = null;
let priceSeries = null, volumeSeries = null, rsiSeries = null;
let dma10Series = null, dma20Series = null, dma50Series = null, dma200Series = null;

let chartType = 'candles';
let currentPeriod = '1y';
let indicators = { dma10: false, dma20: false, dma50: true, dma200: true, vol: true, rsi: false };
let stockData = null;

let isAllReportsShown = false;
let panelStates = {};

function togglePanel(panelId, arrowId) {
  panelStates[panelId] = !panelStates[panelId];
  const panel = document.getElementById(panelId);
  const arrow = document.getElementById(arrowId);
  panel.style.display = panelStates[panelId] ? 'block' : 'none';
  arrow.classList.toggle('open', panelStates[panelId]);
}

function switchScreenerTab(tabId) {
  document.querySelectorAll('.screener-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.screener-tab-content').forEach(c => c.style.display = 'none');
  event.target.classList.add('active');
  document.getElementById(tabId).style.display = 'block';
}

function toggleMoreBrokerageReports() {
  isAllReportsShown = !isAllReportsShown;
  renderBrokerageTable();
}

function renderBrokerageTable() {
  const tableBody = document.getElementById('brokerage-table-body');
  const btn = document.getElementById('btn-view-more-reports');
  tableBody.innerHTML = '';
  
  if (!stockData || !stockData.brokerage_reports || stockData.brokerage_reports.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--muted);">No institutional brokerage reports filed recently.</td></tr>';
    btn.style.display = 'none';
    return;
  }

  const reports = stockData.brokerage_reports;
  const showCount = isAllReportsShown ? reports.length : Math.min(5, reports.length);
  
  for (let i = 0; i < showCount; i++) {
    const r = reports[i];
    const tr = document.createElement('tr');
    const up = ((r.target - stockData.price) / stockData.price) * 100;
    const upClass = up >= 0 ? 'pos' : 'neg';
    tr.innerHTML = `
      <td style="font-weight:700; color:#f8fafc;">${r.firm}</td>
      <td style="color:var(--muted);">${r.date}</td>
      <td><span style="color:${r.rating.includes('Buy') || r.rating.includes('Outperform') ? 'var(--green)' : 'var(--amber)'}; font-weight:700;">${r.rating}</span></td>
      <td style="font-weight:700;">₹${r.target.toFixed(2)}</td>
      <td class="${upClass}" style="font-weight:700;">${up >= 0 ? '+' : ''}${up.toFixed(1)}%</td>
      <td><a href="${r.url}" target="_blank" class="report-link">📄 View Report ↗</a></td>
    `;
    tableBody.appendChild(tr);
  }

  if (reports.length > 5) {
    btn.style.display = 'block';
    btn.innerText = isAllReportsShown ? '➖ Show Top 5 Reports Only' : `➕ View More Brokerage Reports (${reports.length - 5} more)`;
  } else {
    btn.style.display = 'none';
  }
}

function quickSelect(t) {
  document.getElementById('ticker').value = t;
  document.getElementById('peer1').value = '';
  document.getElementById('peer2').value = '';
  loadStock();
}

function showStatus(text, type) {
  const box = document.getElementById('status-box');
  box.className = 'status-notice ' + type;
  box.innerText = text;
}

function setTimeframe(period) {
  currentPeriod = period;
  document.querySelectorAll('.chart-toolbar .btn-group:nth-child(2) .tool-btn').forEach(btn => {
    btn.classList.toggle('active', btn.innerText.toLowerCase() === period.replace('mo','m'));
  });
  loadStock();
}

function setChartType(type) {
  chartType = type;
  document.getElementById('btn-candles').classList.toggle('active', type === 'candles');
  document.getElementById('btn-area').classList.toggle('active', type === 'area');
  renderAll();
}

function toggleIndicator(ind) {
  indicators[ind] = !indicators[ind];
  const btn = document.getElementById('btn-' + ind);
  if (btn) btn.classList.toggle('on', indicators[ind]);
  renderAll();
}

function initCharts() {
  const container = document.getElementById('main-chart');
  container.innerHTML = '';
  
  mainChart = LightweightCharts.createChart(container, {
    width: container.clientWidth,
    height: 380,
    layout: { background: { color: '#080c14' }, textColor: '#94a3b8' },
    grid: { vertLines: { color: 'rgba(31, 44, 66, 0.4)' }, horzLines: { color: 'rgba(31, 44, 66, 0.4)' } },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    rightPriceScale: { borderColor: '#1f2c42' },
    timeScale: { borderColor: '#1f2c42', timeVisible: false }
  });

  const rsiBox = document.getElementById('rsi-chart');
  if (indicators.rsi) {
    rsiBox.style.display = 'block';
    rsiBox.innerHTML = '';
    rsiChart = LightweightCharts.createChart(rsiBox, {
      width: rsiBox.clientWidth,
      height: 130,
      layout: { background: { color: '#080c14' }, textColor: '#94a3b8' },
      grid: { vertLines: { color: 'rgba(31, 44, 66, 0.3)' }, horzLines: { color: 'rgba(31, 44, 66, 0.3)' } },
      rightPriceScale: { borderColor: '#1f2c42', scaleMargins: { top: 0.1, bottom: 0.1 } },
      timeScale: { borderColor: '#1f2c42', timeVisible: false }
    });

    mainChart.timeScale().subscribeVisibleTimeRangeChange(tr => {
      if (rsiChart && tr) rsiChart.timeScale().setVisibleRange(tr);
    });
  } else {
    rsiBox.style.display = 'none';
    rsiChart = null;
  }

  window.addEventListener('resize', () => {
    if (mainChart) mainChart.applyOptions({ width: container.clientWidth });
    if (rsiChart) rsiChart.applyOptions({ width: container.clientWidth });
  });
}

function renderAll() {
  if (!stockData || !stockData.candles || stockData.candles.length === 0) return;
  initCharts();

  if (chartType === 'candles') {
    priceSeries = mainChart.addCandlestickSeries({
      upColor: '#4ade80', downColor: '#f43f5e',
      borderUpColor: '#4ade80', borderDownColor: '#f43f5e',
      wickUpColor: '#4ade80', wickDownColor: '#f43f5e'
    });
    priceSeries.setData(stockData.candles);
  } else {
    priceSeries = mainChart.addAreaSeries({
      topColor: 'rgba(56, 189, 248, 0.35)', bottomColor: 'rgba(56, 189, 248, 0.0)',
      lineColor: '#38bdf8', lineWidth: 2
    });
    priceSeries.setData(stockData.area);
  }

  if (indicators.vol && stockData.volume) {
    volumeSeries = mainChart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      scaleMargins: { top: 0.8, bottom: 0 }
    });
    volumeSeries.setData(stockData.volume);
  }

  if (indicators.dma10 && stockData.dma10_line) {
    dma10Series = mainChart.addLineSeries({ color: '#38bdf8', lineWidth: 1.5, title: '10 DMA' });
    dma10Series.setData(stockData.dma10_line);
  }
  if (indicators.dma20 && stockData.dma20_line) {
    dma20Series = mainChart.addLineSeries({ color: '#c084fc', lineWidth: 1.5, title: '20 DMA' });
    dma20Series.setData(stockData.dma20_line);
  }
  if (indicators.dma50 && stockData.dma50_line) {
    dma50Series = mainChart.addLineSeries({ color: '#4ade80', lineWidth: 1.5, title: '50 DMA' });
    dma50Series.setData(stockData.dma50_line);
  }
  if (indicators.dma200 && stockData.dma200_line) {
    dma200Series = mainChart.addLineSeries({ color: '#fbbf24', lineWidth: 2, title: '200 DMA' });
    dma200Series.setData(stockData.dma200_line);
  }

  if (indicators.rsi && stockData.rsi_line && rsiChart) {
    rsiSeries = rsiChart.addLineSeries({ color: '#c084fc', lineWidth: 2, title: 'RSI(14)' });
    rsiSeries.setData(stockData.rsi_line);

    const rsi70 = rsiChart.addLineSeries({ color: 'rgba(244, 63, 94, 0.4)', lineWidth: 1, lineStyle: 2 });
    const rsi30 = rsiChart.addLineSeries({ color: 'rgba(74, 222, 128, 0.4)', lineWidth: 1, lineStyle: 2 });
    
    rsi70.setData(stockData.candles.map(c => ({ time: c.time, value: 70 })));
    rsi30.setData(stockData.candles.map(c => ({ time: c.time, value: 30 })));

    rsiChart.timeScale().fitContent();
  }

  mainChart.timeScale().fitContent();
}

async function loadStock() {
  const sym = document.getElementById('ticker').value.trim().toUpperCase();
  const peer1 = document.getElementById('peer1').value.trim().toUpperCase();
  const peer2 = document.getElementById('peer2').value.trim().toUpperCase();
  
  showStatus(`Running live queries for ${sym}${peer1 ? ', '+peer1 : ''}${peer2 ? ', '+peer2 : ''}...`, 'notice-loading');

  let url = `/api/stock?symbol=${encodeURIComponent(sym)}&period=${encodeURIComponent(currentPeriod)}`;
  if (peer1) url += `&peer1=${encodeURIComponent(peer1)}`;
  if (peer2) url += `&peer2=${encodeURIComponent(peer2)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();

    if (data.error) {
      showStatus(`❌ ${data.error}`, 'notice-error');
      return;
    }

    stockData = data;
    document.getElementById('name').innerText = data.name;
    document.getElementById('symbol').innerText = data.symbol;
    document.getElementById('price').innerText = `₹${data.price.toFixed(2)}`;
    document.getElementById('unit-curr').innerText = data.currency;

    // Sector & Comparison Table
    document.getElementById('sector-info-text').innerText = `Sector: ${data.sector} • Industry: ${data.industry}`;
    document.getElementById('th-stock1').innerText = data.comparison.stock1.name + ` (${data.comparison.stock1.ticker})`;
    
    const th2 = document.getElementById('th-stock2');
    const th3 = document.getElementById('th-stock3');
    th2.style.display = data.comparison.stock2 ? 'table-cell' : 'none';
    th3.style.display = data.comparison.stock3 ? 'table-cell' : 'none';
    if (data.comparison.stock2) th2.innerText = data.comparison.stock2.name + ` (${data.comparison.stock2.ticker})`;
    if (data.comparison.stock3) th3.innerText = data.comparison.stock3.name + ` (${data.comparison.stock3.ticker})`;

    const compBody = document.getElementById('comparison-table-body');
    compBody.innerHTML = '';
    
    const metrics = [
      { label: "Current Price", key: "price", pre: "₹" },
      { label: "Market Cap", key: "mcap", pre: "₹ ", post: " Cr" },
      { label: "Trailing P/E", key: "pe", post: "x" },
      { label: "P/B Ratio", key: "pb", post: "x" },
      { label: "ROCE (%)", key: "roce", post: "%" },
      { label: "ROE (%)", key: "roe", post: "%" },
      { label: "Debt / Equity", key: "de" },
      { label: "1Y Return (%)", key: "ret_1y", post: "%" }
    ];

    metrics.forEach(m => {
      const tr = document.createElement('tr');
      let html = `<td style="font-weight:700; color:#f8fafc;">${m.label}</td>`;
      
      const s1Val = data.comparison.stock1[m.key];
      html += `<td style="font-weight:700; color:var(--blue);">${s1Val !== null && s1Val !== undefined ? (m.pre||"") + s1Val.toLocaleString() + (m.post||"") : 'N/A'}</td>`;
      
      if (data.comparison.stock2) {
        const s2Val = data.comparison.stock2[m.key];
        html += `<td style="font-weight:700; color:var(--purple);">${s2Val !== null && s2Val !== undefined ? (m.pre||"") + s2Val.toLocaleString() + (m.post||"") : 'N/A'}</td>`;
      }
      if (data.comparison.stock3) {
        const s3Val = data.comparison.stock3[m.key];
        html += `<td style="font-weight:700; color:var(--green);">${s3Val !== null && s3Val !== undefined ? (m.pre||"") + s3Val.toLocaleString() + (m.post||"") : 'N/A'}</td>`;
      }
      tr.innerHTML = html;
      compBody.appendChild(tr);
    });

    // Populate Screener Financial Tables HTML
    document.getElementById('quarterly-table-container').innerHTML = data.screener_tables.quarterly;
    document.getElementById('pnl-table-container').innerHTML = data.screener_tables.pnl;
    document.getElementById('bs-table-container').innerHTML = data.screener_tables.bs;
    document.getElementById('cf-table-container').innerHTML = data.screener_tables.cf;
    document.getElementById('ratios-table-container').innerHTML = data.screener_tables.ratios;

    isAllReportsShown = false;
    renderBrokerageTable();

    // AI Pattern & Trade Setup
    document.getElementById('breakout-badge').innerText = data.ai_trade.breakout_status;
    document.getElementById('breakout-badge').style.background = data.ai_trade.is_bullish ? 'rgba(74, 222, 128, 0.2)' : 'rgba(244, 63, 94, 0.2)';
    document.getElementById('breakout-badge').style.color = data.ai_trade.is_bullish ? 'var(--green)' : 'var(--rose)';
    document.getElementById('pattern-desc').innerText = data.ai_trade.pattern_analysis;
    
    document.getElementById('ai-entry').innerText = `₹${data.ai_trade.entry_zone}`;
    document.getElementById('ai-t1').innerText = `₹${data.ai_trade.target_1}`;
    document.getElementById('ai-t2').innerText = `₹${data.ai_trade.target_2}`;
    document.getElementById('ai-sl').innerText = `₹${data.ai_trade.stop_loss}`;
    document.getElementById('ai-rr').innerText = data.ai_trade.risk_reward;

    // Advanced Technicals Details
    document.getElementById('p-candle').innerText = data.technicals_detailed.candle_pattern;
    document.getElementById('p-structure').innerText = data.technicals_detailed.chart_structure;
    document.getElementById('p-cross').innerText = data.technicals_detailed.ma_cross;
    document.getElementById('p-cross').style.color = data.technicals_detailed.ma_cross.includes('Golden') ? 'var(--green)' : (data.technicals_detailed.ma_cross.includes('Death') ? 'var(--rose)' : 'var(--blue)');
    document.getElementById('p-bb').innerText = `₹${data.technicals_detailed.bb_lower} - ₹${data.technicals_detailed.bb_upper}`;
    document.getElementById('p-atr').innerText = `₹${data.technicals_detailed.atr14.toFixed(2)} (${data.technicals_detailed.volatility_status})`;
    document.getElementById('p-pivot').innerText = `P: ₹${data.technicals_detailed.pivot.toFixed(1)} (S1: ₹${data.technicals_detailed.s1.toFixed(0)} | R1: ₹${data.technicals_detailed.r1.toFixed(0)})`;

    // OI & Sentiment Predictor
    document.getElementById('oi-sentiment-badge').innerText = data.oi_analysis.signal;
    document.getElementById('oi-sentiment-badge').style.background = data.oi_analysis.is_bullish ? 'rgba(74, 222, 128, 0.2)' : 'rgba(244, 63, 94, 0.2)';
    document.getElementById('oi-sentiment-badge').style.color = data.oi_analysis.is_bullish ? 'var(--green)' : 'var(--rose)';
    document.getElementById('oi-pcr').innerText = data.oi_analysis.pcr ? data.oi_analysis.pcr.toFixed(2) : 'N/A';
    document.getElementById('oi-support').innerText = `₹${data.oi_analysis.max_put_oi_strike}`;
    document.getElementById('oi-resistance').innerText = `₹${data.oi_analysis.max_call_oi_strike}`;
    document.getElementById('oi-prediction').innerText = data.oi_analysis.prediction;
    document.getElementById('oi-prediction').className = 'stat-val ' + (data.oi_analysis.is_bullish ? 'pos' : 'neg');
    document.getElementById('oi-analysis-text').innerText = data.oi_analysis.interpretation;

    // Base Valuation Ratios
    document.getElementById('pe').innerText = data.pe ? `${data.pe.toFixed(2)}x` : 'N/A';
    document.getElementById('pb').innerText = data.pb ? `${data.pb.toFixed(2)}x` : 'N/A';
    document.getElementById('eps').innerText = data.eps ? `₹${data.eps.toFixed(2)}` : 'N/A';
    document.getElementById('bvps').innerText = data.bvps ? `₹${data.bvps.toFixed(2)}` : 'N/A';

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

    const listEl = document.getElementById('mgmt-highlights');
    listEl.innerHTML = '';
    if (data.management_highlights && data.management_highlights.length > 0) {
      data.management_highlights.forEach(h => {
        const li = document.createElement('li');
        li.innerText = h;
        listEl.appendChild(li);
      });
    }

    const evList = document.getElementById('events-list');
    evList.innerHTML = '';
    if (data.events && data.events.length > 0) {
      data.events.forEach(e => {
        const li = document.createElement('li');
        li.innerText = e;
        evList.appendChild(li);
      });
    }

    const newsBox = document.getElementById('news-container');
    newsBox.innerHTML = '';
    if (data.news && data.news.length > 0) {
      data.news.forEach(n => {
        const div = document.createElement('div');
        div.className = 'news-item';
        div.innerHTML = `<a href="${n.link}" target="_blank" class="news-headline">${n.title}</a><div class="news-meta">${n.publisher} • ${n.time}</div>`;
        newsBox.appendChild(div);
      });
    }

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

    renderAll();
    showStatus(`✅ Live market feed, Screener financials & firm-wise targets loaded for ${data.name}.`, 'notice-success');
  } catch (e) {
    showStatus(`❌ Connection error: ${e.message}`, 'notice-error');
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

function setDmaCard(valId, diffId, dmaVal, curPrice) {
  const elV = document.getElementById(valId);
  const elD = document.getElementById(diffId);
  if (!dmaVal) {
    elV.innerText = 'N/A'; elD.innerText = '-'; elD.className = ''; return;
  }
  elV.innerText = `₹${dmaVal.toFixed(2)}`;
  const diff = ((curPrice - dmaVal) / dmaVal) * 100;
  elD.innerText = (diff >= 0 ? '+' : '') + diff.toFixed(2) + '% ' + (diff >= 0 ? 'Above' : 'Below');
  elD.className = diff >= 0 ? 'pos' : 'neg';
}

function setRet(id, val) {
  const el = document.getElementById(id);
  if (val === null || val === undefined) {
    el.innerText = 'N/A'; el.className = 'stat-val';
  } else {
    el.innerText = (val >= 0 ? '+' : '') + val.toFixed(2) + '%';
    el.className = 'stat-val ' + (val >= 0 ? 'pos' : 'neg');
  }
}

window.onload = loadStock;
</script>
</body>
</html>
