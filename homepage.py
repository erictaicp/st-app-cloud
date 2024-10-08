import streamlit as st
from PIL import Image
from utils import add_logo

# Set page configuration and theme
st.set_page_config(
    page_title="Project Alchemist",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add logo to all pages
add_logo()

# Custom CSS
st.markdown("""
    <style>
    .main > div {
        padding-top: 1rem;
    }
    .stButton>button {
        background-color: #7C3AED;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }
    .feature-card {
        background-color: white !important;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1F2937 !important;
    }
    .feature-description {
        font-size: 0.9rem;
        color: #4B5563 !important;
        flex-grow: 1;
    }
    [data-testid="stMarkdownContainer"] > .feature-card {
        background-color: white !important;
        color: #1F2937 !important;
    }
    [data-testid="stMarkdownContainer"] > div > p {
        color: #4B5563 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>Project <span style='color: #7C3AED;'>Alchemist</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #4B5563;'>Revolutionizing document and order management with AI-powered automation</p>", unsafe_allow_html=True)

# Features
st.markdown("## 🚀 Key Features")

features = [
    ("🧙‍♂️", "Supplier Search", "AI-powered supplier search agent to find suppliers based on specific criteria and retrieve relevant documents."),
]

# Render features in a grid with 3 columns
for i in range(0, len(features), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(features):
            icon, title, description = features[i + j]
            with cols[j]:
                st.markdown(f"""
                <div class='feature-card'>
                    <div class='feature-icon'>{icon}</div>
                    <div class='feature-title'>{title}</div>
                    <div class='feature-description'>{description}</div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)  # Add some vertical spacing between rows


# Footer
st.markdown("---")
st.markdown("© 2024 Project Alchemist. All rights reserved.")