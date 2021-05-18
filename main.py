import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests


st.set_page_config(page_title='Stonks',page_icon='https://yt3.ggpht.com/a/AATXAJwroVzth0tJxbrngf8YX6wYb3fQHoDS3cY40w=s900-c-k-c0xffffffff-no-rj-mo',layout='wide')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title('Stonks Analysis')
with st.sidebar.form(key='user input'):
    input_ticker = st.text_input('Enter Ticker',value='AAPL')
    input_exchange = st.selectbox('Select a Stock Exchange',['NYSE','NSE'],index=0)
    submit_button = st.form_submit_button('Submit')
page = st.sidebar.radio('Select Page',['Home','Historical Price','Screener'])

if input_exchange == 'NYSE':
    ticker = yf.Ticker(input_ticker.upper())
elif input_exchange == 'NSE':
    input_ticker = input_ticker.upper() + '.NS'
    ticker = yf.Ticker(input_ticker)

if page =='Home':
    c1,c2,c3,c4 = st.beta_columns(4)
    with c1:
        st.subheader('Market Cap')
        st.write(ticker.info['currency'] +' '+ str(ticker.info['marketCap']))
    with c2:
        st.subheader('TTM P/E')
        st.write(str(ticker.info['trailingPE']))
    with c3:
        st.subheader('Beta')
        st.write(str(ticker.info['beta']))
    with c4:
        st.image(ticker.info['logo_url'])

    st.header('Summary')
    st.write(ticker.info['longBusinessSummary'])
    # st.write(ticker.info)

if page == 'Historical Price':
    start_dt = st.date_input('Start Date',value = datetime(2020,1,1))
    end_dt = st.date_input('End Date')
    history = ticker.history(period = 'max',start=start_dt,end=end_dt)
    figure = go.Figure(
        data = [
                go.Candlestick(
                    x = history.index,
                    low = history.Low,
                    high = history.High,
                    close = history.Close,
                    open = history.Open,
                    # increasing_line_color = 'green',
                    # decreasing_line_color = 'red'
                )
        ]
)
    figure.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(figure)

if page == 'Screener':
    url = 'https://www.screener.in/screens/376961/ALGO/?page=1'
    req = requests.get(url)
    indx = req.text.find('Showing page ')
    afindx = int(req.text[indx+18])
    table = pd.DataFrame()
    for i in range(1,afindx+1):
        stri = str(i)
        url = f'https://www.screener.in/screens/376961/ALGO/?page={stri}'
        req = requests.get(url)
        html = req.content
        df_list = pd.read_html(html,index_col='S.No.')
        df = df_list[0]
        df.drop(df.columns[[4,5,6,7,8]], axis = 1, inplace = True)
        df.dropna(inplace=True)
        try:
            df.drop(['S.No.'],inplace=True)
        except:
            pass
        table = pd.concat([table,df])
    newtable = table.astype({'Name':str, 'CMP  Rs.':float, 'P/E':float, 'Mar Cap  Rs.Cr.':float, 'ROCE  %':float, 'ROA 12M  %':float})
    newtable.sort_values(by='ROA 12M  %',inplace=True,ascending=False)
    newtable.columns = ['Name','Price','P/E','Market Cap(Cr)','ROCE(%)','ROA(%)']
    newtable['ROA rank'] = [*range(1,newtable.shape[0]+1)]
    newtable.sort_values('P/E',inplace=True)
    newtable['P/E rank'] = [*range(1,newtable.shape[0]+1)]
    newtable['Sum'] = newtable['P/E rank'] + newtable['ROA rank']
    newtable.sort_values('Sum',inplace=True)
    newtable['Final Rank'] = [*range(1,newtable.shape[0]+1)]
    newtable.reset_index(drop=True, inplace=True)
    newtable.set_index('Final Rank',inplace=True)
    newtable.drop('Sum',axis=1,inplace=True)
    newtable['Price'] = newtable['Price'].round(2)
    st.table(newtable.style.format({'Price': '{:.2f}', 'P/E': '{:.2f}', 'Market Cap(Cr)': '{:.2f}','ROCE(%)': '{:.2f}','ROA(%)':'{:.2f}'}))
