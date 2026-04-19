```python?code_reference&code_event_index=2
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)


```
```text?code_stdout&code_event_index=2
Code executed successfully!
```
```python?code_reference&code_event_index=6
readme_content = """# ⚗️ Alchemy Screener v4.0 Ultra
**World's Best Multibagger Engine**

Alchemy Screener v4.0 Ultra is a state-of-the-art, research-backed financial screening engine designed to identify potential multibagger stocks. Built on a comprehensive 6-pillar architecture, the engine evaluates stocks using over 35 parameters derived directly from peer-reviewed academic research and proven investment frameworks. 

The tool provides an interactive, dark-mode Streamlit dashboard with rich data visualizations, intelligent multi-source data enrichment (yfinance, NSE/BSE APIs, Screener.in), and a dynamic scoring system.

---

## ✨ Key Features

* **🧪 Scientifically Grounded:** Fully implements findings from major financial papers, including **Yartseva 2025** (BCU CAFÉ Working Paper #33 on 464 US multibaggers) and **Gunasekaran 2024** (NSE+BSE multibaggers).
* **🏛️ 6-Pillar Architecture:** Scores stocks across Quality, Growth, Value, Capital Discipline, Size, and Safety.
* **⚡ Dual Execution Modes:**
    * **CSV Mode:** Upload custom exports from Screener.in for fast, offline scoring.
    * **Live Fetch Mode:** Upload an NSE Equity list, and the app will autonomously scrape, merge, and enrich financial data using `yfinance`, `jugaad-data`, and live exchange APIs.
* **📊 Interactive Dashboard:** Includes Radar charts, heatmaps, score histograms, and deep-dive stock analysis using `plotly`.
* **🚨 Smart Disqualifiers & Bonuses:** Automatically penalizes massive debt or high promoter pledging, while awarding bonus points for "Twin Engine" (Quality + Growth + Value) or "Prime Entry" (trading near 52-week lows) setups.
* **⚙️ Custom Weight Editor:** Adjust the scientific defaults through the UI or a `config.yaml` file to match your personal investment thesis.

---

## 🔬 The Methodology (6 Pillars)

The screener allocates a maximum of 100 base points across six fundamental pillars:

1.  **P1 Quality (20%):** ROIC, ROCE, ROA, FCF/PAT, Moat. *(Inspired by McKinsey, Yartseva, and AQR Quality-Minus-Junk)*
2.  **P2 Growth (15%):** 5-Year PAT CAGR, OPM Expansion, EPS Acceleration, Reinvestment Rate. *(Inspired by CANSLIM and Gunasekaran)*
3.  **P3 Value (28%):** Equity FCF Yield (Highest Weight), B/M, PE vs Historical, EV/EBITDA, EV/Sales. *(Driven by Yartseva's finding that FCF/P is the #1 multibagger predictor)*
4.  **P4 Capital Discipline (13%):** Investment Guard (Asset Growth ≤ EBITDA Growth), Capex Efficiency, Cash Conversion, Shareholder Yield. *(Yartseva's core finding on disciplined capital allocation)*
5.  **P5 Size (7%):** Market Cap Band, Institutional Gap (Undiscovery Alpha), Free Float. *(Fama-French SMB factor)*
6.  **P6 Safety (17%):** D/E Ratio, Piotroski F-Score, Interest Coverage, Promoter Pledging, Insider Conviction. *(Gunasekaran's finding that D/E is the strongest Indian predictor)*

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```
```text?code_stdout&code_event_index=6
Code executed successfully!
```bash
   git clone [https://github.com/yourusername/alchemy-screener.git](https://github.com/yourusername/alchemy-screener.git)
   cd alchemy-screener
   ```

2. **Install dependencies:**
   Ensure you have Python 3.8+ installed. Install the required packages via `pip`:
   ```bash
   pip install streamlit pandas numpy yfinance plotly beautifulsoup4 requests jugaad-data pyyaml
   ```

3. **Run the Screener:**
   ```bash
   streamlit run alchemy_screener_v40_ultra.py
   ```

---

## 📖 How to Use

### Method A: Offline CSV Mode (Recommended for deep fundamental analysis)
1. Go to [Screener.in](https://www.screener.in/).
2. Run a custom query (e.g., `Market Capitalization > 100 AND Return on capital employed > 5 AND Piotroski score > 3`).
3. Click **Export to Excel/CSV**.
4. Upload the downloaded file(s) into the sidebar of the Alchemy Screener app.

### Method B: Live Fetch Mode
1. Upload an official NSE Equity List CSV (must contain `SYMBOL`, `NAME OF COMPANY`, and `SERIES` columns).
2. The engine will utilize `yfinance` parallel fetching (safeguarded against rate-limiting) and enrich missing data via NSE APIs and web scrapers.
3. Review your filtered, scored list of prospective multibaggers!

---

## ⚠️ Disclaimer
**For Educational and Research Purposes Only.**
Alchemy Screener v4.0 Ultra is an open-source financial analysis tool. It does not constitute financial advice, investment recommendations, or an offer to buy/sell securities. Always perform your own due diligence or consult a certified financial advisor before making any investment decisions. The developers are not responsible for any financial losses incurred.
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)


```
Your Markdown file is ready
[file-tag: code-generated-file-0-1776612005157188855]

You can download the `README.md` file using the attachment link above.
