import json
from tkinter.font import names
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from sqlalchemy import desc
from sympy import pprint
import re
from google import genai
from google.genai import types
import base64
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz, process
from nltk import ngrams

# url = "https://www.autotrader.co.uk/search-form?postcode=rm94xu"
# chrome_options = Options()
# chrome_options.headless = True  
# driver = webdriver.Chrome(options=chrome_options)
# driver.get(url)
# driver.implicitly_wait(5) 
# iframe = WebDriverWait(driver, 50).until(
#     EC.presence_of_element_located((By.ID, "sp_message_iframe_1086457"))
#     # sp messages swaps between 1086457 and 1086458
# )
# driver.switch_to.frame(iframe)

# driver.execute_script("""
# var overlay = document.querySelector('.message-overlay');
# if (overlay) { overlay.remove(); }
# """)


# reject_button = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable(
#         (By.CSS_SELECTOR, ".message-component.message-button.no-children.focusable.sp_choice_type_13")
#     )
# )
# reject_button.click()

# driver.switch_to.default_content()

# print("✅ Cookies rejected successfully.")

# driver.implicitly_wait(5)

# make_model_button = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable(
#         (By.XPATH, "//*[@id='make_and_model']/button"))
# )
# make_model_button.click()

# driver.implicitly_wait(5)
# car_makes = driver.find_elements(By.XPATH, "//*[@id='make']/option")

# makes = []
# makes_models = []

# for make in car_makes:
#     makes.append(make.get_attribute("value"))



# soup = BeautifulSoup(driver.page_source, 'html.parser')

# # get makes and models

# for i in range(len(makes)):
#     if makes[i] == "Any":
#         continue
#     else:
#         car_url = f"https://www.autotrader.co.uk/search-form?make={makes[i]}&postcode=rm94xu&sort=relevance"
#     driver.get(car_url)
#     driver.implicitly_wait(5)

#     make_model_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable(
#             (By.XPATH, "//*[@id='make_and_model']/button"))
#     )
#     make_model_button.click()
#     models = driver.find_elements(By.XPATH, "//*[@id='model']/option")
#     for model in models:
#         makes_models.append((makes[i], model.get_attribute("value")))


# # get makes and models and variants

# limit = 0

# makes_models_variants = []

# # for make, model in makes_models:
# #     try: 
# #         car_url = f"https://www.autotrader.co.uk/search-form?make={make}&model={model}&postcode=rm94xu&sort=relevance"
# #         driver.get(car_url)
# #         driver.implicitly_wait(5)
# #         make_model_button = WebDriverWait(driver, 10).until(
# #             EC.element_to_be_clickable(
# #                 (By.XPATH, "//*[@id='make_and_model']/button"))
# #         )
# #         make_model_button.click()
# #         variants = driver.find_elements(By.XPATH, "//*[@id='aggregated_trim']/option")
# #         for variant in variants:
# #             makes_models_variants.append((make, model, variant.get_attribute("value")))
# #     except: 
# #         print(f"Error with make: {make}, model: {model}")


# # for make, model, variant in makes_models_variants:
# #     print(f"Make: {make}, Model: {model}, Variant: {variant}")

# # create csv of make, model, variant

# cars_df = pd.DataFrame(makes_models, columns=["Make", "Model"])
# cars_df.to_csv("cars.csv", index=False)

# the number on the cars href can be extracted to query the api directly 

