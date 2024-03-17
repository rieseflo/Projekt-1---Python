# new terminal
# cd spider/downloads
# python .\mongo_import.py -c tracks -i ../file.jl -u 'mongodb+srv://<user>:<password>@tuttimongodbcluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000'

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor

from pymongo import MongoClient

import gpxpy
import gpxpy.gpx
from pathlib import Path

def to_document(base_dir, item):
    try:
        doc = {
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "price": item.get("price", ""),
            "zip": item.get("zip", ""),
            "km": item.get("km", ""),
            "first_registration": item.get("first_registration", ""),
            "difficulty": ""  # Since there's no difficulty field in motorcycles.py, set it to default value
        }
        return doc
            
    except Exception as e:
        print("Error processing item:", e)
        return None

class JsonLinesImporter:

    def __init__(self, file, mongo_uri, batch_size=30, db='tracks', collection='tracks'):
        self.file = file
        self.base_dir = os.path.dirname(file)
        self.batch_size = batch_size
        self.client = MongoClient(mongo_uri)
        self.db = db
        self.collection = collection

    def read_lines(self):
            with open(self.file, encoding='UTF-8') as f:
                batch = []
                for line in f:
                    batch.append(json.loads(line))
                    if len(batch) == self.batch_size:
                        yield batch
                        batch.clear()
                yield batch

    def save_to_mongodb(self):
            db = self.client[self.db]
            collection = db[self.collection]
            for idx, batch in enumerate(self.read_lines()):
                print("inserting batch", idx)
                collection.insert_many(self.prepare_documents(batch))

    def prepare_documents(self, batch):
        documents = []
        with ProcessPoolExecutor() as executor:
            for document in executor.map(to_document, [self.base_dir] * len(batch), batch):
                if document is not None:
                    documents.append(document)
        return documents

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uri', required=True, help="mongodb uri with username/password")
    parser.add_argument('-i', '--input', required=True, help="input file in JSON Lines format")
    parser.add_argument('-c', '--collection', required=True, help="name of the mongodb collection where the tracks should be stored")
    args = parser.parse_args()
    importer = JsonLinesImporter(args.input, collection=args.collection, mongo_uri=args.uri)
    importer.save_to_mongodb()
