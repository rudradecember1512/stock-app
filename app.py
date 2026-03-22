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
        "1d": {"period": "1d", "interval": "5m", "is_intraday": True},
        "5d": {"period": "5d", "interval": "15m", "is_intraday": True},
        "1mo": {"period": "1mo", "interval": "1d", "is_intraday": False},
        "3mo": {"period": "3mo", "interval": "1d", "is_intraday": False},
        "6mo": {"period": "6mo", "interval": "1d", "is_intraday": False},
        "1y": {"period": "1y", "interval": "1d", "is_intraday": False},
    }
    return period_map.get(selected_period, period_map["6mo"])


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


def make_chart_labels(index_values, is_intraday):
    labels = []

    for dt in index_values:
        try:
            if is_intraday:
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


def calculate_support_resistance(hist):
    if hist.empty or len(hist) < 20:
        return [], []

    highs = hist["High"].reset_index(drop=True)
    lows = hist["Low"].reset_index(drop=True)

    raw_supports = []
    raw_resistances = []

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

    if not hist.empty:
        current_price = safe_float(hist["Close"].iloc[-1], 0)

        supports_below = [x for x in support_levels if x <= current_price]
        resistances_above = [x for x in resistance_levels if x >= current_price]

        support_levels = supports_below[-2:] if supports_below else support_levels[:2]
        resistance_levels = resistances_above[:2] if resistances_above else resistance_levels[-2:]

    support_levels = sorted(support_levels)
    resistance_levels = sorted(resistance_levels)

    return support_levels, resistance_levels


def get_stock_news(company_name, symbol):
    news_list = []

    if not NEWS_API_KEY:
        return news_list

    try:
        clean_symbol = str(symbol).replace(".NS", "").replace(".BO", "").strip()
        company_name = str(company_name or "").strip()

        search_queries = []

        if company_name and company_name.upper() != str(symbol).upper():
            search_queries.extend([
                f'"{company_name}"',
                f'"{company_name}" AND stock',
                f'"{company_name}" AND earnings'
            ])

        if clean_symbol:
            search_queries.append(f'"{clean_symbol}" AND stock')

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
                source = article.get("source", {}).get("name", "Unknown Source")
                url_link = article.get("url") or "#"
                published_at = (article.get("publishedAt") or "")[:10]

                combined_text = f"{title} {description}".lower()
                company_check = company_name.lower()
                symbol_check = clean_symbol.lower()

                if company_check in combined_text or symbol_check in combined_text:
                    already_exists = any(item["url"] == url_link for item in news_list)
                    if not already_exists:
                        news_list.append({
                            "title": title,
                            "source": source,
                            "url": url_link,
                            "published_at": published_at,
                            "description": description
                        })

                if len(news_list) >= 6:
                    return news_list

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


def get_safe_info(stock):
    try:
        info = stock.info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}


