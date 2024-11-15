# Import Libraries
import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
import pdfkit
import json

# Function to scrape website data
def scrape_website(url, extraction_type):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if extraction_type == "All Text":
        data = [p.text.strip() for p in soup.find_all('p')]
    elif extraction_type == "Images":
        data = [img['src'] for img in soup.find_all('img')]
    elif extraction_type == "Links":
        data = [a['href'] for a in soup.find_all('a', href=True)]
    elif extraction_type == "Tables":
        data = []
        tables = soup.find_all('table')
        for table in tables:
            df = pd.read_html(str(table))
            data.append(df[0])
    return data

# Function to convert data to DataFrame
def convert_to_df(data):
    if isinstance(data, list):
        df = pd.DataFrame(data, columns=['Data'])
    else:
        df = pd.concat(data, ignore_index=True)
    return df

# Streamlit Application
st.title("Web Data Scraper")

# Input URL
url = st.text_input("Enter URL:", placeholder="https://www.example.com")

# Extraction type
extraction_type = st.selectbox("Select Extraction Type:", ["All Text", "Images", "Links", "Tables"])

# Scrape data button
if st.button("Scrape Data"):
    data = scrape_website(url, extraction_type)
    if extraction_type == "Images":
        st.write("Extracted Images:")
        for img_url in data:
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            st.image(img)
    elif extraction_type == "Tables":
        df = convert_to_df(data)
        st.write(df)
    else:
        df = convert_to_df(data)
        st.write(df)

    # Download options
    download_format = st.selectbox("Select Download Format:", ["CSV", "Excel", "JSON", "PDF"])
    if download_format == "CSV":
        @st.cache
        def convert_df(x):
            return x.to_csv(index=False)
        csv = convert_df(df)
        st.download_button(label="Download CSV", data=csv, file_name="data.csv")
    elif download_format == "Excel":
        @st.cache
        def convert_df(x):
            return x.to_excel(index=False)
        excel = convert_df(df)
        st.download_button(label="Download Excel", data=excel, file_name="data.xlsx")
    elif download_format == "JSON":
        @st.cache
        def convert_df(x):
            return x.to_json(orient='records')
        json = convert_df(df)
        st.download_button(label="Download JSON", data=json, file_name="data.json")
    elif download_format == "PDF":
        @st.cache
        def convert_df(x):
            return pdfkit.from_string(x.to_html(), False)
        pdf = convert_df(df)
        st.download_button(label="Download PDF", data=pdf, file_name="data.pdf")

# Additional Features
st.header("Additional Features")
col1, col2 = st.columns(2)

with col1:
    if st.button("Get Website Screenshot"):
        st.write("Screenshot of the Website:")
        # Use selenium or pyppeteer to take screenshot

with col2:
    if st.button("Get Website Meta Tags"):
        st.write("Meta Tags of the Website:")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            st.write(tag.attrs)

# Settings
st.header("Settings")
col1, col2 = st.columns(2)

with col1:
    st.write("User Agent:")
    user_agent = st.text_input("", placeholder="Default User Agent")

with col2:
    st.write("Timeout:")
    timeout = st.slider("", min_value=1, max_value=10, value=5)
