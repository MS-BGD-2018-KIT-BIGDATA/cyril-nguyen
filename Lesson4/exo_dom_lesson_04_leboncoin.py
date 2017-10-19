import json
import re
from multiprocessing import Pool

import numpy as np
import pandas as pd
import requests

from distributable_function import get_car_details, get_soup_for_url

zen_re = re.compile('.*zen.*')
intens_re = re.compile('.*intens.*')
life_re = re.compile('.*life.*')
key_re = re.compile('.*"(.*)".*')
p = Pool()


def get_url_from_search_page(region, page_number):
    soup = get_soup_for_url(
        'https://www.leboncoin.fr/voitures/offres/' + region + '/?o='
        + str(page_number) + '&brd=Renault&mdl=Zoe')
    if soup is not None:
        cars = soup.find_all('section', class_='item_infos')
        return [get_car_main_infos(car, region) for car in cars]


def get_car_main_infos(car_soup, region):
    type = get_modele_from_title(str(car_soup.h2.string))
    price = int(car_soup.h3['content'])
    is_pro = len(car_soup.find_all(class_='ispro')) != 0
    url = car_soup.parent['href']
    return [type, price, is_pro, url, region]


def get_modele_from_title(title):
    if zen_re.match(title.strip().lower()) is not None:
        return 'zen'
    if intens_re.match(title.strip().lower()) is not None:
        return 'intens'
    if life_re.match(title.strip().lower()) is not None:
        return 'life'
    return np.nan


def get_phone_number_from_api(soup):
    key_tags = soup.find_all('script', text=re.compile('var apiKey = '))
    if len(key_tags) != 0:
        key_text = str(key_tags[0])
        m = key_re.search(key_text)
        key = m.group(1)
        id = str(soup.find_all('span', class_='saveAd')[0]['data-savead-id'])
        return call_phone_number_api(key, id)
    else:
        return np.nan


def call_phone_number_api(key, car_id):
    data = {
        'list_id': car_id,
        'app_id': 'leboncoin_web_utils',
        'key': key,
        'text': '1'
    }
    result = requests.post(
        'https://api.leboncoin.fr/api/utils/phonenumber.json', data)
    json_result = json.loads(result.text)
    if json_result['utils']['status'] == 'OK':
        return json_result['utils']['phonenumber']
    else:
        return np.nan


if __name__ == '__main__':
    cars_details = []
    regions = ['ile_de_france', 'provence_alpes_cote_d_azur', 'aquitaine']
    for region in regions:
        i = 1
        cars_infos = get_url_from_search_page(region, i)
        while len(cars_infos) > 0:
            cars_details += map(get_car_details, cars_infos)
            i += 1
            cars_infos = get_url_from_search_page(region, i)
    df = pd.DataFrame(cars_details,
                      columns=['model', 'price', 'pro', 'url', 'region', 'tel',
                               'year', 'km', 'argus'])
    df = df.assign(more_expansive_than_argus=df['price'] > df['argus'])
    df.to_csv("results.csv", index=False)
