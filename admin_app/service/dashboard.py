import json
from datetime import datetime

from django.contrib.auth.models import User

from admin_app.models import AuditLog, User_Profile
from admin_app.parameter.average_true_range import average_true_range
from admin_app.source.koingecko import market_chart


def service_dashboard():

    # Statistics
    total_users = User.objects.count()
    total_admins = User_Profile.objects.filter(role="admin").count()
    total_logs = AuditLog.objects.count()
    recent_logs = AuditLog.objects.select_related("user")[:10]

    # Generate crypto candlestick data
    candlestick_data = generate_crypto_candlestick_data()

    print(candlestick_data)

    # Analyze crypto data
    crypto_analysis = analyze_crypto_data(candlestick_data)

    atr = average_true_range(candlestick_data, 14)

    context = {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_logs": total_logs,
        "recent_logs": recent_logs,
        "candlestick_data": json.dumps(candlestick_data),
        "crypto_analysis": crypto_analysis,
    }

    return context


def generate_crypto_candlestick_data():
    """Generate crypto candlestick data from CoinGecko API for last 24 hours"""
    market_data = market_chart("bitcoin", "usd", "1")
    prices = market_data.get("prices", [])

    if not prices:
        return []

    # Group prices by hour
    hourly_data = {}
    for timestamp, price in prices:
        dt = datetime.fromtimestamp(timestamp / 1000)  # timestamp is in milliseconds
        hour_key = dt.replace(minute=0, second=0, microsecond=0)

        if hour_key not in hourly_data:
            hourly_data[hour_key] = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
            }
        else:
            # Update high and low
            hourly_data[hour_key]["high"] = max(hourly_data[hour_key]["high"], price)
            hourly_data[hour_key]["low"] = min(hourly_data[hour_key]["low"], price)
            hourly_data[hour_key]["close"] = price  # Last price becomes close

    # Convert to candlestick format
    candlestick_data = []
    for hour_key, ohlc in sorted(hourly_data.items()):
        candlestick_data.append(
            {
                "x": hour_key.strftime("%Y-%m-%d %H:%M"),
                "o": round(ohlc["open"], 2),
                "h": round(ohlc["high"], 2),
                "l": round(ohlc["low"], 2),
                "c": round(ohlc["close"], 2),
            }
        )

    return candlestick_data


def analyze_crypto_data(candlestick_data):
    """Analyze crypto data and calculate indicators"""
    prices = [candle["c"] for candle in candlestick_data]

    # Calculate Simple Moving Average (SMA)
    sma_7 = sum(prices[-7:]) / 7
    sma_14 = sum(prices[-14:]) / 14

    # Calculate RSI (Relative Strength Index)
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else 0
    avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else 0

    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if rs > 0 else 0

    # Get latest price and calculate change
    latest_price = prices[-1]
    prev_price = prices[-2] if len(prices) > 1 else latest_price
    price_change = latest_price - prev_price
    price_change_percent = (price_change / prev_price * 100) if prev_price != 0 else 0

    # Determine trend
    trend = "BULLISH" if sma_7 > sma_14 else "BEARISH"

    return {
        "latest_price": round(latest_price, 2),
        "price_change": round(price_change, 2),
        "price_change_percent": round(price_change_percent, 2),
        "sma_7": round(sma_7, 2),
        "sma_14": round(sma_14, 2),
        "rsi": round(rsi, 2),
        "trend": trend,
        "highest_price": round(max(prices), 2),
        "lowest_price": round(min(prices), 2),
    }
