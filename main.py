import streamlit as st
from streamlit import beta_util
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title='Stonks',page_icon='https://yt3.ggpht.com/a/AATXAJwroVzth0tJxbrngf8YX6wYb3fQHoDS3cY40w=s900-c-k-c0xffffffff-no-rj-mo',layout='wide')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# with st.sidebar.form(key='user input'):
#     input_ticker = st.text_input('Enter Ticker',value='AAPL')
#     input_exchange = st.selectbox('Select a Stock Exchange',['NYSE','NSE'],index=0)
#     submit_button = st.form_submit_button('Submit')
# page = st.sidebar.radio('Select Page',['Home','Historical Price','Screener'])

# if input_exchange == 'NYSE':
#     ticker = yf.Ticker(input_ticker.upper())
# elif input_exchange == 'NSE':
#     input_ticker = input_ticker.upper() + '.NS'
#     ticker = yf.Ticker(input_ticker)

# if page =='Home':
#     st.title('Stonks Analysis')
#     with st.spinner('Fetching...'): 
#         c1,c2,c3,c4 = st.beta_columns(4)
#         try:
#             summary = ticker.info['longBusinessSummary']  
#         except:
#             summary = "Not Available"
#         try:
#             currency = ticker.info['currency']  
#         except:
#             currency = "Not Available"
#         try:
#             marketcap = ticker.info['marketCap']  
#         except:
#             marketcap = "Not Available"
#         try:
#             trailingpe = ticker.info['trailingPE'] 
#         except:
#             trailingpe = "Not Available"
#         try:
#             beta = ticker.info['beta']
#         except:
#             beta = "Not Available"
#         with c1:
#             st.subheader('Market Cap')
#             st.write(str(currency) +' '+ str(marketcap))
#         with c2:
#             st.subheader('TTM P/E')
#             st.write(str(trailingpe))
#         with c3:
#             st.subheader('Beta')
#             st.write(str(beta))
#         with c4:
#             st.image(ticker.info['logo_url'])
#     st.header('Summary')
#     st.write(summary)
#     # st.write(ticker.info)

# if page == 'Historical Price':
#     st.title('Historical Price')
#     with st.spinner('Drawing...'): 
#         start_dt = st.date_input('Start Date',value = datetime(2020,1,1))
#         end_dt = st.date_input('End Date')
#         history = ticker.history(period = 'max',start=start_dt,end=end_dt)
#         figure = go.Figure(
#             data = [
#                     go.Candlestick(
#                         x = history.index,
#                         low = history.Low,
#                         high = history.High,
#                         close = history.Close,
#                         open = history.Open,
#                         # increasing_line_color = 'green',
#                         # decreasing_line_color = 'red'
#                     )
#                 ]
#             )
#         figure.update_layout(xaxis_rangeslider_visible=False)
#     st.plotly_chart(figure)

# if page == 'Screener':
    # with st.spinner('Calculating...'): 

url = 'https://www.screener.in/screens/376961/ALGO/?page=1'
req = requests.get(url)
indx = req.text.find('Showing page ')
afindx = int(req.text[indx+18])
table = pd.DataFrame()
for i in range(1,afindx+1):
    stri = str(i)
    url = f'https://www.screener.in/screens/376961/algo/?sort=EVEBITDA&order=asc&page={stri}'
    req = requests.get(url)
    html = req.content
    soup = BeautifulSoup(html, 'lxml')
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))
    for item in list(links):
        if '/company/' not in item:
            links.remove(item)
    newlist = []
    for item in list(links):
        indx = item.find('y/')
        tkr = item[indx+2:]
        indx = tkr.find('/')
        tkr = tkr[:indx]
        newlist.append(tkr)
    df_list = pd.read_html(html,index_col='S.No.')
    df = df_list[0]
    df.drop(df.columns[[4,5,6,7,8]], axis = 1, inplace = True)
    try:
        df.drop(['S.No.'],inplace=True)
    except:
        pass
    df['Ticker/Code'] = newlist
    df.dropna(inplace=True)
    table = pd.concat([table,df])
