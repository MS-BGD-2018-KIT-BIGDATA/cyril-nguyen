import requests
from bs4 import BeautifulSoup
import re

base_url = "http://alize2.finances.gouv.fr/communes/eneuro/detail.php?icom=" \
           "056&dep=075&type=BPS&param=5&exercice="
line_titles = {"A" : "TOTAL DES PRODUITS DE FONCTIONNEMENT",
               "B" : "TOTAL DES CHARGES DE FONCTIONNEMENT",
               "C" : "TOTAL DES RESSOURCES D'INVESTISSEMENT",
               "D" : "TOTAL DES EMPLOIS D'INVESTISSEMENT"}
years_to_retrieve = range(2010, 2016)


def get_soup_for_year(year):
    res = requests.get(base_url + str(year))
    if res.status_code == 200:
        return BeautifulSoup(res.text, 'html.parser')


def get_line_data(soup, line_title):
    title_cell = soup.find_all("td", class_="libellepetit G",
                                 string=re.compile(line_title))[0]
    strate_avg = title_cell.previous_sibling.previous_sibling.string.strip()
    euro_per_inhabitants = title_cell.previous_sibling.previous_sibling\
                           .previous_sibling.previous_sibling.string.strip()
    return [strate_avg, euro_per_inhabitants]


def get_data_for_years(years_to_get):
    data = {}
    for year in years_to_get:
        data[year] = [get_line_data(get_soup_for_year(year), line_titles[line])
             for line in line_titles.keys()]
    return data


def print_data(data):
    # print(data)
    print("Moyenne par an, par habitant et par strate du :")
    print("  - " + "\n  - ".join(line_titles.values()))
    print()
    for year in data.keys():
        print("------  Année %d  ------" % year)

        for line in data[year]:
            print(" | ".join(line))


data = get_data_for_years(years_to_retrieve)
print_data(data)