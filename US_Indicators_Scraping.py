import requests
from bs4 import BeautifulSoup
from datetime import datetime

KOREAN_INDICATORS = {
    "GDP Growth Rate": "GDP 성장률",
    "GDP Annual Growth Rate": "연간 GDP 성장률",
    "Unemployment Rate": "실업률",
    "Non Farm Payrolls": "비농업 신규 고용자 수",
    "Inflation Rate": "소비자물가 상승률 (YoY)",
    "Inflation Rate MoM": "소비자물가 상승률 (MoM)",
    "Interest Rate": "연방 기준금리",
    "Balance of Trade": "무역수지",
    "Current Account": "경상수지",
    "Current Account to GDP": "경상수지 / GDP 비율",
    "Government Debt to GDP": "정부 부채 / GDP 비율",
    "Government Budget": "정부 재정 수지",
    "Business Confidence": "기업 경기 신뢰지수",
    "Manufacturing PMI": "제조업 구매관리자지수 (PMI)",
    "Consumer Confidence": "소비자 신뢰지수",
    "Retail Sales MoM": "소매판매 증감률 (전월대비)",
    "Building Permits": "주택 허가 건수"
}
INDICATOR_KOR_MAP = {k.strip(): v for k, v in KOREAN_INDICATORS.items()}

# 미국 경제지표 (TradingEconomics에서 미국 경제 관련 지표 일부 스크래핑)
def get_us_economic_indicators():
    url = "https://tradingeconomics.com/united-states/indicators"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    print(f"\n📅 미국 경제 지표 (기준일: {datetime.now().strftime('%Y-%m-%d')}):")
    try:
        table = soup.find('table', {'class': 'table'})
        rows = table.find_all('tr')[1:]

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                indicator = cols[0].text.strip()
                actual = cols[1].text.strip()
                previous = cols[2].text.strip()
                #print(indicator) 
                if indicator in INDICATOR_KOR_MAP:
                    kor_name = INDICATOR_KOR_MAP[indicator]
                    # 상승/하락 판단
                    try:
                        a_val = float(actual)
                        p_val = float(previous)
                        if a_val > p_val:
                            emoji = "🔺"
                        elif a_val < p_val:
                            emoji = "🔻"
                        else:
                            emoji = "➖"
                    except ValueError:
                        emoji = ""
                    print(f" - {kor_name}: 현재 {actual}, 이전 {previous} {emoji}  # {indicator}")
    except Exception as e:
        print("경제 지표 스크래핑 오류:", e)


if __name__ == "__main__":
    print(f"📅 데이터 기준일: {datetime.now().strftime('%Y-%m-%d')}")
    get_us_economic_indicators()