newtable = table.astype({'Name':str, 'CMP  Rs.':float, 'P/E':float, 'Mar Cap  Rs.Cr.':float, 'ROCE  %':float, 'ROA 12M  %':float,'EV / EBITDA':float})
newtable.sort_values(by='ROCE  %',inplace=True,ascending=False)
newtable.columns = ['Name','Price','P/E','Market Cap(Cr)','ROCE(%)','ROA(%)','EV/EBITDA','Ticker/Code']
newtable['ROCE rank'] = [*range(1,newtable.shape[0]+1)]
newtable.sort_values('EV/EBITDA',inplace=True)
newtable['EV/EBITDA rank'] = [*range(1,newtable.shape[0]+1)]
newtable['Sum'] = newtable['EV/EBITDA rank'] + newtable['ROCE rank']
newtable.sort_values('Sum',inplace=True)
newtable['Final Rank'] = [*range(1,newtable.shape[0]+1)]
newtable.reset_index(drop=True, inplace=True)
newtable.set_index('Final Rank',inplace=True)
newtable.drop('Sum',axis=1,inplace=True)
newtable['Price'] = newtable['Price'].round(2)
newtable = newtable.reindex(['Name','Price','P/E','Market Cap(Cr)','ROCE(%)','ROA(%)','EV/EBITDA','EV/EBITDA rank','ROCE rank','Ticker/Code'],axis="columns")
newtable['Ticker/Code'] = newtable['Ticker/Code'].astype('string')
options = list(newtable.columns)
st.title('Screener')
uploaded_file = st.file_uploader('Upload csv from tickertape')
# st.write(type(list(options)))
st.write('Eliminate all utilities and financial stocks (i.e., mutual funds, banks, and insurance companies) from the list. If a stock has a very low P/E ratio, say 5 or less, that may indicate that the previous year or the data being used are unusual in some way. You may want to eliminate these stocks from your list. You may also want to eliminate any company that has announced earnings in the last week. (This should help minimize the incidence of incorrect or untimely data.)')
# options = st.multiselect('Select columns to display',['Price','P/E','Market Cap(Cr)','ROCE(%)','ROA(%)','EV/EBITDA','EV/EBITDA rank','ROCE rank','Ticker/Code'],['Price','P/E','Market Cap(Cr)','ROCE(%)','ROA(%)'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # df.dropna(inplace=True)/
    df.columns = df.columns.str.replace('Â','').str.replace('','').str.replace('','').str.replace('â','')

    df.sort_values(by='EV / EBIT Ratio',inplace=True,ascending=True)
    df['EV/EBIT rank'] = [*range(1,df.shape[0]+1)]

    df['EBIT/ROC'] = df['PBIT']/df['Return on Capital']
    df.sort_values(by='EBIT/ROC',inplace=True,ascending=False)
    df['EBIT/ROC rank'] = [*range(1,df.shape[0]+1)]

    df['combined'] = df['EBIT/ROC rank'] + df['EBIT/ROC']
    df.sort_values(by='combined',inplace=True,ascending=True)
    df['Final rank'] = [*range(1,df.shape[0]+1)]

    df.set_index('Final rank',inplace=True)
    options = list(df.columns)
    options = st.multiselect('Select columns to display',options,options[:3]+options[-5:-1])
    df = df[options]
else:
    options = st.multiselect('Select columns to display',options[1:],options[1:6])
    options.insert(0, 'Name')
    newtable = newtable[options]
    df = newtable.style.format({'Price': '{:.2f}', 'P/E': '{:.2f}', 'Market Cap(Cr)': '{:.2f}','ROCE(%)': '{:.2f}','ROA(%)':'{:.2f}','EV/EBITDA':'{:.2f}'})



