# -*- coding: utf-8 -*-
"""
Finance Chatbot Engine - Natural Language Interface for Finance Infrastructure
Uses keyword-based string matching with weighted scoring for intelligent responses.
Save this file as UTF-8 in VS Code: bottom-right corner > click encoding > Save with Encoding > UTF-8
"""

import re
from datetime import datetime
import random

# Knowledge Base - all emoji replaced with text alternatives to avoid charmap errors
FINANCE_KB = {
    "stock": {
        "keywords": ["stock", "stocks", "share", "shares", "equity", "nse", "bse", "sensex", "nifty", "market", "ipo", "demat"],
        "responses": [
            "[STOCKS] Stock Market Overview: Stocks represent ownership in a company. Key Indian indices include NSE Nifty 50 and BSE Sensex. To invest, you need a Demat + Trading account with brokers like Zerodha or Upstox.\n\nStocks are volatile short-term but historically give 12-15% CAGR over long periods. Start with index funds if you are new.",
            "[STOCKS] A stock is a unit of ownership in a company. When you buy shares, you become a part-owner. Prices change based on company earnings, market sentiment, and economic conditions.\n\nKey Metric - P/E Ratio = Price divided by EPS. A lower P/E may indicate the stock is undervalued.",
        ],
        "followups": ["Want to know about how to read stock prices?", "Should I explain P/E ratio?"]
    },
    "budget": {
        "keywords": ["budget", "budgeting", "expense", "expenses", "spending", "monthly", "plan", "50/30/20", "allocation", "track"],
        "responses": [
            "[BUDGET] The 50/30/20 Budget Rule:\n  50% -> Needs: rent, food, utilities, EMIs\n  30% -> Wants: dining, entertainment, shopping\n  20% -> Savings and investments\n\nFor Rs. 50,000 salary: Rs. 25,000 needs | Rs. 15,000 wants | Rs. 10,000 savings.",
            "[BUDGET] Budget Planning Steps:\n  1. List all income sources\n  2. Track every expense for 1 month\n  3. Categorize: fixed vs variable\n  4. Set limits per category\n  5. Use apps like Walnut or Money Manager\n\nGoal: spend less than you earn, invest the difference.",
        ],
        "followups": ["Want a sample monthly budget for Rs. 40,000 salary?", "Should I explain zero-based budgeting?"]
    },
    "loan": {
        "keywords": ["loan", "loans", "emi", "borrow", "borrowing", "interest", "debt", "credit", "home loan", "personal loan", "car loan"],
        "responses": [
            "[LOAN] EMI Formula: A = [P x R x (1+R)^N] / [(1+R)^N - 1]\n  P = Principal, R = Monthly Rate, N = Months\n\nExample: Rs. 10L loan at 9% for 20 years = Rs. 8,997/month EMI.\nLonger tenure = lower EMI but more total interest paid.",
            "[LOAN] Loan Types and Rates (2024):\n  Home Loan    : 8-9%    | 20-30 years\n  Car Loan     : 8-12%   | 5-7 years\n  Personal Loan: 10-18%  | 1-5 years\n  Education    : 9-11%   | 5-15 years\n\nAlways compare total cost (APR), not just the interest rate.",
        ],
        "followups": ["Should I compare fixed vs floating interest rates?", "Want tips to reduce EMI burden?"]
    },
    "investment": {
        "keywords": ["invest", "investment", "investments", "mutual fund", "sip", "fd", "fixed deposit", "ppf", "gold", "portfolio", "returns", "roi", "elss", "nps"],
        "responses": [
            "[INVEST] Investment Options - Returns vs Risk:\n  FD          : 6-7%   | Very Low risk\n  PPF         : 7.1%   | No risk\n  Debt MF     : 7-8%   | Low risk\n  Balanced MF : 9-12%  | Medium risk\n  Equity MF   : 12-15% | High risk\n\nDiversify across asset classes for best results!",
            "[INVEST] SIP (Systematic Investment Plan):\nInvest a fixed amount monthly in mutual funds.\n\nBenefits:\n  - Rupee Cost Averaging: buy more units when prices drop\n  - Power of Compounding: returns grow exponentially\n  - Discipline: automatic investing habit\n\nRs. 1,000/month at 12% for 20 years = Rs. 9.9 Lakhs!",
        ],
        "followups": ["Want to understand lump sum vs SIP?", "Should I explain large-cap vs mid-cap funds?"]
    },
    "tax": {
        "keywords": ["tax", "taxes", "income tax", "gst", "tds", "itr", "return", "deduction", "80c", "section", "tax saving", "slab"],
        "responses": [
            "[TAX] Income Tax Slabs FY 2024-25 (New Regime):\n  Up to Rs. 3L     : No tax\n  Rs. 3L  - 7L    : 5%\n  Rs. 7L  - 10L   : 10%\n  Rs. 10L - 12L   : 15%\n  Rs. 12L - 15L   : 20%\n  Above Rs. 15L   : 30%\n\nNew regime: lower rates but fewer deductions.",
            "[TAX] Tax Saving Under Old Regime:\n  Section 80C  : Rs. 1.5L - ELSS, PPF, LIC, EPF\n  Section 80D  : Rs. 25,000 - Health insurance premium\n  NPS 80CCD   : Rs. 50,000 - Extra deduction\n  HRA          : If you pay rent\n  Sec 24       : Rs. 2L Home loan interest\n\nFile ITR by July 31 to avoid penalty!",
        ],
        "followups": ["Want to compare Old vs New tax regime?", "How to maximize 80C savings?"]
    },
    "insurance": {
        "keywords": ["insurance", "insure", "policy", "premium", "term", "life insurance", "health insurance", "cover", "claim", "ulip"],
        "responses": [
            "[INSURANCE] Insurance Types:\n  Term Insurance  : Pure life cover. Rs. 1Cr for ~Rs. 8,000/yr at age 25. Best value.\n  Health Insurance: Rs. 5-10L minimum cover. Cashless hospitals.\n  ULIP            : Insurance + Investment hybrid. High fees - NOT recommended.\n\nBuy term + mutual funds separately. Always better value.",
            "[INSURANCE] Health Insurance Checklist:\n  - Minimum Rs. 5L sum insured (Rs. 10L preferred)\n  - Cashless hospital network near you\n  - Low or no co-pay clause\n  - Restoration benefit included\n  - Pre-existing disease waiting period under 2 years\n  - No room rent limit\n\nBuy young - premiums nearly double every 5 years!",
        ],
        "followups": ["Want to know top-rated health insurance plans?", "Should I explain claim settlement ratio?"]
    },
    "cryptocurrency": {
        "keywords": ["crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain", "defi", "nft", "web3", "btc", "eth", "altcoin"],
        "responses": [
            "[CRYPTO] Cryptocurrency Basics:\n  Bitcoin (BTC)  : Digital gold, store of value, limited to 21M coins\n  Ethereum (ETH) : Smart contract platform, powers DeFi and NFTs\n  Blockchain     : Decentralized, immutable, transparent ledger\n\nIndia taxes crypto at 30% flat + 1% TDS. Very volatile - invest only what you can lose.",
            "[CRYPTO] Crypto Safety Rules:\n  1. Use reputable exchanges: CoinDCX, WazirX, Binance\n  2. Enable 2FA on all accounts\n  3. Never share your private keys\n  4. Use hardware wallet for large holdings\n  5. Beware of pump and dump scams\n  6. Diversify - do not go all-in on one coin",
        ],
        "followups": ["Want to understand DeFi vs CeFi?", "Should I explain how blockchain works?"]
    },
    "savings": {
        "keywords": ["save", "savings", "emergency fund", "liquid", "bank", "account", "recurring deposit", "rd", "liquid fund"],
        "responses": [
            "[SAVINGS] Emergency Fund First: Build 3-6 months of expenses in liquid assets BEFORE investing.\n\nBest places:\n  - High-yield savings account (5-6%)\n  - Liquid mutual funds (7%+, redemption in 1 day)\n  - Short-term FD\n\nNever keep emergency fund in stocks - you may need it when markets are down.",
            "[SAVINGS] Savings Options Compared:\n  Regular SA    : 3-4%   | Instant\n  High-yield SA : 5-7%   | Instant\n  Liquid Fund   : 7-7.5% | 1 day\n  RD 6 months   : 6.5%   | Moderate\n  FD 1 year     : 7-7.5% | Low\n\nAutomate savings: set up auto-debit on salary day!",
        ],
        "followups": ["Want to know which banks offer best savings rates?", "Should I explain pay-yourself-first strategy?"]
    },
    "inflation": {
        "keywords": ["inflation", "cpi", "purchasing power", "prices", "cost of living", "real return", "deflation", "rbi"],
        "responses": [
            "[INFLATION] Understanding Inflation: India average CPI inflation is 5-6% per year.\n\nReal Return = Nominal Return - Inflation Rate\n\nExample: FD at 7% with 6% inflation = only 1% real gain!\n\nAssets that beat inflation:\n  + Equities (12-15% CAGR)\n  + Real estate (8-10%)\n  ~ Gold (6-8% partially)\n  - Cash savings: barely keeps up",
            "[INFLATION] Why Inflation Matters:\n  Rs. 1,00,000 today = only Rs. 74,000 worth in 5 years at 6% inflation!\n\nRule of 70: Divide 70 by inflation rate = years for prices to double.\nAt 7% inflation, prices double in just 10 years.\n\nKeeping large cash savings is actually losing money every day.",
        ],
        "followups": ["Want to understand real vs nominal returns?", "Should I explain RBI's role in controlling inflation?"]
    },
    "compound_interest": {
        "keywords": ["compound", "compounding", "compound interest", "power of compounding", "rule of 72", "double money", "cagr"],
        "responses": [
            "[COMPOUND] Compound Interest Formula: A = P(1 + r/n)^(nt)\n\nRule of 72: Divide 72 by annual return to find years to double money:\n  At 6%  -> doubles in 12 years\n  At 9%  -> doubles in 8 years\n  At 12% -> doubles in 6 years\n  At 24% -> doubles in 3 years!\n\nStarting early is the single biggest wealth-building factor.",
            "[COMPOUND] Power of Compounding Example:\nInvesting Rs. 5,000/month at 12% returns:\n  After 10 years: Rs. 11.6 Lakhs  (invested Rs. 6L)\n  After 20 years: Rs. 49.9 Lakhs  (invested Rs. 12L)\n  After 30 years: Rs. 1.76 Crores (invested Rs. 18L)\n\nStarting 10 years earlier gives 3.5x more wealth!",
        ],
        "followups": ["Want to compare starting at 25 vs 35 years?", "Should I explain CAGR vs absolute returns?"]
    },
    "help": {
        "keywords": ["help", "what can you do", "topics", "menu", "commands", "guide", "start", "begin", "options"],
        "responses": [
            """[FINBOT HELP] Topics I Can Answer:

  Topic           | Example Query
  --------------- | -------------------------------
  Stocks          | explain nifty, what is P/E ratio
  Budgeting       | 50/30/20 rule, monthly budget
  Loans & EMI     | what is EMI, home loan rates
  Investments     | SIP vs FD, mutual fund guide
  Income Tax      | 80C deductions, tax slabs
  Insurance       | term vs ULIP, health cover
  Crypto          | bitcoin basics, crypto tax
  Savings         | emergency fund, RD vs FD
  Inflation       | beat inflation, real returns
  Compounding     | rule of 72, double money

  Just type naturally - I understand plain English!"""
        ],
        "followups": []
    },
    "greeting": {
        "keywords": ["hello", "hi", "hey", "good morning", "good evening", "howdy", "namaste", "sup"],
        "responses": [
            "Hello! I am FinBot, your personal finance assistant.\nAsk me about stocks, loans, budgeting, tax saving, investments, insurance, and more!\nType 'help' to see all topics.",
        ],
        "followups": ["What financial topic interests you today?"]
    },
    "thanks": {
        "keywords": ["thank", "thanks", "thank you", "thx", "appreciate", "great", "awesome", "helpful"],
        "responses": [
            "Happy to help! Financial literacy is the first step to financial freedom. Ask anything else anytime!",
            "Glad that was useful! Small, consistent financial decisions compound into big results over time.",
        ],
        "followups": []
    }
}


