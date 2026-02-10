
def average_true_range(candlestick_data, period):
    """
    Menghitung Average True Range (ATR) dari data candlestick.

    Args:
        candlestick_data (list): List of dictionaries, each containing
                                 'h' (high), 'l' (low), 'c' (close) prices
                                 for a specific date. Assumes data is
                                 ordered chronologically (oldest first).
        period (int): Periode untuk menghitung ATR (default 14).

    Returns:
        float: Nilai Average True Range (ATR) terbaru. Mengembalikan 0.0
               jika tidak ada cukup data.
    """
    true_ranges = []

    if not candlestick_data:
        return 0.0

    # Calculate True Range (TR) for each day
    # For the first day, TR is typically High - Low if no prior close is available.
    # For subsequent days, TR = max(High - Low, abs(High - PrevClose), abs(Low - PrevClose)).

    # Calculate TR for the first candle (index 0)
    # The 'h' (high) and 'l' (low) keys are expected in the candlestick data.
    true_ranges.append(round(candlestick_data[0]["h"] - candlestick_data[0]["l"], 2))

    # Calculate TR for subsequent candles
    for i in range(1, len(candlestick_data)):
        current_high = candlestick_data[i]["h"]
        current_low = candlestick_data[i]["l"]
        previous_close = candlestick_data[i - 1][
            "c"
        ]  # Use close price from the previous candle

        tr1 = current_high - current_low
        tr2 = abs(current_high - previous_close)
        tr3 = abs(current_low - previous_close)

        true_range = max(tr1, tr2, tr3)
        true_ranges.append(round(true_range, 2))

    # Check if there is enough data to calculate ATR for the given period
    # We need at least 'period' true ranges to calculate the initial ATR.
    if len(true_ranges) < period:
        # If not enough data, return the average of available true ranges if any, or 0.0
        return round(sum(true_ranges) / len(true_ranges), 2) if true_ranges else 0.0

    # Calculate the initial ATR (Simple Moving Average of the first 'period' True Ranges)
    atr_values = []
    initial_atr = sum(true_ranges[:period]) / period
    atr_values.append(round(initial_atr, 2))

    # Calculate subsequent ATRs using Wilder's smoothing method:
    # ATR_i = ((ATR_{i-1} * (period - 1)) + TR_i) / period
    for i in range(period, len(true_ranges)):
        prev_atr = atr_values[-1]
        current_tr = true_ranges[i]
        next_atr = ((prev_atr * (period - 1)) + current_tr) / period
        atr_values.append(round(next_atr, 2))

    # Return the latest calculated ATR value
    return atr_values[-1] if atr_values else 0.0