def build_stock_payload(symbol, selected_period="6mo", original_input=None):
    stock = yf.Ticker(symbol)
    config = get_history_config(selected_period)

    hist_main = stock.history(period=config["period"], interval=config["interval"])
    hist_6mo = stock.history(period="6mo", interval="1d")
    hist_2d = stock.history(period="2d", interval="1d")

    info = get_safe_info(stock)

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
    latest_macd = "N/A"
    latest_signal_line = "N/A"
    macd_status = "N/A"

    chart_labels = []
    chart_prices = []
    volume_values = []
    volume_colors = []
    macd_values = []
    signal_values = []
    candle_data = []
    support_levels = []
    resistance_levels = []

    if not hist_main.empty:
        hist_main = hist_main.copy()

        chart_labels = make_chart_labels(hist_main.index, config["is_intraday"])
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
        hist_main["MACD"] = ema12_main - ema26_main
        hist_main["SignalLine"] = hist_main["MACD"].ewm(span=9, adjust=False).mean()

        macd_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["MACD"].tolist()]
        signal_values = [round(safe_float(v), 2) if pd.notna(v) else None for v in hist_main["SignalLine"].tolist()]

    if not hist_6mo.empty:
        hist_6mo = hist_6mo.copy()

        hist_6mo["RSI"] = calculate_rsi(hist_6mo["Close"])
        hist_6mo["MA20"] = hist_6mo["Close"].rolling(window=20).mean()

        ema12 = hist_6mo["Close"].ewm(span=12, adjust=False).mean()
        ema26 = hist_6mo["Close"].ewm(span=26, adjust=False).mean()
        hist_6mo["MACD"] = ema12 - ema26
        hist_6mo["SignalLine"] = hist_6mo["MACD"].ewm(span=9, adjust=False).mean()

        latest_rsi = hist_6mo["RSI"].iloc[-1]
        latest_ma20 = hist_6mo["MA20"].iloc[-1]
        latest_macd = hist_6mo["MACD"].iloc[-1]
        latest_signal_line = hist_6mo["SignalLine"].iloc[-1]

        latest_rsi = "N/A" if pd.isna(latest_rsi) else round(float(latest_rsi), 2)
        latest_ma20 = "N/A" if pd.isna(latest_ma20) else round(float(latest_ma20), 2)
        latest_macd = "N/A" if pd.isna(latest_macd) else round(float(latest_macd), 2)
        latest_signal_line = "N/A" if pd.isna(latest_signal_line) else round(float(latest_signal_line), 2)

        if isinstance(latest_macd, (int, float)) and isinstance(latest_signal_line, (int, float)):
            if latest_macd > latest_signal_line:
                macd_status = "Bullish Crossover"
            elif latest_macd < latest_signal_line:
                macd_status = "Bearish Crossover"
            else:
                macd_status = "Neutral"

        recent_hist = hist_6mo.tail(90)
        support_levels, resistance_levels = calculate_support_resistance(recent_hist)

    market_cap = format_market_cap(info.get("marketCap"))
    pe_ratio = info.get("trailingPE", "N/A")
    if isinstance(pe_ratio, (int, float)):
        pe_ratio = round(pe_ratio, 2)

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

    company_name = info.get("longName") or symbol
    clean_name = clean_company_name(company_name)
    news = get_stock_news(clean_name, symbol)

    data = {
        "symbol": symbol,
        "name": company_name,
        "price": round(current_price, 2),
        "change": round(change, 2),
        "percent": round(percent_change, 2),
        "sector": info.get("sector", "N/A"),
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "currency": info.get("currency", "USD"),
        "rsi": latest_rsi,
        "ma20": latest_ma20,
        "macd": latest_macd,
        "signal_line": latest_signal_line,
        "macd_status": macd_status,
        "signal": signal,
        "signal_reason": signal_reason,
        "volume": format_volume(current_volume),
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "resolved_from": original_input if original_input else symbol
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
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "selected_period": selected_period,
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
    chart_labels = []
    chart_prices = []
    candle_data = []
    volume_values = []
    volume_colors = []
    macd_values = []
    signal_values = []
    support_levels = []
    resistance_levels = []
    news = []
    ai_summary = None
    error_message = None
    selected_period = "6mo"
    is_intraday = False

    if request.method == "POST":
        user_input = request.form.get("symbol", "").strip()
        selected_period = request.form.get("period", "6mo")

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
                    support_levels = result["support_levels"]
                    resistance_levels = result["resistance_levels"]
                    is_intraday = result["is_intraday"]

            except Exception as e:
                print("App error:", e)
                error_message = "Something went wrong while fetching stock data."

    return render_template(
        "index.html",
        data=data,
        chart_labels=chart_labels,
        chart_prices=chart_prices,
        candle_data=candle_data,
        volume_values=volume_values,
        volume_colors=volume_colors,
        macd_values=macd_values,
        signal_values=signal_values,
        support_levels=support_levels,
        resistance_levels=resistance_levels,
        selected_period=selected_period,
        news=news,
        ai_summary=ai_summary,
        error_message=error_message,
        is_intraday=is_intraday
    )


@app.route("/live-data/<symbol>")
def live_data(symbol):
    selected_period = request.args.get("period", "6mo")

    try:
        result = build_stock_payload(symbol, selected_period, original_input=symbol)
        return jsonify(result)
    except Exception as e:
        print("Live data error:", e)
        return jsonify({
            "success": False,
            "error_message": "Something went wrong while fetching live data."
        })


if __name__ == "__main__":
    app.run(debug=True)