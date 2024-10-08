import streamlit as st
import requests
import os, yaml, uuid
from pymongo import MongoClient
from dotenv import load_dotenv 
import math
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from typing import Union
from bson import ObjectId
from utils import add_logo

load_dotenv()  

# MongoDB connection setup  
# client = MongoClient(os.getenv("SUPPLIER_MONGOCONN"))
# supplier_db = client['uat-suppliers']
# supplier_collection = supplier_db['gold']

client = MongoClient(os.getenv("POC_MONGOCONN"))
search_db = client['search-agent']

supplier_search_collection = search_db['supplier_search_history']
product_search_collection = search_db['product_search_history']

supplier_collection = search_db['sub_gold']
product_collection = search_db['sub_gold_product']

# Azure Blob Service Client
blob_container = 'uploads'
blob_service_client = BlobServiceClient.from_connection_string(os.getenv('POC_BLOB_CONN'))

SYSTEM_PROMPT = """You are LFX Supplier and Product Search Assistant, a highly efficient, professional assistant specializing in performing comprehensive searches.
Your primary role is to provide users with helpful, polite, and accurate assistance tailored to their search needs.
- Utilize the 'supplier_search' tool to address user queries related to factories or suppliers, offering detailed information and relevant insights.
- Utilize the 'product_search' tool to address user queries related to products, providing comprehensive details and relevant data.
Maintain a professional demeanor, ensure clarity in your responses, and strive to meet user expectations effectively.
"""


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


# Add this at the beginning of the file, after the imports
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "lfxpassword":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True
    

def get_supplier_ids(search_id, query, thread_id):
    
    prompt = f"""
I would like to perform a supplier search with the following details:

- search id: {search_id}
- query: {query}

Please execute the supplier_search function using these parameters.
"""

    url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"
    payload = {'message': prompt, 
               'user_id': 'iamadmin', 
               'thread_id': thread_id,
               "ai_role": SYSTEM_PROMPT,}
    
    response = requests.post(url, json=payload)
    
    
def get_product_ids(search_id, thread_id, query=None, uploaded_file=None):
    
    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_name = f"product_search_{str(uuid.uuid4())}.{uploaded_file.type.split('/')[-1]}"
        blob_path = f"{file_name}"
        
        # Upload file to blob storage and get URL
        image_path = upload_blob_and_get_url(container_name=blob_container,
                                        blob_name=blob_path,
                                        data=file_bytes,
                                        blob_service_client=blob_service_client)
    else:
        image_path = None
        
    prompt = f"""
I would like to perform a product search with the following details:

- search id: {search_id}
- query: {query}
- image path: {image_path}

Please execute the product_search function using these parameters.
"""

    url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"
    payload = {'message': prompt, 
               'user_id': 'iamadmin', 
               'thread_id': thread_id,
               "ai_role": SYSTEM_PROMPT,}
    
    response = requests.post(url, json=payload)


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


def remove_none_and_specific_keys(d, keys_to_remove):
        if isinstance(d, dict):
            return {k: remove_none_and_specific_keys(v, keys_to_remove) 
                    for k, v in d.items() 
                    if v is not None and v != "" and k not in keys_to_remove}
        elif isinstance(d, list):
            return [remove_none_and_specific_keys(v, keys_to_remove) for v in d if v is not None and v != ""]
        else:
            return d

# List of keys to remove
keys_to_remove = ['_id', 'FacilityImage']


def display_supplier_record(record):
    supplier_basic = record['SupplierBasic']['Demographics']
    
    supplier_id = record['System']['ID']
    entity_full_name = supplier_basic['EntityFullName']
    registration_country = supplier_basic['RegistrationCountry']
    year_established = supplier_basic.get('YearEstablished', 'Unknown')
    headquarter_address = supplier_basic.get('HeadquarterAddress', 'Not specified')

    return f"""
    <div style="border:1px solid #d1d1d1; padding: 10px 20px; border-radius: 10px; height: 150px; background-color: #f9f9f9; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 5px 0; max-height: 35px; overflow-y: auto; color: #2c3e50; font-size: 20px;">{entity_full_name}</h3>
        <div style="display: flex; justify-content: space-between; margin: 5px 0; color: #2c3e50; font-size: 14px;">
            <p style="margin: 0;"><strong>🆔 ID:</strong> {supplier_id}</p>
            <p style="margin: 0;"><strong>🌍 Country:</strong> {registration_country}</p>
            <p style="margin: 0;"><strong>📅 Established:</strong> {year_established}</p>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; color: #2c3e50; font-size: 14px;">
            <p style="margin: 0; max-height: 30px; overflow-y: auto;"><strong>🏢 HQ:</strong> {headquarter_address}</p>
            <a href="https://stasduseanplfs2uatui.z23.web.core.windows.net/supplier/{supplier_id}" target="_blank">
                <button style="padding: 10px 20px; background-color: #2980b9; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                    Details
                </button>
            </a>
        </div>
    </div>
    """


