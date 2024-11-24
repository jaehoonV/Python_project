import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta

# 1. 데이터 다운로드
ticker = "AAPL"
print("Downloading stock data...")
stock = yf.Ticker(ticker)
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')

data = stock.history(start=start_date, end=end_date)

# 데이터가 비어 있을 경우 처리
if data.empty:
    print(f"No data available for {ticker} in the specified period.")
    exit()

# 2. 이동평균선 계산
data['MA5'] = data['Close'].rolling(window=5).mean()
data['MA20'] = data['Close'].rolling(window=20).mean()
data['MA60'] = data['Close'].rolling(window=60).mean()
data['MA120'] = data['Close'].rolling(window=120).mean()

# 볼린저 밴드 계산
data['BB_upper'] = data['MA20'] + (data['Close'].rolling(window=20).std() * 2)
data['BB_lower'] = data['MA20'] - (data['Close'].rolling(window=20).std() * 2)

# 3. 캔들 차트에 필요한 데이터 포맷 변경
data_candles = data[['Open', 'High', 'Low', 'Close', 'Volume']]

# 4. 이동 평균선 및 볼린저 밴드 추가
apds = [
    mpf.make_addplot(data['MA5'], color='blue'),
    mpf.make_addplot(data['MA20'], color='orange'),
    mpf.make_addplot(data['MA60'], color='green'),
    mpf.make_addplot(data['MA120'], color='red'),
    mpf.make_addplot(data['BB_upper'], color='purple'),
    mpf.make_addplot(data['BB_lower'], color='purple')
]

# 5. 차트 그리기
mpf.plot(data_candles, type='candle', style='charles',
         title=f"{ticker} Stock Prices with Moving Averages", ylabel="Price (USD)",
         ylabel_lower="Volume", volume=True, addplot=apds)
