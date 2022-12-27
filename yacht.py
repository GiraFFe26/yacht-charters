import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv
from requests.exceptions import RetryError


def collect_data(url):
    ua = UserAgent()
    retry_strategy = Retry(
        total=10,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    category = 'Y'
    lang = 'RU'
    sku = 13000
    with open(f'{category}{lang}.csv', 'w', encoding='cp1251', errors='replace', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        spamwriter.writerow(["Category", "Title", "Description", "Text", "Photo", "Price", "SKU"])
        k = 1
        r = http.get(url, headers={'user-agent': ua.random})
        soup = BeautifulSoup(r.text, 'lxml')
        items = soup.find('div', class_='yacht-plugin yacht-columns-container').find_all('div', class_='yacht-plugin'
                                                                                                       ' yacht-single')
        for item in items:
            url = item.find('a').get('href')
            price = str(item.find('span', class_='yacht-plugin yacht-present-price').text)
            price = price.split()[0].replace('$', '').replace(',', '').replace('฿', '')
            capac = item.find('div', class_='icon-5-1').text
            overn = item.find('div', class_='icon-6-1').text
            try:
                r = http.get(url, headers={'user-agent': ua.random})
            except RetryError:
                continue
            soup = BeautifulSoup(r.text, 'lxml')
            try:
                name = soup.find('h3', class_='yacht-plugin yacht-single-title').text
            except AttributeError:
                continue
            description = f'Capacity: {capac} Guests | Overnight: {overn} Guests'
            images = soup.find_all('img', class_='skip-lazy bwg_standart_thumb_img_0')
            image_urls = [soup.find('div', class_='yacht-plugin yacht-featured').find('img').get('src')]
            for image in images:
                url = image.get('data-src')
                image_urls.append(url)
            info = soup.find('div', class_='yacht-plugin yacht-single-info').find_all('p')
            text = info[0].text
            for i in info[1:]:
                text += f'\n\n{i.text}'
            text = text.replace('✓', '').replace('✖', '').strip()
            pos = f'{category}{k}'
            k += 1
            sku += 1
            spamwriter.writerow([f'{category}/{lang}', pos,
                                 description, text.replace(name, pos), ';'.join(image_urls), price, sku])
            with open(f'{category}{lang}.txt', 'a', encoding='UTF-8') as file:
                file.write(f'{name} - {pos}\n')


def main():
    collect_data('https://yacht-charters-phuket.com')


if __name__ == '__main__':
    main()
