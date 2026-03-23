from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import requests
import difflib
import os

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "cb5588210c094009b4b4879bed6be892")

STOCK_ALIASES = {
    # India
    "RELIANCE": "RELIANCE.NS",
    "RELIANCE INDUSTRIES": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "TATA CONSULTANCY SERVICES": "TCS.NS",
    "INFY": "INFY.NS",
    "INFOSYS": "INFY.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "SBI": "SBIN.NS",
    "STATE BANK OF INDIA": "SBIN.NS",
    "SBI BANK": "SBIN.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "TATA STEEL": "TATASTEEL.NS",
    "WIPRO": "WIPRO.NS",
    "HCL": "HCLTECH.NS",
    "HCL TECH": "HCLTECH.NS",
    "HCL TECHNOLOGIES": "HCLTECH.NS",
    "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
    "HUL": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "BAJAJ FINANCE": "BAJFINANCE.NS",
    "BAJAJ FINSERV": "BAJAJFINSV.NS",
    "KOTAK BANK": "KOTAKBANK.NS",
    "KOTAK MAHINDRA BANK": "KOTAKBANK.NS",
    "AXIS BANK": "AXISBANK.NS",
    "MARUTI": "MARUTI.NS",
    "MARUTI SUZUKI": "MARUTI.NS",
    "ASIAN PAINTS": "ASIANPAINT.NS",
    "SUN PHARMA": "SUNPHARMA.NS",
    "SUN PHARMACEUTICAL": "SUNPHARMA.NS",
    "BHARTI AIRTEL": "BHARTIARTL.NS",
    "AIRTEL": "BHARTIARTL.NS",
    "LT": "LT.NS",
    "L&T": "LT.NS",
    "LARSEN": "LT.NS",
    "LARSEN AND TOUBRO": "LT.NS",
    "ONGC": "ONGC.NS",
    "NTPC": "NTPC.NS",
    "POWER GRID": "POWERGRID.NS",
    "POWERGRID": "POWERGRID.NS",
    "ULTRATECH": "ULTRACEMCO.NS",
    "ULTRATECH CEMENT": "ULTRACEMCO.NS",
    "NESTLE INDIA": "NESTLEIND.NS",
    "NESTLE": "NESTLEIND.NS",
    "TITAN": "TITAN.NS",
    "ADANI ENTERPRISES": "ADANIENT.NS",
    "ADANI PORTS": "ADANIPORTS.NS",
    "COAL INDIA": "COALINDIA.NS",
    "JSW STEEL": "JSWSTEEL.NS",
    "INDUSIND BANK": "INDUSINDBK.NS",
    "TECH MAHINDRA": "TECHM.NS",
    "TECHM": "TECHM.NS",
    "M&M": "M&M.NS",
    "MM": "M&M.NS",
    "MAHINDRA": "M&M.NS",
    "MAHINDRA AND MAHINDRA": "M&M.NS",
    "BAJAJ AUTO": "BAJAJ-AUTO.NS",
    "HEROMOTO": "HEROMOTOCO.NS",
    "HERO MOTOCORP": "HEROMOTOCO.NS",
    "EICHER MOTORS": "EICHERMOT.NS",
    "DR REDDY": "DRREDDY.NS",
    "DR REDDYS": "DRREDDY.NS",
    "DR REDDY'S": "DRREDDY.NS",
    "CIPLA": "CIPLA.NS",
    "DIVIS LAB": "DIVISLAB.NS",
    "DIVI'S LAB": "DIVISLAB.NS",
    "APOLLO HOSPITALS": "APOLLOHOSP.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "GRASIM": "GRASIM.NS",
    "HINDALCO": "HINDALCO.NS",
    "TATACONSUMER": "TATACONSUM.NS",
    "TATA CONSUMER": "TATACONSUM.NS",
    "SHRIRAM FINANCE": "SHRIRAMFIN.NS",
    "BPCL": "BPCL.NS",
    "IOC": "IOC.NS",
    "INDIAN OIL": "IOC.NS",
    "PIDILITE": "PIDILITIND.NS",
    "SIEMENS": "SIEMENS.NS",
    "DMART": "DMART.NS",
    "AVENUE SUPERMARTS": "DMART.NS",
    "ZOMATO": "ZOMATO.NS",
    "SWIGGY": "SWIGGY.NS",
    "IRCTC": "IRCTC.NS",
    "HAL": "HAL.NS",
    "BEL": "BEL.NS",
    "BHEL": "BHEL.NS",
    "RVNL": "RVNL.NS",
    "IREDA": "IREDA.NS",
    "TRENT": "TRENT.NS",
    "VEDANTA": "VEDL.NS",
    "JIO FINANCIAL": "JIOFIN.NS",
    "JIOFIN": "JIOFIN.NS",
    "DABUR": "DABUR.NS",
    "MOTHERSON": "MOTHERSON.NS",
    "SAMVARDHANA MOTHERSON": "MOTHERSON.NS",

    # US
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "TESLA": "TSLA",
    "NVIDIA": "NVDA",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
    "AMAZON": "AMZN",
    "META": "META",
    "FACEBOOK": "META",
    "NETFLIX": "NFLX",
    "AMD": "AMD",
    "INTEL": "INTC",
    "PALANTIR": "PLTR",
    "UBER": "UBER",
    "COINBASE": "COIN",
    "BERKSHIRE": "BRK-B",
    "BERKSHIRE HATHAWAY": "BRK-B",
    "JPMORGAN": "JPM",
    "JPM": "JPM",
    "VISA": "V",
    "MASTERCARD": "MA",
    "WALMART": "WMT",
    "DISNEY": "DIS",
    "BOEING": "BA",
    "NIKE": "NKE",
    "SALESFORCE": "CRM",
    "ADOBE": "ADBE",
    "QUALCOMM": "QCOM",
    "ORACLE": "ORCL",
    "CISCO": "CSCO",
    "EXXON": "XOM",
    "CHEVRON": "CVX",
    "PFIZER": "PFE",
    "MCDONALDS": "MCD",
    "STARBUCKS": "SBUX"
}

INDEX_SYMBOLS = {
    "Nifty 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bank Nifty": "^NSEBANK",
    "Nifty Midcap 50": "^NSEMDCP50",
    "Bankex": "^BSEBANK",
    "Nifty IT": "^CNXIT"
}


