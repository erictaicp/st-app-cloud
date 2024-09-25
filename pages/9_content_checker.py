import streamlit as st
import requests
import os, yaml, uuid, re
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv
from utils import add_logo 

load_dotenv()  

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
collection = db['air8_checker']


# Define the function to call the API and run the document content checking
def run_content_checking(order_id, rules, doc_types_to_check, thread_id):
    
    prompt = f"""I am sending this request on the behalf of Air8.
Could you perform field validation on documents submitted under a unique order ID, ensuring compliance with the given rule set?
The order ID is {order_id}
The rule set is {rules}
The document types that need to be checked are {doc_types_to_check}
"""
    #url = "http://localhost:8080/agent/agent-call"
    url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"

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

add_logo()
# Streamlit app
st.title('📘 Document Content Checker 🔬')
st.markdown("""
##### AI-Powered Content Checking Tool 📋

Meticulously validate the content of your documents according to predefined rules, ensuring they meet all necessary criteria.

Please provide the following details below:
- 🆔 **Order ID**: The unique identifier associated with the application.
- 📄 **Document Types**: A list of document types that need to be checked.
- 📏 **Rules**: A set of predefined rules to follow when checking the content of the documents. (Use an index to separate the rules.)

Let's get started by entering the required details below!
""", unsafe_allow_html=True)

# Order ID
order_id = st.text_input("Order ID 🪪")
# Document Types
all_document_types = config_Air8['possible_doc_type']
selected_doc_types = st.multiselect("Document Types 📄", list(all_document_types), default=all_document_types)
# Rules
default_rules = config_Air8['check_rules']
rule_string = "\n".join(default_rules)
rules_set = st.text_area("Rule Set 📜", value=rule_string, height=330)
# Button
run_button = st.button(label='Run Content Validation')

if run_button and rules_set and order_id and selected_doc_types:
    with st.spinner("Validating content..."):
        thread_id = str(uuid.uuid4())

        run_content_checking(order_id, rules_set, selected_doc_types, thread_id)

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

colors = [
    "#8B0000",  # Dark Red
    "#B22222",  # Firebrick
    "#DC143C",  # Crimson
    "#FF8C00",  # Dark Orange
    "#DAA520",  # Goldenrod
    "#BDB76B",  # Dark Khaki
    "#6B8E23",  # Olive Drab
    "#228B22",  # Forest Green
    "#2E8B57",  # Sea Green
    "#006400",  # Dark Green
]

def get_color(score):
    if score == 0:
        return "#4B0000"
    else:
        return colors[score - 1]

def display_json(report):
    def sort_rules(rule_key):
        match = re.search(r'rule_(\d+)', rule_key)
        return int(match.group(1)) if match else float('inf')

    rule_result = {k: v for k, v in report.items() if k.startswith('rule_')}

    # Sort the data keys
    sorted_keys = sorted(rule_result.keys(), key=sort_rules)
    for rule_key in sorted_keys:
        rule_data = rule_result[rule_key]
        rule_str, num_str = rule_key.split('_')
        st.markdown(f"### {rule_str.capitalize()} {num_str}")
        st.markdown(f"##### 🔖 {rule_data['Rule']}")
        for doc_type, fields in rule_data["Field Comparison"].items():
            st.write(f"**{doc_type}:**")
            for field_name, field_value in fields.items():
                st.write(f"-      {field_name}: {field_value}")
        st.write(f"**Comment:**")
        st.text(f"{rule_data['Reason']}")

        col1, col2, col3, col4 = st.columns([1.1, 5, 1, 1])
        with col1:
            color = get_color(rule_data['Score'])
            st.markdown(
                f"<p style='font-size:20px; background-color:{color}; border-radius:10px; padding:5px; text-align:center;'><b>Score:</b> {rule_data['Score']}</p>", 
                unsafe_allow_html=True
                )
        with col3:
            approve_button = st.button("Approve ✅", key=f"approve_{report['_id']}_{rule_key}")
            if approve_button:
                filter_criteria = {"_id": report['_id']}
                update_criteria = {"$set": {f"{rule_key}.approval_status": "Approved"}}

                # Update the document
                result = collection.update_one(filter_criteria, update_criteria)
                # st.success(f"Approved")
        with col4:
            reject_button = st.button("Reject ❌", key=f"reject_{report['_id']}_{rule_key}")
            if reject_button:
                filter_criteria = {"_id": report['_id']}
                update_criteria = {"$set": {f"{rule_key}.approval_status": "Rejected"}}

                # Update the document
                result = collection.update_one(filter_criteria, update_criteria)
                # st.success(f"Rejected")
        if approve_button:
            st.success(f"🔔 The Status has been updated: Approved")
        if reject_button:
            st.error(f"🔔 The Status has been updated: Rejected")
        st.markdown("---")

if order_id:
    st.divider()
    st.markdown(f"### 📝 Content Checking Report of {order_id}")
    order_query = {'Order ID': {'$regex': order_id, '$options': 'i'}}
    reports = list(collection.find(order_query).sort("created_time", DESCENDING))
    if len(reports) > 0:
        report = reports[0]
        display_json(report)

        st.text(f"Report Validation Status: {reports[0]['human_validate_status']}") 
        if st.button("Confirm 🆗", key=f"save_{reports[0]['_id']}"):
            collection.update_one(
                {"_id": reports[0]['_id']},
                {"$set": {"human_validate_status": True}}
            )
            st.success(f"🆗 The report is validated")
    else:
        st.write(f"⛔ The report is currently unavailable because the specified order ID does not exist. Kindly run the content validation to generate the report.")