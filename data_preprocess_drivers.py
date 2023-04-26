import requests
import csv
import pandas as pd
from datetime import datetime

def csv_to_dict(filename):
    with open(filename, encoding="utf-8") as f:
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
        return [x[0] for x in data.json()['daily']]
    except:
        return 0

circuits = csv_to_dict('data/circuits.csv') # used to fetch lat and lng for race
races = csv_to_dict('data/races.csv') # used to fetch date
drivers = csv_to_dict('data/drivers.csv')

final_results = {}

# curr_results = csv_to_dict('data/results-driver-changes.csv')
curr_results = csv_to_dict('data/results.csv')

for i,line in enumerate(curr_results.values()):
    circuitId = races[line['raceId']]['circuitId']
    lat, lng = circuits[circuitId]['lat'], circuits[circuitId]['lng']
    date = races[line['raceId']]['date']
    if int(date.split('-')[0][1:]) < 2017:
        continue
    weather = fetch_weather(lat, lng, date)
    dob = drivers[line['driverId']]['dob'][1:-1]
    final_results[i] = {
        'race_id': line['raceId'],
        'precipitation_sum': weather['precipitation_sum'],
        'temperature_2m_max': weather['temperature_2m_max'],
        'temperature_2m_min': weather['temperature_2m_min'],
        'temperature_2m_mean': weather['temperature_2m_mean'],
        'windspeed_10m_max': weather['windspeed_10m_max'],
        'circuit_id': circuitId,
        #'rookie_drivers': line['rookieDrivers'],
        #'driver_swaps': line['driverSwaps'],
        #'return_drivers': line['returnDrivers'],
        'month': int(date.split('-')[1]),
        'year': int(date.split('-')[0][1:]),
        'driverId': line['driverId'],
        'grid': line['grid'],
        'driver_age': round((datetime.strptime(today, '%Y-%m-%d') - datetime.strptime(dob, '%Y-%m-%d')).days / 365.25),
        'constructor': line['constructorId'],
        'driver_count': 0,
        'results': 1 if line['statusId'] in ['1', '11', '12', '13', '14', '15', '16', '17', '18', '19'] else 0 #['3', '4'] for collisions/accidents
        #'results': 0 if line['positionText'][1:-1] in {'R', 'D', 'W'} or int(line['positionText'][1:-1]) > 3 else int(line['positionText'][1:-1])
    }

driver_count = {}
for racer in final_results:
    raceId = final_results[racer]['race_id']
    if raceId not in driver_count:
        driver_count[raceId] = 0
    driver_count[raceId] += 1

for key in final_results:
    racer = final_results[key]
    racer['driver_count'] = driver_count[racer['race_id']]
    del racer['race_id']

try:
    with open('results_processed_drivers_all.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(final_results[list(final_results.keys())[0]]))
        writer.writeheader()
        for data in list(final_results.values()):
            writer.writerow(data)
except IOError:
    print("I/O error")