def normalize_user_input(user_input):
    return " ".join(str(user_input).strip().upper().split())


def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def is_symbol_valid(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d", interval="1d")
        return not hist.empty
    except Exception:
        return False


def get_symbol_suggestions(query, limit=8):
    query = normalize_user_input(query)

    if not query:
        return []

    suggestions = []
    seen = set()

    for name, symbol in STOCK_ALIASES.items():
        if query in name or query in symbol.upper():
            item = {
                "name": name.title(),
                "symbol": symbol
            }
            key = (item["name"], item["symbol"])
            if key not in seen:
                suggestions.append(item)
                seen.add(key)

    if not suggestions:
        alias_keys = list(STOCK_ALIASES.keys())
        close_matches = difflib.get_close_matches(query, alias_keys, n=limit, cutoff=0.4)

        for match in close_matches:
            item = {
                "name": match.title(),
                "symbol": STOCK_ALIASES[match]
            }
            key = (item["name"], item["symbol"])
            if key not in seen:
                suggestions.append(item)
                seen.add(key)

    suggestions.sort(key=lambda x: (not x["name"].upper().startswith(query), x["name"]))
    return suggestions[:limit]


def resolve_symbol(user_input):
    cleaned_input = normalize_user_input(user_input)

    if cleaned_input in STOCK_ALIASES:
        return STOCK_ALIASES[cleaned_input]

    normalized_variants = {
        cleaned_input,
        cleaned_input.replace("&", "AND"),
        cleaned_input.replace("AND", "&"),
        cleaned_input.replace(".", ""),
        cleaned_input.replace("-", " "),
        cleaned_input.replace("  ", " ")
    }

    for variant in normalized_variants:
        if variant in STOCK_ALIASES:
            return STOCK_ALIASES[variant]

    alias_keys = list(STOCK_ALIASES.keys())
    matches = difflib.get_close_matches(cleaned_input, alias_keys, n=3, cutoff=0.65)
    if matches:
        return STOCK_ALIASES[matches[0]]

    if "." not in cleaned_input:
        possible_symbols = [
            cleaned_input,
            cleaned_input.replace(" ", ""),
            f"{cleaned_input}.NS",
            f"{cleaned_input}.BO",
            f"{cleaned_input.replace(' ', '')}.NS",
            f"{cleaned_input.replace(' ', '')}.BO"
        ]

        for candidate in possible_symbols:
            if is_symbol_valid(candidate):
                return candidate

    return cleaned_input


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_atr(hist, period=14):
    if hist.empty:
        return pd.Series(dtype=float)

    high_low = hist["High"] - hist["Low"]
    high_close = (hist["High"] - hist["Close"].shift(1)).abs()
    low_close = (hist["Low"] - hist["Close"].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def calculate_stochastic(hist, period=14, smooth_k=3, smooth_d=3):
    if hist.empty:
        empty = pd.Series(dtype=float)
        return empty, empty

    lowest_low = hist["Low"].rolling(window=period).min()
    highest_high = hist["High"].rolling(window=period).max()
    denominator = (highest_high - lowest_low).replace(0, pd.NA)
    raw_k = ((hist["Close"] - lowest_low) / denominator) * 100
    stoch_k = raw_k.rolling(window=smooth_k).mean()
    stoch_d = stoch_k.rolling(window=smooth_d).mean()
    return stoch_k, stoch_d


def clean_company_name(name):
    if not name:
        return ""

    cleaned = str(name)
    remove_words = [
        "Limited", "Ltd.", "Ltd", "Inc.", "Inc",
        "Corporation", "Corp.", "Corp", "PLC", "plc"
    ]

    for word in remove_words:
        cleaned = cleaned.replace(word, "").strip()

    return " ".join(cleaned.split())


def get_history_config(selected_period):
    period_map = {
        "1min": {"period": "7d", "interval": "1m", "is_intraday": True, "label": "1MIN"},
        "5min": {"period": "30d", "interval": "5m", "is_intraday": True, "label": "5MIN"},
        "15min": {"period": "60d", "interval": "15m", "is_intraday": True, "label": "15MIN"},
        "1h": {"period": "60d", "interval": "60m", "is_intraday": True, "label": "1H"},
        "1d": {"period": "1y", "interval": "1d", "is_intraday": False, "label": "1D"},
        "5d": {"period": "5d", "interval": "1d", "is_intraday": False, "label": "5D"},
        "1mo": {"period": "1mo", "interval": "1d", "is_intraday": False, "label": "1MO"},
        "6mo": {"period": "6mo", "interval": "1d", "is_intraday": False, "label": "6MO"},
    }
    return period_map.get(selected_period, period_map["1d"])


def format_market_cap(market_cap):
    if isinstance(market_cap, (int, float)):
        if market_cap >= 1_000_000_000_000:
            return f"{market_cap / 1_000_000_000_000:.2f} T"
        elif market_cap >= 1_000_000_000:
            return f"{market_cap / 1_000_000_000:.2f} B"
        elif market_cap >= 1_000_000:
            return f"{market_cap / 1_000_000:.2f} M"
    return "N/A"


def format_volume(volume):
    if isinstance(volume, (int, float)):
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.2f} B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.2f} M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.2f} K"
        else:
            return str(int(volume))
    return "N/A"


def make_chart_labels(index_values, is_intraday, interval=None):
    labels = []

    for dt in index_values:
        try:
            if is_intraday and interval in {"1m", "5m", "15m", "60m"}:
                labels.append(dt.strftime("%d %b %H:%M"))
            elif is_intraday:
                labels.append(dt.strftime("%H:%M"))
            else:
                labels.append(dt.strftime("%Y-%m-%d"))
        except Exception:
            labels.append(str(dt))

    return labels


def dedupe_price_levels(levels, tolerance_ratio=0.015):
    if not levels:
        return []

    levels = sorted(levels)
    deduped = []

    for level in levels:
        if not deduped:
            deduped.append(level)
            continue

        prev = deduped[-1]
        if prev == 0:
            if level != 0:
                deduped.append(level)
            continue

        if abs(level - prev) / prev > tolerance_ratio:
            deduped.append(level)

    return deduped