class auto_assistant():
    def __init__(self):
        self.full_input = ""
        self.contents = []
        self.final_output = ""


    def generate(self, user_input):
        client = genai.Client(
            vertexai=True,
            project="gcptutorial-468212",
            location="global"
        )
        response = ''
        si_text1 = """You are a middle man between a user and a car dealership site. 
        Based on a user's input you want to extract all possible information that matches the structured output. 
        You will ask questions simulating an actual car dealer so that the user can develop the prompt to fill 
        as much information as possible with as many additional options as possible.
        Based on the chat history provided you must decide whether to ask more questions or return the final output Query. 
        You have two options, either ask questions or return the final query but you cannot do both. 
        You must always use the chat history to inform your decision. 
        At each stage you must also tell the customer what information you already have. 
        You at a minimum must know 6 fields about the vehicle the customer wants. 
        After asking questions you must return a final JSON structured output that 
        gives the summarised information. Where information it can be included in the features column. 
        Do not make any assumptions on fields that have not been provided. 
        Wherever you have identified a field should exist it must be included. 
        Make sure to ask the user for additional options they may want the car to have like heated seats or cruise control.
        Note that you can only choose from the options specified in the files found in the data store. 
        You will take any input and return it in the correct JSON format. 
        Where you lack the ability to fill fields you can just ignore them, just fill the fields that can be filled. 
        You do not ask more than 3 questions and you must return the structured JSON at the end. 
        When you return the final structured query you will start the result with \"Query:\"

        each field and what it means is specified:
        make: The manufacturer or brand of the car (e.g., Toyota, BMW, Ford).
        model: The specific model name of the car (e.g., Corolla, 3 Series, Fiesta).
        variant: The trim or version of the model, often specifying engine size or features.
        annual-tax-cars: The annual road tax cost bracket for the car, usually based on emissions or fuel type.
        body-type: The style or shape of the car's body (e.g., SUV, Hatchback, Coupe).
        bootSizeValues: The storage capacity of the car's boot (e.g., Small, Medium, Large).
        co2-emissions-cars: The CO₂ emission bracket for the car, measured in grams per kilometre.
        colour: The exterior colour of the car.
        drivetrain: The system delivering power to the wheels (e.g., Four Wheel Drive, Front Wheel Drive).
        fuel-consumption: The fuel efficiency bracket of the car (e.g., OVER_30 means more than 30 mpg).
        fuel-type: The type of fuel or propulsion system the car uses (e.g., Petrol, Diesel, Electric).
        insuranceGroup: The UK insurance group classification of the car (lower numbers are usually cheaper to insure) a number will always have \"U\" after it for queries.
        max-engine-power: The maximum engine output of the car, typically in horsepower or kW.
        maximum-badge-engine-size: The largest engine size displayed on the car's badge (in litres).
        maximum-mileage: The maximum allowed mileage for search results (in miles).
        min-engine-power: The minimum engine output of the car to include in search results.
        minimum-badge-engine-size: The smallest engine size displayed on the badge (in litres).
        minimum-mileage: The minimum mileage for search results (in miles).
        postcode: The postcode from which to search for cars (for location-based filtering).
        price-from: The minimum price for cars in the search.
        price-to: The maximum price for cars in the search.
        quantity-of-doors: The number of doors the car has (including boot door for hatchbacks).
        seats_values: The number of seats in the car.
        seller-type: Whether the seller is a private individual or a trade dealer.
        transmission: The type of gearbox the car has (e.g., Automatic, Manual).
        year-from: The earliest year of manufacture to include.
        year-to: The latest year of manufacture to include.
        zero-to-60: The acceleration bracket from 0 to 60 mph (in seconds)."""

        model = "gemini-2.5-flash"
        contents = [
            types.Content(
            role="user",
            parts=[types.Part.from_text(text=self.full_input)
            ]
            )
        ]
        tools = [
            types.Tool(
            retrieval=types.Retrieval(
                vertex_rag_store=types.VertexRagStore(
                rag_resources=[
                    types.VertexRagStoreRagResource(
                    rag_corpus="projects/gcptutorial-468212/locations/us-central1/ragCorpora/6917529027641081856"
                    )
                ],
                )
            )
            )
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature = 0.6,
            top_p = 0.95,
            seed = 0,
            max_output_tokens = 65535,
            safety_settings = [types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
            )],
            tools = tools,
            system_instruction=[types.Part.from_text(text=si_text1)],
            thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
            ),
        )

        for chunk in client.models.generate_content_stream(
            model = model,
            contents = self.contents,
            config = generate_content_config,
            ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue
            response += chunk.candidates[0].content.parts[0].text
            
        
        print(response)

        return response

    def conversation(self):
        res = ''
        while "Query:" not in res: 
            print("------------------------------")
            user_input = input("Enter your car query: ")
            if user_input.lower() == "exit":
                break
            self.full_input += user_input + "\n"
            self.contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_input)]
                )
            )
            res = self.generate(user_input)
            self.contents.append(
            types.Content(
                role="model", 
                parts=[types.Part.from_text(text=res)]
            )
            )
            print("------------------------------")
        self.final_output = res
        return self.final_output

    def clean_output(self):
        parts = self.final_output.split("```json")
        if len(parts) > 1:
            json_str = parts[1].split("```")[0].strip()
            data = json.loads(json_str)
            return data
    
    def get_user_input(self):
        return self.full_input


