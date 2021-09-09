from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import requests
import json
import csv


headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
car_sales_url = "https://www.carsales.com.au/cars/"

# file save path
path = "/Users/xingxing/Desktop/"


# make the url to fetch data
def get_url(brand = None, model = None, state = None, bodystyle = None, price_min = None, price_max = None, sort = None):

    # initiate url
    search_url = car_sales_url

    # format = /cars/"brand"/"state"/"body-style"/"price-range"/sort
    if brand != None:
        search_url = search_url + brand + '/'
    if model != None:
        search_url = search_url + model + '/'
    if state != None:
        search_url = search_url + state + '-state/'
    if bodystyle != None:
        search_url = search_url + bodystyle + '-bodystyle/'
    # default price range = 0 - 800000
    if (price_min != None and price_max != None):
        search_url = search_url + "between-" + price_min + "-" + price_max + '/'

    # Show searching url
    print("Searching url: " + search_url)

    return search_url

# extract json data from raw html
def extract_html(html):
    # initialize beautiful soup
    soup = BeautifulSoup(html, 'html.parser')

    # extract json data from <script type=application/ld+json>
    try: 
        car_json = json.loads(soup.find('script', type='application/ld+json').string)
    except:
        
        # internet or server error 
        return "Fetching Data Error"

    return car_json

# clean data as list
def clean_data(car_json):
    # empty bin
    print("Result_list: Fetching data")
    result = []

    #fetch every records
    for cars in car_json['mainEntity']['itemListElement']:
        url = cars['item']['url']
        description = cars['item']['name']
        brand = cars['item']['brand']['name']
        model = cars['item']['model']
        bodytype = cars['item']['bodyType']
        km = cars['item']['mileageFromOdometer']['value']
        engine = cars['item']['vehicleEngine']['engineDisplacement']['value']
        price = cars['item']['offers']['price']
        # append to the result
        result.append([url, description, brand, model, bodytype, km, engine, price])

    return result

# save data as csv 
def save_as_csv(cars):
    print("Pandas: saving as csv........")

    now = datetime.now()
    time = str(now.strftime("%m.%d-%H:%M:%S"))
    print("Datetime: Current time = " + time)
    
    pd_data = pd.DataFrame(cars, columns = ['ID', 'URL','DESC', 'BRAND', 'MODEL', 'TYPE', 'KM', 'ENGINE', 'PRICE'])
    #pd_data = pd.DataFrame(cars, columns = ['ID','DESC', 'MODEL', 'KM', 'ENGINE', 'PRICE'])
    pd_data.to_csv(path+"carsales_data_"+time+".csv", index = False, encoding='utf-8', na_rep='MISSING')

    return None


# get n pages data
def get_n_pages(url, n):
    # ============parameters============
    # brand = None, # model = None, 
    # state = None, # bodystyle = None, 
    # price_min = '3000', # price_max = '150000', 
    # sort = None, # page = None
    # ============parameters============

    data = []
    id = 0

    for i in range(0,n+1):
        if i == 0:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url+ "?offset="+str(i*12), headers=headers)

        if (response.status_code == 200):
            print("Requests: request success......")
            car_json = extract_html(response.text)
        else:
            print("Requests: request fail......")
            return False

        offset_data = clean_data(car_json)

        for j in offset_data:
            data.append([id] + j)
            id = id + 1

        print("offset = "+str(i) + " append success")

    return data


# Main funtion
if __name__ == "__main__":
    # print start working
    print("Script: Start working: ........")

    #Build searching url
    url = get_url(brand = 'mercedes-benz', bodystyle = "suv", price_min = '10000', price_max = '150000')
    print(url)
    data = get_n_pages(url, 80)

    save_as_csv(data)

