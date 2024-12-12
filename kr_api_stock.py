import requests
import xml.etree.ElementTree as ET
import pandas as pd
import json

def load_config(file_path):
    tree = ET.parse(file_path)  # XML 파일 파싱
    root = tree.getroot()

    # 필요한 데이터 추출
    app_key = root.find("./api/app_key").text

    return app_key

url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

app_key = load_config("./API_Key/apis_key.xml")

url += "?serviceKey=" + app_key
url += "&numOfRows=" + "3000"
url += "&pageNo=" + "1"
url += "&resultType=" + "json"
url += "&basDt=" + "20241211"

print(url)

try:
    # Sending GET request to the API
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the JSON response
    data = json.loads(response.text)
    stock_data = data['response']['body']['items']

    if not stock_data:
        print("No stock data found.")

    # Converting to a Pandas DataFrame for analysis
    df = pd.DataFrame(stock_data)
    print(df)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
