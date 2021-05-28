"""Runs the flask-server for warframe-trader."""
import os

from src import app

app.secret_key = os.environ.get("APP_SECRET")