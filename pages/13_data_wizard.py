import streamlit as st
import requests
import os, yaml, uuid, sys
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv 
from utils import add_logo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

load_dotenv()  

# Get the absolute path of the directory of the current script    
dir_path = os.path.dirname(os.path.realpath(__file__))    
  
# Use os.path.join to navigate to the config.yaml file    
config_path = os.path.join(dir_path, 'app', 'config.yaml')    
with open(config_path, 'r') as file:    
    config = yaml.safe_load(file)     

configInputDict = config['inputs'] 

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


# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()

# Main app logic
if check_password():

    # Streamlit app
    st.title('🧙‍♂️ Data Wizard 🔮')
    st.markdown("""
##### AI-Powered Data Visualization and Insights 🧠

Welcome to the Data Wizard, your go-to tool for transforming raw data into insightful visualizations and answers. Harness the power of AI to explore and understand your data effortlessly!

- 📊 **Dynamic Visualizations**: Create stunning and interactive graphs and charts.
- 🧩 **Insightful Analysis**: Get answers to your data-related questions using natural language queries.
- 🌟 **User-Friendly**: Intuitive interface designed for seamless interaction and exploration.

Ready to unveil the hidden stories within your data? Just upload your dataset and let the magic begin!
""", unsafe_allow_html=True)

    import streamlit.components.v1 as components

    # Function to read HTML file content
    def read_html_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()


    mongo_conn_str = os.getenv("POC_MONGOCONN")
    client = MongoClient(mongo_conn_str)
    data_viz_db = client['data-viz-agent']
    data_viz_collection = data_viz_db['data_visualization']

    query = {"data_visualization_result": {"$ne": None}}
    uuids = data_viz_collection.find(query, {"uuid": 1, "_id": 0})

    st.subheader("uuid Menu")
    selected_uuid = st.selectbox("Select a uuid:", uuids)
    
    st.markdown("")

    # uuid_to_find = '5e46d557-c17c-4d00-bf44-3cc6b39dc691'
    uuid_to_find = '1d50c3d7-263f-47b8-aaf8-ac2fb2f6cd9a'

    query = {"uuid": selected_uuid}
    record = data_viz_collection.find_one(query)
    html_content = record['data_visualization_result']

    # Display the Plotly chart in Streamlit
    components.html(html_content, height=450)

    question = record['question']
    ai_answer = record['answer']
    visualization_reason = record['visualization_reason']

    st.markdown(f"""
        <div style="border:1px solid #388e3c; background-color: #c8e6c9; padding: 20px 25px 5px 20px; border-radius: 10px; margin: 5px;">
            <p style="color: #2e7d32; font-size: 16px;">🙋 : {question}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="border:1px solid #1565c0; background-color: #bbdefb; padding: 20px 25px 5px 20px; border-radius: 10px; margin: 5px;">
            <p style="color: #0d47a1; font-size: 16px;">🤖 : {ai_answer}<br>{visualization_reason}</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.stop()  # Don't run the rest of the app.