def calculate_support_resistance(hist, current_price=None):
    if hist.empty or len(hist) < 5:
        return [], []

    highs = hist["High"].reset_index(drop=True)
    lows = hist["Low"].reset_index(drop=True)

    raw_supports = []
    raw_resistances = []

    if len(hist) < 20:
        raw_supports = [round(safe_float(value), 2) for value in lows.tolist() if safe_float(value, None) is not None]
        raw_resistances = [round(safe_float(value), 2) for value in highs.tolist() if safe_float(value, None) is not None]
    else:
        for i in range(2, len(hist) - 2):
            current_low = safe_float(lows.iloc[i], None)
            current_high = safe_float(highs.iloc[i], None)

            if current_low is not None:
                if (
                    current_low <= safe_float(lows.iloc[i - 1], current_low)
                    and current_low <= safe_float(lows.iloc[i - 2], current_low)
                    and current_low <= safe_float(lows.iloc[i + 1], current_low)
                    and current_low <= safe_float(lows.iloc[i + 2], current_low)
                ):
                    raw_supports.append(round(current_low, 2))

            if current_high is not None:
                if (
                    current_high >= safe_float(highs.iloc[i - 1], current_high)
                    and current_high >= safe_float(highs.iloc[i - 2], current_high)
                    and current_high >= safe_float(highs.iloc[i + 1], current_high)
                    and current_high >= safe_float(highs.iloc[i + 2], current_high)
                ):
                    raw_resistances.append(round(current_high, 2))

    support_levels = dedupe_price_levels(raw_supports)
    resistance_levels = dedupe_price_levels(raw_resistances)

    if current_price is None and not hist.empty:
        current_price = safe_float(hist["Close"].iloc[-1], 0)

    if current_price is not None:
        supports_below = [x for x in support_levels if x <= current_price]
        resistances_above = [x for x in resistance_levels if x >= current_price]

        if len(supports_below) >= 2:
            support_levels = supports_below[-2:]
        elif len(supports_below) == 1:
            fallback_support = [x for x in support_levels if x < supports_below[0]]
            support_levels = fallback_support[-1:] + supports_below
        else:
            support_levels = support_levels[:2]

        if len(resistances_above) >= 2:
            resistance_levels = resistances_above[:2]
        elif len(resistances_above) == 1:
            fallback_resistance = [x for x in resistance_levels if x > resistances_above[0]]
            resistance_levels = resistances_above + fallback_resistance[:1]
        else:
            resistance_levels = resistance_levels[-2:]

    support_levels = sorted(support_levels)
    resistance_levels = sorted(resistance_levels)

    return support_levels, resistance_levels


def get_safe_info(stock):
    try:
        info = stock.info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}


def get_safe_fast_info(stock):
    try:
        fast_info = stock.fast_info
        return dict(fast_info) if fast_info else {}
    except Exception:
        return {}


def safe_get_market_cap(info, fast_info):
    market_cap = info.get("marketCap")

    if not isinstance(market_cap, (int, float)):
        market_cap = fast_info.get("market_cap")

    return format_market_cap(market_cap) if isinstance(market_cap, (int, float)) else "N/A"


def safe_get_pe_ratio(info):
    pe_ratio = info.get("trailingPE")

    if isinstance(pe_ratio, (int, float)):
        return round(pe_ratio, 2)

    forward_pe = info.get("forwardPE")
    if isinstance(forward_pe, (int, float)):
        return round(forward_pe, 2)

    return "N/A"


def safe_get_sector(info):
    sector = info.get("sector")
    if sector and str(sector).strip():
        return sector

    industry = info.get("industry")
    if industry and str(industry).strip():
        return industry

    quote_type = info.get("quoteType")
    if quote_type and str(quote_type).strip():
        return quote_type

    return "N/A"


def safe_get_beta(info):
    beta = info.get("beta")
    if isinstance(beta, (int, float)):
        return round(beta, 2)
    return "N/A"


def safe_get_average_volume(info, fast_info):
    avg_volume = info.get("averageVolume") or info.get("averageVolume10days")

    if not isinstance(avg_volume, (int, float)):
        avg_volume = fast_info.get("ten_day_average_volume")

    if isinstance(avg_volume, (int, float)):
        return avg_volume

    return None


def safe_get_52_week_range(info, hist_6mo, current_price):
    week_high = info.get("fiftyTwoWeekHigh")
    week_low = info.get("fiftyTwoWeekLow")

    if not isinstance(week_high, (int, float)):
        if not hist_6mo.empty:
            week_high = safe_float(hist_6mo["High"].max(), None)

    if not isinstance(week_low, (int, float)):
        if not hist_6mo.empty:
            week_low = safe_float(hist_6mo["Low"].min(), None)

    position_pct = "N/A"
    if isinstance(week_high, (int, float)) and isinstance(week_low, (int, float)) and week_high > week_low:
        position_pct = round(((current_price - week_low) / (week_high - week_low)) * 100, 2)

    return (
        round(week_low, 2) if isinstance(week_low, (int, float)) else "N/A",
        round(week_high, 2) if isinstance(week_high, (int, float)) else "N/A",
        position_pct
    )


def build_trade_setup(data, news):
    score = 50

    rsi = data.get("rsi")
    price = safe_float(data.get("price"), 0)
    ma20 = data.get("ma20")
    macd_status = str(data.get("macd_status", ""))
    signal = str(data.get("signal", ""))
    news_sentiment = detect_news_sentiment(news)

    if isinstance(ma20, (int, float)):
        score += 8 if price > ma20 else -8

    if isinstance(rsi, (int, float)):
        if 50 <= rsi <= 68:
            score += 10
        elif rsi >= 70:
            score -= 8
        elif rsi <= 30:
            score += 4
        else:
            score -= 4

    if "Bullish" in macd_status:
        score += 12
    elif "Bearish" in macd_status:
        score -= 12

    if "Buy" in signal or "Bullish" in signal:
        score += 12
    elif "Sell" in signal or "Bearish" in signal or "Caution" in signal:
        score -= 12

    if news_sentiment == "Positive":
        score += 8
    elif news_sentiment == "Negative":
        score -= 8

    score = max(0, min(100, score))

    if score >= 72:
        label = "Strong Setup"
    elif score >= 58:
        label = "Constructive"
    elif score >= 42:
        label = "Balanced"
    else:
        label = "High Risk"

    return score, label, news_sentiment