class auto_scrape:
    def __init__(self, base_url, postcode):
        self.base_url = base_url
        self.postcode = postcode
        chrome_options = Options()
        chrome_options.headless = True
        self.driver = webdriver.Chrome(options=chrome_options)
        self.car_links = []
        self.cookies_rejected = False
        self.low_priority_params = [
            "colour", 
            "drivetrain", 
            "fuel-consumption",
            "fuel-type", 
            "variant"
        ]
        self.params = [
            "make",
            "model",
            "variant",
            "annual-tax-cars",
            "body-type",
            "bootSizeValues",
            "co2-emissions-cars",
            "colour",
            "drivetrain",
            "fuel-consumption",
            "fuel-type",
            "insuranceGroup",
            "max-engine-power",
            "maximum-badge-engine-size",
            "maximum-mileage",
            "min-engine-power",
            "minimum-badge-engine-size",
            "minimum-mileage",
            "postcode",
            "price-from",
            "price-to",
            "quantity-of-doors",
            "seats_values",
            "seller-type",
            "transmission",
            "year-from",
            "year-to",
            "zero-to-60",
            "features"
            ]
        self.min_numeric_params = [
            "min-engine-power",
            "minimum-mileage",
            "price-from"
        ]
        self.max_numeric_params = [
            "max-engine-power",
            "maximum-mileage",
            "price-to",
        ]

    def close(self):
        self.driver.quit()

    def scrape_listings_page(self, page, url):
        url = url + f"&page={page}"
        self.driver.get(url)
        print("Navigating to:", url)
        if not self.cookies_rejected:
            self.reject_cookies()
            self.cookies_rejected = True
        self.driver.implicitly_wait(5)
        time.sleep(1)  # Allow time for the page to load
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        listings = soup.find_all("li", class_="at__sc-mddoqs-1 hTOmMI")
        if not listings:
            return False
        for listing in listings: 
            self.car_links.append(listing.find("a")["href"])
        return True
    
    def scrape_car_page(self, url):
        match = re.search(r'car-details/(\d+)', url)
        if match:
            print(match.group(1))
            carID = match.group(1)
        else:
            print("Car ID not found in URL.")
            return
        api_url = f"https://www.autotrader.co.uk/product-page/v1/advert/{carID}?channel=cars&postcode=rm94xu"
        self.driver.get(api_url)
        json_text = self.driver.find_element("tag name", "pre").text
        data = json.loads(json_text)
        if data:
            # print("Car Data Retrieved Successfully:")
            return data
        else:
            print("Failed to retrieve car data.")

    def reject_cookies(self):
        try:
            iframe = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.ID, "sp_message_iframe_1086457"))
            )
            self.driver.switch_to.frame(iframe)
            reject_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".message-component.message-button.no-children.focusable.sp_choice_type_13")
                )
            )
            reject_button.click()
            self.driver.switch_to.default_content()
            print("✅ Cookies rejected successfully.")

        except NoSuchElementException:
            print("❌ Cookie rejection button not found.")
        
    def create_search_form(self, query):
        query1_params = ""
        query2_params = ""
        query3_params = ""
        for k, v in query.items():
            if k != 'features':
                if k in self.min_numeric_params:
                    new_val = int(int(v) * 0.9)
                    query2_params += f"&{k}={new_val}"
                if k in self.max_numeric_params:
                    new_val = int(int(v) * 1.1)
                    query2_params += f"&{k}={new_val}"
                if k == 'minimum-badge-engine-size':
                    new_val = min(0, float(float(v) - 0.5))
                    query2_params += f"&{k}={new_val}"
                if k == 'maximum-badge-engine-size':
                    new_val = float(float(v) + 0.5)
                    query2_params += f"&{k}={new_val}"
                if isinstance(v, list):
                    for item in v:
                        query1_params += f"&{k}={item}"
                        query2_params += f"&{k}={item}"
                        if k not in self.low_priority_params:
                            query3_params += f"&{k}={item}"
                else:
                    query1_params += f"&{k}={v}"
                    if k != 'variant':
                        query2_params += f"&{k}={v}"
                    if k not in self.low_priority_params:
                        query3_params += f"&{k}={v}"

        main_url = "https://www.autotrader.co.uk/car-search?postcode=" + self.postcode + query1_params
        alt_url = "https://www.autotrader.co.uk/car-search?postcode=" + self.postcode + query2_params 
        alt_url2 = "https://www.autotrader.co.uk/car-search?postcode=" + self.postcode + query3_params

        return main_url, alt_url, alt_url2



    def similarity_score(self, car, query):
        if "features" in query.keys():
            match_conditions = len(query) - 1 + len(query["features"])
        else:
            match_conditions = len(query)

        met_conditions = 0

        if 'make' in query.keys():
            if query['make'].lower() in car["heading"]["title"].lower():
                met_conditions += 1

        if 'model' in query.keys():
            if query['model'].lower() in car["heading"]["title"].lower():
                met_conditions += 1

        if 'variant' in query.keys():
            if query['variant'].lower() in car["heading"]["subTitle"].lower():
                met_conditions += 1
        if 'annual-tax-cars' in query.keys():
            if query['annual-tax-cars'][0:4] == "OVER":
                met_conditions += 1

            else:
                query_tax = int(query['annual-tax-cars'].split("_")[1])
                car_tax = next(
                    (item['value'] for item in car['runningCostsV2']['items'] if item['label'] == 'Tax per year'),
                    None
                )
                car_tax = int(car_tax[1:]) if car_tax else 0
                if query_tax >= car_tax:
                    met_conditions += 1
        if 'body-type' in query.keys():
            car_body = next(
                (item["value"] for item in car["keySpecification"] if item["label"] == "Body type"),
                None 
                )
            if car_body in query['body-type']:
                met_conditions += 1
        if 'bootSizeValues' in query.keys():
            boot_space_up = next(
                (item["value"] for spec in car["specs"] for item in spec["items"] if item["name"] == "Boot space (seats up)"),
                None
                )
        if 'co2-emissions-cars' in query.keys():
            if query['co2-emissions-cars'][0:4] == "OVER":
                met_conditions += 1
            else:
                query_emissions = int(query['co2-emissions-cars'].split("_")[1])
                running_costs = car['runningCostsV2']['items']
                car_emissions = int(item[:-4] for item in running_costs if item['label'] == 'CO₂ emissions' and item['value'].endswith('g/km'))
                if query_emissions >= car_emissions:
                    met_conditions += 1
        if 'colour' in query.keys():
            car_col = next(
                (item["value"] for item in car["keySpecification"] if item["label"] == "Body colour"),
                None
            )
            if car_col in query['colour']:
                met_conditions += 1
        if 'drivetrain' in query.keys():
            drivetrain = car['history']['vehicleContext']['standardDrivetrain']
            if drivetrain in query['drivetrain']:
                met_conditions += 1
        if 'fuel-consumption' in query.keys():
            mpg = next(
                (item["value"] for spec in car["specs"] for item in spec["items"] if item["name"] == "Miles per gallon"),
                None
            )
            mpg = int(mpg[:-3]) if mpg else 0
            if int(query['fuel-consumption'][5:]) <= mpg:
                met_conditions += 1
        if 'fuel-type' in query.keys():
            fuel = next((item['value'] for item in car['keySpecification'] if item['label'] == 'Fuel type'), None)
            if fuel in query['fuel-type']:
                met_conditions += 1
        if 'insuranceGroup' in query.keys():
            groupMet = True
            ing = next((item['value'] for item in car['runningCostsV2']['items'] if item['label'] == 'Insurance group'), None)
            for group in query['insuranceGroup']:
                if ing[:-1] >= group[:-1]:
                    groupMet = False
                    break
            if groupMet:
                met_conditions += 1
        if 'quantity-of-doors' in query.keys():
            doors = next(
                (item["value"] for item in car["keySpecification"] if item["label"] == "Doors"),
                None
            )
            if doors in query['quantity-of-doors']:
                met_conditions += 1
        if 'seats_values' in query.keys():
            seats = next(
                (item["value"] for item in car["keySpecification"] if item["label"] == "Seats"),
                None
            )
            if seats in query['seats_values']:
                met_conditions += 1

        if 'seller-type' in query.keys():
            seller = car['seller']['type'].lower()
            if seller in query['seller-type'].lower():
                met_conditions += 1

        if 'transmission' in query.keys():
            trans = next(
                (item["value"] for item in car["keySpecification"] if item["label"] == "Gearbox"),
                None
            )
            if trans in query['transmission']:
                met_conditions += 1

        if 'zero-to-60' in query.keys():
            acc_match = False
            perf = car['specs']
            specs = []
            for item in perf:
                if item['category'] == 'Performance':
                    specs = item['items']
                    break
            for spec in specs:
                if spec['name'] == '0-62mph' or spec['name'] == '0-60mph':
                    acc = float(spec['value'].split(" ")[0])
                    break
            for acc_range in query['zero-to-60']:
                if acc_range == "TO_4":
                    if acc <= 4:
                        acc_match = True
                if acc_range == "4_TO_6":
                    if 4 < acc <= 6:
                        acc_match = True
                if acc_range == "6_TO_8":
                    if 6 < acc <= 8:
                        acc_match = True
                if acc_range == "8_TO_10":
                    if 8 < acc <= 10:
                        acc_match = True
                if acc_range == "10_TO_12":
                    if 10 < acc <= 12:
                        acc_match = True
                if acc_range == "OVER_12":
                    if acc > 12:
                        acc_match = True
            if acc_match:
                print(f"Acceleration matched: {acc}")
                met_conditions += 1
        if 'price-to' in query.keys() or 'price-from' in query.keys():
            mini= query.get('price-from', None)
            maxi= query.get('price-to', None)
            mini= int(mini) if mini else None
            maxi= int(maxi) if maxi else None
            price = int(car['heading']['priceBreakdown']['price']['price'])
            if self.cont_values(price, max_desired=maxi, min_desired=mini):
                met_conditions += 1
        
        if 'minimum-badge-engine-size' in query.keys() or 'maximum-badge-engine-size' in query.keys():
            mini= query.get('minimum-badge-engine-size', None)
            maxi= query.get('maximum-badge-engine-size', None)
            mini= float(mini) if mini else None
            maxi= float(maxi) if maxi else None
            keys = car['keySpecification']
            for item in keys:
                if item['label'] == 'Engine':
                    engine_size = float(item['value'][:-1])
                    break
            if self.cont_values(engine_size, max_desired=maxi, min_desired=mini):
                met_conditions += 1

        if 'year-from' in query.keys() or 'year-to' in query.keys():
            mini= query.get('year-from', None)
            maxi= query.get('year-to', None)
            mini= int(mini) if mini else None
            maxi= int(maxi) if maxi else None
            keys = car['keySpecification']
            for item in keys:
                if item['label'] == 'Registration':
                    year = int(item['value'][:4])
                    break
            if self.cont_values(year, max_desired=maxi, min_desired=mini):
                met_conditions += 1

        if 'maximum-mileage' in query.keys() or 'minimum-mileage' in query.keys():
            mileage = None
            mini= query.get('minimum-mileage', None)
            maxi= query.get('maximum-mileage', None)
            mini= int(mini) if mini else None
            maxi= int(maxi) if maxi else None
            keys = car['keySpecification']
            for item in keys:
                if item['label'] == 'Mileage':
                    mileage = int(item['value'].split(" ")[0].replace(",", ""))
                    break
            if self.cont_values(mileage if mileage else 0, max_desired=maxi, min_desired=mini):
                met_conditions += 1

        if 'min-engine-power' in query.keys() or 'max-engine-power' in query.keys():
            mini= query.get('min-engine-power', None)
            maxi= query.get('max-engine-power', None)
            mini= int(mini) if mini else None
            maxi= int(maxi) if maxi else None
            perf = [item for item in car['specs'] if item['category'] == 'Performance']
            perf = perf[0] if perf else {}
            power = None
            for item in perf['items']:
                power = item["value"] if item["name"] == "Engine power" else power
            power = power[:-3] if power else None
            if power:
                met = self.cont_values(int(power), max_desired=maxi, min_desired=mini)
                if met:
                    met_conditions += 1
        
        if 'features' in query.keys():
            # create dictionary of features with their strongest match
            # after both searches see strongest match and weight accordingly
            query_feat = {feature: 0 for feature in query['features']}
            car_feat = car['featuresWithDisclaimer']['features']
            try:
                car_desc = car['description']['text'][0]
            except:
                car_desc = ""

            for feature in query_feat.keys():
                ngram_score = self.ngram_match_score(feature, car_desc)
                weighted_score = (sum(ngram_score['1-gram']) + sum(ngram_score['2-gram'])) / (len(ngram_score["1-gram"]) + len(ngram_score["2-gram"]))
                query_feat[feature] = max(query_feat[feature], weighted_score)

            for feat in query_feat.keys():
                for category in car_feat:
                    for item in category['items']:
                        if fuzz.partial_ratio(item['name'].lower(), feat.lower()) > 80:
                            scores = self.ngram_match_score(feat, item['name'])
                            weighted_score = (sum(scores['1-gram']) * 1.2 + sum(scores['2-gram']) * 0.8) / (len(scores["1-gram"]) + len(scores["2-gram"]))
                            query_feat[feat] = max(query_feat[feat], weighted_score)
                            break
            
            features_found = []
            for feat, score in query_feat.items():
                if score > 80:
                    features_found.append(feat)
                    met_conditions += 1
        
        final_score = met_conditions / match_conditions if match_conditions > 0 else 0

        return final_score, features_found

    def ngram_match_score(self, phrase, description, n_values=[1, 2]):
        phrase = phrase.lower()
        description = description.lower()
        
        scores = {}
        for n in n_values:
            grams = list(ngrams(phrase.split(), n))
            gram_scores = []
            for gram in grams:
                gram_text = " ".join(gram)
                score = fuzz.partial_ratio(gram_text, description)
                gram_scores.append(score)
            scores[f"{n}-gram"] = gram_scores
        return scores


    def cont_values(self, actual, max_desired=None, min_desired=None):
        # will be used to handle values like mileage and price 
        if min_desired and max_desired:
            return min_desired <= actual <= max_desired
        elif min_desired:
            return actual >= min_desired
        elif max_desired:
            return actual <= max_desired
        else:
            return True

    def find_matches(self, query):
        # This function will find matches for the given query
        matchlist = []
        main_url, alt_url, alt_url2 = self.create_search_form(query)
        page = 0
        while True:
            scraping = self.scrape_listings_page(page, main_url)
            page += 1
            if not scraping or page > 20:
                page = 0
                break
        while True:
            scraping = self.scrape_listings_page(page, alt_url)
            if not scraping or page > 20:
                break
            page += 1
        while True:
            scraping = self.scrape_listings_page(page, alt_url2)
            if not scraping or page > 20:
                break
            page += 1

        for link in self.car_links:
            car = self.scrape_car_page(link)
            match_score, found_features = self.similarity_score(car, query)
            matchlist.append((link, match_score, found_features))

        matchlist = sorted(matchlist, key=lambda x: x[1], reverse=True)
        print(matchlist[0:5])  # Print top 10 matches
        return matchlist

