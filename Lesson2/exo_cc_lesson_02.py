import requests
from bs4 import BeautifulSoup

acer_URL = "https://www.cdiscount.com/informatique/ordinateurs-pc-portables/pc-portables/lf-228394_6-acer.html#_his_"
dell_URL = "https://www.cdiscount.com/informatique/ordinateurs-pc-portables/pc-portables/lf-228394_6-dell.html#_his_"

def getRebates(url):
    rebates = []
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    prdt_blocs = soup.find_all("div", class_="prdtBloc")
    for product in prdt_blocs:
        prices = getPrices(product)
        rebates.append(prices[0] / prices[1])
    return rebates

def printRebates(rebates):
    print("Ratios entre ancien prix et nouveau prix")
    for rebate in rebates:
        print(rebate)

def getPrices(tag):
    current_str_price = tag.find_all("div", class_="prdtPrice")[0].find_all("span", class_ = "price")[0].contents[0]
    current_price = int(current_str_price)
    previous_str_price_tag = tag.find_all("div", class_="prdtPInfoT")[
        0].find_all("div", class_="prdtPrSt")
    if len(previous_str_price_tag) == 0:
        previous_price = current_price
    else:
        previous_price = int(previous_str_price_tag[0].string.split(",")[0])
    return previous_price, current_price

print("Dell")
printRebates(getRebates(dell_URL))

print("\nAcer")
printRebates(getRebates(acer_URL))
