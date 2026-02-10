import requests

def market_chart(coin, currency, days):

    url = "https://api.coingecko.com/api/v3/coins/" + coin + "/market_chart?vs_currency=" + currency + "&days=" + days
    response = requests.get(url)

    return response.json()
