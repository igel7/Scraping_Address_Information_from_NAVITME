import os #作業ディレクトリの確認
import time
from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート
from urllib.error import HTTPError
from urllib.error import URLError
import datetime

# -------------使用上の注意点--------------
# 注意点１.
# 対象の種別（セブンイレブンとか、パチンコとか）を変更する場合、コード中のURLを２箇所変更する必要がある（★をつけている箇所）

# 注意点２.
# 関数gettext()を定義している中で、replaceで文字列を適宜消しているものがあるが、これは対象の種別によって変えたほうが良い
# 同じく関数定義の中で、結果を格納するテキストファイルの名前を指定しているので、ここは適宜変更する

# 注意点３.
# 関数gettext()を定義しているコードの後ろに、２つコードブロックがあり、1つ目は対象が少ない都道府県、2つ目は対象が多い都道府県に対応する
# ナビタイムのページを実際に開いてみて、1ページにつき15件×50ページ=750以上の件数がある都道府県は、2つ目のブロックに指定する

# 注意点４.
# 二つ目のブロックでは、都道府県によって市区町村のコードが異なるため、その最大番号を入力する必要がある（◆をつけている個所）
# 同じく二つ目のブロックでは、「市区町村の中の各ページを繰り返し処理」の中で、最大番号を入力する必要がある
# ここでは、1ページにつき15件 × 〇ページ、の最大ページ番号を入力する
# -------------使用上の注意点--------------

os.chdir('C:\\Users\\ryasu\\Desktop\\WPy64-31050\\notebooks\\web_jikken')


def gettext():

    response = request.urlopen(url)
    print(url)
    soup = BeautifulSoup(response)
    response.close()

    # 得られたsoupオブジェクトを操作していく
 
    for t in soup.find_all(class_="spot-text"):
        texts=t.get_text()
        # ここで結果を格納するテキストファイルの場所・名前を指定する
        with open('C:\\Users\\ryasu\\Desktop\\WPy64-31050\\notebooks\\web_jikken\\kekka.txt', 'a', encoding='UTF-8') as f:
            print(str(ken_code) + '|' +texts.replace('\n','').replace('セブンイレブン ','').replace('電話番号','|').replace('住所','|').replace('営業時間','|').replace('取り扱い','|').replace('アクセス','|'), file = f)
        # print(texts.replace('\n','').replace('取り扱い','|'))
        

# just for debug
# url = 'https://www.navitime.co.jp/category/0201001001/13'
# ken = str(9).zfill(2)
# gettext()

# 対象が750件以下の都道府県に対応した処理
for ken_code in range(11,12): #都道府県の繰り返し処理。エンド値は「未満」を示すことに注意！
    print(ken_code)
    hajime = 'https://www.navitime.co.jp/category//0201001011/{}'.format(str(ken_code).zfill(2)) # ★
    url = hajime
    ken = str(ken_code).zfill(2)
    if ken_code in [13, 14, 23, 27]:
        print("pass")
        pass
    else:
        gettext()#1ページ目はURLの体裁が違う
        print(url)#URL確認
        dt_now = datetime.datetime.now()
        print(str(ken_code) + '  ' + dt_now.strftime('%Y年%m月%d日_%H:%M:%S'))
        for i in range(1,51):#都道府県の中の各ページを繰り返し処理
            tsugi = hajime + '/?page={}'.format(i)
            url = tsugi
            print(str(ken_code) + '   page: ' + str(i))
            #print(url)#URLを出力してみる
            try:
                gettext()#テキストの出力
                time.sleep(2) # 少し時間を空けるのは、マナーと、速すぎるとエラーで途中のページを飛ばすことがあるため
            except HTTPError:
                print("HTTPError_pass")
                pass
            except URLError:
                print("URLError_pass")
                pass

    
    
# 対象が751件以上の都道府県に対応した処理 
# ken = [11, 13, 14, 23, 27]
ken = [1]
for ken_code in ken:
    for t in range(1101,1457): #　◆ 最大値＋１を入力すること！
        area = str(t).zfill(5)
        hajime = 'https://www.navitime.co.jp/category/0201001011/' + area # ★
        url = hajime
        print(url)
        dt_now = datetime.datetime.now()
        print(area + '  ' + dt_now.strftime('%Y年%m月%d日_%H:%M:%S'))
        try:
            gettext()#1ページ目はURLの体裁が違う
        except HTTPError:
            print("HTTPError_pass")
            continue
        except URLError:
            print("URLError_pass")
            continue
        # print(url)#URL確認
    
        for i in range(1,12):#市区町村の中の各ページを繰り返し処理
            tsugi = hajime + '/?page={}'.format(i)
            url = tsugi
            print('page: ' + str(i))
            #print(url)#URLを出力してみる
            try:
                gettext()#テキストの出力
                time.sleep(2) # 少し時間を空けるのは、マナーと、速すぎるとエラーで途中のページを飛ばすことがあるため
            except HTTPError:
                print("HTTPError_pass")
                pass
            except URLError:
                print("URLError_pass")
                pass
                        
    
    
    
    
    
    