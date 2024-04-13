from flask import Flask,render_template
import numpy as np
import pandas as pd
import yfinance as yf
import requests

app=Flask(__name__)

@app.route('/stocks')
def stocks():
    bnData = yf.Ticker("HDFCBANK.NS")
    realtimedata = bnData.history(period="1d",interval="15m")
    data = pd.DataFrame(realtimedata)
    high = data['High']
    hl = data[['High','Low']]
    print(data[['High','Low']])
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
    return data

@app.route('/')
def index():
    token = '6948125146:AAEQxTyicZ2ugJ7rGumOOaLYKDfNz_zR4TY'
    # chatid = '5128656629'
    # message = 'Hello World'
    # url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text={message}"

    grpId = '-4188291699'
    grpMsg = 'Hello World.\nThis is an automated message.'

    data = stocksDetails('HDFCBANK.NS')

    urlGrp = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={grpId}&text={data}"
    return requests.get(urlGrp).json()

if __name__ == '__main__':
    app.run(debug=True)