def preprocess(text):
    """Tokenize and clean input text."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s/]", "", text)
    tokens = text.split()
    return tokens


def score_category(tokens, keywords):
    """Score a category based on keyword matches using weighted scoring."""
    score = 0
    token_set = set(tokens)
    full_text = " ".join(tokens)

    for kw in keywords:
        kw_lower = kw.lower()
        if " " in kw_lower:        # multi-word keyword gets higher weight
            if kw_lower in full_text:
                score += 3
        elif kw_lower in token_set:
            score += 2
        elif any(kw_lower in t for t in tokens):
            score += 1

    return score


def get_response(user_input):
    """Main matching function - returns best response dict."""
    if not user_input.strip():
        return {
            "response": "Please type a question! Type 'help' to see what I can answer.",
            "category": "unknown",
            "confidence": 0,
            "followup": None
        }

    tokens = preprocess(user_input)

    scores = {}
    for category, data in FINANCE_KB.items():
        scores[category] = score_category(tokens, data["keywords"])

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    if best_score == 0:
        return {
            "response": "I am not sure about that. Try asking about stocks, loans, budget, investments, tax, insurance, savings, or crypto. Type 'help' for a full guide!",
            "category": "unknown",
            "confidence": 0,
            "followup": "Type 'help' for all available topics."
        }

    category_data = FINANCE_KB[best_category]
    response_text = random.choice(category_data["responses"])
    followup = random.choice(category_data["followups"]) if category_data["followups"] else None
    confidence = min(100, best_score * 20)

    return {
        "response": response_text,
        "category": best_category,
        "confidence": confidence,
        "followup": followup,
        "timestamp": datetime.now().strftime("%H:%M")
    }


def run_cli():
    """Command-line interface for the chatbot."""
    # Force UTF-8 output for Windows terminals
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "=" * 60)
    print("  FinBot -- Natural Language Finance Assistant (CLI)")
    print("=" * 60)
    print("  Type your finance question. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("  You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye", "q"]:
                print("\n  FinBot: Goodbye! Invest wisely!\n")
                break
            result = get_response(user_input)
            print("\n  FinBot: " + result["response"])
            if result.get("followup"):
                print("\n  Tip: " + result["followup"])
            print()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  FinBot: Goodbye!\n")
            break
        except UnicodeDecodeError:
            print("  [Note: Use UTF-8 terminal or run: chcp 65001 on Windows]\n")


if __name__ == "__main__":
    run_cli()
