from utils import util as utils
import os
from dotenv import load_dotenv
import time

load_dotenv()

url = os.getenv("WEB_URL_THREE")

soup = utils.fetch_and_parse(url)

cars = soup.select('.masonry-item')


data = {
    'price': [],
    'brand': [],
    'description': [],
    'category': [],
    'type': [],
    'location': [],
}

for car in cars:
    price = car.select_one('.qa-advert-price').get_text(strip=True)
    brand = car.select_one('.b-list-advert-base__description').get_text(strip=True)
    description = car.select_one('.b-list-advert-base__description-text').get_text(strip=True)
    category = car.select('.b-list-advert-base__item-attr')[0].get_text(strip=True)
    type = car.select('.b-list-advert-base__item-attr')[1].get_text(strip=True)
    location = car.select_one('.b-list-advert__region__text').get_text(strip=True)

    data['price'].append(price)
    data['brand'].append(brand)
    data['description'].append(description)
    data['category'].append(category)
    data['type'].append(type)
    data['location'].append(location)


print(data)


