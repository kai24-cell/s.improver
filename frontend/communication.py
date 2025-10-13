import requests

API_URL="https://httpbin.org/post" #テスト用URL,テスト済

#ファイルを受け取って処理ファイルへデータを辞書にして送る関数
def data_to_api(data_FILE):
    try:
        response=requests.post(API_URL,json=data_FILE)
        response.raise_for_status()#exceptへ
        return response.json()
    except requests.exceptions.RequestException as e:
        print("ファイルを受け取れませんでした")
        return None