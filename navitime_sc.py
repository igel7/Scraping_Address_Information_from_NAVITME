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
# 現在はとりあえず遊園地のurlを貼り付けています。
# ----------------------------------------

# %% 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M')
RESULT_FILE = os.path.join(BASE_DIR, f'kekka_{current_time}.txt')

# ★★★ 対象カテゴリ URL
BASE_CATEGORY_URL = "https://www.navitime.co.jp/category/0202001003/"

# ◆ 閾値 / 1ページ件数
CITY_THRESHOLD = 750
PER_PAGE = 15

# ◆ 行数カウンタ / 都道府県別取得
total_lines_written = 0
pref_obtained = {}

# ◆ 市区町村 URL パターン（道路リンク除外）
CITY_URL_PATTERN = re.compile(r"/category/\d+/\d{5}/?$")

# ◆ 重複判定用セットとカウンタ
seen_lines = set()   # ◆ これまでに書き込んだユニーク行
dup_skipped = 0      # ◆ 重複でスキップした行数合計

# ◆ 都道府県URLパターン（道路リンク排除用）
PREF_URL_PATTERN = re.compile(r"/category/\d+/\d{2}/?$")  # 例: /category/0101001/01/


def get_prefecture_info():
    response = request.urlopen(BASE_CATEGORY_URL)
    soup = BeautifulSoup(response, 'html.parser')
    response.close()
    
    pref_info = {}
    for a in soup.select("ul.shortcut-link-area li a.shortcut-link-area__item__link"):
        href = a.get("href") or ""
        # ◆ 道路など別種リンクは除外: '?road=' を含む or /road/category? を含む
        if '?road=' in href or '/road/category' in href:
            continue  # ◆ 道路リンクをスキップ
        # ◆ 都道府県URLパターンにマッチしないものは除外
        if not PREF_URL_PATTERN.search(href):
            continue
        code = href.rstrip('/').split('/')[-1]
        if len(code) != 2 or not code.isdigit():
            continue  # ◆ 念のため桁数チェック
        text = a.get_text(strip=True)
        m = re.search(r"(.+?)\((\d+)\)", text)
        if not m:
            continue
        name = m.group(1)
        count = int(m.group(2))
        pref_info[code] = (name, count)
        print(f"{name}({code}): {count}件")  # ◆ 都道府県のみ出力
    return pref_info


def get_city_list(pref_code):
    """◆ 市区町村リンク抽出（道路リンク除外）"""
    pref_url = f"{BASE_CATEGORY_URL}{pref_code}/"
    try:
        resp = request.urlopen(pref_url)
    except (HTTPError, URLError):
        print(f"◆ get_city_list エラー: {pref_code}")
        return []
    soup = BeautifulSoup(resp, 'html.parser')
    resp.close()

    cities = []
    for a in soup.select("a.shortcut-link-area__item__link"):
        href = a.get('href', '')
        if not CITY_URL_PATTERN.search(href):
            continue
        code = href.rstrip('/').split('/')[-1]
        if len(code) != 5 or not code.startswith(pref_code):
            continue
        text = a.get_text(strip=True)
        m = re.search(r"(.+?)\((\d+)\)", text)
        if not m:
            continue
        name = m.group(1)
        cnt = int(m.group(2))
        if cnt == 0:
            continue
        cities.append((code, name, cnt, href.rstrip('/')))
    return cities


pref_info = get_prefecture_info()
big_pref_codes = {code for code, (name, count) in pref_info.items() if count >= CITY_THRESHOLD}
print("750件以上の結果がある都道府県のコード:", big_pref_codes)


def gettext(suppress_fetch_log=False):
    """
    ◆ 1ページ分取得してファイルへ書き込む。
       - 重複（全列一致）判定を行い、既存ならスキップ
       - 書き込んだ行数を返す
       - suppress_fetch_log=True で 'Fetching: URL' 行を出さない
    """
    global ken_code, current_pref_name
    global total_lines_written, dup_skipped, seen_lines
    response = request.urlopen(url)
    if not suppress_fetch_log:
        print("Fetching:", url)   # ◆ ログ抑制対象
    soup = BeautifulSoup(response, 'html.parser')
    response.close()

    wrote = 0
    for t in soup.find_all(class_="spot-text"):
        texts = t.get_text()
        line = (str(ken_code) + '|' + texts.replace('\n','')
                .replace('電話番号','|')
                .replace('住所','|')
                .replace('営業時間','|')
                .replace('取り扱い','|')
                .replace('アクセス','|')
                )
        line = re.sub(r'\|[^|]*駅から徒歩[^|]*', '', line)
        line = current_pref_name + '|' + line
        cols = line.split('|')
        if len(cols) >= 5:
            m = re.match(r'(\d+)', cols[4])
            if m:
                cols[4] = m.group(1)
            line = '|'.join(cols[:5])

        # ◆ 重複判定
        norm_line = line.strip()
        if norm_line in seen_lines:
            dup_skipped += 1
            continue
        seen_lines.add(norm_line)

        with open(RESULT_FILE, 'a', encoding='UTF-8') as f:
            print(line, file=f)

        wrote += 1
        total_lines_written += 1
    return wrote


