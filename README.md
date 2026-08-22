# Universal Live Stock Fundamentals & Valuation Screener

A financial dashboard that automatically extracts balance sheets, cash flow metrics, real-time prices, and multi-period daily moving average charts for Indian (NSE/BSE) and Global stocks.

## Features
- **Real-Time Data Extraction**: Automatically extracts EPS, BVPS, Debt, Cash, CFO, FCF, and Operating Margins using `yfinance`.
- **Dual-Mode Technical Charts**: Toggle between a clean raw area line chart and an advanced technical candlestick terminal (50/100/200 DMA + RSI).
- **Cash Flow Health Check**: Evaluates Cash Ratio (strict liquidity), CFO-to-Net Profit (earnings quality), and Free Cash Flow Yield.
- **Sensitivity Sliders**: Stress-test valuations by adjusting margins, debt levels, or interest rate spikes.

## Quick Start Guide

### 1. Clone or Download the Repository
```bash
git clone https://github.com/your-username/stock-screener.git
cd stock-screener
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python app.py
```

### 4. Open in Browser
Visit `http://localhost:5000` in your web browser.