def build_trade_checklist(price, ema20, ema50, rsi, macd_status, stoch_k, stoch_d, volume_vs_avg):
    checklist = []

    checklist.append({
        "label": "Price above EMA20",
        "status": isinstance(ema20, (int, float)) and price > ema20
    })
    checklist.append({
        "label": "EMA20 above EMA50",
        "status": isinstance(ema20, (int, float)) and isinstance(ema50, (int, float)) and ema20 > ema50
    })
    checklist.append({
        "label": "RSI above 50",
        "status": isinstance(rsi, (int, float)) and rsi > 50
    })
    checklist.append({
        "label": "MACD bullish",
        "status": "Bullish" in str(macd_status)
    })
    checklist.append({
        "label": "Stochastic K above D",
        "status": isinstance(stoch_k, (int, float)) and isinstance(stoch_d, (int, float)) and stoch_k > stoch_d
    })
    checklist.append({
        "label": "Volume above average",
        "status": isinstance(volume_vs_avg, (int, float)) and volume_vs_avg >= 100
    })

    passed = sum(1 for item in checklist if item["status"])
    return checklist, passed


def build_risk_profile(current_price, atr, beta, volume_vs_avg, support_levels):
    score = 45
    reasons = []

    if isinstance(beta, (int, float)):
        if beta >= 1.5:
            score += 18
            reasons.append("beta is elevated")
        elif beta <= 0.85:
            score -= 8
            reasons.append("beta is relatively defensive")
        else:
            reasons.append("beta is in a moderate range")

    if isinstance(current_price, (int, float)) and current_price > 0 and isinstance(atr, (int, float)):
        atr_pct = (atr / current_price) * 100
        if atr_pct >= 4:
            score += 22
            reasons.append("ATR implies wide price swings")
        elif atr_pct >= 2:
            score += 10
            reasons.append("ATR shows moderate movement")
        else:
            score -= 6
            reasons.append("ATR is relatively contained")

    if isinstance(volume_vs_avg, (int, float)):
        if volume_vs_avg >= 160:
            score += 10
            reasons.append("volume is running hot versus average")
        elif volume_vs_avg <= 70:
            score -= 4
            reasons.append("volume participation is lighter than average")

    if isinstance(current_price, (int, float)) and support_levels:
        nearest_support = next((lvl for lvl in support_levels if isinstance(lvl, (int, float))), None)
        if isinstance(nearest_support, (int, float)) and current_price > 0:
            distance_pct = abs(current_price - nearest_support) / current_price * 100
            if distance_pct <= 1.2:
                score += 8
                reasons.append("price is sitting close to support, so a break could matter quickly")

    score = max(0, min(100, round(score)))

    if score >= 72:
        label = "High Risk"
    elif score >= 52:
        label = "Moderate Risk"
    else:
        label = "Controlled Risk"

    reason = ". ".join(reasons[:3]).capitalize() if reasons else "Risk profile is based on volatility, beta, and participation."
    if reason and not reason.endswith("."):
        reason += "."

    return score, label, reason


def get_market_indices_snapshot():
    indices = []

    for name, symbol in INDEX_SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d", interval="1d")

            if hist.empty:
                indices.append({
                    "name": name,
                    "symbol": symbol,
                    "price": "N/A",
                    "change": "N/A",
                    "percent": "N/A",
                    "trend": "Unavailable",
                    "sparkline": []
                })
                continue

            close_values = hist["Close"].dropna().tolist()
            latest_price = safe_float(close_values[-1], 0)
            previous_price = safe_float(close_values[-2], latest_price) if len(close_values) >= 2 else latest_price
            change = latest_price - previous_price
            percent = (change / previous_price * 100) if previous_price else 0

            indices.append({
                "name": name,
                "symbol": symbol,
                "price": round(latest_price, 2),
                "change": round(change, 2),
                "percent": round(percent, 2),
                "trend": "Bullish" if change >= 0 else "Bearish",
                "sparkline": [round(safe_float(value), 2) for value in close_values[-5:]]
            })
        except Exception:
            indices.append({
                "name": name,
                "symbol": symbol,
                "price": "N/A",
                "change": "N/A",
                "percent": "N/A",
                "trend": "Unavailable",
                "sparkline": []
            })

    return indices


def detect_currency(symbol, info, fast_info):
    currency = info.get("currency") or fast_info.get("currency")

    if currency and str(currency).strip():
        return str(currency).upper()

    if str(symbol).upper().endswith(".NS") or str(symbol).upper().endswith(".BO"):
        return "INR"

    return "USD"


def is_relevant_article(text, company_name, clean_symbol):
    combined_text = str(text or "").lower()
    company_check = str(company_name or "").strip().lower()
    symbol_check = str(clean_symbol or "").strip().lower()

    if not combined_text:
        return False

    company_tokens = [token for token in company_check.replace("&", " ").split() if len(token) > 2]

    if company_check and company_check in combined_text:
        return True

    if symbol_check and symbol_check in combined_text:
        return True

    if company_tokens and sum(token in combined_text for token in company_tokens) >= min(2, len(company_tokens)):
        return True

    return False


def append_news_item(news_list, article):
    url_link = article.get("url") or "#"

    if any(item["url"] == url_link for item in news_list):
        return

    news_list.append({
        "title": article.get("title") or "No title",
        "source": article.get("source") or "Unknown Source",
        "url": url_link,
        "published_at": article.get("published_at") or "",
        "description": article.get("description") or "No description available."
    })


