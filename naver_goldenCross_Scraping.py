import requests
from bs4 import BeautifulSoup

url = 'https://finance.naver.com/sise/item_gold.naver'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table with class 'type_5'
table = soup.find('table', {'class': 'type_5'})
rows = table.find_all('tr')[2:]  # Skip header and empty row

output = ""
for row in rows:
    cols = row.find_all('td')
    if len(cols) > 1:
        stock_name = cols[1].get_text(strip=True)
        stock_code = cols[1].find('a')['href'].split('=')[-1]
        current_price = cols[2].get_text(strip=True)
        change = cols[3].get_text(strip=True)
        percent_change = cols[4].get_text(strip=True)

        if '상승' in change:
            change = "▲ " + change.replace('상승', '').strip()
        elif '하락' in change:
            change = "▼ " + change.replace('하락', '').strip()
        else:
            change = "-"
        
        output += f"종목명: {stock_name}, 종목코드: {stock_code}, 현재가: {current_price}, 전일비: {change}, 등락률: {percent_change}\n"

print(output)
