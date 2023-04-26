import requests
import csv
import pandas as pd
from datetime import datetime

def csv_to_dict(filename):
    with open(filename) as f:
        csv_list = [[val.strip() for val in r.split(",")] for r in f.readlines()]

    (_, *header), *data = csv_list
    csv_dict = {}
    for row in data:
        key, *values = row
        csv_dict[key] = {key: value for key, value in zip(header, values)}
    return csv_dict

fetched_weather = csv_to_dict('data/fetched_weather.csv')
today = datetime.today().strftime('%Y-%m-%d')

def within_last_10_days(date):
    date = datetime.strptime(date, '%Y-%m-%d')
    today = datetime.today()
    return (today - date).days < 10

def fetch_weather(lat, lng, date):
    date = date[1:-1]
    if date + str(lat) + str(lng) in fetched_weather:
        return fetched_weather[date + str(lat) + str(lng)]
    try:
        print('fetching weather for ' + date + ', lat: ' + str(lat) + ', lng: ' + str(lng))
        data = requests.get(
        ("https://api.open-meteo.com/v1/forecast" if within_last_10_days(date) else
        "https://archive-api.open-meteo.com/v1/archive?latitude=") + str(lat) + 
        "&longitude=" + str(lng) + "&start_date=" + date + 
        "&end_date=" + date + "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,windspeed_10m_max&timezone=America%2FSao_Paulo")
        fetched_weather[date + str(lat) + str(lng)] = data.json()['daily']
        with open('data/fetched_weather.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([date + str(lat) + str(lng)] + [x[0] for x in list(data.json()['daily'].values())[1:]])
        return data.json()['daily']
    except:
        return 0


circuits = csv_to_dict('data/circuits.csv') # used to fetch lat and lng for race
races = csv_to_dict('data/races.csv') # used to fetch date

final_results = {}

curr_results = csv_to_dict('data/results.csv')


for line in curr_results.values():
    circuitId = races[line['raceId']]['circuitId']
    lat, lng = circuits[circuitId]['lat'], circuits[circuitId]['lng']
    date = races[line['raceId']]['date']
    if int(date.split('-')[0][1:]) < 2000:
        continue
    weather = fetch_weather(lat, lng, date)
    if line['raceId'] not in final_results:
        final_results[line['raceId']] = {
            #'raceId': line['raceId'],
            'precipitation_sum': weather['precipitation_sum'],
            'temperature_2m_max': weather['temperature_2m_max'],
            'temperature_2m_min': weather['temperature_2m_min'],
            'temperature_2m_mean': weather['temperature_2m_mean'],
            'windspeed_10m_max': weather['windspeed_10m_max'],
            'circuit_id': circuitId,
            'year': int(date.split('-')[0][1:]),
            'month': int(date.split('-')[1]),
            'driver_count': 0,
            'results': 0,
        }
    if line['statusId'] in ['3', '4']:#['1', '11', '12', '13', '14', '15', '16', '17', '18', '19']:
        final_results[line['raceId']]['results'] += 1
    final_results[line['raceId']]['driver_count'] += 1

try:
    with open('results_processed_accidents.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(final_results.values())[0].keys())
        writer.writeheader()
        for data in list(final_results.values()):
            writer.writerow(data)
except IOError:
    print("I/O error")

