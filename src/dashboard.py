import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

st_autorefresh(interval=60000, key="datarefresh")

st.sidebar.title("Dashboard Settings")

ticker = st.sidebar.text_input(
    "Primary Stock",
    "AAPL"
).upper()

compare_ticker = st.sidebar.text_input(
    "Compare With",
    "MSFT"
).upper()

timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["1 Month", "3 Months", "6 Months", "1 Year", "5 Years"]
)

timeframe_map = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "5 Years": "5y"
}

period = timeframe_map[timeframe]

#title and description
st.title("📈 Real-Time Stock Analysis Dashboard")

st.markdown(
    """
    Analyze stock performance with:
    - Real-time price tracking
    - Technical indicators
    - Stock comparison
    - Interactive candlestick charts
    """
)

@st.cache_data
def load_stock_data(symbol, period):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    return df

df = load_stock_data(ticker, period)
compare_df = load_stock_data(compare_ticker, period)

if df.empty:
    st.error(f"No data found for {ticker}")
    st.stop()

if compare_df.empty:
    st.error(f"No data found for {compare_ticker}")
    st.stop()

df['SMA_10'] = df['Close'].rolling(window=10).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()

# Daily Return
df['Daily Return %'] = df['Close'].pct_change() * 100

# Volatility
df['Volatility'] = df['Daily Return %'].rolling(10).std()

# RSI
delta = df['Close'].diff()

gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

rs = avg_gain / avg_loss

df['RSI'] = 100 - (100 / (1 + rs))

latest_price = df['Close'].iloc[-1]

daily_return = df['Daily Return %'].iloc[-1]

highest_price = df['High'].max()

lowest_price = df['Low'].min()

avg_volume = df['Volume'].mean()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Latest Price",
    f"${latest_price:.2f}"
)

col2.metric(
    "Daily Return",
    f"{daily_return:.2f}%"
)

col3.metric(
    "Highest Price",
    f"${highest_price:.2f}"
)

col4.metric(
    "Lowest Price",
    f"${lowest_price:.2f}"
)

col5.metric(
    "Avg Volume",
    f"{avg_volume:,.0f}"
)

st.subheader(f"{ticker} Closing Price")

st.line_chart(df['Close'])

st.subheader(f"{ticker} vs {compare_ticker}")

comparison_df = pd.DataFrame({
    ticker: df['Close'],
    compare_ticker: compare_df['Close']
})

st.line_chart(comparison_df)

st.subheader("Trading Volume")

st.bar_chart(df['Volume'])


st.subheader("Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])

fig.update_layout(
    height=600,
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

#moving averages
st.subheader("Moving Averages")

ma_chart = pd.DataFrame({
    'Close': df['Close'],
    'SMA 10': df['SMA_10'],
    'SMA 50': df['SMA_50']
})

st.line_chart(ma_chart)

st.subheader("RSI Indicator")

rsi_fig = go.Figure()

rsi_fig.add_trace(go.Scatter(
    x=df.index,
    y=df['RSI'],
    mode='lines',
    name='RSI'
))

rsi_fig.update_layout(
    height=400,
    yaxis_title="RSI",
    xaxis_title="Date",
    template="plotly_dark"
)

st.plotly_chart(rsi_fig, use_container_width=True)


st.subheader("Market Volatility")

volatility_chart = pd.DataFrame({
    'Volatility': df['Volatility']
})

st.line_chart(volatility_chart)


# raw data
with st.expander("View Raw Data"):
    st.dataframe(df)


# download the file
csv = df.to_csv().encode('utf-8')

st.download_button(
    label="Download Stock Data CSV",
    data=csv,
    file_name=f"{ticker}_stock_data.csv",
    mime='text/csv'
)