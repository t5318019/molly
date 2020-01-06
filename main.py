import requests
import csv
import os.path
import os
from urllib.parse import urlparse
requests.packages.urllib3.disable_warnings()

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PAGE_DIR = os.path.join(os.path.dirname(__file__), 'page')

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
if not os.path.exists(PAGE_DIR):
    os.mkdir(PAGE_DIR)

HEADERS = {
    'ACCEPT-LANGUAGE': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'ACCEPT-ENCODING': 'gzip, deflate, br',
    'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

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
        url = urlparse(row['網址'])
        urlpath = 'http://' + url.netloc
        response = requests.get(urlpath, headers=HEADERS, verify=False)
        for encoding in requests.utils.get_encodings_from_content(response.text):
            response.encoding = encoding
        if response.encoding.lower() == 'iso-8859-1':
            response.encoding = 'utf-8'
        
        html_filename = url.netloc + '.html'
        with open(os.path.join(PAGE_DIR, html_filename), 'w') as f:
            f.write(response.text)
        print(row['學校名稱'], url.netloc, response.encoding, sep=': ')
