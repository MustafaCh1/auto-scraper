from autotraderScraper import auto_scrape
import pandas as pd
import pickle  
import gzip
import sklearn


class price_predict:

    def __init__(self):
        with gzip.open('RF.sav.gz', 'rb') as file:
            self.rf_pipeline = pickle.load(file)

    def create_data(self):
        limits = [0, 7500, 14000, 22500, 2000000]

        auto_scraper = auto_scrape("https://www.autotrader.co.uk", "rm94xu")
        auto_scraper.start()


        price_from = 0
        price_to = 7500
        cars_to_add = []

        for i in range(4):
            for j in range(1, 75):
                auto_scraper.scrape_listings_page(j, f"https://www.autotrader.co.uk/car-search?postcode=rm94xu&price-from={limits[i] + 1}&price-to={limits[i + 1]}")


        for car in auto_scraper.car_links:
            try:
                data = auto_scraper.scrape_car_page(car)
                if data:
                    cars_dict = {}
                    cars_dict['make'] = data['advertTrackingData']['vehicleContext']['standardMake']
                    cars_dict['model'] = data['advertTrackingData']['vehicleContext']['standardModel']
                    cars_dict['variant'] = data['heading']['subTitle']
                    cars_dict['description'] = data['description']['text']
                    for spec in data['keySpecification']:
                        cars_dict[spec['label']] = spec['value']
                    if len(data['specs']) > 0:
                        for perfSpec in data['specs'][0]['items']:
                            cars_dict[perfSpec['name']] = perfSpec['value']
                    if 'runningCostsV2' in data:
                        cars_dict['insuranceGroup'] = next((item['value'] for item in data['runningCostsV2']['items'] if item['label'] == 'Insurance group'), "50U")
                    numOfFeatures = 0
                    if 'featuresWithDisclaimer' in data:
                        for featureTitle in data['featuresWithDisclaimer']['features']:
                            for feature in featureTitle['items']:
                                numOfFeatures += len(feature)
                    cars_dict['numOfFeatures'] = numOfFeatures
                    cars_dict['price'] = data['heading']['priceBreakdown']['price']['price']
                    cars_to_add.append(cars_dict)


            except Exception as e:
                print(f"Error scraping car page: {car}, Error: {e}")


        auto_scraper.close()

        df = pd.DataFrame(cars_to_add)
        df.to_csv("new_priceDB.csv", index=False)


    def dropcols(self, d):
        d.drop(columns=[ 'Number of keys', 'description','0-62mph', 'Service history',
                'Wheelbase', 'Minimum kerb weight', 'Range', 'Manufacturer warranty',
                'Driver position', 'variant', '0-60mph', 'Owners', 'Engine torque', 'Cylinders', 'Valves', 'model', 
                'Miles per gallon', 'Doors'], inplace=True, errors='ignore')
        d.dropna(inplace=True)
        return d

    def car_feng(self, car_df):
        car = car_df.copy()
        car['Mileage'] = car_df['Mileage'].str.replace(',', '').str.extract('(\d+)').astype(int)
        car.drop(columns=['Fuel type', 'Emission class'], inplace=True, errors='ignore')
        car['Age'] = 2025 - car_df['Registration'].str.split(" ").str[0].astype(int)
        car.drop(columns=['Registration'], inplace=True, errors='ignore')
        car['Engine'] = car_df['Engine'].str[:-1].astype(float)
        car['Top speed'] = car_df['Top speed'].str[:-3].astype(int)
        car['insuranceGroup'] = car_df['insuranceGroup'].str[:-1].astype(int)
        car['Engine power'] = car_df['Engine power'].str.replace(',', '').str[:-3].astype(int)
        car['Body colour'] = car_df['Body colour'].isin(['Black', 'White', 'Silver', 'Grey']).astype(int)
        car['Seats'] = car_df['Seats'].apply(lambda x: 1 if int(x) > 2 else 0)
        car.dropna(inplace=True)
        return car


    def create_car_df(self,data):
        try:
            if data:
                cars_dict = {}
                cars_dict['make'] = data['advertTrackingData']['vehicleContext']['standardMake']
                cars_dict['model'] = data['advertTrackingData']['vehicleContext']['standardModel']
                cars_dict['variant'] = data['heading']['subTitle']
                cars_dict['description'] = data['description']['text']
                for spec in data['keySpecification']:
                    cars_dict[spec['label']] = spec['value']
                if len(data['specs']) > 0:
                    for perfSpec in data['specs'][0]['items']:
                        cars_dict[perfSpec['name']] = perfSpec['value']
                if 'runningCostsV2' in data:
                    cars_dict['insuranceGroup'] = next((item['value'] for item in data['runningCostsV2']['items'] if item['label'] == 'Insurance group'), "50U")
                numOfFeatures = 0
                if 'featuresWithDisclaimer' in data:
                    for featureTitle in data['featuresWithDisclaimer']['features']:
                        for feature in featureTitle['items']:
                            numOfFeatures += len(feature)
                cars_dict['numOfFeatures'] = numOfFeatures
                cars_dict['price'] = data['heading']['priceBreakdown']['price']['price']
                return cars_dict

        except Exception as e:
            print(f"Error creating car DataFrame: {e}")
            return None

        return pd.DataFrame([cars_dict])


    def predict(self, car):
        car = self.create_car_df(car)
        if car is None:
            return "Prediction failed due to missing data."
        car_df = pd.DataFrame([car])
        car_df = self.dropcols(car_df)
        car_df = self.car_feng(car_df)
        return self.rf_pipeline.predict(car_df)
