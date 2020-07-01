import requests
from bs4 import BeautifulSoup
import json
import glob
import pandas as pd

# agar tetap bisa akses diperlukan session login
session = requests.session()

# metode login
def login():
    print('login...')
    datas = {
        'username': 'user',
        'password': 'user12345'
    }
    res = session.post('http://167.172.70.208:9999/login', data=datas)
    f = open('./res.html', 'w+')
    f.write(res.text)
    f.close()

# mendapatkan jumlah total page
    soup = BeautifulSoup(res.text, 'html5lib')
    page_item = soup.find_all('li', attrs={'class': 'page-item'})
    total_page = len(page_item) - 2
    return total_page

# mengambil url tiap page
def get_urls(page):
    print('getting page...{}'.format(page))
    params = {
        'page': page
    }
    res = session.get('http://167.172.70.208:9999', params=params)
    soup = BeautifulSoup(res.text, 'html5lib')

# ambil url langsung dari file yang sudah di generate res.html
#    soup = BeautifulSoup(open('./res.html'), 'html5lib')

    titles = soup.find_all('h4', attrs={'class': 'card-title'})
    urls = []
    for title in titles:
        url = title.find('a')['href']
        urls.append(url)

    return urls

# ambil detail tiap url
def get_detail(url):
    print('getting detail...{}'.format(url))
    res = session.get('http://167.172.70.208:9999'+url)

    # f = open('./res.html', 'w+')
    # f.write(res.text)
    # f.close()

    soup = BeautifulSoup(res.text, 'html5lib')
    title = soup.find('title').text.strip()
    price = soup.find('h4', attrs={'class': 'card-price'}).text.strip()
    stock = soup.find('span', attrs={'class': 'card-stock'}).text.strip().replace('stock: ', '')
    category = soup.find('span', attrs={'class': 'card-category'}).text.strip().replace('category: ', '')
    description = soup.find('p', attrs={'class': 'card-text'}).text.strip().replace('Description: ', '')

    dict_data = {
        'title': title,
        'price': price,
        'stock': stock,
        'category': category,
        'description': description,
    }
    with open('./results/{}.json'.format(url.replace('/', '')), 'w') as outfile:
        json.dump(dict_data, outfile)

# membuat file csv dari detail tiap url
def create_csv():
    print('csv generated ...')
    files = sorted(glob.glob('./results/*.json'))

    datas = []
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
        datas.append(data)
    df = pd.DataFrame(datas)
    df.to_csv('result.csv', index=False)



# program running
def run():
    total_pages = login()
    total_urls = []
    for i in range(total_pages):
        page = i + 1
        urls = get_urls(page)
        total_urls += urls #total_urls = total_urls + urls

    with open('all_urls.json', 'w') as outfile:
        json.dump(total_urls, outfile)

    with open('all_urls.json') as json_file:
        all_url = json.load(json_file)

    for url in all_url:
        get_detail(url)

    create_csv()

if __name__ == '__main__':
    run()
