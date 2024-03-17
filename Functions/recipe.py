# app.py
import streamlit as st
import requests

# Function to fetch a random recipe
def get_random_recipe():
    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    response = requests.get(url)
    data = response.json()
    return data["meals"][0]