# new terminal
# cd model
# python model.py -u 'mongodb+srv://<user>:<password>@carpricemongodb.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000' -d 'tracks' -c 'tracks'

# _________________________________________________________________________________________________
# Data preprocessing
# _________________________________________________________________________________________________

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

# Drop '_id' columns from the DataFrame
df.drop(columns=['_id'], inplace=True)

# info about the DataFrame
print(df.info())

# Handle missing values
df.replace('', np.nan, inplace=True)
print(df.isnull().sum())

# Drop rows with NaN values in, 'km' and 'first_registration' columns
df.dropna(subset=['km', 'first_registration', 'aufbau', 'marke', 'modell', 'türen', 'farbe', 'treibstoff', 'getriebeart', 'leistung'], inplace=True)
print(df.isnull().sum())

# Change data types
df['price'] = df['price'].astype(float)
df['zip'] = df['zip'].astype(int)
df['km'] = df['km'].astype(int)
df['first_registration'] = df['first_registration'].astype(int)
df['aufbau'] = df['aufbau'].astype('category')
df['marke'] = df['marke'].astype('category')
df['modell'] = df['modell'].astype('category')
df['türen'] = df['türen'].astype(int)
df['farbe'] = df['farbe'].astype('category')
df['treibstoff'] = df['treibstoff'].astype('category')
df['getriebeart'] = df['getriebeart'].astype('category')
df['leistung'] = df['leistung'].astype(int)

# info about the DataFrame
print(df.info())
print(df.head())

# Label Encoding
from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()
df['aufbau_encoded'] = label_encoder.fit_transform(df['aufbau'])
df['marke_encoded'] = label_encoder.fit_transform(df['marke'])
df['modell_encoded'] = label_encoder.fit_transform(df['modell'])
df['farbe_encoded'] = label_encoder.fit_transform(df['farbe'])
df['treibstoff_encoded'] = label_encoder.fit_transform(df['treibstoff'])
df['getriebeart_encoded'] = label_encoder.fit_transform(df['getriebeart'])

# Print the updated DataFrame info and look at its first few rows
print(df.info())
print(df.head())

# Dictionary to store mappings for all columns
all_mappings = {}

# Perform label encoding for each column and store mappings
for column in ['aufbau', 'marke', 'modell', 'farbe', 'treibstoff', 'getriebeart']:
    encoded_column = column + '_encoded'
    df[encoded_column] = label_encoder.fit_transform(df[column])
    mappings = dict(zip(df[encoded_column], df[column]))
    all_mappings[column] = mappings

# Drop specified columns from the DataFrame
columns_to_remove = ['aufbau', 'marke', 'modell', 'farbe', 'treibstoff', 'getriebeart']
df.drop(columns=columns_to_remove, inplace=True)

# Print mappings for all columns
for column, mappings in all_mappings.items():
    print(f"{column.capitalize()} mappings:")
    for encoded_value, original_label in mappings.items():
        print(f"{encoded_value}: {original_label}")
    print()

# Iterate over each column
for column in df.columns:
    # Check if the column is categorical
    if df[column].dtype.name == 'category':
        continue  # Skip categorical columns

    # Calculate mean and standard deviation
    mean = df[column].mean()
    std_dev = df[column].std()

    # Define threshold for outliers (e.g., 3 standard deviations away from the mean)
    threshold = 3 * std_dev

    # Identify outliers
    outliers = df[(df[column] > mean + threshold) | (df[column] < mean - threshold)]

    # Print or visualize the outliers
    print(f"Outliers within '{column}':")
    print(outliers)

    # Remove outliers
    df = df.drop(outliers.index)

    # Confirm the removal of outliers
    print("DataFrame after removing outliers:")
    print(df.info())

corr = df.corr(numeric_only=True)
print(corr)

plt.figure(figsize=(10, 8))
sn.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix Heatmap')
plt.show()

# _________________________________________________________________________________________________
# Model
# _________________________________________________________________________________________________

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Splitting data into features and target variable
X = df.drop(columns=['price'])
y = df['price']

# Splitting the dataset into the Training set and Test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training and evaluation
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest Regression": RandomForestRegressor(),
    "Gradient Boosting Regression": GradientBoostingRegressor(),
    "SVR": SVR(),
    "KNN": KNeighborsRegressor()
}

for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"{name} MSE: {mse}")
    print(f"{name} R2 Score: {r2}")
    
# Gradient boosting regression has the highest r2 score and lowest mse and is therefore chosen for the demo
y_pred_gbr = models["Gradient Boosting Regression"].predict(X_test)

# Evaluate the model
r2_gbr = r2_score(y_test, y_pred_gbr)
mse_gbr = mean_squared_error(y_test, y_pred_gbr)

print("Gradient Boosting Regression Model:")
print("r2:\t{}\nMSE: \t{}".format(r2_gbr, mse_gbr))

