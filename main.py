from utils import util as utils
import os
from dotenv import load_dotenv
import time

load_dotenv()


url = os.getenv("WEB_URL_TWO")
baseUrl = os.getenv("BASE_URL_TWO")

soup = utils.fetch_and_parse(url)
raw_data = []
#title, price, currency, property type, location, size, no rooms, amenities, age of property

def get_all_page_links(soup):
    print("Extracting data...")
    time.sleep(2)

    pagination_links = soup.select("ul.pagination li a")
    
    if pagination_links:
        first_link = pagination_links[0]['href']
        
        if '?' in first_link:
            base_url = first_link.rsplit('=', 1)[0] + '='
        else:
            base_url = first_link.rsplit('/', 1)[0] + '/'
        expanded_links = [f"{base_url}{page}" for page in range(1, 51)]
       
    links = [baseUrl + a for a in expanded_links]

    return links

def get_data_from_page(soup):
    pages = soup.select("div.property-listing")
    page_data = []
    for item in pages:
       
        title = item.find('h1').get_text(strip=True)
        price = item.find('h2').get_text(strip=True)

        spans = item.find_all("span")

        # print(spans[2])

        if title and price:
            property_type = item.find('p').get_text(strip=True)
            location = item.find('h4').get_text(strip=True)
            size = item.find('li').get_text(strip=True)
            status = spans[2].get_text(strip=True)
            type = spans[3].get_text(strip=True)
            date_added = item.find(class_ = "listing-added-date").get_text(strip=True)
            
            if location:
                page_data.append({
                    "title": title, 
                    "price": price, 
                    "property type": property_type,
                    "location": location,
                    "size": size,
                    "status": status,
                    "type": type,
                    "date": date_added
                })
            else:
                print(f"Skipping article with link {url} due to missing content.")
        else:
            print(f"Could not find title or link on {url}") 
    return page_data


links = get_all_page_links(soup)

if (len(links) <= 0):
    page_soup = utils.fetch_and_parse(url)
    page_data = get_data_from_page(page_soup)
    raw_data.extend(page_data)

for link in links[:-1]:
    print(f"{link}")
    page_soup = utils.fetch_and_parse(link)
    page_data = get_data_from_page(page_soup)
    raw_data.extend(page_data)

print(len(raw_data))

output_file = 'data/estate_data_lagos_sale.csv'
fieldnames = ["title", "price", "property type", "location", "size", "status", "type", "date"]
utils.save_to_csv(raw_data, output_file, fieldnames)