# %% メイン処理
start_time = time.time()

TEST_MODE = False
TEST_PREFECTURE_COUNT = 5

max_prefecture = 48
if 'TEST_MODE' in globals() and TEST_MODE:
    max_prefecture = min(TEST_PREFECTURE_COUNT + 1, 48)
    print(f"テストモード: 最初の{TEST_PREFECTURE_COUNT}都道府県のみ処理します")

total_pref = max_prefecture - 1
current_count = 0
total_records = 0

national_theoretical_total = sum(count for (name, count) in pref_info.values())

for ken_code in range(1, max_prefecture):
    current_count += 1
    ken = str(ken_code).zfill(2)
    if ken not in pref_info:
        print(f"{ken} の情報が見つからなかったのでスキップします")
        continue
    current_pref_name, count = pref_info[ken]
    pref_start_total = total_lines_written

    if ken in big_pref_codes:
        print(f"[{current_count}/{total_pref}] {current_pref_name}({ken}): {count}件 - 市区町村レベルで取得します")
        cities = get_city_list(ken)
        total_cities = len(cities)
        print(f"  ◆ 市区町村抽出数: {total_cities} 件 ({current_pref_name})")

        for idx, (city_code, city_name, city_count, city_url) in enumerate(cities, start=1):
            if idx > 1:
                time.sleep(1)  # ◆ city 間 1 秒
            city_begin_total = total_lines_written
            hajime = city_url
            url = hajime
            # dt_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # print(f"  {city_code}: {city_name} {city_count}件 {dt_str}")  # ◆ 開始ログ（維持）

            try:
                wrote_first = gettext(suppress_fetch_log=True)  # ◆ Fetching 非表示
            except (HTTPError, URLError):
                print(f"   Error_pass: {city_code} (1st page)")
                wrote_first = 0

            pages_to_fetch = math.ceil(city_count / PER_PAGE)
            if pages_to_fetch > 1 and wrote_first > 0:
                for page in range(2, pages_to_fetch + 1):
                    url = hajime + f'/?page={page}'
                    # ◆ 市区町村は中間ページ進捗と Fetching ログを非表示
                    try:
                        gettext(suppress_fetch_log=True)
                        time.sleep(2)
                    except (HTTPError, URLError):
                        print(f"    Error_pass: {city_code} page {page}")
                        continue

            city_written = total_lines_written - city_begin_total
            print(f"  {idx}/{total_cities} {city_code}: {city_name} 取得完了 {city_written}/{city_count}件")  # ◆ 完了ログ（維持）

        pref_obtained[ken] = total_lines_written - pref_start_total

    else:
        pages_to_fetch = math.ceil(count / PER_PAGE)
        print(f"[{current_count}/{total_pref}] {current_pref_name}({ken}): {count}件 - 都道府県レベルで取得します (1～{pages_to_fetch}ページ)")
        hajime = f"{BASE_CATEGORY_URL}{ken}"
        for page in range(1, pages_to_fetch + 1):
            if page == 1:
                url = hajime
            else:
                url = hajime + f'/?page={page}'
            print(f"    {current_pref_name}({ken}) - page: {page}/{pages_to_fetch}")  # ◆ ページ進捗は維持
            try:
                gettext(suppress_fetch_log=True)  # ◆ Fetching 非表示
                time.sleep(2)
            except (HTTPError, URLError):
                print(f"    Error_pass: {current_pref_name}({ken}) page {page}")
                continue
        pref_obtained[ken] = total_lines_written - pref_start_total

# 取得完了サマリ
elapsed_time = time.time() - start_time
if os.path.exists(RESULT_FILE):
    with open(RESULT_FILE, 'r', encoding='UTF-8') as f:
        total_records = sum(1 for _ in f)
else:
    total_records = 0

print("\n==== 取得完了 ====")
print(f"取得した都道府県数: {current_count}")
print(f"取得した全体の件数(行数): {total_records}")
print(f"かかった時間: {elapsed_time:.1f}秒")
print(f"結果ファイル名: {os.path.basename(RESULT_FILE)}")
print(f"結果ファイルの保存先: {os.path.dirname(RESULT_FILE)}")

# ◆ 全国 & 都道府県別サマリ
print("\n==== 全国サマリ ====")
print(f"全国：{national_theoretical_total}件中{total_lines_written}件取得")
for code in sorted(pref_info.keys()):
    name, theoretical = pref_info[code]
    obtained = pref_obtained.get(code, 0)
    print(f"{name}：{theoretical}件中{obtained}件取得")

# ◆ 重複スキップ統計
print(f"\n◆ 重複スキップ行数: {dup_skipped} (ユニーク {total_lines_written} 行)")
