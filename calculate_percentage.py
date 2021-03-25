import argparse
import configparser
import datetime
import requests

from us_holidays import US_HOLIDAYS


def is_market_open(given_date: datetime):
    # if given_date is weekend
    if given_date.date().weekday() > 4:
        return False
    # if given_date is a US holiday
    if given_date in US_HOLIDAYS:
        return False
    return True


def find_last_open_market_date(given_date: datetime):
    day_difference = datetime.timedelta(days=1)
    while True:
        if not is_market_open(given_date):
            given_date = given_date - day_difference
            continue
        return given_date


parser = argparse.ArgumentParser()
parser.add_argument("stock_ticker", help="ticker symbol")
parser.add_argument("number_of_days", help="number of days you want to go back to (integer)", type=int)
args = parser.parse_args()

stock_ticker = args.stock_ticker
number_of_days = args.number_of_days

# get API Key from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
polygon_api_key = config['polygon.io']['API_KEY']
fmp_api_key = config['FMP']['API_KEY']

fmp_base_url = 'https://financialmodelingprep.com'
fmp_payload = {'apikey': fmp_api_key}
fmp_real_time_url = '{0}/api/v3/quote-short/{1}'.format(fmp_base_url, stock_ticker)
polygon_base_url = 'https://api.polygon.io'
polygon_payload = {'unadjusted': 'false', 'apiKey': polygon_api_key}
polygon_previous_close_url = '{0}/v2/aggs/ticker/{1}/prev'.format(polygon_base_url, stock_ticker)
current_date = datetime.datetime.today()
latest_price = None

# if market is open (check time and non weekend/US holiday)
if is_market_open(current_date):
    real_time_price_response = requests.get(fmp_real_time_url, params=fmp_payload)
    real_time_price_response.raise_for_status()
    latest_price = real_time_price_response.json()[0]['price']
# else find last closing price
# TODO: check how the API works when market has just closed/weekends
else:
    previous_close_response = requests.get(polygon_previous_close_url, params=polygon_payload)
    previous_close_response.raise_for_status()
    # TODO: try - except: raise json()['resultsCount']=0 if empty response set
    latest_price = previous_close_response.json()['results'][0]['c']

# if latest_price is still None, Exception, unexpected err
if not latest_price:
    raise Exception


# find prev date (prev_date = latest_date - number_of_days)
# if market was not open on prev_date, find last date before prev_date when market was open and take closing price
current_date_str = current_date.strftime('%Y-%m-%d')
day_difference = datetime.timedelta(days=number_of_days)
prev_date = current_date - day_difference
prev_date_str = prev_date.strftime('%Y-%m-%d')
prev_market_open_date = find_last_open_market_date(prev_date)
prev_market_open_date_str = prev_market_open_date.strftime('%Y-%m-%d')

day_open_close_url = '{0}/v1/open-close/{1}/{2}'.format(polygon_base_url, stock_ticker, prev_market_open_date_str)
prev_price_response = requests.get(day_open_close_url, params=polygon_payload)
prev_price_response.raise_for_status()
prev_price = prev_price_response.json()['close']


print('\nLatest closing price [as of {0}] = {1}'.format(current_date, latest_price))
print('Closing price {0} days back on {1} = {2}'.format(number_of_days, prev_market_open_date_str, prev_price))
percentage_change = (latest_price - prev_price) * 100 / prev_price
percentage_change = round(percentage_change, 2)
print('\nPercentage change = {0}%\n'.format(percentage_change))
