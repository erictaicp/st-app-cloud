import streamlit as st
import requests
import os, yaml, uuid
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv 
import math
from utils import add_logo

load_dotenv()  

# Get the absolute path of the directory of the current script    
dir_path = os.path.dirname(os.path.realpath(__file__))    
  
# Use os.path.join to navigate to the config.yaml file in the root directory
config_path = os.path.join(dir_path, '..', 'config.yaml')

try:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    configInputDict = config['inputs']
except FileNotFoundError:
    st.error(f"Configuration file not found at {config_path}. Please ensure it exists and contains the necessary settings.")
    config = {}
    configInputDict = {}

# MongoDB connection setup  
# client = MongoClient(os.getenv("SUPPLIER_MONGOCONN"))
# supplier_db = client['uat-suppliers']
# supplier_collection = supplier_db['gold']

# client = MongoClient(os.getenv("POC_MONGOCONN"))
# supplier_db = client['search-agent']
# supplier_collection = supplier_db['sub_gold']

client = MongoClient(os.getenv("POC_MONGOCONN"))
search_db = client['search-agent']
search_collection = search_db['search_history']
supplier_collection = search_db['sub_gold']

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
    

# Define the function to call the API and get the research report
def get_supplier_ids(search_id, query, thread_id):
    prompt = f"""
I would like to perform a supplier search with the following details:

- search id: {search_id}
- query: {query}

Please execute the supplier_search function using these parameters.
"""
    url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"

    # url = "http://localhost:8080/agent/agent-call"
    payload = {'message': prompt, 
               'user_id': configInputDict['admin_id'][0], 
               'thread_id': thread_id}
    
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


# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add logo to all pages
add_logo()

# Main app logic
if check_password():

    # Streamlit app
    st.title('🏭 Supplier Search 🔍')
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

    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("query", 
                            placeholder="Enter supplier name, ID, or any relevant criteria...", 
                            key="query", 
                            label_visibility='collapsed')
    with col2:
        search_button = st.button(label='Search', 
                                  key="search_button", 
                                  help="Click to search", 
                                  use_container_width=True)


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


    def display_record(record):
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
        st.markdown(f"### 🏬 Suppliers Search Results")
        
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

                        cols[col].markdown(display_record(supplier_record), unsafe_allow_html=True)
                        
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
                            # filtered_record = remove_none_and_specific_keys(supplier_record, keys_to_remove)
                            # st.json(filtered_record)
                            st.markdown(content)
                    else:
                        cols[col].markdown("")
        except:
            pass


    if search_button:
        if query:
            with st.spinner("Searching..."):
                search_id = str(uuid.uuid4())
                thread_id = str(uuid.uuid4())

                # Make sure configInputDict['admin_id'] exists before using it
                admin_id = configInputDict.get('admin_id', [None])[0]
                if admin_id is None:
                    st.error("Admin ID not found in configuration. Please check your config.yaml file.")
                else:
                    get_supplier_ids(search_id, query, thread_id)

                    log = wait_for_log(thread_id, timeout=30)

                    if log is None:
                        st.error("Failed to retrieve the log entry within the timeout period.")
                    else:
                        token_usage = log['token_usage']
                        ai_answer = log['ai_response']
                        st.success(f"🤖: {ai_answer}")

                        # col1, col2, col3 = st.columns(3)
                        # col1.metric(label="Total Tokens", value=f"{token_usage['total_tokens']:,}")
                        # col2.metric(label="Prompt Tokens", value=f"{token_usage['prompt_tokens']:,}")
                        # col3.metric(label="Completion Tokens", value=f"{token_usage['completion_tokens']:,}")

                        critiria = {"search_id": search_id}
                        search_record = search_collection.find_one(critiria)

                        supplier_ids = search_record.get('supplier_ids')
                        reasons = search_record.get('reasons')
                        contents = search_record.get('retrieved_data')

                        st.divider()

                        display_limit = 30
                        display_supplier_grid(supplier_ids[:display_limit], 
                                              reasons[:display_limit], 
                                              contents[:display_limit])
else:
    st.stop()  # Don't run the rest of the app.