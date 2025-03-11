import pandas as pd
import requests
import time
import os

BASE_URL = os.getenv("BASE_URL")

def scrape_cars(max_pages=1000):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    all_ads = []

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/api_web/v1/listing?slug=cars&init_page=true&page={page}&webp=false&lsmid=1741338785267"

        for attempt in range(3): 
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status() 
                
                data = response.json()
                ads = data.get("adverts_list", {}).get("adverts", [])
                all_ads.extend(ads)
                
                print(f"Scraped page {page} - {len(ads)} ads found")
                time.sleep(2) 
                break  
            
            except requests.exceptions.RequestException as e:
                print(f"Error on page {page}, attempt {attempt+1}: {e}")
                time.sleep(2**attempt)  

    return all_ads

# Run the scraper
cars_data = scrape_cars()

# Process data into structured format
flattened_data = []
for ad in cars_data:
    condition = transmission = mileage = None  
    
    attrs = ad.get("attrs", [])  
    for attr in attrs:
        if attr['name'] == 'Condition':
            condition = attr['value']
        elif attr['name'] == 'Transmission':
            transmission = attr['value']
        elif attr['name'] == 'Mileage':
            mileage = attr['value']

    flattened_data.append({
        "title": ad.get("title"),
        "price": ad.get("price_title"),
        "location": ad.get("region"),
        "condition": condition,
        "transmission": transmission,
        "mileage": mileage,
        "description": ad.get("short_description"),
        "phone": ad.get("user_phone"),
        "status": ad.get("status"),
    })

# Convert to DataFrame
df = pd.DataFrame(flattened_data)

# Save data in chunks to CSV
chunksize = 10_000  # Adjust based on need
for i, chunk in enumerate(range(0, len(df), chunksize)):
    chunk_df = df.iloc[chunk:chunk + chunksize]
    output_file = f'./data/cars/car_data_{i}.csv'
    
    chunk_df.to_csv(output_file, index=False, header=(i == 0))
    print(f"Saved chunk {i} to {output_file}")
