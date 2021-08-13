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
def get_url(brand = None, model = None, state = None, bodystyle = None, price_min = '3000', price_max = '150000', sort = None):

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
        car_id = str(cars['position'])
        url = cars['item']['url']
        description = cars['item']['name']
        brand = cars['item']['brand']['name']
        model = cars['item']['model']
        bodytype = cars['item']['bodyType']
        km = cars['item']['mileageFromOdometer']['value']
        engine = cars['item']['vehicleEngine']['engineDisplacement']['value']
        price = cars['item']['offers']['price']
        # append to the result
        result.append([car_id, url, description, brand, model, bodytype, km, engine, price])
        print("Result_list: Id = " + car_id + " append success......")

    return result

# save data as csv 
def save_as_csv(cars):
    print("Pandas: saving as csv........")

    now = datetime.now()
    time = str(now.strftime("%m.%d-%H:%M:%S"))
    print("Datetime: Current time = " + time)
    
    pd_data = pd.DataFrame(cars, columns = ['ID', 'URL','DESC', 'BRAND', 'MODEL', 'TYPE', 'KM', 'ENGINE', 'PRICE'])
    pd_data.to_csv(path+"carsales_data_"+time+".csv", index = False, encoding='utf-8', na_rep='MISSING')


    return None

    
# Main funtion
if __name__ == "__main__":
    # print start working
    print("Script: Start working: ........")

    #Build searching url
    url = get_url(brand = "bmw", model = "4-series", state = "new-south-wales",price_min = '3000', price_max = '30000')

    # get responce with cheap request
    response = requests.get(url, headers=headers)

    # check response valid
    if (response.status_code == 200):
        print("Requests: request success......")
        car_json = extract_html(response.text)
    else:
        print("Requests: request fail......")

    cars = clean_data(car_json)
    save_as_csv(cars)

#https://www.carsales.com.au/cars/bmw/4-series/new-south-wales-state/between-3000-40000/

