import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
import yaml
from azure.storage.blob import BlobServiceClient
import pandas as pd
import ast
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
collection_name = 'chase_order'

# MongoDB connection setup
mongo_conn_str = os.getenv("MONGOCONN")

# Azure Blob Service Client
blob_container = os.getenv('BLOB_CONTAINER')
blob_service_client = BlobServiceClient.from_connection_string(os.getenv('BLOB_CONN'))

client = MongoClient(mongo_conn_str)
db = client[db_name]
collection = db[collection_name]

# Retrieve all orders for the dropdown
all_orders = collection.distinct("Order")

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
st.title("Human Validation")
# Move search functionality to the sidebar
st.sidebar.title("🔍 Search Options")
use_free_text_search = st.sidebar.checkbox("Enable free text search 📝")
filter_option = st.sidebar.selectbox("Filter by Validation Status", ["All", "Validated", "Not Validated"])

if use_free_text_search:
    search_term = st.sidebar.text_input("Search 🔍", "")
else:
    search_type = st.sidebar.selectbox("Search Type 🔍", ["Prefix", "Full"])
    search_term = st.sidebar.selectbox("Select Order 📦", [""] + all_orders)

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
                    query.append({f"{full_key}.{idx}": {"$regex": search_term, "$options": "i"}})
        else:
            query.append({full_key: {"$regex": search_term, "$options": "i"}})
    return query

# Retrieve documents from the collection with live search
query = {}
if search_term:
    if use_free_text_search:
        sample_doc = collection.find_one()
        if sample_doc:
            query = {"$or": build_recursive_search_query(search_term, sample_doc)}
    else:
        if search_type == "Prefix":
            prefix = search_term.split('_')[0]
            query = {"Order": {"$regex": f"^{prefix}_", "$options": "i"}}
        else:  # Full selection
            query = {"Order": search_term}

if filter_option == "Validated":
    query["human_validate_status"] = True
elif filter_option == "Not Validated":
    query["human_validate_status"] = {"$ne": True}

documents = list(collection.find(query))

# Function to display nested content with Markdown and allow modification
def display_nested_content(content, doc_id, parent_key='', indent=0, index=0):
    updated_content = {}
    for key, value in content.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        unique_key = f"{doc_id}_{full_key}_{index}"
        if isinstance(value, str):
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                pass
        if isinstance(value, dict):
            st.markdown(f"<div style='margin-left: {indent}px'><strong>{key}:</strong></div>", unsafe_allow_html=True)
            updated_content[key] = display_nested_content(value, doc_id, full_key, indent + 20, index)
        elif isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                all_keys = set().union(*(item.keys() for item in value))
                st.markdown(f"<div style='margin-left: {indent}px'><strong>{key}:</strong></div>", unsafe_allow_html=True)
                df = pd.DataFrame([{k: item.get(k, None) for k in all_keys} for item in value])
                edited_df = st.data_editor(df)
                updated_content[key] = edited_df.to_dict('records')
            else:
                try:
                    st.markdown(f"<div style='margin-left: {indent}px'><strong>{key}:</strong></div>", unsafe_allow_html=True)
                    updated_content[key] = [display_nested_content(item, doc_id, full_key, indent + 20, idx) if isinstance(item, dict) else item for idx, item in enumerate(value)]
                except:
                    pass
        else:
            new_value = st.text_input(f"{full_key}", value, key=unique_key)
            updated_content[key] = new_value
    return updated_content

# Function to display document details
def display_document(doc):
    with st.expander(f"📄 Document ID: {doc['_id']}", expanded=False):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📋 Basic Info")
            st.text(f"Order: {doc.get('Order', 'N/A')}")
            st.text(f"Status: {doc.get('Status', 'N/A')}")
            st.text(f"Document: {doc.get('Document', 'N/A')}")
            st.text(f"Created Time: {doc.get('Created Time', 'N/A')}")
            st.text(f"Due Date: {doc.get('Due Date', 'N/A')}")
            st.text(f"Blob Path: {doc.get('blob_path', 'N/A')}")
            st.subheader("📞 Contact Details")
            st.text(f"Target Email: {doc.get('Target Email', 'N/A')}")
            st.text(f"Target Whatsapp: {doc.get('Target Whatsapp', 'N/A')}")
            st.text(f"Target Wechat: {doc.get('Target Wechat', 'N/A')}")
            st.text(f"Validation Status: {'✅ Validated' if doc.get('human_validate_status') else '❌ Not Validated'}")
            
        with col2:
            try:
                st.subheader("🔍 Extracted Fields")
                updated_fields = display_nested_content(doc.get('Extracted Fields', {}), doc['_id'], 'Extracted Fields')
            except:
                pass
        if st.button("💾 Save & Confirm ✅", key=f"save_{doc['_id']}"):
            collection.update_one(
                {"_id": doc['_id']},
                {"$set": {"Extracted Fields": updated_fields, "human_validate_status": True}}
            )
            st.success(f"Document {doc['_id']} updated successfully ✅")

for doc in documents:
    display_document(doc)
    st.markdown("---")