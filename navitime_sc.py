import os # for checking working directory
import time
from urllib import request
from bs4 import BeautifulSoup  # BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import datetime

# -------------使用上の注意点--------------
# Note 1.
# If you need to change the target category (such as Seven-Eleven or pachinko parlors), you need to change the URL in two places in the code (marked with ★).
# 対象の種別（セブンイレブンとか、パチンコとか）を変更する場合、コード中のURLを２箇所変更する必要がある（★をつけている箇所）

# Note 2.
# Inside the definition of the function gettext(), there are replacements to appropriately remove strings, which should be modified depending on the target category.
# Similarly, within the function definition, the name of the text file where results are stored is specified, so this should be changed as needed.
# 関数gettext()を定義している中で、replaceで文字列を適宜消しているものがあるが、これは対象の種別によって変えたほうが良い
# 同じく関数定義の中で、結果を格納するテキストファイルの名前を指定しているので、ここは適宜変更する

# Note 3.
# Following the code that defines the function gettext(), there are two code blocks; the first is for prefectures with fewer targets, and the second is for prefectures with many targets.
# Open the Navitime page and check; prefectures with more than 15 items × 50 pages = 750 items per page should be assigned to the second block.
# 関数gettext()を定義しているコードの後ろに、２つコードブロックがあり、1つ目は対象が少ない都道府県、2つ目は対象が多い都道府県に対応する
# ナビタイムのページを実際に開いてみて、1ページにつき15件×50ページ=750以上の件数がある都道府県は、2つ目のブロックに指定する

# Note 4.
# In the second block, as the codes for cities/towns/villages vary by prefecture, you need to enter the maximum number for each.
# Also in the second block, within the loop for each page in the city/town/village, you need to input the maximum page number.
# Here, you input the maximum page number as 15 listings per page times the number of pages.
# 二つ目のブロックでは、都道府県によって市区町村のコードが異なるため、その最大番号を入力する必要がある（◆をつけている個所）
# 同じく二つ目のブロックでは、「市区町村の中の各ページを繰り返し処理」の中で、最大番号を入力する必要がある
# ここでは、1ページにつき15件 × 〇ページ、の最大ページ番号を入力する
# -------------使用上の注意点--------------

os.chdir('your working directory')


def gettext():

    response = request.urlopen(url)
    print(url)
    soup = BeautifulSoup(response)
    response.close()

    # handle the beautiful soup object 
 
    for t in soup.find_all(class_="spot-text"):
        texts=t.get_text()
        # Name and directory of a result text file
        with open('your working directory\\kekka.txt', 'a', encoding='UTF-8') as f:
            print(str(ken_code) + '|' +texts.replace('\n','').replace('セブンイレブン ','').replace('電話番号','|').replace('住所','|').replace('営業時間','|').replace('取り扱い','|').replace('アクセス','|'), file = f)
        # print(texts.replace('\n','').replace('取り扱い','|'))
        

# just for debug
# url = 'https://www.navitime.co.jp/category/0201001001/13'
# ken = str(9).zfill(2)
# gettext()

# Target hit Number < 750
# 対象が750件以下の都道府県に対応した処理

for ken_code in range(1,48): #Iterating through prefectures. Note that the end value indicates "less than".都道府県の繰り返し処理。エンド値は「未満」を示すことに注意！
    print(ken_code)
    hajime = 'https://www.navitime.co.jp/category//0504001/{}'.format(str(ken_code).zfill(2)) # ★
    url = hajime
    ken = str(ken_code).zfill(2)

    # Prefectures with more than 750 results must be excluded here.
    # 750件以上結果がある県はここで除外設定しないといけない
    if ken_code in [1,12,13,14,23,27,28,]:
        print("pass")
        pass
    else:
        # The format of the URL is different for the first page.
        # 1ページ目はURLの体裁が違う
        gettext()
        print(url)# check URL
        dt_now = datetime.datetime.now()
        print(str(ken_code) + '  ' + dt_now.strftime('%Y年%m月%d日_%H:%M:%S'))

        # Loop through each page within the prefectures.
        # 都道府県の中の各ページを繰り返し処理
        for i in range(1,51): 
            tsugi = hajime + '/?page={}'.format(i)
            url = tsugi
            print(str(ken_code) + '   page: ' + str(i))
            #print(url) # check URL again
            try:
                gettext() # show text
                
                # Allow a little time between requests as a courtesy to avoid overloading the server and to prevent errors that may cause skipping of pages if requests are made too quickly.
                # 少し時間を空けるのは、マナーと、速すぎるとエラーで途中のページを飛ばすことがあるため
                time.sleep(2) 
            except HTTPError:
                print("HTTPError_pass")
                pass
            except URLError:
                print("URLError_pass")
                pass

    
# Process tailored for prefectures with more than 751 entries.
# 対象が751件以上の都道府県に対応した処理 
ken = [11, 13, 14, 23, 27]
for ken_code in ken:
    # Enter the maximum value plus one!
    #　◆ 最大値＋１を入力すること！
    for t in range(101,564): 
        area = str(ken_code).zfill(2)+str(t)
        hajime = 'https://www.navitime.co.jp/category/0504001/' + area # ★
        url = hajime
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
        # print(url) # check URL
    
        # Loop through each page within the cities, towns, and villages.
        # 市区町村の中の各ページを繰り返し処理
        for i in range(1,12):
            tsugi = hajime + '/?page={}'.format(i)
            url = tsugi
            print('page: ' + str(i))
            #print(url) # check URL
            try:
                gettext() #see text

                # Allow a little time between requests as a courtesy to avoid overloading the server and to prevent errors that may cause skipping of pages if requests are made too quickly.
                # 少し時間を空けるのは、マナーと、速すぎるとエラーで途中のページを飛ばすことがあるため
                time.sleep(2)
            except HTTPError:
                print("HTTPError_pass")
                pass
            except URLError:
                print("URLError_pass")
                pass
                        
    
    
    
    
    
    