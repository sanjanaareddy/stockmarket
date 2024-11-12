import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData 
from stocknews import StockNews

st.title("Stock Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

# Download data and handle potential errors
try:
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Check if the DataFrame is empty
    if data.empty:
        st.error("No data available for this ticker and date range.")
    else:
        # Ensure 'Adj Close' is a Series
        adj_close = data['Adj Close']
        
        # Check if 'Adj Close' is valid for plotting
        if isinstance(adj_close, pd.Series) and not adj_close.empty:
            # Plotting the adjusted close price
            fig = px.line(data_frame=data.reset_index(), x='Date', y='Adj Close', title=ticker)
            st.plotly_chart(fig)

            # Pricing Data Tab
            pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])
            
            with pricing_data:
                st.header('Price Movements')
                data['% Change'] = data['Adj Close'].pct_change()
                data.dropna(inplace=True)
                st.write(data)
                annual_return = data['% Change'].mean() * 252 * 100
                st.write('Annual Return is ', annual_return, '%')
                stdev = np.std(data['% Change']) * np.sqrt(252)
                st.write('Standard Deviation is ', stdev * 100, '%')
                st.write('Risk Adj. Return is ', annual_return / (stdev * 100))

            # Fundamental Data Tab
            with fundamental_data:
                key = 'OW1639L63B5UCYYL'  # Replace with your actual API key
                fd = FundamentalData(key, output_format='pandas')
                
                # Balance Sheet
                st.subheader('Balance Sheet')
                balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
                bs = balance_sheet.T[2:]
                bs.columns = list(balance_sheet.T.iloc[0])
                st.write(bs)
                
                # Income Statement
                st.subheader('Income Statement')
                income_statement = fd.get_income_statement_annual(ticker)[0]
                is1 = income_statement.T[2:]
                is1.columns = list(income_statement.T.iloc[0])
                st.write(is1)
                
                # Cash Flow Statement
                st.subheader('Cash Flow Statement')
                cash_flow = fd.get_cash_flow_annual(ticker)[0]
                cf = cash_flow.T[2:]
                cf.columns = list(cash_flow.T.iloc[0])
                st.write(cf)

            # News Tab
            with news:
                st.header(f'News of {ticker}')
                sn = StockNews(ticker, save_news=False)
                df_news = sn.read_rss()
                
                for i in range(min(10, len(df_news))):  # Ensure we don't exceed available news items
                    st.subheader(f'News {i + 1}')
                    st.write(df_news['published'][i])
                    st.write(df_news['title'][i])
                    st.write(df_news['summary'][i])
                    title_sentiment = df_news['sentiment_title'][i]
                    st.write(f'Title Sentiment: {title_sentiment}')
                    news_sentiment = df_news['sentiment_summary'][i]
                    st.write(f'News Sentiment: {news_sentiment}')
        else:
            st.error("Adjusted Close data is not available for plotting.")

except Exception as e:
    st.error(f"An error occurred: {e}")
