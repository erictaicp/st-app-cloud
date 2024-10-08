import streamlit as st

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://e7.pngegg.com/pngimages/343/892/png-clipart-li-fung-logo-supply-chain-chief-executive-organization-business-company-text-thumbnail.png);
                background-repeat: no-repeat;
                background-size: 140px;
                padding-top: 150px;
                top: -30px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "©SDU All rights reserved.";
                margin-left: 20px;
                font-size: 10px;
                position: relative;
                top: -8x;
                color: #666;
            }
            [data-testid="stSidebarNav"] > ul {
                padding-top: 5px;
            }
            .sidebar-content {
                padding-top: 0px !important;
            }
            [data-testid="stSidebarNav"] > ul > li:first-child {
                margin-top: -5px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )