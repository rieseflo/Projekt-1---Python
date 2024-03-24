# cd backend
# python -m flask --debug --app service run

import datetime
import os
import pickle
from pathlib import Path

import pandas as pd
from azure.storage.blob import BlobServiceClient
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# init app, load model from storage
print("*** Init and load model ***")
if 'AZURE_STORAGE_CONNECTION_STRING' in os.environ:
    azureStorageConnectionString = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    blob_service_client = BlobServiceClient.from_connection_string(azureStorageConnectionString)

    print("fetching blob containers...")
    containers = blob_service_client.list_containers(include_metadata=True)
    for container in containers:
        existingContainerName = container['name']
        print("checking container " + existingContainerName)
        if existingContainerName.startswith("carprice-"):
            parts = existingContainerName.split("-")
            print(parts)
            suffix = 1
            if (len(parts) == 3):
                newSuffix = int(parts[-1])
                if (newSuffix > suffix):
                    suffix = newSuffix

    container_client = blob_service_client.get_container_client("carprice-" + str(suffix))
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)

    # Download the blob to a local file
    Path("../model").mkdir(parents=True, exist_ok=True)
    download_file_path = os.path.join("../model", "GradientBoostingRegressor.pkl")
    print("\nDownloading blob to \n\t" + download_file_path)

    with open(file=download_file_path, mode="wb") as download_file:
         download_file.write(container_client.download_blob(blob.name).readall())

else:
    print("CANNOT ACCESS AZURE BLOB STORAGE - Please set connection string as env variable")
    print(os.environ)
    print("AZURE_STORAGE_CONNECTION_STRING not set")    

file_path = Path(".", "../model/", "GradientBoostingRegressor.pkl")
with open(file_path, 'rb') as fid:
    model = pickle.load(fid)

print("*** Init Flask App ***")
app = Flask(__name__)
cors = CORS(app)
app = Flask(__name__, static_url_path='/', static_folder='../frontend/build')

@app.route("/")
def indexPage():
     return send_file("../frontend/build/index.html")  

@app.route("/api/predict")
def predict():
    # Retrieve parameters from the request query string
    zip_code = request.args.get('zip_code', default=-1, type=int)
    km = request.args.get('km', default=-1, type=int)
    first_registration = request.args.get('first_registration', default=-1, type=int)
    aufbau = request.args.get('aufbau', default=-1, type=int) 
    marke = request.args.get('marke', default=-1, type=int)   
    modell = request.args.get('modell', default=-1, type=int) 
    türen = request.args.get('türen', default=-1, type=int)    
    farbe = request.args.get('farbe', default=-1, type=int)    
    treibstoff = request.args.get('treibstoff', default=-1, type=int) 
    getriebeart = request.args.get('getriebeart', default=-1, type=int)  
    leistung = request.args.get('leistung', default=-1, type=int)  
    
    # Create input data for prediction
    input_data = [[zip_code, km, first_registration, türen, leistung, aufbau, marke, modell, farbe, treibstoff, getriebeart]]
    df = pd.DataFrame(columns=['zip', 'km', 'first_registration', 'türen', 'leistung', 'aufbau_encoded', 'marke_encoded', 'modell_encoded', 'farbe_encoded', 'treibstoff_encoded', 'getriebeart_encoded'], data=input_data)
    
    # Predict car price using the loaded model
    predicted_price = model.predict(df)
    
    # Prepare response
    response = {'Price': predicted_price[0]}
    
    return jsonify(response)

