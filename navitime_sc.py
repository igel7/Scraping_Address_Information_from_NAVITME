# %%
import os 
import time
from urllib import request
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError
import datetime
import re
import math

# -------------使用上の注意点--------------
# 対象の種別（セブンイレブンとか、パチンコとか）を変更する場合、
# NAVITIMEのこのページ（https://www.navitime.co.jp/category/）に行って、
# 対象の種別を選び、そのurlをコード中の★★★をつけている箇所に貼り付けてください。
# 現在はとりあえずセブンイレブンのurlを貼り付けています。
# ----------------------------------------

# %% 
# 作業ディレクトリをスクリプトファイルのあるディレクトリに設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 結果を書き込むテキストファイルのパスを設定 
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M')
RESULT_FILE = os.path.join(BASE_DIR, f'kekka_{current_time}.txt')

# ※対象カテゴリのトップURLをグローバル変数として設定　★★★
BASE_CATEGORY_URL = "https://www.navitime.co.jp/category/0201001001/"


# 都道府県ごとの件数情報を取得する関数
def get_prefecture_info():
    response = request.urlopen(BASE_CATEGORY_URL)
    soup = BeautifulSoup(response, 'html.parser')
    response.close()
    
    # 辞書：キーは都道府県コード（例："01"）、値は (都道府県名, 件数)
    pref_info = {}
    
    # 各都道府県のリンク情報を取得
    for a in soup.select("ul.shortcut-link-area li a.shortcut-link-area__item__link"):
        # 例: "北海道(1020)" の形式
        text = a.get_text(strip=True)
        m = re.search(r"(.+?)\((\d+)\)", text)
        if m:
            name = m.group(1)
            count = int(m.group(2))
            # href例: "https://www.navitime.co.jp/category/0201001001/01/"
            href = a.get("href")
            code = href.rstrip('/').split('/')[-1]
            pref_info[code] = (name, count)
            print(f"{name}({code}): {count}件")
    return pref_info

# 取得した都道府県情報
pref_info = get_prefecture_info()
# print(pref_info)

# 750件以上の場合は市区町村レベルで処理するので、そのコードだけを抽出
big_pref_codes = {code for code, (name, count) in pref_info.items() if count >= 750}
print("750件以上の結果がある都道府県のコード:", big_pref_codes)

# ページ取得用関数
def gettext():
    global ken_code, current_pref_name  # 外部で設定する都道府県名とコードを利用
    response = request.urlopen(url)
    print("Fetching:", url)
    soup = BeautifulSoup(response, 'html.parser')  # パーサーを指定
    response.close()

    # BeautifulSoupオブジェクトの処理
    for t in soup.find_all(class_="spot-text"):
        texts = t.get_text()
        # 改行・各要素の区切りを置換
        line = (str(ken_code) + '|' + texts.replace('\n','')
                .replace('電話番号','|')
                .replace('住所','|')
                .replace('営業時間','|')
                .replace('取り扱い','|')
                .replace('アクセス','|'))
        # 「駅から徒歩」が含まれる部分を削除（先頭の | から始まる部分を除去）
        line = re.sub(r'\|[^|]*駅から徒歩[^|]*', '', line)
        # 対象都道府県名を先頭に追加（都道府県名|番号|・・・）
        line = current_pref_name + '|' + line
        with open(RESULT_FILE, 'a', encoding='UTF-8') as f:
            print(line, file=f)

# %% メイン処理
start_time = time.time()  # 処理開始のタイムスタンプ

# ※テストモード：最初の5都道府県のみ処理する場合、以下の設定のコメントアウトを外して使用してください。
TEST_MODE = True
TEST_PREFECTURE_COUNT = 5  # テストする都道府県数

max_prefecture = 48
if 'TEST_MODE' in globals() and TEST_MODE:
    max_prefecture = min(TEST_PREFECTURE_COUNT + 1, 48)  # 1～TEST_PREFECTURE_COUNT
    print(f"テストモード: 最初の{TEST_PREFECTURE_COUNT}都道府県のみ処理します")

total_pref = max_prefecture - 1
current_count = 0
total_records = 0  # 取得した全体の件数をカウントする変数

for ken_code in range(1, max_prefecture):
    current_count += 1
    ken = str(ken_code).zfill(2)
    if ken not in pref_info:
        print(f"{ken} の情報が見つからなかったのでスキップします")
        continue
    # 外部にグローバルで利用する対象都道府県名
    current_pref_name, count = pref_info[ken]
    
    # 750件以上の結果がある場合は市区町村レベルで取得
    if ken in big_pref_codes:
        print(f"[{current_count}/{total_pref}] {current_pref_name}({ken}): {count}件 - 市区町村レベルで取得します")
        for t in range(101, 564):
            area = ken + str(t)
            # 市区町村レベルの場合もBASE_CATEGORY_URLを利用
            hajime = f"{BASE_CATEGORY_URL}{area}"
            url = hajime
            dt_now = datetime.datetime.now()
            print(f"  {area}: {dt_now.strftime('%Y年%m月%d日_%H:%M:%S')}")
            try:
                gettext()
            except (HTTPError, URLError):
                print(f"   Error_pass: {area}")
                continue
            for i in range(1, 12):
                tsugi = hajime + f'/?page={i}'
                url = tsugi
                print(f"    {area} - page: {i}")
                try:
                    gettext()
                    time.sleep(2)
                except (HTTPError, URLError):
                    print(f"    Error_pass: {area} page {i}")
                    continue
    else:
        # 都道府県レベルの場合：1ページあたり15件とし、検索結果件数から最大ページ数を計算
        pages_to_fetch = math.ceil(count / 15) + 1
        print(f"[{current_count}/{total_pref}] {current_pref_name}({ken}): {count}件 - 都道府県レベルで取得します (1～{pages_to_fetch}ページ)")
        hajime = f"{BASE_CATEGORY_URL}{ken}"
        for page in range(1, pages_to_fetch + 1):
            if page == 1:
                url = hajime
            else:
                url = hajime + f'/?page={page}'
            print(f"    {current_pref_name}({ken}) - page: {page}/{pages_to_fetch}")
            try:
                gettext()
                time.sleep(2)
            except (HTTPError, URLError):
                print(f"    Error_pass: {current_pref_name}({ken}) page {page}")
                continue

# 取得がすべて完了したらサマリを出力
elapsed_time = time.time() - start_time
if os.path.exists(RESULT_FILE):
    with open(RESULT_FILE, 'r', encoding='UTF-8') as f:
        total_records = sum(1 for _ in f)
else:
    total_records = 0

print("\n==== 取得完了 ====")
print(f"取得した都道府県数: {current_count}")
print(f"取得した全体の件数: {total_records}")
print(f"かかった時間: {elapsed_time:.1f}秒")
print(f"結果ファイル名: {os.path.basename(RESULT_FILE)}")
print(f"結果ファイルの保存先: {os.path.dirname(RESULT_FILE)}")