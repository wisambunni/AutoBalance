from robin_stocks import *
from constants import *
import logging
from sheets_helper import SheetsHelper

logging.basicConfig(level=logging.INFO)


def update_holdings(robinhood_holdings, sheet_holdings, sheet_client):
    for row in range(len(sheet_holdings)):
        platform = sheet_holdings[row][PLATFORM_COL]
        ticker = sheet_holdings[row][TICKER_COL]

        if platform == Platform.ROBINHOOD.value and ticker in robinhood_holdings:
            logging.info(f'Updating {ticker} from {Platform.ROBINHOOD.value}')

            quantity = robinhood_holdings[ticker]['quantity']
            avg_price = robinhood_holdings[ticker]['average_buy_price']

            range_name = f'{SHEET_NAME}!{SHARES_COL}{row+1}:{COST_COL}{row+1}'
            update_values = [[quantity, avg_price]]

            sheet_client.update_values(range_name, update_values)


def main():
    logging.info('Logging in to Robinhood')
    rh_login = robinhood.login(store_session=True)

    logging.info('Building Robinhood holdings')
    rh_holdings = robinhood.build_holdings()

    logging.info('Initiating Google Sheeets client')
    sheets = SheetsHelper(sheet_id=SHEET_ID)
    sheet_values = sheets.get_values(RANGE_NAME)

    update_holdings(rh_holdings, sheet_values, sheets)


if __name__ == '__main__':
    main()
