from enum import Enum
# GOOGLE SHEET CONSTANTS
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '14absY1Ae4swi2nEChVA1zzC7lxVcORIo48R79ZG-CD0'
SHEET_NAME = 'BetaStocks'
RANGE_START = 'A'
RANGE_END = 'O'
RANGE_NAME = f'{SHEET_NAME}!{RANGE_START}:{RANGE_END}'
PLATFORM_COL = 0
TICKER_COL = 2
SHARES_COL = 'G'
COST_COL = 'H'


class Platform(Enum):
    ROBINHOOD = 'Robinhood'
    TD_AMERITRADE = 'TD Ameritrade'
    WEBULL = 'Webull'
    STASH = 'Stash'
    VANGUARD = 'Vanguard'
    FIDELITY = 'Fidelity'
    ALLY = 'Ally'
    COINBASE = 'Coinbase'
