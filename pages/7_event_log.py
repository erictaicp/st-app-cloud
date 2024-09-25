import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
import yaml
import ast
import re
import pandas as pd
from azure.storage.blob import BlobServiceClient
from datetime import datetime  # Import datetime module
from utils import add_logo

# Load environment variables
load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'app')))

# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Use os.path.join to navigate to the config.yaml file
config_path = os.path.join(dir_path, '..', '..', 'app', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

configInputDict = config['inputs']
configDBDict = config['database']
db_name = configDBDict['db_name']

# MongoDB connection setup
mongo_conn_str = os.getenv("MONGOCONN")

event_log_collection_name = 'event_log'
client = MongoClient(mongo_conn_str)
db = client[db_name]
event_log_collection = db[event_log_collection_name]

# Retrieve all event types for the multi-select checkbox
all_event_types = event_log_collection.distinct("event_type")

# Retrieve all order IDs for the dropdown
all_order_ids = event_log_collection.distinct("order_id")

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
# Move search functionality to the sidebar
st.sidebar.title("Search Options")
use_free_text_search = st.sidebar.checkbox("Enable free text search")

# Initialize search_term
search_term = ""

if use_free_text_search:
    search_term = st.sidebar.text_input("Search", "")
else:
    selected_event_types = st.sidebar.multiselect("Select Event Types", all_event_types)
    selected_order_id = st.sidebar.selectbox("Select Order ID", [""] + all_order_ids)

# Function to build a recursive search query
def build_recursive_search_query(search_term, content, parent_key=''):
    query = []
    for key, value in content.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            query.extend(build_recursive_search_query(search_term, value, full_key))
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    query.extend(build_recursive_search_query(search_term, item, f"{full_key}.{idx}"))
                else:
                    query.append({full_key: {"$regex": search_term, "$options": "i"}})
        else:
            query.append({full_key: {"$regex": search_term, "$options": "i"}})
    return query

# Retrieve documents from the collection with live search
query = {}
if search_term:
    if use_free_text_search:
        sample_doc = event_log_collection.find_one()
        if sample_doc:
            query = {"$or": build_recursive_search_query(search_term, sample_doc)}
    else:
        if selected_order_id:
            query["order_id"] = selected_order_id

if not use_free_text_search and selected_event_types:
    query["event_type"] = {"$in": selected_event_types}

event_log_documents = list(event_log_collection.find(query))

# Parse and sort event log documents by created_time
for doc in event_log_documents:
    doc['created_time'] = datetime.strptime(doc['created_time'], "%d/%m/%Y %I:%M%p")

event_log_documents.sort(key=lambda x: x['created_time'])

# Function to display event log document details
def display_event_log_document(doc):
    with st.expander(f"Time: {doc['created_time']} - Event Type: {doc.get('event_type', 'N/A')}", expanded=False):
        st.text(f"Created Time: {doc['created_time'].strftime('%d/%m/%Y %I:%M%p')}")
        st.text(f"Event ID: {doc.get('_id', 'N/A')}")
        st.text(f"Event Type: {doc.get('event_type', 'N/A')}")
        st.text(f"Order ID: {doc.get('order_id', 'N/A')}")
        # st.text(f"Activity: {doc.get('activity', 'N/A')}")

        # Reformat the string
        message = doc.get('activity', 'N/A')
        message = re.sub(r'\s+', ' ', message.strip())
        st.text(f"Activity: {message}")


# Display event logs
st.title("Event Logs")
for doc in event_log_documents:
    display_event_log_document(doc)
    st.markdown("---")