def display_supplier_grid(supplier_ids, reasons, contents):
    st.markdown("### 🏬 Supplier Search Results")
    
    num_to_display = 2
    # Calculate the number of rows needed
    num_suppliers = len(supplier_ids)
    num_rows = math.ceil(num_suppliers / num_to_display)
    try:
        for row in range(num_rows):
            cols = st.columns(num_to_display)
            for col in range(num_to_display):
                index = row * num_to_display + col
                if index < num_suppliers:
                    
                    supplier_id = supplier_ids[index]
                    id_criteria = {"System.ID": supplier_id}
                    supplier_record = supplier_collection.find_one(id_criteria)

                    cols[col].markdown(display_supplier_record(supplier_record), unsafe_allow_html=True)
                    
                    content = contents[index]
                    reason = reasons[index]
                    reason_html = f"""
                    <div style="border: 1px solid #d1d1d1; border-radius: 5px; padding: 10px; background-color: #d4f5d4; color: #2c3e50; font-size: 14px; margin-top: 10px; min-height: 70px;">
                        <strong>Reason:</strong> {reason}
                    </div>
                    """
                    cols[col].markdown(reason_html, unsafe_allow_html=True)
                    
                    # Add expander for more details
                    with cols[col].expander("RAW OUTPUT", expanded=False):
                        st.markdown(content)
                else:
                    cols[col].markdown("")
    except:
        pass
    
    
def display_product_record(record):
    product_id = record['product_id']
    
    product_full_name = record['item_description']
    product_full_name = product_full_name.replace("  ", " ")
    
    product_family = record.get('product_family', 'Not specified')
    product_category = record.get('product_category', 'Not specified')
    
    html_content = f"""
    <div style="border:1px solid #d1d1d1; padding: 10px 20px; border-radius: 10px; height: 150px; background-color: #f9f9f9; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 5px 0; max-height: 35px; overflow-y: auto; color: #2c3e50; font-size: 20px;">{product_full_name}</h3>
        <div style="display: flex; justify-content: space-between; margin: 5px 0; color: #2c3e50; font-size: 14px;">
            <p style="margin: 0;"><strong>🏷️ Category:</strong> {product_category}</p>
            <p style="margin: 0;"><strong>📦 Family:</strong> {product_family}</p>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; color: #2c3e50; font-size: 14px;">
            <p style="margin: 0; max-height: 30px; overflow-y: auto;"><strong>🆔 ID:</strong> {product_id}</p>
        </div>
    </div>
    """

    if record['has_image'] == "yes":
        image_url = record.get('image_url')
        image_url = f"{image_url}?sv=2023-01-03&st=2024-03-07T09%3A40%3A39Z&se=2025-01-31T15%3A59%3A00Z&sr=s&sp=rl&sig=OdgpbBwJ2b9oCTTuvp%2BzVKmJ9xeLjt8DFp7F%2BdARauQ%3D"
        
        html_content = f"""
    <div style="border:1px solid #d1d1d1; padding: 10px 20px; border-radius: 10px; height: 150px; background-color: #f9f9f9; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 5px 0; max-height: 35px; overflow-y: auto; color: #2c3e50; font-size: 20px;">{product_full_name}</h3>
        <div style="display: flex; justify-content: space-between; margin: 5px 0; color: #2c3e50; font-size: 14px;">
            <p style="margin: 0;"><strong>🏷️ Category:</strong> {product_category}</p>
            <p style="margin: 0;"><strong>📦 Family:</strong> {product_family}</p>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; color: #2c3e50; font-size: 14px;">
            <p style="margin: 0; max-height: 30px; overflow-y: auto;"><strong>🆔 ID:</strong> {product_id}</p>
            <a href="{image_url}" target="_blank">
                <button style="padding: 10px 20px; background-color: #2980b9; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                    Image
                </button>
            </a>
        </div>
    </div>
    """

    return html_content
    

def display_product_grid(product_uuids, reasons, contents):
    st.markdown("### 🛍️ Product Search Results")
    
    num_to_display = 2
    # Calculate the number of rows needed
    num_products = len(product_uuids)
    num_rows = math.ceil(num_products / num_to_display)
    try:
        for row in range(num_rows):
            cols = st.columns(num_to_display)
            for col in range(num_to_display):
                index = row * num_to_display + col
                
                if index < num_products:
                    product_uuid = product_uuids[index]
                    id_criteria = {"_id": ObjectId(product_uuid)}
                    product_record = product_collection.find_one(id_criteria)

                    cols[col].markdown(display_product_record(product_record), unsafe_allow_html=True)
                    
                    content = contents[index]
                    reason = reasons[index]
                    reason_html = f"""
                    <div style="border: 1px solid #d1d1d1; border-radius: 5px; padding: 10px; background-color: #d4f5d4; color: #2c3e50; font-size: 14px; margin-top: 10px; min-height: 70px;">
                        <strong>Reason:</strong> {reason}
                    </div>
                    """
                    cols[col].markdown(reason_html, unsafe_allow_html=True)
                    
                    # Add expander for more details
                    with cols[col].expander("RAW OUTPUT", expanded=False):
                        st.markdown(content)
                else:
                    cols[col].markdown("")
    except:
        pass


# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add logo to all pages
add_logo()

# Main app logic
if check_password():

    st.title('🏭 Supplier & Product Search 🛒')

    # Create tabs
    tabs = st.tabs(["Supplier Search", "Product Search"])

    # Supplier Search tab
    with tabs[0]:
        st.markdown("""
        ##### AI-Powered Supplier Search Tool 🛠️

        Use natural language to effortlessly search and explore supplier records. Just type in your search criteria and let us do the rest!

        - 🏢 **Quick Search**: Find suppliers using natural language queries.
        - 🧵 **Detailed Information**: Get comprehensive details about each supplier.
        - 🏗️ **User-Friendly**: Easy to use interface with expandable sections for detailed views.

        Ready to get started? Simply enter your search criteria below!
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
            .elongated-button .stButton button {
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            query_supplier = st.text_input("Supplier Query", 
                                        placeholder="Enter supplier name, ID, or any relevant criteria...", 
                                        key="query_supplier", 
                                        label_visibility='collapsed')
        with col2:
            search_supplier_button = st.button(label='Search Supplier', 
                                            key="search_supplier_button", 
                                            help="Click to search", 
                                            use_container_width=True)

        # Add functionality for the supplier search button here
        if search_supplier_button:
            if query_supplier:
                with st.spinner("Searching for suppliers..."):
                    search_id = str(uuid.uuid4())
                    thread_id = str(uuid.uuid4())

                    get_supplier_ids(search_id, query_supplier, thread_id)

                    log = wait_for_log(thread_id, timeout=30)

                    if log is None:
                        st.error("Failed to retrieve the log entry within the timeout period.")
                    else:
                        token_usage = log['token_usage']
                        ai_answer = log['ai_response']
                        st.success(f"🤖: {ai_answer}")

                        critiria = {"search_id": search_id}
                        search_record = supplier_search_collection.find_one(critiria)

                        supplier_ids = search_record.get('supplier_ids')
                        reasons = search_record.get('reasons')
                        contents = search_record.get('retrieved_data')

                        st.divider()

                        display_limit = 30
                        display_supplier_grid(supplier_ids[:display_limit], 
                                            reasons[:display_limit], 
                                            contents[:display_limit])

    # Product Search tab
    with tabs[1]:
        st.markdown("""
        ##### AI-Powered Product Search Tool 🛠️

        Use natural language to effortlessly search and explore product records. Just type in your search criteria or upload an image, and let us do the rest!

        - 🔍 **Quick Search**: Discover products using natural language queries, images, or a combination of both..
        - 📝 **Detailed Information**: Get comprehensive details about each product.
        - 🖥️  **User-Friendly**: Easy to use interface with expandable sections for detailed views.

        Ready to get started? Simply enter your search criteria or upload an image below!
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
            .elongated-button .stButton button {
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            query_product = st.text_input("Product Query", 
                                        placeholder="Enter product name, ID, or any relevant criteria...", 
                                        key="query_product", 
                                        label_visibility='collapsed')
            image_path = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"], key="image_path")
        with col2:
            search_product_button = st.button(label='Search Product', 
                                            key="search_product_button", 
                                            help="Click to search", 
                                            use_container_width=True)
            if image_path:
                st.image(image_path, caption="Uploaded Image", use_column_width=True)
        # Add functionality for the supplier search button here
        if search_product_button:
            if query_product or image_path:
                with st.spinner("Searching for products..."):
                    search_id = str(uuid.uuid4())
                    thread_id = str(uuid.uuid4())

                    get_product_ids(search_id, thread_id, query_product, image_path)

                    log = wait_for_log(thread_id, timeout=30)

                    if log is None:
                        st.error("Failed to retrieve the log entry within the timeout period.")
                    else:
                        token_usage = log['token_usage']
                        ai_answer = log['ai_response']
                        st.success(f"🤖: {ai_answer}")

                        critiria = {"search_id": search_id}
                        search_record = product_search_collection.find_one(critiria)

                        product_uuids = search_record.get('product_uuids')
                        reasons = search_record.get('reasons')
                        contents = search_record.get('retrieved_data')

                        st.divider()

                        display_limit = 30
                        display_product_grid(product_uuids[:display_limit], 
                                            reasons[:display_limit], 
                                            contents[:display_limit])    
else:
    st.stop()  # Don't run the rest of the app.