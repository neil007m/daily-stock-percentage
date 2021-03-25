import configparser
import datetime
import holidays
import requests


def find_last_open_market_date(given_date: datetime):
    day_difference = datetime.timedelta(days=1)
    us_holidays = holidays.US()
    while True:
        # if given_date is weekend, -1
        if given_date.date().weekday() > 4:
            given_date = given_date - day_difference
            continue
        # if given_date is us holiday, -1
        if given_date in us_holidays:
            given_date = given_date - day_difference
            continue
        return given_date

# base_url = 'https://api.polygon.io'
# stock_and_day_url = '/v1/open-close/{stocksTicker}/{date}'
# get input - stock_ticker, number_of_days
stock_ticker = 'AAPL'
number_of_days = 7  # input

# get API Key from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['polygon.io']['API_KEY']
payload = {'unadjusted': 'false', 'apiKey': api_key}
# if market open, find latest price (aggregate by minute and find desc limit 1)
# else find prev close (check whether it handles if market close)
# find latest date when market was open (latest_date). If currently open, find current price. NOT NEEDED - previous close ("Get the previous day's open, high, low, and close (OHLC) for the specified stock ticker.")
# does this handle as expected when prev day market was closed?
# https://api.polygon.io/v2/aggs/ticker/{stocksTicker}/prev?unadjusted=false&apiKey=* 
latest_price = None
# if market is open (check time and non weekend/US holiday)

# else
prev_close_url = 'https://api.polygon.io/v2/aggs/ticker/{0}/prev'.format(stock_ticker)
prev_close_response = requests.get(prev_close_url, params=payload)
prev_close_response.raise_for_status()
# try - raise json()['resultsCount']=0 is empty response set
latest_price = prev_close_response.json()['results'][0]['c']


# if latest_price is still None, Exception, unexpected err
if not latest_price:
    raise Exception


# find prev date (prev_date = latest_date - number_of_days)
# if market was not open on prev_date, find last date before prev_date when market was open and take closing price
current_date = datetime.datetime.today()
current_date_str = current_date.strftime('%Y-%m-%d')
day_difference = datetime.timedelta(days=number_of_days)
prev_date = current_date - day_difference
prev_date_str = prev_date.strftime('%Y-%m-%d')

prev_market_open_date = find_last_open_market_date(prev_date)
prev_market_open_date_str = prev_market_open_date.strftime('%Y-%m-%d')


day_open_close_url = 'https://api.polygon.io/v1/open-close/{0}/{1}'.format(stock_ticker, current_date)





