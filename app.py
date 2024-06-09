# Python
from flask import Flask,render_template
import numpy as np
import pandas as pd
import yfinance as yf
import requests
import math
import schedule
import time
import threading
from datetime import datetime

app=Flask(__name__)

@app.route('/stocks')
def stocks():
    bnData = yf.Ticker("HDFCBANK.NS")
    realtimedata = bnData.history(period="1d",interval="15m")
    data = pd.DataFrame(realtimedata)
    high = data['High']

    data['EMA_9'] = pd.Series(data['Close']).ewm(span=9, adjust=False).mean()

    ema_9 = data['EMA_9']
    hl = data[['High','EMA_9']]
    # print(data[['High','Low']])

    for index,row in hl.iterrows():
        if math.trunc(row['High']) == math.trunc(row['EMA_9']):
            print(row)
    return render_template('stocks.html', data = hl,high = high)

def botUpates():
    token = '6948125146:AAEQxTyicZ2ugJ7rGumOOaLYKDfNz_zR4TY'
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    print(requests.get(url).json())

def stocksDetails(stock):
    bnData = yf.Ticker(stock)
    realtimedata = bnData.history(period="1d",interval="15m")
    data = pd.DataFrame(realtimedata)
    data = data.drop(['Dividends','Stock Splits'],axis=1)
    # data = data.reset_index()
    data = data.rename_axis('Datetime').reset_index()
    data['Datetime'] = data['Datetime'].astype(str)
    data['Datetime'] = data['Datetime'].str[0:19]
    data['EMA_9'] = pd.Series(data['Close']).ewm(span=9, adjust=False).mean()
    data['EMA_21'] = pd.Series(data['Close']).ewm(span=21, adjust=False).mean()

    data['bullish'] = 0.0
    data['bullish'] = np.where(data['EMA_9'] > data['EMA_21'], 1.0, 0.0)
    data['crossover'] = data['bullish'].diff()
    hl = data[['Datetime','EMA_9','EMA_21','crossover','Close']]
    new_data = hl.where(hl['crossover']!= 0.0).dropna()

    new_data = new_data.sort_values(by='Datetime', ascending=False).head(1)

    details = []
    flag = 0

    for index,row in new_data.iterrows():
        ema_21= round(row['EMA_21'],4)
        ema_9 = round(row['EMA_9'],4)
        close = row['Close']
        cross = row['crossover']
        if stock == '^NSEBANK':
            
            flag = 1
            sign,top_ce,top_pe = getDataOC(close)
        if float(cross) != 0.0:
            #  print(row)
            details.append("Stock Name : " + stock +
                        "\nEMA_9 : " + str(ema_9) + 
                        "\nEMA_21 : "  + str(ema_21) + 
                        "\nCrossover : " + str(cross) + 
                        "\nTime  : " + row.Datetime + "\n\n")
            if flag == 1:
                details.append("\nSignal by Option Chain : " + str(sign) +
                        "\nTop Calls : " +
                        "\n1. " + "Strike Price : " + str(top_ce['strikePrice'].iloc[0]) + 
                                    "  OI : " + str(top_ce['CE.openInterest'].iloc[0]) +
                        "\n2. " + "Strike Price : " + str(top_ce['strikePrice'].iloc[1]) + 
                                    "  OI : " + str(top_ce['CE.openInterest'].iloc[1]) +
                        "\n3. " + "Strike Price : " + str(top_ce['strikePrice'].iloc[2]) + 
                                    "  OI : " + str(top_ce['CE.openInterest'].iloc[2]) +
                        "\n4. " + "Strike Price : " + str(top_ce['strikePrice'].iloc[3]) + 
                                    "  OI : " + str(top_ce['CE.openInterest'].iloc[3]) +
                        "\n5. " + "Strike Price : " + str(top_ce['strikePrice'].iloc[4]) + 
                                    "  OI : " + str(top_ce['CE.openInterest'].iloc[4]) +
                        "\nTop Puts : " +
                        "\n1. " + "Strike Price : " + str(top_pe['strikePrice'].iloc[0]) + 
                                    "  OI : " + str(top_pe['PE.openInterest'].iloc[0]) +
                        "\n2. " + "Strike Price : " + str(top_pe['strikePrice'].iloc[1]) + 
                                    "  OI : " + str(top_pe['PE.openInterest'].iloc[1]) +
                        "\n3. " + "Strike Price : " + str(top_pe['strikePrice'].iloc[2]) + 
                                    "  OI : " + str(top_pe['PE.openInterest'].iloc[2]) + 
                        "\n4. " + "Strike Price : " + str(top_pe['strikePrice'].iloc[3]) + 
                                    "  OI : " + str(top_pe['PE.openInterest'].iloc[3]) +
                        "\n5. " + "Strike Price : " + str(top_pe['strikePrice'].iloc[4]) + 
                                    "  OI : " + str(top_pe['PE.openInterest'].iloc[4]))
        # elif float(cross_bear) == -1.0:
        #     close = row['Close']
        #     getDataOC(close)
        #     print(row)
        #     details.append("Stock Name : " + stock + "\nEMA_9 : " + str(ema_9) + "\nEMA_21 : "  + str(ema_21) + "\nCrossover_Bearish : " + str(cross_bear) + "\nTime  : " + row.Datetime + "\n\n")


    return details

