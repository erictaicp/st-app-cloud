import os
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import yaml
import streamlit as st
from utils import add_logo

# Load environment variables and configurations
load_dotenv()
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'app', 'config.yaml')

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Database configuration
configDBDict = config['database']
db_name = configDBDict['db_name']
collection_name = configDBDict['collection']
mongo_conn_str = os.getenv("MONGOCONN")

# MongoDB connection setup
client = MongoClient(mongo_conn_str)
db = client[db_name]
collection = db[collection_name]

# Function definitions
def load_data():
    data = list(collection.find())
    return pd.DataFrame(data)

def display_logo(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    st.image(image, width=200)

def read_markdown_file(markdown_file):
    with open(markdown_file, "r", encoding="utf-8") as file:
        return file.read()

# Main app logic
def main():
    # Set page configuration and theme
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    add_logo()
    # Title and introduction
    st.title("🛰️ Order Tracking 📡")
    st.markdown("Welcome to Order Tracking! Use the sidebar to navigate between pages. 🧭")

    # Load and process data
    df = load_data()
    process_dataframe(df)

    # Display statistics and recent orders
    display_statistics(df)
    display_recent_orders(df)

def process_dataframe(df):
    if 'Created Time' in df.columns:
        df['Created Time'] = pd.to_datetime(df['Created Time'], errors='coerce', dayfirst=True)
    if 'Last Modified' in df.columns:
        df['Last Modified'] = pd.to_datetime(df['Last Modified'], errors='coerce', dayfirst=True)

def display_statistics(df):
    st.markdown("## 📊 Statistics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    metrics = calculate_statistics(df)
    for col, (label, value) in zip([col1, col2, col3, col4, col5, col6], metrics.items()):
        col.metric(label, value)

def calculate_statistics(df):
    statistics = {
        "Total Docs 📄": len(df),
        "Total Orders 📦": df['Order'].nunique() if 'Order' in df.columns else 0,
        "Pending 🕓": df[df['Status'] == 'Document Required'].shape[0] if 'Status' in df.columns else 0,
        "AI Validated 💻": df[df['Status'] == 'AI Validated'].shape[0] if 'Status' in df.columns else 0,
        "Human Validated 🧑‍💻": df[df['Status'] == 'Human Validated'].shape[0] if 'Status' in df.columns else 0,
        "Approved 🆗": df[df['Status'] == 'Approved'].shape[0] if 'Status' in df.columns else 0,
    }
    return statistics

def display_recent_orders(df):
    st.markdown("## 📑 Recent Orders")
    if 'Order' in df.columns:
        df_grouped = df.groupby('Order').agg(
            Total_Documents=pd.NamedAgg(column='Status', aggfunc='count'),
            Done_Documents=pd.NamedAgg(column='Status', aggfunc=lambda x: (x != 'Document Required').sum())
        )
        df_grouped['Proceed_Rate'] = (df_grouped['Done_Documents'] / df_grouped['Total_Documents'] * 100).round(2)
        df_grouped.reset_index(inplace=True)
        df_grouped.rename(columns={
            'Total_Documents': "Total Documents",
            'Done_Documents': 'Completed Documents',
            'Proceed_Rate': 'Progress Rate'}, 
            inplace=True)
        df_grouped.index = pd.RangeIndex(start=1, stop=len(df_grouped)+1)
        st.table(df_grouped)
    else:
        st.write("No orders to display.")

if __name__ == "__main__":
    main()
