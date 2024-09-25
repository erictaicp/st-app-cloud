import streamlit as st
import requests
import os, yaml, uuid
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv 
import pandas as pd
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
# supportDocs = configInputDict['document_type']
# country_code_dict = configInputDict['country_code']    

# MongoDB connection setup  
mongo_conn_str = os.getenv("POC_MONGOCONN")  
client = MongoClient(mongo_conn_str)  
db = client['postoffice']  
collection = db['air8_company_info_news']

lang_code = {
    "English 🇺🇸": "English",
    "繁體中文 🇭🇰": "Traditional Chinese",
    "简体中文 🇨🇳": "Simplified Chinese",
    }

news_sources = [
    'Google News',
    # 'Baidu',
    ]

nation_code = {
    "Hong Kong 🇭🇰": "Hong Kong",
    "China 🇨🇳": "China",
    "United States 🇺🇸": "United States",
    "India 🇮🇳": "India",
    }


# Define the function to call the API and get the research report
def get_company_report(company_name, 
                       research_languages, 
                       report_language, 
                       news_source,
                       region,
                       additional_focus,
                       num_result_per_focus,
                       num_news_result,
                       search_news_only,
                       search_adverse_news,
                       thread_id):

    prompt = f"""
I am sending this request on behalf of Air8.
Could you search for information and news about a company? Here are the details:
- Target company: {company_name}
- Research languages: {', '.join(research_languages)}
- Report language: {report_language}
- Preferred news source: {news_source}
- Region: {region}
- Additional research focus: {additional_focus}
- Number of results per focus area: {num_result_per_focus}
- Number of news results: {num_news_result}
- Search news only: {search_news_only}
- Search adverse news: {search_adverse_news}
"""
    
    url = "http://localhost:8080/agent/agent-call"
    # url = "https://api.uat.t4s.lfxdigital.app/agents/v1/agent/agent-call"

    payload = {'message': prompt, 
            'user_id': configInputDict['admin_id'][0], 
            'thread_id': thread_id}
    
    response = requests.post(url, json=payload)

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
# Streamlit app
st.title('📊 Company Research & News 🌟')
st.markdown("""
##### AI-Powered Company Research Tool 💼

Discover comprehensive insights into company information and stay updated with the latest news. Our AI delivers detailed, real-time reports with references.

- **📌 Getting Started**: Use the default settings initially for the best experience.
- **ℹ️ How to Use**: Hover over the question mark icon for parameter details.
- **⏳ Note**: Each company research session takes approximately 1-2 minutes.

Dive in and explore the wealth of information our tool offers!
""", unsafe_allow_html=True)

# Input section
st.markdown("")
st.markdown("##### 🗃️ Company Research Basics")
company_name = st.text_input("Company Name 📟", key="company_name", help="Enter the name of the company you want to research")
col1, col2 = st.columns([3, 1])
with col1:
    reseach_langs = st.multiselect("Research Language 🖋️", 
                                   list(lang_code.keys()), 
                                   default=list(lang_code.keys())[:1],
                                   help="A list of languages to conduct the research in.")
    research_languages = [lang_code[reseach_lang] for reseach_lang in reseach_langs]
with col2:
    report_lang = st.selectbox("Report Language 🖌️", 
                               list(lang_code.keys()),
                               help="The language in which the final report should be generated.") 
    report_language = lang_code[report_lang]

st.markdown("")
st.markdown("##### 🗞️ Company News Focuses")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    news_source = st.selectbox("News Source 🔋", 
                               news_sources, 
                               help="The source from which to gather news.")  
with col2:
    region_selected = st.selectbox("Search Engine Region 🧭", 
                          list(nation_code.keys()), 
                          help="The geographical region to focus the search on.")
    region = nation_code[region_selected]
with col3:
    num_news_result = st.number_input("Number of News 🔢", 
                                      value=30, 
                                      min_value=1, 
                                      max_value=100, 
                                      help="The number of news results to retrieve.")
st.markdown("")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    search_news_only = st.toggle("Search News Only", 
                                 value=False,
                                 help="If set to True, only news will be searched.")
with col2:
    search_adverse_news = st.toggle("Search Adverse News", 
                                    value=False, 
                                    help="If set to True, adverse news will be searched.")

additional_focus = None