@app.route('/')
def fun():
    return "Hi"

def index():
    token = '6948125146:AAEQxTyicZ2ugJ7rGumOOaLYKDfNz_zR4TY'
    # chatid = '5128656629'
    # message = 'Hello World'
    # url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text={message}"

    grpId = '-4188291699'
    grpMsg = 'Hello World.\nThis is an automated message.'

    bnMembers = ['AUBANK.NS','AXISBANK.NS','BANDHANBNK.NS','BANKBARODA.NS','FEDERALBNK.NS','HDFCBANK.NS','ICICIBANK.NS','IDFCFIRSTB.NS'
,'INDUSINDBK.NS','KOTAKBANK.NS','PNB.NS','SBIN.NS','^NSEBANK']
    
    finalData = []
    formatted_text = ''
    for i in range(0,len(bnMembers)):
        data = stocksDetails(bnMembers[i])
        formatted_text += '\n\n'.join(data)
        finalData.append(data)


    urlGrp = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={grpId}&text={formatted_text}"
    res = requests.post(urlGrp).json()

    finalData = []
    formatted_text = ''
    data = []

def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(5).minutes.do(index)

@app.route('/trigger_send_message')
def trigger_send_message():
    index()
    return "Hello"

def getDataOC(close):
    # Set up the request headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    # Set up the request URL for the homepage
    homepage_url = 'https://www.nseindia.com'

    # Send the request for the homepage and get the cookies
    try:
        homepage_response = requests.get(homepage_url, headers=headers, timeout=10)
        cookies = homepage_response.cookies
    except requests.exceptions.Timeout:
        print('Homepage request timed out')

    # Set up the request URL and parameters for the options chain data
    options_url = 'https://www.nseindia.com/api/option-chain-indices'
    params = {'symbol': 'BANKNIFTY'}

    # Send the request for the options chain data using the cookies
    try:
        options_response = requests.get(options_url, headers=headers, params=params, cookies=cookies, timeout=10)
        options_data = options_response.json()
        # options_data = options_response.json()['records']['data']
    except requests.exceptions.Timeout:
        print('Options chain request timed out')

    # Convert the response data into a pandas dataframe
    df = pd.DataFrame(options_data)

    data = df['records']['data']

    df_data = pd.json_normalize(data,meta=['strikePrice','expiryDate',['PE','strikePrice'],['PE','expiryDate'],['PE','underlying'],['PE','identifier'],['PE','openInterest'],['PE','changeinOpenInterest'],['PE','pchangeinOpenInterest'],['PE','totalTradedVolume'],['PE','impliedVolatility'],['PE','lastPrice'],['PE','change'],['PE','pChange'],['PE','totalBuyQuantity'],['PE','totalSellQuantity'],['PE','bidQty'],['PE','bidprice'],['PE','askQty'],['PE','askPrice'],['PE','underlyingValue'],['CE','strikePrice'],['CE','expiryDate'],['CE','underlying'],['CE','identifier'],['CE','openInterest'],['CE','changeinOpenInterest'],['CE','pchangeinOpenInterest'],['CE','totalTradedVolume'],['CE','impliedVolatility'],['CE','lastPrice'],['CE','change'],['CE','pChange'],['CE','totalBuyQuantity'],['CE','totalSellQuantity'],['CE','bidQty'],['CE','bidprice'],['CE','askQty'],['CE','askPrice'],['CE','underlyingValue']])

    df_data['expiryDate'] = pd.to_datetime(df_data['expiryDate']).sort_values()

    df_data['expiryDate'].sort_values().drop_duplicates

    current_date = pd.Timestamp.now()

    # Get the current year and month
    current_year = current_date.year
    current_month = current_date.month

    # Filter the DataFrame for the current month and year
    current_month_data = df_data[(df_data['expiryDate'].dt.year == current_year) & (df_data['expiryDate'].dt.month == current_month)]

    current_data = pd.DataFrame(current_month_data).sort_values(by=['expiryDate','strikePrice'])

    latest_date = current_data['expiryDate'].min()

    latest_row = current_data.where(current_data['expiryDate'] == latest_date).dropna()

    nearest = min(latest_row['strikePrice'].values, key=lambda x: abs(x - close))

    ce_oi = sum(latest_row['CE.openInterest'])
    pe_oi = sum(latest_row['PE.openInterest'])

    signal = ''
    if ce_oi > pe_oi:
        signal = "BEARISH"
    else:
        signal = "BULLISH"

    top_3_pe = latest_row[latest_row['strikePrice'] < nearest].sort_values(by='strikePrice', ascending=False).head(5)
    top_3_ce = latest_row[latest_row['strikePrice'] > nearest].sort_values(by='strikePrice', ascending=False).tail(5)

    return signal,top_3_ce,top_3_pe



if __name__ == '__main__':
    threading.Thread(target=scheduler_thread, daemon=True).start()
    app.run(debug=True)