# _________________________________________________________________________________________________
# Demo
# _________________________________________________________________________________________________

print("*** DEMO ***")
# write -1 for variables that are not known 
zip_code_demo = 9524
km_demo = 49000
first_registration_demo = 2020
aufbau_demo = 4 # 1:Coupé,3:Limousine,2:Kombi,4:SUV,0:Cabriolet / Sport,6:Van / Kleinbus,5:Sonstige
marke_demo = 31 # 0:Alfa Romeo,1:Aston Martin,2:Audi,3:Austin,4:BMW,5:CUPRA,6:Cadillac,7:Chevrolet,8:Chrysler,9:Citroën,10:DS AUTOMOBILES,11:Dacia,12:Daihatsu,13:Dodge,14:Fiat,15:Ford,16:Honda,17:Hyundai,18:Jaguar,19:Jeep,20:Kia,21:Lada,22:Lancia,23:Land Rover,24:Lexus,25:Lotus,26:MINI,27:Maserati,28:Mazda,29:Mercedes-Benz,30:Mini,31:Mitsubishi,32:Nissan,33:Opel,34:Peugeot,35:Pontiac,36:Porsche,37:Renault,38:Rover,39:SEAT,40:Saab,41:Skoda,42:Smart,43:SsangYong,44:Subaru,45:Suzuki,46:Tesla,47:Toyota,48:Volkswagen,49:Volvo      
modell_demo = -1 # 0:1-serien,1:107,2:108,3:1100,4:116,5:118,6:120,7:124,8:125,9:135,10:147,11:156,12:159,13:164,14:180,15:190,16:1serien,17:2,18:200,19:2008,20:206,21:207,22:208,23:218,24:220,25:240,26:25,27:3,28:3-serien,29:300,30:300-serien,31:3008,32:306,33:307,34:308,35:309,36:316,37:318,38:320,39:323,40:325,41:328,42:33,43:330,44:335,45:350,46:350Z,47:370Z,48:3serien,49:4008,50:406,51:407,52:420,53:435,54:5,55:5-serien,56:500,57:5008,58:500L,59:500X,60:508,61:520,62:523,63:525,64:528,65:530,66:535,67:540,68:550,69:5serien,70:6,71:600,72:645,73:695 ABARTH,74:6serien,75:730,76:75,77:750,78:780Bertone,79:7serien,80:80,81:807,82:9-3,83:90,84:900,85:9000,86:911,87:93,88:940,89:95,90:960,91:A 250,92:A-CLASS,93:A1,94:A3,95:A4,96:A5,97:A6,98:A7,99:A8,100:ACLASS,101:ADAM,102:AMG,103:ASX,104:ATECA,105:Accent,106:Accord,107:Agila,108:Alfetta,109:Alhambra,110:Altea,111:AlteaXL,112:Alto,113:Amarok,114:Amazon,115:Antara,116:Astra,117:Atos,118:Auris,119:Avensis,120:Aveo,121:Aygo,122:B-CLASS,123:B-MAX,124:B250,125:Baleno,126:Berlingo,127:Barchetta,128:Beetle,129:Berlingo,130:Bipper,131:Biturbo,132:Bora,133:Boxer,134:Boxster,135:Bravo,136:C1,137:C-HR,138:C3,139:C30,140:C4,141:C5,142:C70,143:C8,144:CL,145:CABRIO,146:CAPTUR,147:CCLASS,148:CJ,149:CLA 250,150:CLS,151:CLK,152:CLS,153:CL,154:CMAX,155:COUNTRYMAN,156:COUPÉ,157:CR-V,158:CRV,159:CRX,160:CT,161:CTS,162:CX-7,163:CX7,164:Caddy,165:Caliber,166:Camaro,167:Caprice,168:Captiva,169:Carens,170:Carisma,171:Carnival,172:Cayenne,173:Cayman,174:Cee'd,175:Ceed,176:Celica,177:Cerato,178:Challenger,179:Cherokee,180:Citan,181:Civic,182:Clio,183:Clubman,184:Colt,185:Combo,186:Compass,187:Cooper,188:CooperS,189:Cordoba,190:Corolla,191:CorolVerso,192:Corsa,193:Corvette,194:Countryman,195:Coupe,196:Croma,197:Crossfire,198:Cruze,199:DISCOVERY SPORT,200:DOKKER,201:DS3,202:DS4,203:DS5,204:Db9,205:Defender,206:Delta,207:Demio,208:Discovery,209:Ducato,210:Durango,211:Duster,212:E-CLASS,213:ECLASS,214:EDGE,215:Eos,216:Epica,217:Escalade,218:Espace,219:Esprit,220:Evoque,221:Exeo,222:Expert,223:Explorer,224:F-PACE,225:FORMENTOR,226:FRV,227:Fabia,228:Feroza,229:Fiesta,230:Firebird,231:Flavia,232:Focus,233:Forester,234:Forfour,235:Fortwo,236:Fox,237:Freelander,238:Freemont,239:Fusion,240:G-CLASS,241:GCLASS,242:GL,243:GLC 250,244:GT,245:GT86,246:GTI,247:Galant,248:Galaxie,249:Galaxy,250:Getz,251:Ghibli,252:Giulietta,253:Golf,254:Grand Cherokee,255:GrandCherokee,256:GrandePunto,257:H1,258:Hiace,259:Hilux,260:I10,261:I20,262:I30,263:I40,264:IQ,265:IS,266:Ibiza,267:Ignis,268:Impreza,269:Insignia,270:Ix35,271:Ix55,272:JCW,273:Jazz,274:Jetta,275:Jimny,276:Juke,277:Jumpy,278:Justy,279:KADJAR,280:KAMIQ,281:KODIAQ,282:Ka,283:Kalos,284:Kangoo,285:Koleos,286:Korando,287:Kuga,288:L200,289:L300,290:Lacetti,291:Laguna,292:Lancer,293:LandCruiserserien,294:LeBaron,295:Leaf,296:Legacy/Outback,297:LegacyOutback,298:Leon,299:Lodgy,300:Logo,301:Logan,302:Lupo,303:M,304:M235,305:M5,306:M550,307:M6,308:MINI,309:MKII,310:ML,311:MODEL 3,312:MR2,313:MX-5,314:MX3,315:MX5,316:Master,317:Matiz,318:M
türen_demo = 5              
farbe_demo = 3 # 0:Blau,1:Braun,2:Gelb,3:Grau,4:Grün,5:Rot,6:Schwarz,7:Silber,8:Sonstiges,9:Weiss        
treibstoff_demo = 2 # 0:Benzin,1:Diesel,2:Eco / Hybrid
getriebeart_demo = 0 # 0:Automat,1:Schaltgetriebe
leistung_demo = 220          

