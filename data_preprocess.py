import requests
import pandas as pd

def fetch_precip(lat, lng, date):
    try:
        data = requests.get(
        "https://archive-api.open-meteo.com/v1/archive?latitude=" + str(lat) + 
        "&longitude=" + str(lng) + "&start_date=" + date + 
        "&end_date=" + date + "&hourly=precipitation&models=best_match")
        precip = data.json().precipitation
        return sum(precip)/len(precip)
    except:
        return 0

def csv_to_dict(filename):
    with open(filename) as f:
        csv_list = [[val.strip() for val in r.split(",")] for r in f.readlines()]

    (_, *header), *data = csv_list
    csv_dict = {}
    for row in data:
        key, *values = row
        csv_dict[key] = {key: value for key, value in zip(header, values)}
    return csv_dict

circuits = csv_to_dict('data/circuits.csv') # used to fetch lat and lng for race
races = csv_to_dict('data/races.csv') # used to fetch date

final_results = {}

curr_results = csv_to_dict('data/results-driver-changes.csv')

for line in curr_results.values():
    if line['raceId'] not in final_results:
        final_results[line['raceId']] = []
    



print(fetch_precip(circuits['5']['lat'], circuits['5']['lng'], "2009-03-29"))