def fetch_newsapi_articles(company_name, clean_symbol, news_list):
    if not NEWS_API_KEY:
        return

    search_queries = []

    if company_name and company_name.upper() != clean_symbol.upper():
        search_queries.extend([
            f'"{company_name}"',
            f'"{company_name}" AND stock',
            f'"{company_name}" AND earnings'
        ])

    if clean_symbol:
        search_queries.extend([
            f'"{clean_symbol}" AND stock',
            f'"{clean_symbol}" AND shares'
        ])

    for query in search_queries:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "searchIn": "title,description",
            "apiKey": NEWS_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            continue

        for article in data.get("articles", []):
            title = article.get("title") or "No title"
            description = article.get("description") or "No description available."
            combined_text = f"{title} {description}"

            if not is_relevant_article(combined_text, company_name, clean_symbol):
                continue

            append_news_item(news_list, {
                "title": title,
                "source": article.get("source", {}).get("name", "Unknown Source"),
                "url": article.get("url") or "#",
                "published_at": (article.get("publishedAt") or "")[:10],
                "description": description
            })

            if len(news_list) >= 6:
                return


def fetch_yfinance_articles(stock, company_name, clean_symbol, news_list):
    if stock is None:
        return

    try:
        yahoo_news = stock.news or []
    except Exception:
        yahoo_news = []

    for article in yahoo_news:
        content = article.get("content") if isinstance(article, dict) else {}
        title = (
            article.get("title")
            or content.get("title")
            or "No title"
        )
        summary = (
            article.get("summary")
            or content.get("summary")
            or content.get("description")
            or "No description available."
        )
        url_link = (
            article.get("link")
            or content.get("canonicalUrl", {}).get("url")
            or article.get("url")
            or "#"
        )
        source = (
            article.get("publisher")
            or content.get("provider", {}).get("displayName")
            or "Yahoo Finance"
        )
        published_at = ""
        pub_time = article.get("providerPublishTime") or content.get("pubDate")
        if isinstance(pub_time, (int, float)):
            published_at = pd.to_datetime(pub_time, unit="s", errors="coerce").strftime("%Y-%m-%d")
        elif isinstance(pub_time, str):
            published_at = pub_time[:10]

        combined_text = f"{title} {summary}"
        if not is_relevant_article(combined_text, company_name, clean_symbol):
            continue

        append_news_item(news_list, {
            "title": title,
            "source": source,
            "url": url_link,
            "published_at": published_at,
            "description": summary
        })

        if len(news_list) >= 6:
            return


def get_stock_news(company_name, symbol, stock=None):
    news_list = []

    try:
        clean_symbol = str(symbol).replace(".NS", "").replace(".BO", "").strip()
        company_name = str(company_name or "").strip()
        fetch_newsapi_articles(company_name, clean_symbol, news_list)

        if len(news_list) < 6:
            fetch_yfinance_articles(stock, company_name, clean_symbol, news_list)

    except Exception as e:
        print("News fetch error:", e)

    return news_list


def detect_news_sentiment(news):
    positive_words = [
        "gain", "gains", "rise", "rises", "up", "surge", "surges", "jump", "jumps",
        "growth", "profit", "profits", "beat", "beats", "strong", "bullish",
        "record", "expansion", "upgrade", "buyback", "partnership", "win", "wins"
    ]

    negative_words = [
        "fall", "falls", "drop", "drops", "down", "decline", "declines", "loss", "losses",
        "weak", "miss", "misses", "bearish", "cut", "cuts", "downgrade", "lawsuit",
        "probe", "crash", "slump", "warning", "concern", "concerns"
    ]

    score = 0

    for article in news:
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()

        for word in positive_words:
            if word in text:
                score += 1

        for word in negative_words:
            if word in text:
                score -= 1

    if score >= 3:
        return "Positive"
    elif score <= -3:
        return "Negative"
    return "Mixed"


def generate_ai_summary(data, news, selected_period):
    if not data:
        return "No summary available."

    name = data.get("name", "This stock")
    price = data.get("price", "N/A")
    signal = data.get("signal", "Neutral")
    signal_reason = data.get("signal_reason", "Indicators are mixed")
    rsi = data.get("rsi", "N/A")
    ma20 = data.get("ma20", "N/A")
    macd_status = data.get("macd_status", "N/A")
    volume = data.get("volume", "N/A")
    supports = data.get("support_levels", [])
    resistances = data.get("resistance_levels", [])

    config = get_history_config(selected_period)
    timeframe_text = "intraday" if config["is_intraday"] else "swing"

    summary_parts = [
        f"{name} is currently trading near {price}. The current {timeframe_text} indicator signal is {signal.lower()}.",
        f"Technical reading suggests: {signal_reason}."
    ]

    if volume != "N/A":
        summary_parts.append(f"Recent traded volume is around {volume}.")

    if supports:
        summary_parts.append(f"Nearby support levels are around {', '.join(str(x) for x in supports)}.")

    if resistances:
        summary_parts.append(f"Nearby resistance levels are around {', '.join(str(x) for x in resistances)}.")

    if isinstance(rsi, (int, float)):
        if rsi >= 70:
            summary_parts.append(f"RSI is at {rsi}, which suggests the stock may be in the overbought zone.")
        elif rsi <= 30:
            summary_parts.append(f"RSI is at {rsi}, which suggests the stock may be in the oversold zone.")
        elif 50 <= rsi < 70:
            summary_parts.append(f"RSI is at {rsi}, indicating relatively healthy bullish momentum.")
        elif 30 < rsi < 50:
            summary_parts.append(f"RSI is at {rsi}, showing weaker momentum.")

    if isinstance(ma20, (int, float)):
        if safe_float(data.get("price", 0)) > ma20:
            summary_parts.append(f"The current price is above the 20-day moving average of {ma20}, which is generally supportive.")
        else:
            summary_parts.append(f"The current price is below the 20-day moving average of {ma20}, which may reflect weakness.")

    if macd_status != "N/A":
        summary_parts.append(f"MACD status currently shows {str(macd_status).lower()}.")

    news_sentiment = detect_news_sentiment(news)

    if news:
        if news_sentiment == "Positive":
            summary_parts.append("Recent news flow appears positive overall, which may support sentiment around the stock.")
        elif news_sentiment == "Negative":
            summary_parts.append("Recent news flow appears negative overall, which may create pressure on sentiment.")
        else:
            summary_parts.append("Recent news flow looks mixed, so sentiment is not strongly one-sided right now.")
    else:
        summary_parts.append("No relevant recent news was found, so the summary is based mainly on technical indicators.")

    summary_parts.append("This summary is for educational use only and should not be treated as financial advice.")
    return " ".join(summary_parts)


def build_stock_payload(symbol, selected_period="6mo", original_input=None):
    stock = yf.Ticker(symbol)
    config = get_history_config(selected_period)

    hist_main = stock.history(period=config["period"], interval=config["interval"])
    hist_6mo = stock.history(period="6mo", interval="1d")
    hist_2d = stock.history(period="2d", interval="1d")

    info = get_safe_info(stock)
    fast_info = get_safe_fast_info(stock)

    if hist_main.empty and hist_6mo.empty and hist_2d.empty:
        return {
            "success": False,
            "error_message": "Invalid stock symbol or data not available."
        }

    current_price = 0.0
    previous_price = 0.0
    current_volume = 0.0

    if not hist_2d.empty:
        current_price = safe_float(hist_2d["Close"].iloc[-1], 0)
        current_volume = safe_float(hist_2d["Volume"].iloc[-1], 0)
        if len(hist_2d) >= 2:
            previous_price = safe_float(hist_2d["Close"].iloc[-2], current_price)
        else:
            previous_price = current_price
    elif not hist_main.empty:
        current_price = safe_float(hist_main["Close"].iloc[-1], 0)
        current_volume = safe_float(hist_main["Volume"].iloc[-1], 0)
        if len(hist_main) >= 2:
            previous_price = safe_float(hist_main["Close"].iloc[-2], current_price)
        else:
            previous_price = current_price

    change = current_price - previous_price
    percent_change = (change / previous_price) * 100 if previous_price else 0

    latest_rsi = "N/A"
    latest_ma20 = "N/A"
    latest_ema20 = "N/A"
    latest_ema50 = "N/A"
    latest_macd = "N/A"
    latest_signal_line = "N/A"
    macd_status = "N/A"
    latest_atr = "N/A"
    latest_stoch_k = "N/A"
    latest_stoch_d = "N/A"
    latest_bb_upper = "N/A"
    latest_bb_middle = "N/A"
    latest_bb_lower = "N/A"
    bb_position = "N/A"

    chart_labels = []
    chart_prices = []
    volume_values = []
    volume_colors = []
    macd_values = []
    signal_values = []
    stoch_k_values = []
    stoch_d_values = []
    ema20_values = []
    ema50_values = []
    bb_upper_values = []
    bb_middle_values = []
    bb_lower_values = []
    candle_data = []
    support_levels = []
    resistance_levels = []

    if not hist_main.empty:
        hist_main = hist_main.copy()

        chart_labels = make_chart_labels(hist_main.index, config["is_intraday"], config["interval"])
        chart_prices = [round(safe_float(price), 2) for price in hist_main["Close"].tolist()]
        volume_values = [int(safe_float(v, 0)) for v in hist_main["Volume"].tolist()]

        for i in range(len(hist_main)):
            try:
                open_price = round(float(hist_main["Open"].iloc[i]), 2)
                close_price = round(float(hist_main["Close"].iloc[i]), 2)

                candle_data.append({
                    "x": chart_labels[i],
                    "y": [
                        open_price,
                        round(float(hist_main["High"].iloc[i]), 2),
                        round(float(hist_main["Low"].iloc[i]), 2),
                        close_price
                    ]
                })

                volume_colors.append("#16a34a" if close_price >= open_price else "#dc2626")
            except Exception:
                continue

        ema12_main = hist_main["Close"].ewm(span=12, adjust=False).mean()
        ema26_main = hist_main["Close"].ewm(span=26, adjust=False).mean()
        hist_main["EMA20"] = hist_main["Close"].ewm(span=20, adjust=False).mean()
        hist_main["EMA50"] = hist_main["Close"].ewm(span=50, adjust=False).mean()
        hist_main["BB_MIDDLE"] = hist_main["Close"].rolling(window=20).mean()
        bb_std = hist_main["Close"].rolling(window=20).std()
        hist_main["BB_UPPER"] = hist_main["BB_MIDDLE"] + (bb_std * 2)
        hist_main["BB_LOWER"] = hist_main["BB_MIDDLE"] - (bb_std * 2)
        stoch_k_main, stoch_d_main = calculate_stochastic(hist_main)
        hist_main["MACD"] = ema12_main - ema26_main
        hist_main["SignalLine"] = hist_main["MACD"].ewm(span=9, adjust=False).mean()

        macd_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["MACD"].tolist()]
        signal_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["SignalLine"].tolist()]
        ema20_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["EMA20"].tolist()]
        ema50_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["EMA50"].tolist()]
        bb_upper_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["BB_UPPER"].tolist()]
        bb_middle_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["BB_MIDDLE"].tolist()]
        bb_lower_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["BB_LOWER"].tolist()]
        stoch_k_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in stoch_k_main.tolist()]
        stoch_d_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in stoch_d_main.tolist()]

    if not hist_6mo.empty:
        hist_6mo = hist_6mo.copy()

        hist_6mo["RSI"] = calculate_rsi(hist_6mo["Close"])
        hist_6mo["MA20"] = hist_6mo["Close"].rolling(window=20).mean()
        hist_6mo["EMA20"] = hist_6mo["Close"].ewm(span=20, adjust=False).mean()
        hist_6mo["EMA50"] = hist_6mo["Close"].ewm(span=50, adjust=False).mean()
        hist_6mo["ATR"] = calculate_atr(hist_6mo)
        hist_6mo["BB_MIDDLE"] = hist_6mo["Close"].rolling(window=20).mean()
        bb_std_6mo = hist_6mo["Close"].rolling(window=20).std()
        hist_6mo["BB_UPPER"] = hist_6mo["BB_MIDDLE"] + (bb_std_6mo * 2)
        hist_6mo["BB_LOWER"] = hist_6mo["BB_MIDDLE"] - (bb_std_6mo * 2)
        hist_6mo["STOCH_K"], hist_6mo["STOCH_D"] = calculate_stochastic(hist_6mo)

        ema12 = hist_6mo["Close"].ewm(span=12, adjust=False).mean()
        ema26 = hist_6mo["Close"].ewm(span=26, adjust=False).mean()
        hist_6mo["MACD"] = ema12 - ema26
        hist_6mo["SignalLine"] = hist_6mo["MACD"].ewm(span=9, adjust=False).mean()

        latest_rsi = hist_6mo["RSI"].iloc[-1]
        latest_ma20 = hist_6mo["MA20"].iloc[-1]
        latest_ema20 = hist_6mo["EMA20"].iloc[-1]
        latest_ema50 = hist_6mo["EMA50"].iloc[-1]
        latest_macd = hist_6mo["MACD"].iloc[-1]
        latest_signal_line = hist_6mo["SignalLine"].iloc[-1]
        latest_atr = hist_6mo["ATR"].iloc[-1]
        latest_stoch_k = hist_6mo["STOCH_K"].iloc[-1]
        latest_stoch_d = hist_6mo["STOCH_D"].iloc[-1]
        latest_bb_upper = hist_6mo["BB_UPPER"].iloc[-1]
        latest_bb_middle = hist_6mo["BB_MIDDLE"].iloc[-1]
        latest_bb_lower = hist_6mo["BB_LOWER"].iloc[-1]

        latest_rsi = "N/A" if pd.isna(latest_rsi) else round(float(latest_rsi), 2)
        latest_ma20 = "N/A" if pd.isna(latest_ma20) else round(float(latest_ma20), 2)
        latest_ema20 = "N/A" if pd.isna(latest_ema20) else round(float(latest_ema20), 2)
        latest_ema50 = "N/A" if pd.isna(latest_ema50) else round(float(latest_ema50), 2)
        latest_macd = "N/A" if pd.isna(latest_macd) else round(float(latest_macd), 2)
        latest_signal_line = "N/A" if pd.isna(latest_signal_line) else round(float(latest_signal_line), 2)
        latest_atr = "N/A" if pd.isna(latest_atr) else round(float(latest_atr), 2)
        latest_stoch_k = "N/A" if pd.isna(latest_stoch_k) else round(float(latest_stoch_k), 2)
        latest_stoch_d = "N/A" if pd.isna(latest_stoch_d) else round(float(latest_stoch_d), 2)
        latest_bb_upper = "N/A" if pd.isna(latest_bb_upper) else round(float(latest_bb_upper), 2)
        latest_bb_middle = "N/A" if pd.isna(latest_bb_middle) else round(float(latest_bb_middle), 2)
        latest_bb_lower = "N/A" if pd.isna(latest_bb_lower) else round(float(latest_bb_lower), 2)

        if isinstance(latest_bb_upper, (int, float)) and isinstance(latest_bb_lower, (int, float)):
            if current_price >= latest_bb_upper:
                bb_position = "Above Upper Band"
            elif current_price <= latest_bb_lower:
                bb_position = "Below Lower Band"
            else:
                bb_position = "Inside Bands"

        if isinstance(latest_macd, (int, float)) and isinstance(latest_signal_line, (int, float)):
            if latest_macd > latest_signal_line:
                macd_status = "Bullish Crossover"
            elif latest_macd < latest_signal_line:
                macd_status = "Bearish Crossover"
            else:
                macd_status = "Neutral"

        level_hist = hist_main.copy() if len(hist_main) >= 20 else hist_6mo.tail(120).copy()
        support_levels, resistance_levels = calculate_support_resistance(level_hist, current_price=current_price)

    market_cap = safe_get_market_cap(info, fast_info)
    pe_ratio = safe_get_pe_ratio(info)
    currency = detect_currency(symbol, info, fast_info)
    beta = safe_get_beta(info)
    average_volume_raw = safe_get_average_volume(info, fast_info)
    week_low, week_high, price_position_52w = safe_get_52_week_range(info, hist_6mo, current_price)

    signal = "Neutral"
    signal_reason = "Indicators are mixed"

    if (
        isinstance(latest_rsi, (int, float)) and
        isinstance(latest_ma20, (int, float)) and
        isinstance(latest_macd, (int, float)) and
        isinstance(latest_signal_line, (int, float))
    ):
        if current_price > latest_ma20 and 50 < latest_rsi < 70 and latest_macd > latest_signal_line:
            signal = "Strong Buy Bias"
            signal_reason = "Price is above MA20, RSI is bullish, and MACD is above signal line"
        elif current_price < latest_ma20 and 30 < latest_rsi < 50 and latest_macd < latest_signal_line:
            signal = "Strong Sell Bias"
            signal_reason = "Price is below MA20, RSI is weak, and MACD is below signal line"
        elif latest_rsi >= 70:
            signal = "Caution"
            signal_reason = "RSI indicates overbought zone"
        elif latest_rsi <= 30:
            signal = "Watch for Reversal"
            signal_reason = "RSI indicates oversold zone"
        elif latest_macd > latest_signal_line:
            signal = "Bullish Momentum"
            signal_reason = "MACD is above signal line, indicating positive momentum"
        elif latest_macd < latest_signal_line:
            signal = "Bearish Momentum"
            signal_reason = "MACD is below signal line, indicating negative momentum"

    company_name = info.get("longName") or fast_info.get("shortName") or symbol
    clean_name = clean_company_name(company_name)
    news = get_stock_news(clean_name, symbol, stock=stock)

    volume_vs_avg = "N/A"
    volume_trend = "Normal"
    if isinstance(average_volume_raw, (int, float)) and average_volume_raw > 0 and current_volume > 0:
        volume_vs_avg = round((current_volume / average_volume_raw) * 100, 2)
        if volume_vs_avg >= 140:
            volume_trend = "High Volume"
        elif volume_vs_avg <= 70:
            volume_trend = "Light Volume"

    risk_level = "Balanced"
    if isinstance(beta, (int, float)):
        if beta >= 1.5:
            risk_level = "Aggressive"
        elif beta <= 0.85:
            risk_level = "Defensive"

    risk_score, risk_score_label, risk_reason = build_risk_profile(
        round(current_price, 2),
        latest_atr,
        beta,
        volume_vs_avg if isinstance(volume_vs_avg, (int, float)) else None,
        support_levels
    )

    setup_score, setup_label, news_sentiment = build_trade_setup({
        "rsi": latest_rsi,
        "price": round(current_price, 2),
        "ma20": latest_ma20,
        "macd_status": macd_status,
        "signal": signal
    }, news)
    checklist_items, checklist_passed = build_trade_checklist(
        round(current_price, 2),
        latest_ema20,
        latest_ema50,
        latest_rsi,
        macd_status,
        latest_stoch_k,
        latest_stoch_d,
        volume_vs_avg if isinstance(volume_vs_avg, (int, float)) else None
    )

    data = {
        "symbol": symbol,
        "name": company_name,
        "price": round(current_price, 2),
        "change": round(change, 2),
        "percent": round(percent_change, 2),
        "sector": safe_get_sector(info),
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "currency": currency,
        "rsi": latest_rsi,
        "ma20": latest_ma20,
        "ema20": latest_ema20,
        "ema50": latest_ema50,
        "macd": latest_macd,
        "signal_line": latest_signal_line,
        "atr": latest_atr,
        "stoch_k": latest_stoch_k,
        "stoch_d": latest_stoch_d,
        "bb_upper": latest_bb_upper,
        "bb_middle": latest_bb_middle,
        "bb_lower": latest_bb_lower,
        "bb_position": bb_position,
        "macd_status": macd_status,
        "signal": signal,
        "signal_reason": signal_reason,
        "volume": format_volume(current_volume),
        "avg_volume": format_volume(average_volume_raw) if isinstance(average_volume_raw, (int, float)) else "N/A",
        "volume_vs_avg": volume_vs_avg,
        "volume_trend": volume_trend,
        "beta": beta,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_score_label": risk_score_label,
        "risk_reason": risk_reason,
        "week_52_low": week_low,
        "week_52_high": week_high,
        "price_position_52w": price_position_52w,
        "setup_score": setup_score,
        "setup_label": setup_label,
        "news_sentiment": news_sentiment,
        "checklist_items": checklist_items,
        "checklist_passed": checklist_passed,
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "resolved_from": original_input if original_input else symbol,
        "display_period": config["label"]
    }

    ai_summary = generate_ai_summary(data, news, selected_period)

    return {
        "success": True,
        "data": data,
        "news": news,
        "ai_summary": ai_summary,
        "chart_labels": chart_labels,
        "chart_prices": chart_prices,
        "candle_data": candle_data,
        "volume_values": volume_values,
        "volume_colors": volume_colors,
        "macd_values": macd_values,
        "signal_values": signal_values,
        "stoch_k_values": stoch_k_values,
        "stoch_d_values": stoch_d_values,
        "ema20_values": ema20_values,
        "ema50_values": ema50_values,
        "bb_upper_values": bb_upper_values,
        "bb_middle_values": bb_middle_values,
        "bb_lower_values": bb_lower_values,
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "selected_period": selected_period,
        "display_period": config["label"],
        "is_intraday": config["is_intraday"]
    }


