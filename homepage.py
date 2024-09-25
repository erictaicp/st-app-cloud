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
    ("🧠", "AI Agent", "Intelligent AI agent powered by GPT-4 for complex tasks, queries, and document processing workflows."),
    ("📊", "Order Management", "Streamlined order placement, status tracking, and document submission with real-time updates."),
    ("📄", "Document Processing", "AI-driven document validation, type recognition, and field extraction for various document types."),
    ("🔍", "Content Checker", "AI-powered checking system with customizable rules for validating orders and documents across the same order ID."),
    ("🚀", "Extraction Express", "Rapid document validation and key field extraction tool for efficient data processing."),
    ("📚", "Chase Book", "Comprehensive order management system for viewing, editing, and tracking all orders in one place."),
    ("🔔", "Smart Reminders", "Automated reminders via email and WhatsApp for timely document submission and updates."),
    ("👥", "Role-Based Access", "Tailored functionalities for admins and clients with secure access control and user management."),
    ("🌐", "Multi-Country Support", "Configurable settings for different countries with country-specific document types and key fields."),
    ("📱", "Multi-Channel Integration", "Seamless communication through various channels like email, WhatsApp, and web portal using a unified API."),
    ("📈", "Market Researcher", "AI-powered online market research agent to gather information about interested companies and industry trends."),
    ("🧙‍♂️", "Data Wizard", "Advanced data visualization and insights tool for transforming raw data into actionable intelligence.")
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

# Supported Document Types
st.markdown("## 📄 Supported Document Types")
st.write("Certificate of Origin, Commercial Invoice, Proof of Payment, Contract, Bill of Lading, and more.")

# Tech Stack
st.markdown("## 💻 Cutting-Edge Tech Stack")
st.write("Python 3.10, React, FastAPI, MongoDB, Azure Blob Storage, Langchain with GPT-4")

# Testimonials
st.markdown("## 💬 What Our Users Say")
cols = st.columns(3)
testimonials = [
    ('"Project Alchemist has revolutionized our document management process. It\'s like having a team of experts working 24/7!"', "Sarah J., Operations Manager"),
    ('"The AI-powered content checker has significantly reduced errors and improved our compliance. It\'s a game-changer!"', "Michael L., Compliance Officer"),
    ('"The multi-country support and data visualization tools have given us insights we never had before. Highly recommended!"', "Elena R., Global Logistics Director")
]

for idx, (quote, author) in enumerate(testimonials):
    with cols[idx]:
        st.markdown(f"""
        <div style='background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <p style='font-style: italic;'>{quote}</p>
            <p style='text-align: right;'><strong>- {author}</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Call to Action
st.markdown("## 🚀 Ready to Transform Your Workflow?")
st.write("Join the AI revolution in document and order management today!")
if st.button("Get Started"):
    st.success("Thank you for your interest! Our team will contact you shortly.")

# Footer
st.markdown("---")
st.markdown("© 2024 Project Alchemist. All rights reserved.")