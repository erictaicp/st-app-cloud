import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
import requests
import yaml, uuid
import pandas as pd
from datetime import datetime
from PIL import Image
import pdf2image
from azure.storage.blob import BlobServiceClient
from textwrap import dedent
from concurrent.futures import ThreadPoolExecutor
import threading
from utils import add_logo

# Load environment variables
load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','app')))
import os
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

def dl_file(_container, _blob, _filename = None, _folder = None, blob_service_client=blob_service_client):
    """
    _container = os.getenv('BLOB_CONTAINER')
    _blob = 'NetAPorter/image/event/vacation/pri/1647597326624016.jpg'
    _blobImageHash = dl_file( _container= _container ,_blob = _blob)
    """
    blob_client = blob_service_client.get_blob_client(container=_container, blob=_blob)
    
    # Check if the blob exists and is not empty
    try:
        blob_properties = blob_client.get_blob_properties()
        if blob_properties.size == 0:
            print(f"Blob {_blob} is empty. Skipping download.")
            return None
    except Exception as e:
        print(f"Failed to get properties for blob {_blob}. Error: {str(e)}")
        return None

    if _filename:
        file_hash = _filename
    else:
        filentype = _blob.split('.')[-1]
        file_hash = hashlib.sha256(_blob.encode('utf-8')).hexdigest() + '.' + filentype
    
    if _folder:
        os.makedirs(_folder, exist_ok=True)  # Create the directory if it doesn't exist
        file_hash = os.path.join(_folder, file_hash)
        
    with open(file_hash, "wb") as my_blob:
        download_stream = blob_client.download_blob()
        my_blob.write(download_stream.readall())
        
    return file_hash


def up_file(_container, _blob, _up_name=None, data=None, blob_service_client=blob_service_client):
    # Create a BlobClient object for the container and blob
    blob_client = blob_service_client.get_blob_client(container=_container, blob=_blob)
    if data:
        blob_client.upload_blob(data, overwrite=True)
    elif _up_name:
        # Upload the file to the blob
        with open(_up_name, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
    else:
        raise ValueError("Either 'data' or '_up_name' must be provided.")
    

# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Use os.path.join to navigate to the config.yaml file
config_path = os.path.join(dir_path, 'app', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

configInputDict = config['inputs']
configDBDict = config['database']
db_name = configDBDict['db_name']
collection_name = configDBDict['collection']

# MongoDB connection setup
mongo_conn_str = os.getenv("MONGOCONN")

# Azure Blob Service Client
blob_container = os.getenv('BLOB_CONTAINER')
blob_service_client = BlobServiceClient.from_connection_string(os.getenv('BLOB_CONN'))

client = MongoClient(mongo_conn_str)
db = client[db_name]
collection = db[collection_name]

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
# Title and introduction
st.title("📑 Document Upload Portal 🔮")
st.markdown("Welcome to the document upload portal. Here, you can upload documents related to your orders.")

# Sidebar for input
st.sidebar.title("Order Information")

from fastapi import FastAPI, HTTPException, APIRouter

# Get the query parameters
query_params = st.query_params
order_id = query_params['order_id'] if 'order_id' in query_params else None

if not order_id:
    order_id = st.sidebar.text_input("Enter the Order ID")

upload_lock = threading.Lock()

def handle_file_upload(order, doc_name, uploaded_file):
    with upload_lock:
        file_bytes = uploaded_file.read()
        file_path = f"{order_id}_{doc_name}.{uploaded_file.type.split('/')[-1]}"
        blob_path = f"data/orders/{order_id}/{file_path}"
        up_file(blob_container, _blob=blob_path, data=file_bytes)

        modification_date = str(datetime.now().date())
        
        collection.update_one({"_id": order['_id']}, {"$set": {"st_modified_date": modification_date, "blob_path": blob_path}})
        file_path = dl_file(_container=blob_container, _blob=blob_path, _folder="/mnt/alchemist/temp_data", blob_service_client=blob_service_client)
        
        prompt = dedent(f"""\
                        I would like to submit a document.
                        Please validate the document.
                        doc_type is {doc_name}.
                        order is {order_id},
                        image_path is {file_path}.
                        """).strip()
        
        #url = "http://localhost:8080/agent/agent-call"
        url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"

        payload = {'message': prompt, 
                   'user_id': configInputDict['admin_id'][0], 
                   'thread_id': str(uuid.uuid4())}

        response = requests.post(url, json=payload)
        response_dict = response.json()

        ai_answer = response_dict['ai_response']
        st.write(ai_answer)

        if uploaded_file.type in ["application/pdf"]:
            try:
                images = pdf2image.convert_from_bytes(file_bytes, first_page=1, last_page=1)
                st.image(images[0], caption='Page 1', use_column_width=True)
            except:
                st.write("PDF could not be displayed.")

        elif uploaded_file.type in ["image/png", "image/jpg", "image/jpeg"]:
            image = Image.open(file_path)
            st.image(image, use_column_width=True)
            
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
            df = pd.read_excel(file_path)
            st.dataframe(df)

        elif uploaded_file.type in ["text/plain"]:
            text = open(file_path, 'r').read()
            st.text(text)
        else:
            st.write(file_bytes)

# Only show the upload form if the order ID is entered
if order_id:
    # Check if the order exists
    order_count = collection.count_documents({"Order": order_id})
    if order_count > 0:
        orders = collection.find({"Order": order_id})

        total_missing_docs = 0  # Initialize total missing documents counter

        for order in orders:
            status = order.get('Status', '')

            if status not in ['Approved', 'AI Validated']:
                missing_docs = order.get('Document', '').split(',')
                total_missing_docs += len(missing_docs)
            else:
                missing_docs = []

            if missing_docs:
                with ThreadPoolExecutor() as executor:
                    futures = []
                    for doc_name in missing_docs:
                        st.markdown(f"### 📤 Upload {doc_name}")
                        with st.form(key=f'upload_form_{order_id}_{doc_name}'):
                            st.markdown(f"##### 📁 Select {doc_name} to upload")
                            uploaded_file = st.file_uploader("", type=["pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg"], key=f'file_uploader_{order_id}_{doc_name}')
                            submit_button = st.form_submit_button(label='Upload Document')

                        if submit_button and uploaded_file:
                            future = executor.submit(handle_file_upload, order, doc_name, uploaded_file)
                            futures.append(future)
                            st.success(f"✅ {doc_name} uploaded successfully for Order ID {order_id}!")
                            st.success("📋 The validation result will be delivered via WhatsApp & Email shortly. Thank you!")

                            total_missing_docs -= 1

                    # Wait for all futures to complete
                    for future in futures:
                        future.result()

        if total_missing_docs > 0:
            st.sidebar.warning(f"⚠️ Order ID {order_id} has {total_missing_docs} missing documents.")
        else:
            st.sidebar.success(f"✅ All documents for Order ID {order_id} are complete.")
    else:
        st.sidebar.error(f"❌ Order ID {order_id} not found. Please check and try again.")
else:
    st.sidebar.warning("Please enter an Order ID.")