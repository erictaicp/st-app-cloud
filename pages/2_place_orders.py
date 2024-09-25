import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import yaml
from utils import add_logo

# Load environment variables
load_dotenv()

# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Use os.path.join to navigate to the config.yaml file
config_path = os.path.join(dir_path, 'app', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

configInputDict = config['inputs']
supportDocs = configInputDict['document_type']
country_code_dict = configInputDict['country_code']

configDBDict = config['database']
db_name = configDBDict['db_name']
collection_name = configDBDict['collection']

# MongoDB connection setup
mongo_conn_str = os.getenv("MONGOCONN")
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
st.title("📝 Add New Order 💼")

with st.form(key='order_form'):
    st.markdown("## 📦 Order Details")
    order = st.text_input("Order ID 🪪")
    target_email = st.text_input("Target Email 📧")
    col1, col2 = st.columns([1, 3])
    with col1:
        flags = list(country_code_dict.keys())
        country = st.selectbox("Country 🌏", flags)
        country_code = country_code_dict[country]
    with col2:
        phone_number = st.text_input("Target Whatsapp 📱")
    target_whatsapp = country_code + phone_number
    # target_wechat = st.text_input("Target Wechat 📱")
    documents = st.multiselect("Documents 📄", supportDocs)  # Use multiselect here
    due = st.date_input("Due Date 📅", datetime.now())

    submit_button = st.form_submit_button(label='Submit Order 🚀')

if submit_button:
    # Check if order ID, target email or target whatsapp are not empty
    if not order or (not target_email and not target_whatsapp):
        st.error("Order ID and (phone number or email) are required fields.")
    else:
        # Check if an order with the same ID already exists
        existing_order = collection.find_one({"Order": order})
        if existing_order is not None:
            st.error("An order with this ID already exists.")
        else:
            for document in documents:  # Iterate over the selected document types
                new_entry = {
                    "Order": order,
                    "Target Email": target_email,
                    "Target Whatsapp": target_whatsapp,
                    # "Target Wechat": target_wechat,
                    "Status": 'Document Required',
                    "Document": document,  # This will be a single document type
                    "Last Modified": datetime.now().strftime("%d/%m/%Y %I:%M%p"),
                    "Created Time": datetime.now().strftime("%d/%m/%Y %I:%M%p"),
                    "Due Date": due.strftime("%d/%m/%Y")
                }
                collection.insert_one(new_entry)
            st.success("🎉 Order added successfully!")