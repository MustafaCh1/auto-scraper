from autotraderScraper import auto_assistant
from autotraderScraper import auto_scrape
import streamlit as st
from google import genai
from google.genai import types


assistant = auto_assistant()
# auto = auto_scrape("https://www.autotrader.co.uk", "rm94xu")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


st.write("Welcome to AutoScraper, where we help match you to the perfect car!")


prompt = st.chat_input("Tell me about the car you want - the more descriptive the better!")

if prompt:
    assistant.contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            )
    st.write(assistant.generate(prompt))