if search_news_only is False:
    default_focuses = [
        "Background", 
        "Business model", 
        "Mangament structure and key executives", 
        "Main competitors and market share", 
        ]
    st.markdown(" ")
    st.markdown("##### 💡 Company Information Focuses")
    question_text = "\n".join([f"1. {default_focus}" for default_focus in default_focuses])
    st.markdown(question_text)

    additional_focus = st.text_input("(Optional) Additional Research Focus", 
                                    key="research_focus", 
                                    help="Enter the research focus seperated by comma (e.g., market trends, IPO)")
st.markdown(" ")
generate_button = st.button(label='Generate Report')


def format_string(input_string):
    minor_words_set = {"at", "by", "for", "in", "of", "on", "or", "the", "to", "and", "but"}
    words = input_string.split()

    if words[0].isupper():
        formatted_words = [words[0]]
    else:
        formatted_words = [words[0].capitalize()]

    for word in words[1:]:
        if word.lower() in minor_words_set:
            formatted_words.append(word.lower())
        elif word.isupper():
            formatted_words.append(word)
        else:
            formatted_words.append(word.capitalize())
    
    formatted_string = ' '.join(formatted_words)
    return formatted_string


def escape_markdown(text):
    # Escape special markdown characters
    escape_chars = ['$', '&']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text


def display_nested_findings(findings, urls=None, level=0):
    if isinstance(findings, str):
        st.markdown("  " * level + findings)
    elif isinstance(findings, list):
        for idx, item in enumerate(findings, 1):
            if isinstance(item, dict):
                st.markdown(f"{'  ' * level}**{item.get('research_focus', f'Item {idx}')}**")
                display_nested_findings(item.get('findings', ''), item.get('urls'), level + 1)
            else:
                st.markdown(f"{'  ' * level}{idx}. {item}")
    elif isinstance(findings, dict):
        for key, value in findings.items():
            st.markdown(f"{'  ' * level}**{key}:**")
            display_nested_findings(value, urls, level + 1)
    
    if urls:
        st.markdown("#### Sources")
        sources_df = pd.DataFrame({
            'Source': [f"[Source {i+1}]({url})" for i, url in enumerate(urls)]
        })
        st.dataframe(sources_df, hide_index=True, use_container_width=True)


def display_reports(reports, expanded=True):
    for report in reports:
        with st.expander(f"Report: {report['Company Name']} - {report.get('Created Time', 'N/A')}", expanded=expanded):
            st.markdown(f"**Language:** {report.get('Language', 'N/A')} | **Region:** {report.get('Region', 'N/A')}")
            
            research_results = report.get('Research', [])
            
            tab_titles = [item.get('research_focus', f"Focus {i+1}") for i, item in enumerate(research_results)]
            tabs = st.tabs(tab_titles)
            
            for tab, content in zip(tabs, research_results):
                with tab:
                    st.markdown(f"### {content.get('research_focus', 'Research Focus')}")
                    
                    display_nested_findings(content.get('findings', ''), content.get('urls'))
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Search News Only", "Yes" if report.get('Search News Only') else "No")
            col2.metric("Search Adverse News", "Yes" if report.get('Search Advers News') else "No")
            col3.metric("Created Time", report.get('Created Time', 'N/A')) 


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

if generate_button:
    if company_name:
        with st.spinner("Generating report..."):
            thread_id = str(uuid.uuid4())
            num_result_per_focus = 5 # pre-defined 

            get_company_report(
                company_name, 
                research_languages, 
                report_language, 
                news_source,
                region,
                additional_focus,
                num_result_per_focus,
                num_news_result,
                search_news_only,
                search_adverse_news,
                thread_id
                )

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
                st.markdown(f"### 📝 The Lastest Report")
                comp_query = {'Company Name': {'$regex': company_name, '$options': 'i'}}
                reports = list(collection.find(comp_query).sort("created_time", DESCENDING))
                display_reports(reports[:1], expanded=True)

if company_name:
    st.divider()
    st.markdown(f"### 📝 Reports of {company_name}")
    comp_query = {'Company Name': {'$regex': company_name, '$options': 'i'}}
    reports = list(collection.find(comp_query).sort("created_time", DESCENDING))
    if generate_button:
        display_reports(reports[1:], expanded=False)
    else:
        display_reports(reports[:], expanded=False)