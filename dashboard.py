import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData 
from stocknews import StockNews

st.title("Stock Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input('Ticker', value='AAPL')  # Default ticker
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

# Download data and handle potential errors
try:
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    # Check if the DataFrame is empty
    if data.empty:
        st.error("No data available for this ticker and date range.")
    else:
        # Convert index to UTC for consistency
        data.index = data.index.tz_localize(None)

        # Plotting the adjusted close price
        fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
        st.plotly_chart(fig)

        # Pricing Data Tab
        pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

        with pricing_data:
            st.header('Price Movements')
            data['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
            data.dropna(inplace=True)
            st.write(data)
            annual_return = data['% Change'].mean() * 252 * 100
            st.write('Annual Return is ', annual_return, '%')
            stdev = np.std(data['% Change']) * np.sqrt(252)
            st.write('Standard Deviation is ', stdev * 100, '%')
            st.write('Risk Adj. Return is ', annual_return / (stdev * 100))

        # Fundamental Data Tab
        with fundamental_data:
            key = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Replace with your actual API key
            fd = FundamentalData(key, output_format='pandas')
            
            # Balance Sheet
            st.subheader('Balance Sheet')
            balance_sheet, _ = fd.get_balance_sheet_annual(ticker)
            if balance_sheet.empty:
                st.write("No Balance Sheet data available.")
            else:
                st.write(balance_sheet)

            # Income Statement
            st.subheader('Income Statement')
            income_statement, _ = fd.get_income_statement_annual(ticker)
            if income_statement.empty:
                st.write("No Income Statement data available.")
            else:
                st.write(income_statement)

            # Cash Flow Statement
            st.subheader('Cash Flow Statement')
            cash_flow, _ = fd.get_cash_flow_annual(ticker)
            if cash_flow.empty:
                st.write("No Cash Flow data available.")
            else:
                st.write(cash_flow)

        # News Tab
        with news:
            st.header(f'News of {ticker}')
            sn = StockNews(ticker, save_news=False)
            df_news = sn.read_rss()
            
            if len(df_news) == 0:
                st.write("No news available for this ticker.")
            else:
                for i in range(min(10, len(df_news))):
                    st.subheader(f'News {i + 1}')
                    st.write(df_news['published'][i])
                    st.write(df_news['title'][i])
                    st.write(df_news['summary'][i])
                    title_sentiment = df_news['sentiment_title'][i]
                    st.write(f'Title Sentiment: {title_sentiment}')
                    news_sentiment = df_news['sentiment_summary'][i]
                    st.write(f'News Sentiment: {news_sentiment}')

except Exception as e:
    st.error(f"An error occurred: {e}")

