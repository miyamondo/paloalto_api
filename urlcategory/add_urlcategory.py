import requests
import xml.etree.ElementTree as ET

# ファイアウォールの設定
fw_address = ""
username = ""
password = ""

# 追加する URL とカテゴリ名
new_url = "https://example.com"
url_category = "CustomCategory"

def get_auth_token(fw_address, username, password):
    """認証トークンを取得"""
    api_key_url = f"https://{fw_address}/api/?type=keygen&user={username}&password={password}"
    response = requests.get(api_key_url, verify=False)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        return root.findtext('.//key')
    else:
        raise Exception("認証に失敗しました。")

def add_url_to_category(fw_address, token, category, url):
    """指定されたカテゴリに URL を追加する"""
    # 既存のカテゴリ設定を取得
    get_url = f"https://{fw_address}/api/?type=config&action=get&xpath=/config/devices/entry/vsys/entry[@name='vsys1']/profiles/url-filtering/entry[@name='{category}']&key={token}"
    response = requests.get(get_url, verify=False)
    if response.status_code != 200:
        raise Exception("カテゴリの取得に失敗しました。")
    
    root = ET.fromstring(response.text)
    entry = root.find('.//entry')

    if entry is None:
        raise Exception(f"カテゴリ '{category}' が見つかりません。")

    # 新しい URL を追加
    element = ET.Element('entry', {'name': url})
    entry.append(element)

    # 変更を適用する XML を作成
    edit_url = f"https://{fw_address}/api/?type=config&action=set&xpath=/config/devices/entry/vsys/entry[@name='vsys1']/profiles/url-filtering/entry[@name='{category}']/list&element=entry[@name='{url}']&key={token}"
    response = requests.get(edit_url, verify=False)
    if response.status_code != 200:
        raise Exception("URL の追加に失敗しました。")
    else:
        print(f"URL '{url}' をカテゴリ '{category}' に追加しました。")

def commit_changes(fw_address, token):
    """設定をコミットする"""
    commit_url = f"https://{fw_address}/api/?type=commit&cmd=<commit></commit>&key={token}"
    response = requests.get(commit_url, verify=False)
    if response.status_code == 200:
        print("設定をコミットしました。")
    else:
        raise Exception("コミットに失敗しました。")

def main():
    try:
        token = get_auth_token(fw_address, username, password)
        add_url_to_category(fw_address, token, url_category, new_url)
        commit_changes(fw_address, token)
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    # セキュリティ警告を無視
    requests.packages.urllib3.disable_warnings()
    main()