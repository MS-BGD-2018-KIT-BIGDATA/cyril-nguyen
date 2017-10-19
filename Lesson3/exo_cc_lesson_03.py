import requests
import json
import pandas as pd
from bs4 import BeautifulSoup


def get_distances_between_cities(origns, destinations):
    origins_param = '|'.join(origns)
    destinations_param = '|'.join(destinations)
    result_http = requests.get("http://maps.googleapis.com/maps/api/distancematrix/json?origins=" + origins_param + "&destinations=" + destinations_param)
    json_result = json.loads(result_http.text)
    return json_result


def parse_json_matrix(matrix):
    rows = matrix["rows"]
    destinations = matrix["destination_addresses"]
    origins = matrix["origin_addresses"]
    distance_matrix = {}
    for i, origin in enumerate(origins):
        distance_matrix[origin] = {}
        for j, destination in enumerate(destinations):
            distance_matrix[origin][destination] = rows[i]["elements"][j]["distance"]["value"]
    return distance_matrix


def get_soup_for_url(url):
    res = requests.get(url)
    if res.status_code == 200:
        return BeautifulSoup(res.text, 'html.parser')


def get_df(distance_matrix):
    df = pd.DataFrame(distance_matrix)
    return df


soup = get_soup_for_url("https://lespoir.jimdo.com/2015/03/05/classement-des-plus-grandes-villes-de-france-source-insee/")
cities = soup.find_all("td", class_="xl65")
cities = [str(city.string).strip() for city in cities[1:31:3]]

matrix = get_distances_between_cities(cities, cities)
distance_matrix = parse_json_matrix(matrix)
df = get_df(distance_matrix)
df.to_csv("distances.csv", sep=";")