@app.route("/suggest")
def suggest():
    query = request.args.get("q", "").strip()
    suggestions = get_symbol_suggestions(query)
    return jsonify({"suggestions": suggestions})


@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    market_indices = get_market_indices_snapshot()
    chart_labels = []
    chart_prices = []
    candle_data = []
    volume_values = []
    volume_colors = []
    macd_values = []
    signal_values = []
    stoch_k_values = []
    stoch_d_values = []
    ema20_values = []
    ema50_values = []
    bb_upper_values = []
    bb_middle_values = []
    bb_lower_values = []
    support_levels = []
    resistance_levels = []
    news = []
    ai_summary = None
    error_message = None
    selected_period = "1d"
    is_intraday = False

    if request.method == "POST":
        user_input = request.form.get("symbol", "").strip()
        selected_period = request.form.get("period", "1d")

        if not user_input:
            error_message = "Please enter a stock name or symbol."
        else:
            symbol = resolve_symbol(user_input)

            try:
                result = build_stock_payload(symbol, selected_period, original_input=user_input)

                if not result["success"]:
                    error_message = f"No match found for '{user_input}'. Try exact symbol like AAPL or RELIANCE.NS."
                else:
                    data = result["data"]
                    news = result["news"]
                    ai_summary = result["ai_summary"]
                    chart_labels = result["chart_labels"]
                    chart_prices = result["chart_prices"]
                    candle_data = result["candle_data"]
                    volume_values = result["volume_values"]
                    volume_colors = result["volume_colors"]
                    macd_values = result["macd_values"]
                    signal_values = result["signal_values"]
                    stoch_k_values = result["stoch_k_values"]
                    stoch_d_values = result["stoch_d_values"]
                    ema20_values = result["ema20_values"]
                    ema50_values = result["ema50_values"]
                    bb_upper_values = result["bb_upper_values"]
                    bb_middle_values = result["bb_middle_values"]
                    bb_lower_values = result["bb_lower_values"]
                    support_levels = result["support_levels"]
                    resistance_levels = result["resistance_levels"]
                    is_intraday = result["is_intraday"]

            except Exception as e:
                print("App error:", e)
                error_message = "Something went wrong while fetching stock data."

    return render_template(
        "index.html",
        data=data,
        market_indices=market_indices,
        chart_labels=chart_labels,
        chart_prices=chart_prices,
        candle_data=candle_data,
        volume_values=volume_values,
        volume_colors=volume_colors,
        macd_values=macd_values,
        signal_values=signal_values,
        stoch_k_values=stoch_k_values,
        stoch_d_values=stoch_d_values,
        ema20_values=ema20_values,
        ema50_values=ema50_values,
        bb_upper_values=bb_upper_values,
        bb_middle_values=bb_middle_values,
        bb_lower_values=bb_lower_values,
        support_levels=support_levels,
        resistance_levels=resistance_levels,
        selected_period=selected_period,
        news=news,
        ai_summary=ai_summary,
        error_message=error_message,
        is_intraday=is_intraday
    )
@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/live-data/<symbol>")
def live_data(symbol):
    selected_period = request.args.get("period", "1d")

    try:
        result = build_stock_payload(symbol, selected_period, original_input=symbol)
        return jsonify(result)
    except Exception as e:
        print("Live data error:", e)
        return jsonify({
            "success": False,
            "error_message": "Something went wrong while fetching live data."
        })


@app.route("/market-indices")
def market_indices():
    try:
        return jsonify({
            "success": True,
            "indices": get_market_indices_snapshot()
        })
    except Exception as e:
        print("Market indices error:", e)
        return jsonify({
            "success": False,
            "indices": []
        })


if __name__ == "__main__":
    app.run(debug=True)
