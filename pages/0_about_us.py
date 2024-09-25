import streamlit as st
import os
from utils import add_logo

# Function to read README content
def read_markdown_file(markdown_file):
    with open(markdown_file, "r", encoding="utf-8") as file:
        return file.read()
# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))
# Use os.path.join to navigate to the config.yaml file
readme_file = os.path.join('/'.join(dir_path.split('/')[:-2]),'readme.md')

# Set page configuration and theme
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()
# Read and display the README content
readme_content = read_markdown_file(readme_file)
st.markdown(readme_content, unsafe_allow_html=True)