
#Import packages
import streamlit as st
from datetime import date, datetime
from openai import OpenAI

# Open file with Api Key
with open("openai_ai.key.txt") as f:
    my_api_key = f.read().strip()

# Initialize OpenAI with API key
client = OpenAI(api_key=my_api_key)

#Configure page
st.set_page_config(page_title="PersonApp",layout="wide")

#Write title and text
st.title("PersonApp")
st.write("This is a test")

#Gather current date and time
st.write("Current date and time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
