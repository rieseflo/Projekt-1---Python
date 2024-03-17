# new terminal
# cd model
# python model.py -u 'mongodb+srv://<user>:<password>@tuttimongodbcluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000' -d 'tracks' -c 'tracks'

import argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sn
import numpy as np
from pymongo import MongoClient

parser = argparse.ArgumentParser(description='Import data from Azure Cosmos DB')
parser.add_argument('-u', '--uri', required=True, help="Azure Cosmos DB connection string")
parser.add_argument('-d', '--database', required=True, help="Database name")
parser.add_argument('-c', '--collection', required=True, help="Collection name")
args = parser.parse_args()

mongo_uri = args.uri
mongo_db = args.database
mongo_collection = args.collection

# Connect to Azure Cosmos DB
client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

# Fetch all documents from the collection
cursor = collection.find({})

# Convert documents to a list of dictionaries
data = list(cursor)

# Close MongoDB connection
client.close()

# Convert list of dictionaries to DataFrame
df = pd.DataFrame(data)

# Print the number of documents fetched
print("Number of documents fetched:", len(df))

# Drop '_id' and 'difficulty' columns from the DataFrame
df.drop(columns=['_id', 'difficulty'], inplace=True)

# Handle missing values
df.replace('', np.nan, inplace=True)
print(df.isnull().sum())
# Drop rows with NaN values in 'km' and 'first_registration' columns
df.dropna(subset=['km', 'first_registration'], inplace=True)
print(df.isnull().sum())

# Change data types
df['price'] = df['price'].astype(float)
df['zip'] = df['zip'].astype(int)
df['km'] = df['km'].astype(int)
df['first_registration'] = df['first_registration'].astype(int)

# info about the DataFrame
print(df.info())

corr = df.corr(numeric_only=True)

print(corr)
sn.heatmap(corr, annot=True)

# Model
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Assuming 'df' is your DataFrame and 'price' is the target variable
y = df['price']
x = df.drop(columns=['price', 'title', 'description'])  # Dropping column to use other features as predictors

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42)

# Baseline Linear Regression
lr = LinearRegression()
lr.fit(x_train, y_train)
y_pred_lr = lr.predict(x_test)
r2_lr = r2_score(y_test, y_pred_lr)
mse_lr = mean_squared_error(y_test, y_pred_lr)

print("Linear Regression:")
print("r2:\t{}\nMSE: \t{}".format(r2_lr, mse_lr))

# Gradient Boosting Regressor
gbr = GradientBoostingRegressor(n_estimators=50, random_state=9000)
gbr.fit(x_train, y_train)
y_pred_gbr = gbr.predict(x_test)
r2_gbr = r2_score(y_test, y_pred_gbr)
mse_gbr = mean_squared_error(y_test, y_pred_gbr)

print("\nGradient Boosting Regressor:")
print("r2:\t{}\nMSE: \t{}".format(r2_gbr, mse_gbr))

print("*** DEMO ***")
zip_code_demo = 9524
km_demo = 16100
first_registration_demo = 2019

print("Zip Code: " + str(zip_code_demo))
print("Distance (km): " + str(km_demo))
print("First Registration Year: " + str(first_registration_demo))

demo_input = [[zip_code_demo, km_demo, first_registration_demo]]
demo_df = pd.DataFrame(columns=['zip', 'km', 'first_registration'], data=demo_input)
demo_output = gbr.predict(demo_df)
predicted_price = round(demo_output[0], 2)

print("Predicted Price: " + str(predicted_price))