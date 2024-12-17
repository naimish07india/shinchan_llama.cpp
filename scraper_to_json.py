import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

def extract_model_info(url):
    """Extract model information from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve the page: {e}")
        return None
    
    logging.info("Successfully retrieved the page")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    model_names = []
    model_sizes = []
    download_links = []
    
    download_elements = soup.find_all('a', class_='group col-span-4 flex items-center justify-self-end truncate text-right font-mono text-[0.8rem] leading-6 text-gray-400 md:col-span-3 lg:col-span-2 xl:pr-10')
    logging.info(f"Found {len(download_elements)} download elements")
    
    for element in download_elements:
        href = element.get('href')
        if href:
            model_name = href.split('/')[-1].split('?')[0]
            if model_name.endswith('.gguf'):
                model_names.append(model_name)
                size = element.text.strip().split()[0]
                model_sizes.append(size)
                download_link = f"https://huggingface.co{href}"
                download_links.append(download_link)
                logging.info(f"Found model: {model_name}, Size: {size}")
    
    logging.info(f"Total models found: {len(model_names)}")
    
    df = pd.DataFrame({
        'Capybara Model name': model_names,
        'Size (GB)': model_sizes,
        'HuggingFace Download Link': download_links
    })
    
    return df

def append_to_excel(df, file_path):
    """Append the DataFrame to an existing Excel file or create a new one if it doesn't exist."""
    from openpyxl import load_workbook

    try:
        if os.path.exists(file_path):
            book = load_workbook(file_path)
            writer = pd.ExcelWriter(file_path, engine='openpyxl')
            writer.book = book
            writer.sheets = {ws.title: ws for ws in book.worksheets}
            for sheetname in writer.sheets:
                df_existing = pd.read_excel(file_path, sheet_name=sheetname)
                df = pd.concat([df_existing, df], ignore_index=True)
            df.to_excel(writer, index=False, sheet_name=sheetname)
            writer.save()
        else:
            df.to_excel(file_path, index=False)
        logging.info(f"Data appended to {file_path}")
    except Exception as e:
        logging.error(f"Failed to append data to Excel: {e}")

def save_to_json(df, json_file_path):
    """Save the DataFrame to a JSON file."""
    data = {}
    for _, row in df.iterrows():
        model_name = row['Capybara Model name'].replace('.gguf', '')
        download_link = row['HuggingFace Download Link']
        size_gb = row['Size (GB)']
        data[model_name] = {
            "url": download_link,
            "size_gb": size_gb
        }
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)
        existing_data.update(data)
    else:
        existing_data = data
    
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
        logging.info(f"Data has been successfully saved to {json_file_path}")
    except Exception as e:
        logging.error(f"Failed to save data to JSON: {e}")

def main():
    url = input("Enter URL: ")
    if not url.startswith("http"):
        logging.error("Invalid URL. Please enter a valid URL.")
        return
    
    df = extract_model_info(url)
    if df is not None and not df.empty:
        current_working_dir_path = os.getcwd()
        excel_path = os.path.join(current_working_dir_path, 'models.xlsx')
        json_file_path = os.path.join(current_working_dir_path, 'model_name_urls.json')
        
        append_to_excel(df, excel_path)
        save_to_json(df, json_file_path)
        
        logging.info("\nDataFrame contents:")
        logging.info(df)
    else:
        logging.info("No data to save. DataFrame is empty or None.")

if __name__ == "__main__":
    main()
