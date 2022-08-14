from robin_stocks import *
from constants import *
import logging
from sheets_helper import SheetsHelper

logging.basicConfig(level=logging.INFO)


def update_sheet(holdings, sheet_holdings, sheet_client, sheet_meta):
    '''
    Updates a specific sheet data with Robinhood holdings.

    :param holdings: Robinhood holdings.
    :type holdings: dict

    :param sheet_holdings: Content of the specified Google Sheet.
    :type sheet_holdings: list[][]

    :param sheet_client: Google Sheets client helper.
    :type sheet_client: SheetsHelper

    :param sheet_meta: metadata containing relevant data about the specified sheet.
    :type sheet_meta: Enum
    '''
    # ignore title row
    for row in range(1, len(sheet_holdings)):
        platform = sheet_holdings[row][sheet_meta.PLATFORM_COL.value]
        ticker = sheet_holdings[row][sheet_meta.TICKER_COL.value]

        if platform == Platform.ROBINHOOD.value and ticker in holdings:
            logging.info(f'Updating {ticker} from {Platform.ROBINHOOD.value}')

            quantity = holdings[ticker]['quantity']
            avg_price = holdings[ticker]['average_buy_price']

            range_name = f'{sheet_meta.SHEET_NAME.value}!{sheet_meta.SHARES_COL.value}{row+1}:{sheet_meta.COST_COL.value}{row+1}'
            update_values = [[quantity, avg_price]]

            sheet_client.update_values(range_name, update_values)


def update_holdings(holdings, sheet_client):
    '''
    Updates portfolio holdings using Robinhood data.

    :param holdings: Robinhood holdings
    :type holdings: dict

    :param sheet_client: Google Sheets client helper.
    :type sheet_client: SheetHelper
    '''
    stocks_sheet = sheet_client.get_values(StocksSheet.RANGE_NAME.value)
    crypto_sheet = sheet_client.get_values(CryptoSheet.RANGE_NAME.value)

    update_sheet(holdings, stocks_sheet, sheet_client, StocksSheet)
    update_sheet(holdings, crypto_sheet, sheet_client, CryptoSheet)


def add_to_holdings(holdings, ticker, quantity, average_buy_price='0'):
    '''
    Adds a dictionary item to holdings.

    :param holdings: Robinhood holdings.
    :type holdings: dict

    :param ticker: Ticker symbol to add.
    :type ticker: str

    :param quantity: Quantity to add.
    :type quantity: str

    :param average_buy_price: Cost basis for ticker.
    :type average_buy_price: str

    :return: Robinhood holdings with appended dict item.
    :rtype: dict

    '''
    holdings[ticker] = {'quantity': quantity,
                        'average_buy_price': average_buy_price}

    return holdings


def calculate_currency_data(crypto_holdings):
    '''
    Transforms Robinhood crypto data into standardized values.

    :param crypto_holdings: Robinhood Crypto holdings
    :type crypto_holdings: dict

    :return: Filtered Robinhood Crypto data including cost basis
    :rtype: dict
    '''
    filtered_holdings = []
    for coin in crypto_holdings:
        logging.info(f'{coin["currency"]["code"]}: {coin["quantity"]}')
        symbol = coin['currency']['code']
        # dont add USD wallet to holdings
        if symbol == 'USD':
            continue

        quantity = coin['quantity']
        direct_cost_basis = float(coin['cost_bases'][0]['direct_cost_basis'])
        direct_quantity = float(coin['cost_bases'][0]['direct_quantity'])

        try:
            cost_basis = str(direct_cost_basis/direct_quantity)
        except ZeroDivisionError:
            cost_basis = '0'

        filtered_holdings.append({
            'symbol': symbol,
            'quantity': quantity,
            'cost_basis': cost_basis,
        })

    return filtered_holdings


def main():
    logging.info('Logging in to Robinhood')
    rh_login = robinhood.login(store_session=True)

    logging.info('Building Robinhood user profile')
    rh_cash = robinhood.build_user_profile()

    logging.info('Building Robinhood stock holdings')
    rh_holdings = robinhood.build_holdings()

    add_to_holdings(rh_holdings, ticker='USD',
                    quantity=rh_cash['cash'], average_buy_price='1.0')

    logging.info('Building Robinhood crypto holdings')
    rh_crypto = robinhood.get_crypto_positions()

    filtered_crypto_holdings = calculate_currency_data(rh_crypto)

    for coin in filtered_crypto_holdings:
        add_to_holdings(
            rh_holdings, ticker=coin['symbol'], quantity=coin['quantity'], average_buy_price=coin['cost_basis'])

    logging.info('Initiating Google Sheets client')
    sheets = SheetsHelper(sheet_id=SHEET_ID)

    update_holdings(rh_holdings, sheets)


if __name__ == '__main__':
    main()
