import streamlit as st
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import base64
from utils import add_logo

# Load environment variables
load_dotenv()

demodata="""
{
    "_id" : ObjectId("665455c3384170f240095e89"),
    "Order" : "test0001",
    "Target" : "constantinechung@lifung.com",
    "Target Whatsapp" : "98765432",
    "Status" : "Pending",
    "Document" : "Document1",
    "Last Modified" : "27/05/2024 05:43PM",
    "Created Time" : "27/05/2024 05:43PM",
    "Due" : "31/05/2024"
}
"""

# MongoDB connection setup
mongo_conn_str = os.getenv("MONGOCONN")
client = MongoClient(mongo_conn_str)
db = client['postoffice']
collection = db['chase_order']

# Function to load data from MongoDB
def load_data():
    data = list(collection.find())
    return pd.DataFrame(data)

# Function to convert document data to base64
def to_base64(document_data):
    if document_data:
        # Assume the document data is stored as a base64 string
        return base64.b64encode(document_data).decode()

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
# Title and introduction
st.title("🔍 Chase Book 📚")
st.markdown("Here you can view and manage all orders. 🗂️")

# Load existing data
st.markdown("## 📋 Existing Orders")
data = load_data()
edited_data = st.data_editor(data, key="existing_orders")

# Bulk delete
st.markdown("## 🗑️ Bulk Delete")
delete_order_ids = st.text_input('Enter Order IDs to delete (comma separated)', key='delete_order_ids')
if st.button('Delete Orders'):
    order_ids = delete_order_ids.split(',')
    collection.delete_many({'Order': {'$in': order_ids}})
    st.success('Orders deleted successfully!')
    # Refresh the data
    data = load_data()
    # st.experimental_rerun()
    st.rerun()
# Bulk share
st.markdown("## 📤 Bulk Download")
share_order_ids = st.text_input('If empty will download all. Enter Order IDs to share (comma separated)', key='share_order_ids')
if st.button('Download Orders'):
    if share_order_ids:
        # Split the input by comma and strip spaces from each ID
        order_ids = [order_id.strip() for order_id in share_order_ids.split(',')]
        orders_to_share = collection.find({'Order': {'$in': order_ids}})
    else:
        orders_to_share = collection.find()  # Fetch all orders if no ID is provided
    
    # Convert to DataFrame
    df_to_share = pd.DataFrame(list(orders_to_share))
    
    # Remove the MongoDB ID for privacy/security before sharing
    df_to_share.drop('_id', axis=1, inplace=True)
    
    # Convert DataFrame to CSV
    csv = df_to_share.to_csv(index=False)
    
    # Encode CSV to base64
    b64 = base64.b64encode(csv.encode()).decode()
    
    # Create a download link
    href = f'<a href="data:file/csv;base64,{b64}" download="orders.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    st.success('Orders prepared for download!')