# auto_assist = auto_assistant()
# res = auto_assist.conversation()
# data = auto_assist.clean_output()

test_data = {
  "make": "BMW",
  "colour": [
    "Blue"
  ],
  "body-type": [
    "Convertible", 
    "Coupe", 
    "Hatchback",
    "Saloon"
  ],
  "maximum-mileage": "40000",
  "fuel-type": [
    "Petrol"
  ],
  'zero-to-60': ['TO_4', '4_TO_6', '6_TO_8', '8_TO_10', '10_TO_12', 'OVER_12'], 
  "annual-tax-cars": "TO_400",
  "min-engine-power": "400",
  "minimum-badge-engine-size": "1.5",
  "price-to": "50000",
  'transmission': ['Automatic', 'Manual'], 
  "features": [
    "Leather Seats", 
    "carbon roof", 
    "adaptive headlights"
    "Full package", 
    "Apple car play", 
    "Full service history", 
    "360 parking sensors"
  ]
}

test_data2 = {
  "make": "BMW",
  "model": "1 Series",
  "variant": "118i",
  "maximum-mileage": 100000,
  "fuel-type": [
    "Petrol",
    "Diesel"
  ],
  "features": [
    "red leather seats",
    "ULEZ compliant",
    "best speakers",
    "heated seats",
    "cruise control",
    "lane assist"
  ]
}

if __name__ == '__main__':

    # assist = auto_assistant()
    # data = assist.conversation()
    # data = assist.clean_output()
    auto_scraper = auto_scrape("https://www.autotrader.co.uk", "rm94xu")
    auto_scraper.find_matches(test_data)
    # auto_scraper.scrape_listings_page(1, auto_scraper.create_search_form(test_data2))
    # car = auto_scraper.scrape_car_page(auto_scraper.car_links[0])
    # print(auto_scraper.similarity_score(car, test_data2))


    # print(car)

    # auto_scraper.scrape_listings_page(1, "https://www.autotrader.co.uk/car-search?make=BMW&model=M8&postcode=rm9+4xu&sort=relevance")
    # auto_scraper.scrape_listings_page(2, "https://www.autotrader.co.uk/car-search?make=BMW&model=M8&postcode=rm9+4xu&sort=relevance")
    # auto_scraper.scrape_car_page("https://www.autotrader.co.uk/car-details/202507254830859?journey=FEATURED_LISTING_JOURNEY&sort=relevance&searchId=43ae15a9-e5b6-48e0-bfe8-5f14f74b8c20&postcode=rm94xu&advertising-location=at_cars&fromsra")
    auto_scraper.close()
