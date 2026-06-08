import streamlit as st 


st.markdown('# About Me')

st.text("""
        My name is Wesley de Souza Matos, a Data Scientist from Brazil.

I am based in Rio de Janeiro, where I study and work in Data Science, Risk Analysis, Machine Learning, and Financial Modeling. This project was developed to help users monitor oil market signals, assess uncertainty and risk, explore possible future scenarios, generate forecasts, and perform survival analysis on market dynamics.

The objective of this platform is to provide analytical insights and support decision-making through data-driven approaches.

I hope you find this project useful and informative. Feel free to connect with me on LinkedIn or GitHub.

Thank you for your visit! 🫂


""")
linkedin_url = 'https://www.linkedin.com/in/wesley-matos-5a4b84254/'
github_url = 'https://github.com/WesleySouza13'
col1, col2 = st.columns(2)
with col1:
    st.link_button('Linkedin', url=linkedin_url)
with col2:
    st.link_button('GitHub', url=github_url)

badges = ['![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)', '![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)','![NumPy](https://img.shields.io/badge/NumPy-013243.svg?style=for-the-badge&logo=numpy&logoColor=white)', '![Pandas](https://img.shields.io/badge/Pandas-150458.svg?style=for-the-badge&logo=pandas&logoColor=white)', '![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)', '![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white)', '![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)',
        '![Plotly Dash](https://img.shields.io/badge/plotly-3F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)','![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)','![Yahoo!](https://img.shields.io/badge/Yahoo!-6001D2?style=for-the-badge&logo=Yahoo!&logoColor=white)', '![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)',
        '![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)'
        ]

st.text('Technologies used in this app:')
coln = st.columns(len(badges))

for col, badge in zip(coln, badges):
    with col:
        st.markdown(badge, unsafe_allow_html=True)


with st.container(border=True):
    st.text("""
        Project Statistics

        Forecasting Models: 5
        Market Indicators Monitored: 13+
        Forecast Horizon: Up to 12 Months
        Simulation Capacity: 10,000+ Scenarios
        Survival Models: Kaplan-Meier & Cox PH
            """)
st.markdown("""
    <style>
    .block-container {
        max-width: 80%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)