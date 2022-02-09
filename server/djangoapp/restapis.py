import requests
import json
# import related models here
from .models import CarMake, CarModel, CarDealer, DealerReview

from requests.auth import HTTPBasicAuth
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    #print(kwargs)
    print("GET from {} ".format(url))
    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    #response = {}
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs): 
    response = requests.post(url, json=json_payload)
    return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]
        dealers = dealers["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"], state=dealer_doc["state"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_reviews_from_cf(url, id):
    results = []
    #a= {"id":id}
    json_result = get_request(url, **{"id":id})
    if json_result:
        review_lists = json_result["docs"]
        for review_list in review_lists:
            review_doc = review_list
            sentiment = analyze_review_sentiments(review_doc["review"])
            review_obj = DealerReview(dealership=review_doc["dealership"],name=review_doc["name"],purchase=review_doc["purchase"],
                                      id=review_doc["id"],review=review_doc["review"],purchase_date=review_doc["purchase_date"],
                                      car_make=review_doc["car_make"],car_model=review_doc["car_model"],
                                      car_year=review_doc["car_year"], sentiment = sentiment)
            results.append(review_obj)
            
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    apikey = "80tBSh5QAAwJ9VvKfwcRyVgWfmldTwDLJ9GMoGIvmzzh"
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/76364bf6-31c3-4991-88be-60cdd871f728"

    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01', authenticator=authenticator)

    natural_language_understanding.set_service_url(url) 

    text=dealerreview
    response = natural_language_understanding.analyze(text=text, 
                                                  features = Features(sentiment = SentimentOptions())).get_result()
    
    #print(json.dumps(response, indent=2))
    a=response["sentiment"]
    a=a["document"]
    a=a["label"]
    
    return a


