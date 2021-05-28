"""Sets up the app for flask and the required information."""
from flask import Flask
from flask_caching import Cache
import pyrebase
import os
import os.path as osp
from flask_cachecontrol import FlaskCacheControl

app = Flask(__name__)

cache_dir = osp.join(os.getcwd(), "cache")
if osp.exists(cache_dir):
    cache_dir = cache_dir
else:
    cache_dir = os.getcwd()
config = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DEFAULT_TIMEOUT": 3000,
    "CACHE_DIR": cache_dir,
    "SEND_FILE_MAX_AGE_DEFAULT": 10800,
}
app.config.from_mapping(config)
cache = Cache(app)
flask_cache_control = FlaskCacheControl(app)

config = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": None,
    "projectId": "warframe-metrics",
    "storageBucket": "warframe-metrics.appspot.com",
    "databaseURL": None,
    "serviceAccount": os.environ.get("FIREBASE_CREDENTIALS", "acc.json"),
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
w_secret = os.environ.get("WEBHOOK_SECRET")

import src.views
