import streamlit as st
import requests, os, yaml
from datetime import datetime
from utils import add_logo


# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Use os.path.join to navigate to the config.yaml file
config_path = os.path.join(dir_path, 'app', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

configInputDict = config['inputs']
country_code_dict = configInputDict['country_code']

time_str = datetime.now().strftime("%d-%m-%Y")

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
st.title("🤖 Chatbot Playground 🕹️")

# Initialize chat history
if "admin_messages" not in st.session_state:
    st.session_state.admin_messages = []
if "user_messages" not in st.session_state:
    st.session_state.user_messages = []

# Function to get a response from the FastAPI endpoint
def get_chatbot_response(user_input, thread_id, user_id):
    
    url = "http://localhost:8080/agent/agent-call"
    # url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"

    payload = {
        'message': user_input,
        'thread_id': thread_id,
        'user_id': user_id
    }
    # try:
    response = requests.post(url, json=payload)
    response_dict = response.json()

    ai_answer = response_dict.get('ai_response', 'No response')
    ai_log = response_dict.get('log', '')
    tool_call = response_dict.get('tool_call', '')
    # ai_answer = response_dict['ai_response']

    return ai_answer, ai_log, tool_call
    # except Exception as e:
    #     return f"Error: {e}"

# Create tabs
with st.expander(f"⚙️ Configurations", expanded=True): 
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        tabs = ["Admin Chatbot",
                "Client Chatbot"]
        selected_tab = st.selectbox("Choose a Chatbot", tabs)
    with col2:
        flags = list(country_code_dict.keys())
        country = st.selectbox("Country", flags)
        country_code = country_code_dict[country]
    with col3:
        user_id = st.text_input("Phone Number", help="💬 Enter your phone number to save the chat history.")
        user_id = country_code + user_id
        # st.markdown("💬 Enter your phone number to save the chat history.")
    if selected_tab == "Admin Chatbot":
        st.success("Acting as **ADMIN** with comprehensive access to all tools and records.")
    else:
        st.success("Acting as **CLIENT** with restricted access to tools and records.")

# Run chat interface in Admin tab
if selected_tab == "Admin Chatbot":
    for message in st.session_state.admin_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your question...", key="admin_input"):
        thread_id = f"thread_id_admin_{user_id}_{time_str}"
        st.chat_message("user").markdown(prompt)
        st.session_state.admin_messages.append({"role": "user", "content": prompt})
        response, log, tool_call = get_chatbot_response(prompt, thread_id, 'iamadmin')
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.admin_messages.append({"role": "assistant", "content": response})

        # Optionally display log and tool_call for debugging purposes
        if log:
            with st.sidebar.expander("Log"):
                st.code(log)
        if tool_call:
            with st.sidebar.expander("Tool Call"):
                st.code(tool_call)

# Run chat interface in User tab
if selected_tab == "Client Chatbot":
    for message in st.session_state.user_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your question...", key="user_input"):
        thread_id = f"thread_id_client_{user_id}_{time_str}"
        st.chat_message("user").markdown(prompt)
        st.session_state.user_messages.append({"role": "user", "content": prompt})
        response, log, tool_call = get_chatbot_response(prompt, thread_id, user_id)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.user_messages.append({"role": "assistant", "content": response})

        # Optionally display log and tool_call for debugging purposes
        if log:
            with st.sidebar.expander("Log"):
                st.code(log)
        if tool_call:
            with st.sidebar.expander("Tool Call"):
                st.code(tool_call)