st.table(df)
with st.beta_expander('More Info'):
    st.markdown('''
        ## Return on Capital
>  EBIT/(Net Working Capital + Net Fixed Assets)

Return on capital was measured by calculating the ratio of pretax operating earnings (EBIT) to tangible capital employed (Net Working Capital + Net Fixed Assets). This ratio was used rather than the more commonly used ratios of return on equity (ROE, earnings/equity) or return on assets (ROA, earnings/assets) for several reasons. EBIT (or earnings before interest and taxes) was used in place of reported earnings because companies operate with different levels of debt and differing tax rates. Using operating earnings before interest and taxes, or EBIT, allowed us to view and compare the operating earnings of different companies without the distortions arising from differences in tax rates and debt levels. For each company, it was then possible to compare actual earnings from operations (EBIT) to the cost of the assets used to produce those earnings (tangible capital employed).

Net Working Capital + Net Fixed Assets (or tangible capital employed) was used in place of total assets (used in an ROA calculation) or equity (used in an ROE calculation). The idea here was to figure out how much capital is actually needed to conduct the company’s business. Net working capital was used because a company has to fund its receivables and inventory (excess cash not needed to conduct the business was excluded from this calculation) but does not have to lay out money for its payables, as these are effectively an interest-free loan (short-term interest-bearing debt was excluded from current liabilities for this calculation). In addition to working capital requirements, a company must also fund the purchase of fixed assets necessary to conduct its business, such as real estate, plant, and equipment. The depreciated net cost of these fixed assets was then added to the net working capital requirements already calculated to arrive at an estimate for tangible capital employed.

**NOTE:** Intangible assets, specifically goodwill, were excluded from the tangible capital employed calculations. Goodwill usually arises as a result of an acquisition of another company. The cost of an acquisition in excess of the tangible assets acquired is usually assigned to a goodwill account. In order to conduct its future business, the acquiring company usually only has to replace tangible assets, such as plant and equipment. Goodwill is a historical cost that does not have to be constantly replaced. Therefore, in most cases, return on tangible capital alone (excluding goodwill) will be a more accurate reflection of a business’s return on capital going forward. The ROE and ROA calculations used by many investment analysts are therefore often distorted by ignoring the difference between reported equity and assets and tangible equity and assets in addition to distortions due to differing tax rates and debt levels.

------------


## Earnings Yield
> EBIT/ Enterprise Value

Earnings yield was measured by calculating the ratio of pretax operating earnings (EBIT) to enterprise value (market value of equity + net interest-bearing debt). This ratio was used rather than the more commonly used P/E ratio (price/earnings ratio) or E/P ratio (earnings/price ratio) for several reasons. The basic idea behind the concept of earnings yield is simply to figure out how much a business earns relative to the purchase price of the business.

Enterprise value was used instead of merely the price of equity (i.e., total market capitalization, share price multiplied by shares outstanding) because enterprise value takes into account both the price paid for an equity stake in a business as well as the debt financing used by a company to help generate operating earnings. By using EBIT (which looks at actual operating earnings before interest expense and taxes) and comparing it to enterprise value, we can calculate the pretax earnings yield on the full purchase price of a business (i.e., pretax operating earnings relative to the price of equity plus any debt assumed). This allows us to put companies with different levels of debt and different tax rates on an equal footing when comparing earnings yields.

For example, in the case of an office building purchased for $1 million with an $800,000 mortgage and $200,000 in equity, the price of equity is $200,000, but the enterprise value is $1 million. If the building generates EBIT (earnings before interest and taxes) of $100,000, then EBIT/EV or the pretax earnings yield would be 10 percent ($100,000/ $1,000,000). However, the use of debt can greatly skew apparent returns from the purchase of these same assets when only the price of equity is considered. Assuming an interest rate of 6 percent on an $800,000 mortgage and a 40 percent corporate tax rate, the pretax earnings yield on our equity purchase price of $200,000 would appear to be 26 percent.42 As debt levels change, this pretax earnings yield on equity would keep changing, yet the $1 million cost of the building and the $100,000 EBIT generated by that building would remain unchanged. In other words, P/E and E/P are greatly influenced by changes in debt levels and tax rates, while EBIT/EV is not.
        ''')
