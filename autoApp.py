from autotraderScraper import auto_assistant
from autotraderScraper import auto_scrape
import streamlit as st
import json
from google import genai
from google.genai import types
from price_predictor import price_predict
import price_predictor

# --- Initialize assistant once and keep it in session_state ---
if "assistant" not in st.session_state:
    st.session_state.assistant = auto_assistant(streamCreds=st.secrets["gcp_service_account"])
    st.session_state.messages = []
    st.session_state.assistant_contents = []
    st.session_state.assistant.full_input = ""  # ensure input string persists too

if "scraper" not in st.session_state:
    st.session_state.scraper = auto_scrape("https://www.autotrader.co.uk", "rm94xu")

if "price_predict" not in st.session_state:
    st.session_state.price_predict = price_predict()

if "go" not in st.session_state:
    st.session_state.go = True

assistant = st.session_state.assistant  # shortcut
scraper = st.session_state.scraper  # shortcut

# --- Display past messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def price_bracket(predicted, actual):
    if 0.9 < actual / predicted < 1.1:
        return "Market Average"
    elif actual / predicted < 0.9:
        return "Below Market Average"
    elif actual / predicted < 0.8:
        return "Well Below Market Average"
    elif actual / predicted > 1.1:
        return "Above Market Average"
    elif actual / predicted > 1.2:
        return "Well Above Market Average"
    else:
        return "Average"

st.write("Welcome to AutoScraper, where we help match you to the perfect car!")

st.button("Find Matches", disabled=st.session_state.go)

# --- Chat input ---
prompt = st.chat_input("Tell me about the car you want - the more descriptive the better!")

if prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Keep track in assistant state
    assistant.full_input += prompt + "\n"
    st.session_state.assistant_contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    )
    assistant.contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    )

    # --- Generate response ---
    response = assistant.generate(prompt)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.assistant_contents.append(
        types.Content(role="model", parts=[types.Part.from_text(text=response)])
    )
    assistant.contents.append(
        types.Content(role="model", parts=[types.Part.from_text(text=response)])
    )

    with st.chat_message("assistant"):
        st.markdown(response)


    parsed_query = None
    data = None
    results = None
    text_part = response
    if "Query:" in response:
        st.session_state.go = False
        assistant.final_output = response 
        data = assistant.clean_output()
        text_part, query_part = response.split("Query:", 1)
        text_part = text_part.strip()
        query_part = query_part.strip()
        st.write("Searching for your perfect car now...")
        scraper.start()
        results = scraper.find_matches(data)
        scraper.close()

    if data:
        st.session_state.messages = []
        st.session_state.assistant_contents = []
        st.session_state.assistant.full_input = ""
        st.write("🔎 Searching for your perfect car now...")
    
    
    base_url = "https://www.autotrader.co.uk"

    if results:
        st.subheader("Found the following matches:")

        for link, score, features, carData in results[:10]:
            score = round(score, 2)
            carPricePred = st.session_state.price_predict.predict(carData)
            priceb = price_bracket(carPricePred, int(carData['heading']['priceBreakdown']['price']['price']))
            gallery = carData['gallery']['images'] if 'gallery' in carData else []
            first_img = gallery[0]['url'] if gallery else None
            price = "£" + str(carData['heading']['priceBreakdown']['price']['price'])
            ing = next((item['value'] for item in carData['runningCostsV2']['items'] if item['label'] == 'Insurance group'), "N/A")

            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #ddd;
                        border-radius: 12px;
                        padding: 16px;
                        margin-bottom: 16px;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    ">
                        <h3 style="margin: 0;">{carData['heading']['title']} - {carData['heading']['subTitle']} - {price}</h3>
                        {f'<img src="{first_img}" style="width:100%;border-radius:8px;margin:8px 0;">' if first_img else ''}
                        <p><b>Insurance Group:</b>{ing}</p>
                        <p><b>Match Score:</b>{score * 100}%</p>
                        <p><b>Car is: {priceb}</b>
                        <a href="{base_url}{link}" target="_blank">View Listing</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )



