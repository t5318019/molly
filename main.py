import requests
import csv
import os.path
import os
import re
from urllib.parse import urlparse
from urllib.parse import urljoin
requests.packages.urllib3.disable_warnings()

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PAGE_DIR = os.path.join(os.path.dirname(__file__), 'page')

HEADERS = {
    'ACCEPT-LANGUAGE': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'ACCEPT-ENCODING': 'gzip, deflate, br',
    'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

def get_html(urlpath):
    response = requests.get(urlpath, headers=HEADERS, verify=False)
    encodings = requests.utils.get_encodings_from_content(response.text)
    if encodings:
        response.encoding = encodings[0].lower()
    if response.encoding.lower() == 'iso-8859-1':
        response.encoding = 'utf-8'
    if response.encoding.lower() == 'big-5':
        response.encoding = 'big5'
    return response

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(PAGE_DIR):
        os.mkdir(PAGE_DIR)

    csv_filename = os.path.join(DATA_DIR, 'u1_new.csv')
    if not os.path.exists(csv_filename):
        response = requests.get('http://stats.moe.gov.tw/files/school/108/u1_new.csv', headers=HEADERS, verify=False)
        if response.status_code == 200:
            with open(csv_filename, 'w') as f:
                text = response.text
                text = text.replace('\u3000','')
                text = text.replace(' ','')
                text = text.replace('www2','www')
                f.write(text)

    with open(csv_filename, newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            urlresult = urlparse(row['網址'].lower())
            urlpath = 'http://' + urlresult.netloc

            while True:
                print(urlpath)
                response = get_html(urlpath)
                m = re.search('http-equiv=[\'"]*refresh[\'"]*\s+content=[\'"]\s*\d\s*;\s*url=([\w\/:.-]+)', response.text, flags=re.IGNORECASE)
                if m:
                    refresh_url = m[1].lower()
                    refresh_url = refresh_url if refresh_url.startswith('http') else urljoin(response.url, refresh_url)
                    refresh_url = refresh_url.replace('https', 'http')
                    urlpath = refresh_url
                else:
                    break
            html_filename = urlresult.netloc + '.html'
            with open(os.path.join(PAGE_DIR, html_filename), 'w') as f:
                f.write(response.text)
            print(row['學校名稱'], urlresult.netloc, response.encoding, sep=': ')
