import pandas as pd
import requests
import time
import os
import glob

DATA_DIR = "./data/estates_new/"
CSV_PATTERN = os.path.join(DATA_DIR, "data_*.csv")

BASE_URL = os.getenv("BASE_URL")

def load_seen_ads():
    seen_ads = set()
    csv_files = glob.glob(CSV_PATTERN)
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, dtype={"id": str})
            seen_ads.update(df["id"].astype(str).tolist())
        except Exception as e:
            print(f"Warning: Could not read {file}. Error: {e}")
    
    return seen_ads

def scrape_houses(max_pages=5000):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    seen_ads = load_seen_ads() 
    all_ads = []
    consecutive_empty_pages = 0  

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/api_web/v1/listing?slug=real-estate&init_page=true&page={page}&webp=false&lsmid=1741609386457"

        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                ads = data.get("adverts_list", {}).get("adverts", [])

                # Filter out already scraped ads
                new_ads = [ad for ad in ads if str(ad.get("id")) not in seen_ads]

                if not new_ads:
                    consecutive_empty_pages += 1
                    print(f"Page {page}: No new ads found (streak: {consecutive_empty_pages})")
                    if consecutive_empty_pages >= 5:
                        print("Stopping: No new ads found for multiple pages.")
                        return all_ads
                else:
                    consecutive_empty_pages = 0  
                
                all_ads.extend(new_ads)
                seen_ads.update(str(ad["id"]) for ad in new_ads)

                print(f"Scraped page {page} - {len(new_ads)} new ads found")
                time.sleep(2)
                break  

            except requests.exceptions.RequestException as e:
                print(f"Error on page {page}, attempt {attempt+1}: {e}")
                time.sleep(2**attempt)  

    return all_ads

# Run the scraper
new_houses_data = scrape_houses()

if new_houses_data:
    # Process new ads into structured format
    flattened_data = []
    
    for ad in new_houses_data:
        # Handle missing attributes safely
        property_size = bedrooms = furnishing = bathrooms = "N/A"
        attrs = ad.get("attrs", [])
        
        for attr in attrs:
            if attr['name'] == 'Property size':
                property_size = attr.get('value', 'N/A')
            elif attr['name'] == 'Bedrooms':
                bedrooms = attr.get('value', 'N/A')
            elif attr['name'] == 'Furnishing':
                furnishing = attr.get('value', 'N/A')
            elif attr['name'] == 'Bathrooms':
                bathrooms = attr.get('value', 'N/A')

        flattened_data.append({
            "id": str(ad.get("id")),
            "title": ad.get("title", "N/A"),
            "price": ad.get("price_title", "N/A"),
            "location": ad.get("region", "N/A"),
            "property_size": property_size,
            "bedrooms": bedrooms,
            "furnishing": furnishing,
            "bathrooms": bathrooms,
            "description": ad.get("short_description", "N/A"),
            "status": ad.get("status", "N/A"),
        })

    # Convert to DataFrame
    df = pd.DataFrame(flattened_data)

    # Save new ads in chunks to CSV
    os.makedirs(DATA_DIR, exist_ok=True)
    chunksize = 10_000

    for i, chunk in enumerate(range(0, len(df), chunksize)):
        chunk_df = df.iloc[chunk:chunk + chunksize]
        output_file = os.path.join(DATA_DIR, f"data_{i}.csv")

        chunk_df.to_csv(output_file, index=False, header=(not os.path.exists(output_file)), mode="a")
        print(f"Saved {len(chunk_df)} new ads to {output_file}")

else:
    print("No new ads found. No data saved.")
