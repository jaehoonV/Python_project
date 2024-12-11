import requests
import xml.etree.ElementTree as ET

def load_config(file_path):
    tree = ET.parse(file_path)  # XML 파일 파싱
    root = tree.getroot()

    # 필요한 데이터 추출
    app_key = root.find("./api/app_key").text
    app_secret = root.find("./api/app_secret").text
    access_token = root.find("./api/access_token").text

    return app_key, app_secret, access_token

# Token URL
# url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"

# app_key, app_secret, access_token = load_config("./API_Key/api_key.xml")

# headers = {"content-type": "application/json"}
# data = {
#     "grant_type": "client_credentials",
#     "appkey": app_key,
#     "appsecret": app_secret
# }

# response = requests.post(url, headers=headers, json=data)
# access_token = response.json()['access_token']
# print(f"Access Token: {access_token}")

# 주식현재가 시세
url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"

app_key, app_secret, access_token = load_config("./API_Key/api_key.xml")

headers = {
    "Authorization": f"Bearer {access_token}",
    "appkey": app_key,
    "appsecret": app_secret,
    "tr_id": "FHKST01010100"  # 시세 조회 TR ID
}
params = {
    "fid_cond_mrkt_div_code": "J",  # J : 주식, ETF, ETN / W : ELW
    "fid_input_iscd": "005930"     # 종목 코드 삼성전자(005930)
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
print(data)