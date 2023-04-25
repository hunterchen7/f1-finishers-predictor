import requests
import csv
import pandas as pd
from datetime import datetime

fetched_weather = {}
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
        fetched_weather[date + str(lat) + str(lng)] = data.json()
        return data.json()
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
    circuitId = races[line['raceId']]['circuitId']
    lat, lng = circuits[circuitId]['lat'], circuits[circuitId]['lng']
    date = races[line['raceId']]['date']
    weather = fetch_weather(lat, lng, date)
    if line['raceId'] not in final_results:
        final_results[line['raceId']] = {
            'precipitation_sum': weather['daily']['precipitation_sum'][0],
            'temperature_2m_max': weather['daily']['temperature_2m_max'][0],
            'temperature_2m_min': weather['daily']['temperature_2m_min'][0],
            'temperature_2m_mean': weather['daily']['temperature_2m_mean'][0],
            'windspeed_10m_max': weather['daily']['windspeed_10m_max'][0],
            'circuit_id': circuitId,
            'rookie_drivers': line['rookieDrivers'],
            'driver_swaps': line['driverSwaps'],
            'return_drivers': line['returnDrivers'],
            'month': int(date.split('-')[1]),
            'results': 0,
        }
    if line['statusId'] in ['1', '11', '12', '13', '14', '15', '16', '17', '18', '19']:#['3', '4']:
        final_results[line['raceId']]['results'] += 1

try:
    with open('results_processed.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['precipitation_sum', 'temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean', 'windspeed_10m_max', 'circuit_id', 'rookie_drivers', 'driver_swaps', 'return_drivers', 'month', 'results'])
        writer.writeheader()
        for data in list(final_results.values()):
            writer.writerow(data)
except IOError:
    print("I/O error")

