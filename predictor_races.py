import csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import xgboost as xgb

source = []
target = []

with open('results_processed_drivers_all.csv', 'r') as f:
  csv_reader = csv.reader(f)
  next(csv_reader) # skip header
  for line in csv_reader:
    source.append([float(x) for x in line[:-1]])
    target.append(int(line[-1]))

rf = RandomForestClassifier()

X_train, X_test, y_train, y_test = train_test_split(source, target, test_size=0.2)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

xgb_model = xgb.XGBClassifier(objective="binary:logistic")
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)

'''for i,j in zip(y_test, y_pred):
  print(i,j)'''
print("Accuracy :", accuracy_score(y_test, y_pred))
print("Accuracy XGB:", accuracy_score(y_test, y_pred_xgb))

rf.fit(source, target)

'''
csv_file = "somefile.csv"
with open(csv_file, 'w', newline='') as f:
  writer = csv.writer(f)
  writer.writerow(['precipitation_sum','temperature_2m_max','temperature_2m_min','temperature_2m_mean','windspeed_10m_max','circuit_id','rookie_drivers','driver_swaps','return_drivers','month','finishes'])
  for line in source:
    writer.writerow(line + [rf.predict([line])[0]])
'''