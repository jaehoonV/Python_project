import pandas as pd

# Wikipedia에서 S&P 500 데이터를 가져옵니다
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# 테이블 데이터를 DataFrame으로 로드
tables = pd.read_html(url)
sp500_table = tables[0]  # 첫 번째 테이블이 S&P 500 목록

# 필요한 열만 선택
sp500_table = sp500_table[['Symbol', 'Security']]

# CSV 파일로 저장
csv_file = "sp500_companies.csv"
sp500_table.to_csv(csv_file, index=False)

print(f"S&P 500 종목 데이터가 '{csv_file}'에 저장되었습니다.")
