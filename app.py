import os

from amadeus import Client, ResponseError
from flask import Flask,request,redirect, session
from flask import render_template
import spacy

from main import utilities

app = Flask(__name__)
app.secret_key = "super secret key"

# Create an Amadeus client
amadeus = Client(
    client_id=os.environ.get("AMADEUS_API_KEY"),
    client_secret=os.environ.get("AMADEUS_API_SECRET")
)

nlp = spacy.load("en_core_web_sm")

@app.route("/")
def homepage():
    return render_template('homepage.html')

@app.route("/hotels")
def hotels():
    #response = amadeus.reference_data.locations.cities.get(keyword='chicago')
    #print (response.data)
    hotel_list = amadeus.reference_data.locations.hotels.by_city.get(cityCode='CHI',radius=15)
    print("Hotels",hotel_list.data)
    return render_template('hotel_search_results.html',hotel_location = session['hotel_location'])

@app.route("/search", methods=['GET','POST'])
def search():
    # Get the input text from the form
    query = request.form['query']

    doc = nlp(query)
    
    locations = []
    date_string = None
    error = None
    
    for ent in doc.ents:
        if ent.label_ == "GPE": 
            locations.append(ent.text)
        elif ent.label_ == "DATE":
            date_string = ent.text

    #If no dates are found, return error
    if not date_string:
        error = "No dates provided in query '%s'" % query
        return render_template('homepage.html', error=error)

    dates = utilities.parse_dates(date_string)

    #If no location is found, return error
    if len(locations) == 0:
        #return "Error: No location found"   
        pass
    #If location contains only one value, go to hotels page
    elif len(locations) == 1:
        session['hotel_location'] = locations[0]
        session['dates'] = dates
        return redirect("/hotels")
    #If location contains more than one value, go to flights page
    elif len(locations) > 1:
        #return redirect("/flights?location=" + "+".join(location))
        pass
    
    print("Location:", locations)
    print("Dates:", dates)

    return "nlp"
