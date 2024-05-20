
'''
import pandas as pd
import requests
import json
import dtale
from collections import Counter
import fn_flatten_and_expand_df
import robin_stocks.robinhood as r
from pandasgui import show
'''

'''
#get pickle file
print(r.__file__)

#login to robinhood wrapper api
r.login('*** @gmail.com', '')

#get portfolio holdings data and convert to dataframe
holdings = r.account.build_holdings()
'''

'''
base_url = 'https://data.alpaca.markets/v2/stocks/trades'
#enclosed_tickers = tickers
start_date ='2024-04-29' # <<< format: RFC-3339 or YYYY-MM-DD
end_date = '2024-04-29'
limit = 10000 # <<< max number of datapoints; next page token will generate if limit is exceeded for another call
feed = 'sip' # <<< the source feed of the data. "sip' contains all US exchanges, 'iex' contains only the Investors Exchange; 'otc' contains over the counter exchanges
next_page_token = '' # <<< copy paste token or comment out
sort = 'asc'
'''

'''
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "******",
    "APCA-API-SECRET-KEY": "******"
}
'''

'''
iterations = range(5) # <<< set number of loops
'''

# - ALPACA API Documentation: https://docs.alpaca.markets/reference/stockbars-1

def fn_alpaca_tradesV1( holdings, start_date, end_date, limit, feed, next_page_token, sort, iterations, headers, base_url, show_final=None):
    
    print('''ReadMe: ''')
    print('''Robin$tocks API Docs: https://robin-stocks.readthedocs.io/en/latest/robinhood.html''')
    print('''Alpaca API Docs: https://docs.alpaca.markets/reference/stocktrades-1''')    

    #-------------------------------------------------------------------------------------------------------
    ##### 1. Set initial loop, lists, counters, & import packages etc
    #-------------------------------------------------------------------------------------------------------
    
    import pandas as pd
    import requests
    import json
    import robin_stocks.robinhood as r
    from pandasgui import show
    from collections import Counter
    
    #initialize counters
    string_cnt = 0
    none_cnt = 0

    #initialize lists
    foo = {1:0}
    foo[1]=(0)
    dictionary_list=[]
    trade_list=[]
    
    #-------------------------------------------------------------------------------------------------------
    ##### 2. "Next Page Token" API Function
    #-------------------------------------------------------------------------------------------------------
    
    ## - function iterates the Alpaca API call and retrieves tokens and bar data 
    def api_npt(i,next_page_token):
        if i < 1:
            response = requests.get(f"{base_url}?symbols={enclosed_tickers}&start={start_date}&end={end_date}&limit={limit}&feed={feed}&sort={sort}", headers=headers)
            
            print(
            '''____________________________________________________________________________________________________________________________________
            ''')
            
            print(f'URL {i}:',f"{base_url}?symbols={enclosed_tickers}&start={start_date}&end={end_date}&limit={limit}&feed={feed}&sort={sort}") # <<< print first url address

        else:
            response = requests.get(f"{base_url}?symbols={enclosed_tickers}&start={start_date}&end={end_date}&limit={limit}&feed={feed}&page_token={next_page_token}&sort={sort}", headers=headers)

            print(
            '''____________________________________________________________________________________________________________________________________
            ''')
            
            print(f'URL {i}:',f"{base_url}?symbols={enclosed_tickers}&start={start_date}&end={end_date}&limit={limit}&feed={feed}&page_token={next_page_token}&sort={sort}") # <<< print rest of url addresses

        response_json = response.json()

        ## - get bar data and store in list
        for symbol, trades in response_json['trades'].items():
            for trade in trades:
                trade['symbol'] = symbol  
                trade_list.append(trade)

        ## - appends dictionaries into a list
        trades = response_json.get('trades')

        dictionary_list.append(trades)

        npt = response_json.get('next_page_token')

        print(f'Next Token ->',npt)
        return(npt)

    #-------------------------------------------------------------------------------------------------------
    ##### 3. Extract Robinhood Portfolio Tickers
    #-------------------------------------------------------------------------------------------------------
    
    print(
    '''
---------------------------------------------
            Portfolio Holdings
---------------------------------------------
    ''')    

    #holdings_data = r.account.build_holdings()
    holdings_df = pd.DataFrame(holdings).transpose()
    
    ## - rename the 'index' column to 'symbol'; dont run more than once otherwise there will be more than one symbol column
    holdings_df = holdings_df.reset_index().rename(columns={'index': 'symbol'})
    holdings_df.info()
    
    print(
    '''
---------------------------------------------
                Stock Tickers
---------------------------------------------
    ''')

    ## - filter down only tickers
    holdings_df = holdings_df.filter(['symbol'])
    holdings = holdings_df.transpose()
    print(holdings)


    ## - concatenate all tickers as one string; using %2 as separator per api requirements
    tickers = "%2C".join(holdings_df["symbol"])
    enclosed_tickers = tickers
    #print(tickers)
    
    #-------------------------------------------------------------------------------------------------------
    ##### 4. Main Token Loop
    #-------------------------------------------------------------------------------------------------------
    
    for i in iterations:
        j = (i + 1)
        if i < 1:

            print(next_page_token)

            #next_page_token = api_npt(i,next_page_token)
            next_page_token = next_page_token

            foo[1]=(next_page_token)
        else:
            next_page_token = api_npt(i,next_page_token)

            foo[i+1] = (next_page_token)
            
    print(
    '''____________________________________________________________________________________________________________________________________
    ''')

    ## - print list of all tokens retrieved
    print(">>> List of all tokens in Alpaca call:", foo)

    ## - the show() function is for the pandasGUI package; is optional to include; https://pypi.org/project/pandasgui/
    #dictionary_list=[]
    #show(dictionary_list)
    #show(bar_list)

    ## - count all tokens
    for value in foo.values():
        if isinstance(value, str):
            string_cnt += 1
        elif value is None:
            none_cnt += 1

    print(">>> Number of Tokens:", string_cnt-1)
    
    print(
    '''____________________________________________________________________________________________________________________________________
    ''')
    
    #-------------------------------------------------------------------------------------------------------
    ##### 5. Final Table
    #-------------------------------------------------------------------------------------------------------
    
    trade_df = pd.DataFrame(trade_list)
    #show(trade_df)

    final_df = fn_flatten_and_expand_df.flatten_and_expand_df(trade_df)
    
    print(
    '''
---------------------------------------------
                Final Table
---------------------------------------------
    ''')
    
    print(''' 
>>> Final DataFrame name can be referenced as "final_df".
''')
    
    final_df.info()
    final_df.describe()
    
    if show_final == 'Y':
        show(final_df)
        
        print(""" 
>>>  Final Table set to show in pandasGUI; pip install pandasgui if error occurs.
     PandasGUI Docs: https://pypi.org/project/pandasgui/ """)
        
        print(""" 
>>>  Variables in Query:

    t | date-time | Timestamp in RFC-3339 format with nanosecond precision
    x | string | Exchange code. See v2/stocks/meta/exchanges for more details.
    p | double | Trade price
    s | uint32 | Trade size
    i | uint64 | Trade ID sent by the exchange
    c | array of strings | Condition flags. See https://docs.alpaca.markets/reference/stockmetaconditions-1 for more details.
    z | string | Tape A is the New York Stock Exchange, Tape B is NYSE Arca, Bats, IEX and other regional exchanges, Tape C is NASDAQ, Tape O is OTC; A B C O""")

    else:
        
        print(""" 
>>>  Final Table set to NOT show; change keyword function argument to final='Y' to display final DataFrame.""")
        
        print(""" 
>>>  Variables in Query:

    t | date-time | Timestamp in RFC-3339 format with nanosecond precision
    x | string | Exchange code. See v2/stocks/meta/exchanges for more details.
    p | double | Trade price
    s | uint32 | Trade size
    i | uint64 | Trade ID sent by the exchange
    c | array of strings | Condition flags. See https://docs.alpaca.markets/reference/stockmetaconditions-1 for more details.
    z | string | Tape A is the New York Stock Exchange, Tape B is NYSE Arca, Bats, IEX and other regional exchanges, Tape C is NASDAQ, Tape O is OTC; A B C O
    
    """)
    return(final_df)