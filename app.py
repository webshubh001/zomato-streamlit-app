# Streamlit App for Zomato Data Analysis (Multi-page Setup with Login)

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Zomato Data Analysis", layout="wide")

# Simulated login credentials
USER_CREDENTIALS = {"admin": "password123", "user": "zomato2024"}

@st.cache_data

def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, encoding='latin-1')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)

    df['rate'] = df['rate'].astype(str)
    df = df[~df['rate'].isin(['NEW', '-', 'nan'])]
    df['rate'] = df['rate'].str.extract(r'(\d+\.?\d*)')
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

    df['approx_costfor_two_people'] = df['approx_costfor_two_people'].astype(str).str.replace(',', '')
    df['approx_costfor_two_people'] = pd.to_numeric(df['approx_costfor_two_people'], errors='coerce')

    df.rename(columns={
        'rate': 'aggregate_rating',
        'approx_costfor_two_people': 'average_cost_for_two',
        'online_order': 'has_online_delivery',
        'listed_intype': 'listed_in_type'
    }, inplace=True)

    df.dropna(subset=['aggregate_rating', 'average_cost_for_two'], inplace=True)
    return df

# Login functionality
def login():
    st.title("🔐 Zomato Data Portal - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# Welcome page
def welcome():
    st.title("🍽️ Welcome to Zomato Data Explorer")
    st.markdown("""
        This dashboard provides insights into restaurant ratings, costs, and service types
        based on the Zomato dataset.

        **Use the sidebar to log in and navigate between pages.**
    """)

# Initialize login state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Navigation
if not st.session_state.logged_in:
    login()
else:
    uploaded_file = st.sidebar.file_uploader("Upload Zomato CSV File", type=["csv"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)

        st.sidebar.title("Zomato Data Explorer")
        page = st.sidebar.radio("Go to", ["Welcome", "Overview", "Rating Distribution", "Online Ordering", "Cost vs Rating", "Restaurant Types"])

        if page == "Welcome":
            welcome()

        elif page == "Overview":
            st.title("Zomato Data Overview")
            st.dataframe(df.head(50))

        elif page == "Rating Distribution":
            st.title("Distribution of Aggregate Ratings")
            fig, ax = plt.subplots()
            sns.histplot(df['aggregate_rating'], bins=20, kde=True, color='teal', ax=ax)
            ax.set_xlabel("Rating")
            ax.set_ylabel("Count")
            st.pyplot(fig)

        elif page == "Online Ordering":
            st.title("Online Ordering Availability")
            if 'has_online_delivery' in df.columns:
                fig, ax = plt.subplots()
                df['has_online_delivery'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'], ax=ax)
                ax.set_ylabel('')
                st.pyplot(fig)
            else:
                st.warning("Online delivery column is missing.")

        elif page == "Cost vs Rating":
            st.title("Cost for Two vs Aggregate Rating")
            fig, ax = plt.subplots()
            sns.scatterplot(x='average_cost_for_two', y='aggregate_rating', data=df, alpha=0.6, ax=ax)
            ax.set_xlabel("Average Cost for Two")
            ax.set_ylabel("Rating")
            st.pyplot(fig)

        elif page == "Restaurant Types":
            st.title("Top 10 Restaurant Types")
            if 'listed_in_type' in df.columns and not df['listed_in_type'].dropna().empty:
                fig, ax = plt.subplots()
                df['listed_in_type'].value_counts().head(10).plot(kind='bar', color='coral', ax=ax)
                ax.set_xlabel("Type")
                ax.set_ylabel("Number of Restaurants")
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
                st.pyplot(fig)
            else:
                st.warning("Restaurant types data not available.")
    else:
        st.warning("Please upload a CSV file to proceed.")