print("Zip Code: " + str(zip_code_demo))
print("Distance (km): " + str(km_demo))
print("First Registration Year: " + str(first_registration_demo))
print("Body Type: " + str(aufbau_demo))
print("Brand: " + str(marke_demo))
print("Model: " + str(modell_demo))
print("Number of Doors: " + str(türen_demo))
print("Color: " + str(farbe_demo))
print("Fuel Type: " + str(treibstoff_demo))
print("Transmission: " + str(getriebeart_demo))
print("Power: " + str(leistung_demo))

# Encode demo input features
demo_input = [[zip_code_demo, km_demo, first_registration_demo, aufbau_demo, marke_demo, modell_demo, türen_demo, farbe_demo, treibstoff_demo, getriebeart_demo, leistung_demo]]
demo_df = pd.DataFrame(columns=['zip', 'km', 'first_registration', 'aufbau', 'marke', 'modell', 'türen', 'farbe', 'treibstoff', 'getriebeart', 'leistung'], data=demo_input)
# Replace missing values with a placeholder
demo_df.fillna(-1, inplace=True)

# Encode categorical features in demo data
demo_df['aufbau'] = demo_df['aufbau'].astype('category')
demo_df['marke'] = demo_df['marke'].astype('category')
demo_df['modell'] = demo_df['modell'].astype('category')
demo_df['farbe'] = demo_df['farbe'].astype('category')
demo_df['treibstoff'] = demo_df['treibstoff'].astype('category')
demo_df['getriebeart'] = demo_df['getriebeart'].astype('category')

# Apply label encoding to categorical features
demo_df['aufbau_encoded'] = label_encoder.fit_transform(demo_df['aufbau'])
demo_df['marke_encoded'] = label_encoder.fit_transform(demo_df['marke'])
demo_df['modell_encoded'] = label_encoder.fit_transform(demo_df['modell'])
demo_df['farbe_encoded'] = label_encoder.fit_transform(demo_df['farbe'])
demo_df['treibstoff_encoded'] = label_encoder.fit_transform(demo_df['treibstoff'])
demo_df['getriebeart_encoded'] = label_encoder.fit_transform(demo_df['getriebeart'])

# Drop original categorical columns from demo data
demo_df.drop(columns=['aufbau', 'marke', 'modell', 'farbe', 'treibstoff', 'getriebeart'], inplace=True)

# Predict using the Random Forest Regressor
demo_output_gbr = models["Gradient Boosting Regression"].predict(demo_df)
predicted_price_gbr = round(demo_output_gbr[0], 2)

print("Predicted Price using Gradient Boosting Regression: " + str(predicted_price_gbr))

# Save To Disk
import pickle

# save the classifier
with open('GradientBoostingRegressor.pkl', 'wb') as fid:
    pickle.dump(models["Gradient Boosting Regression"], fid)
    
# load it again
with open('GradientBoostingRegressor.pkl', 'rb') as fid:
    gbr_loaded = pickle.load(fid)