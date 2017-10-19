import json
import re

import numpy as np
import requests
from bs4 import BeautifulSoup

km_re = re.compile('\s*([0-9]*\s*[0-9]+)\sKM')
# phone_number_re = re.compile('(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}')
phone_number_re = re.compile('(0|\+33)[1-9]([-. ]?[0-9]{2}){4}')


def get_car_details(car_infos):
    soup = get_soup_for_url('http:' + car_infos[3])
    phone_number = get_phone_number(soup)
    year = int(
        str(soup.find_all("span", itemprop="releaseDate")[0].string).strip())
    km = get_km(soup)
    if car_infos[0] is not np.nan:
        price = get_price(car_infos[0], year, car_infos[4], km)
    else:
        price = np.nan
    return car_infos + [phone_number, year, km, price]


def get_phone_number(soup):
    description_tags = soup.find_all("p", itemprop="description")
    if len(description_tags) > 0:
        phone_numbers = description_tags[0].find_all(text=phone_number_re)
        if len(phone_numbers) > 0:
            return phone_number_re.search(phone_numbers[0])[0].replace(
                ' ', '').replace('.', '')
    return np.nan


def get_km(soup):
    km_str = str(soup.find_all('span', class_='property',
                               text=re.compile('Kilométrage'))[0]
                 .next_sibling.next_sibling.string).strip()
    return int(km_re.search(km_str).group(1).replace(' ', ''))


def get_soup_for_url(url):
    res = requests.get(url)
    if res.status_code == 200:
        return BeautifulSoup(res.text, 'html.parser')


def get_la_centrale_url(model, year):
    if 2012 <= year < 2017:
        return ('https://www.lacentrale.fr/cote-auto-renault-zoe-' + model +
                '+charge+rapide+type+2-' + str(year) + '.html')
    elif year == 2017:
        return ('https://www.lacentrale.fr/cote-auto-renault-zoe-' +
                model + '+gamme+2017-2017.html')


def get_centrale_price_url(km, region):
    if region == 'ile_de_france':
        return ('https://www.lacentrale.fr/get_co_prox.php?km='
                + str(km) + '&zipcode=75001&month=01')
    elif region == 'provence_alpes_cote_d_azur':
        return ('https://www.lacentrale.fr/get_co_prox.php?km='
                + str(km) + '&zipcode=13001&month=01')
    elif region == 'aquitaine':
        return ('https://www.lacentrale.fr/get_co_prox.php?km='
                + str(km) + '&zipcode=33000&month=01')


def get_price(model, year, region, km=0):
    model_url = get_la_centrale_url(model, year)
    if model_url is not None:
        r = requests.get(model_url)
        session_id = r.cookies['php_sessid']
        my_cookies = requests.cookies.RequestsCookieJar()
        my_cookies.set('php_sessid', session_id)
        my_cookies.set('user_type', 'acheteur')
        r2 = requests.get(get_centrale_price_url(km, region),
                          cookies=my_cookies)
        response = json.loads(r2.text)
        if km == 0:
            return int(response['cote_brute'])
        else:
            return int(response['cote_perso'])
