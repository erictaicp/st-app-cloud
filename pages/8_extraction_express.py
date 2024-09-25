import streamlit as st    
import requests    
import uuid    
from datetime import datetime    
from PIL import Image    
import pdf2image    
import os    
from dotenv import load_dotenv    
from pymongo import MongoClient, ASCENDING, DESCENDING 
import yaml    
import pandas as pd  
import ast  
from azure.storage.blob import BlobServiceClient
import sys
from utils import add_logo 
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from typing import Union


def upload_blob_and_get_url(container_name: str, 
                            blob_name: str, 
                            data: Union[bytes, str], 
                            blob_service_client: BlobServiceClient) -> str:
    """
    Uploads a blob to Azure Blob Storage and returns a public URL.

    Args:
        container_name (str): The name of the container to upload to.
        blob_name (str): The name to give the blob in storage.
        data (Union[bytes, str]): The content to upload.
        blob_service_client (BlobServiceClient): The BlobServiceClient instance.

    Returns:
        str: The public URL of the uploaded blob.
    """
    try:
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)

        # Create the container if it doesn't exist
        if not container_client.exists():
            container_client.create_container()

        # Upload the blob
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)

        # Generate a SAS token that's valid for 24 hours
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now() + timedelta(days=365)
        )

        # Construct the full URL
        blob_url = f"{blob_client.url}?{sas_token}"

        return blob_url

    except Exception as e:
        # Handle exceptions and provide a meaningful error message
        raise RuntimeError(f"An error occurred while uploading the blob: {str(e)}")


# Load environment variables    
load_dotenv()    

# Azure Blob Service Client
blob_container = os.getenv('BLOB_CONTAINER')
blob_service_client = BlobServiceClient.from_connection_string(os.getenv('BLOB_CONN'))
  
# Get the absolute path of the directory of the current script    
dir_path = os.path.dirname(os.path.realpath(__file__))    
  
# Use os.path.join to navigate to the config.yaml file    
config_path = os.path.join(dir_path, 'app', 'config.yaml')    
with open(config_path, 'r') as file:    
    config = yaml.safe_load(file)    
  
config_path = os.path.join(dir_path, 'app', 'config_Air8.yaml')  
with open(config_path, 'r') as file:  
    config_Air8 = yaml.safe_load(file)  
  
configInputDict = config['inputs']  
supportDocs = configInputDict['document_type']  
country_code_dict = configInputDict['country_code']  
  
configDBDict = config['database']  
db_name = configDBDict['db_name']   
  
# MongoDB connection setup  
mongo_conn_str = os.getenv("POC_MONGOCONN")  
client = MongoClient(mongo_conn_str)  
db = client[db_name]  
collection = db['air8_kyc']

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
# Title and introduction  
st.title("🚀 Document Validation Express 🏎️")  
st.markdown("""
##### AI-Powered Document Validation & Extraction Tool 🗂️

Seamlessly validate documents and extract key fields with the expert assistance of our AI Agent.
            
Alternatively, you can search for records by entering the order ID.

- 🔍 **Validate Documents**: Ensure your documents meet all necessary criteria.
- 🔑 **Extract Key Fields**: Automatically extract important information from your documents.
- 🆔 **Search by Order ID**: Quickly find records using the unique order identifier.

Ready to streamline your document management? Let’s get started below!
""", unsafe_allow_html=True)

st.markdown("### 📨 Submission Details")  
# Order ID
order_id = st.text_input("Order ID 🪪")

# Toggle between single-doc and multi-doc modes
mode = st.radio("Select Mode", ("Single Document", "Multiple Documents"), horizontal=True)

if mode == "Single Document":
    col1, col2 = st.columns([1, 3])
    with col1:
        # Country selection  
        countries = list(config_Air8['country_mapping'].keys())  
        selected_country = st.selectbox("Nation 🌏", countries)
    with col2:
        # Document type selection
        nation = config_Air8['country_mapping'][selected_country]
        document_types = list(config_Air8[nation].keys())
        selected_doc_type = st.selectbox("Document Type 📄", document_types)
else:
    all_document_types = config_Air8['possible_doc_type']
    # Use st.multiselect to allow the user to select multiple document types
    selected_doc_types = st.multiselect("Document Types 📄", list(all_document_types), default=all_document_types)

# File upload section  
st.markdown("#### 📁 Select a document to upload")  
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])
submit_button = st.button(label='Upload Document')  


def wait_for_log(thread_id, timeout=60, poll_interval=2):

    client = MongoClient(os.getenv("POC_MONGOCONN"))  
    db = client['ai-agent']  
    log_collection = db['agent_log']

    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        log = log_collection.find_one({'thread_id': thread_id})
        if log:
            return log
        time.sleep(poll_interval)
    return None


import io

def handle_file_upload(order_id, uploaded_file, doc_type, nation, multi_doc_type, possible_doc_type):
    file_bytes = uploaded_file.read()
    file_name = f"{order_id}_{doc_type}.{uploaded_file.type.split('/')[-1]}"
    blob_path = f"data/orders/{order_id}/{file_name}"
    
    # Upload file to blob storage and get URL
    file_url = upload_blob_and_get_url(container_name=blob_container,
                                       blob_name=blob_path,
                                       data=file_bytes,
                                       blob_service_client=blob_service_client)

    file_type = uploaded_file.type.split('/')[-1]

    if multi_doc_type:
        statement = "This document contains multiple document types."
    else:
        statement = "This document contains only one document type."

    prompt = f"""I am sending this request on the behalf of Air8.
Could you perform Know Your Customer (KYC) verification?
The order id is {order_id}
The image path is {file_url}
The file type is {file_type}
The nationality of the applicant is from {nation}
The possible document types are {possible_doc_type}
The target document type is {doc_type}
{statement}
"""
        
    #url = "http://localhost:8080/agent/agent-call"
    url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"

    thread_id = str(uuid.uuid4())
    payload = {'message': prompt, 
               'user_id': configInputDict['admin_id'][0], 
               'thread_id': thread_id}
    
    response = requests.post(url, json=payload)

    log = wait_for_log(thread_id, timeout=180)

    if log is None:
        st.error("Failed to retrieve the log entry within the timeout period.")
    else:
        token_usage = log['token_usage']
        ai_answer = log['ai_response']
        st.success(f"🤖: {ai_answer}")

        col1, col2, col3 = st.columns(3)
        col1.metric(label="Total Tokens", value=f"{token_usage['total_tokens']:,}")
        col2.metric(label="Prompt Tokens", value=f"{token_usage['prompt_tokens']:,}")
        col3.metric(label="Completion Tokens", value=f"{token_usage['completion_tokens']:,}")
        
    st.divider()
    
    with st.expander("🩻 Document Images", expanded=True):
        if uploaded_file.type in ["application/pdf"]:
            try:
                images = pdf2image.convert_from_bytes(file_bytes, first_page=1, last_page=3)
                captions = [f'Page {n+1}' for n in range(len(images))]
                st.image(images, caption=captions, use_column_width=True)
            except Exception as e:
                st.write(f"PDF could not be displayed. Error: {str(e)}")
        elif uploaded_file.type in ["image/png", "image/jpg", "image/jpeg"]:
            st.image(file_url, use_column_width=True)
        else:
            st.write("File type not supported for preview.")

if submit_button and uploaded_file and order_id:
    with st.spinner("Running document validation and extraction..."):
        if mode == "Single Document":
            handle_file_upload(order_id=order_id, 
                            doc_type=selected_doc_type, 
                            uploaded_file=uploaded_file,
                            nation=nation,
                            multi_doc_type=False,
                            possible_doc_type=None
                            )
        else:
            nation = "General"
            handle_file_upload(order_id=order_id, 
                            doc_type=None, 
                            uploaded_file=uploaded_file,
                            nation=nation,
                            multi_doc_type=True,
                            possible_doc_type=selected_doc_types
                            )


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
def display_document(doc, expanded=True):  
    with st.expander(f"Record Details of {doc['Doc Type']}", expanded=expanded): 
        st.divider() 
        st.markdown("##### 📋 Basic Info")  
        st.text(f"Order ID: {doc.get('Order ID', 'N/A')}")  
        st.text(f"Nation: {doc.get('Nation', 'N/A')}")  
        st.text(f"Document Type: {doc.get('Doc Type', 'N/A')}")  
        st.text(f"Document ID: {doc.get('Doc ID', 'N/A')}")  
        st.text(f"Validation Result: {doc.get('Result', 'N/A')}")
        st.text(f"Reason: {doc.get('Reason', 'N/A')}")
        
        st.divider() 
        st.markdown("##### 🔍 Extracted Fields")  
        st.write(doc.get('Extracted Fields', 'No extracted fields available.'))
        updated_fields = display_nested_content(doc.get('Extracted Fields', {}), doc['_id'], 'Extracted Fields')
        human_validation = '✅ Human Validated' if doc.get('human_validate_status') is True else '❌ Not Human Validated'
        
        st.divider() 
        st.text(f"Validation Status: {human_validation}") 
        if st.button("💾 Save & Confirm ✅", key=f"save_{doc['_id']}"):
            collection.update_one(
                {"_id": doc['_id']},
                {"$set": {"Extracted Fields": updated_fields, "human_validate_status": True}}
            )
            st.success(f"✅ Document {doc['_id']} updated successfully")

other_query = {"Order ID": order_id}
other_documents = list(collection.find(other_query).sort("created_time", DESCENDING))
if len(other_documents) > 0:
    st.divider()
    st.markdown(f"#### Records of Order ID: {order_id}")
    # Display existing documents  
    for doc in other_documents:
        # if doc['Doc ID'] != doc_id:
        display_document(doc, expanded=False)