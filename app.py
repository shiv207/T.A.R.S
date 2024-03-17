from gpt4all import GPT4All
from os import system
import warnings
import wikipedia
from Functions.weather import get_weather
from Functions.Email import generate_email_draft
from Functions.maps import get_nearby_places
from Functions.recipe import get_random_recipe
from Functions.albums import get_top_songs
from googlesearch import search
from bs4 import BeautifulSoup
from summarizer import Summarizer
from googletrans import Translator
import re
import requests
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

model = GPT4All("/Users/shivamshsr/Desktop/TARS/Models/T.A.R.S.gguf", allow_download=False)
listening_for_prompt = True
counter = 0  # Initialize the counter

def extract_location(prompt_text):
    # Use a simple regex to find words that might represent locations
    matches = re.findall(r'\b(?:city|town|location|in)\s+([A-Za-z]+)\b', prompt_text, flags=re.IGNORECASE)
    return matches[0] if matches else None

def speak(text):
    ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
    clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
    st.write(f"Ultron : {text}")
    system(f"say '{clean_text}'")

def perform_web_search(query):
    search_results = google_search(query)
    if search_results:
        best_result_url = search_results[0]

        page_content = get_page_content(best_result_url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            visible_text = soup.get_text()

            summary = summarize_text(visible_text)
            st.write("\nSummary:")
            speak(summary)
    else:
        st.write("No search results found.")

def prompt_gpt(prompt_text):
    global listening_for_prompt, counter
    try:
        if len(prompt_text) == 0:
            speak("Empty prompt. Please speak again.")
            listening_for_prompt = True

        elif "weather" in prompt_text.lower():
            location = extract_location(prompt_text)
            if location:
                weather_info = get_weather(location)
                st.write(f"ULTRON (Weather 🌏) in {location.capitalize()}:", weather_info)
                speak(weather_info)
            else:
                st.write("ULTRON: Unable to identify the location in the prompt.")

        elif "wikipedia" in prompt_text.lower():
            search_query = prompt_text.replace("wikipedia", "").strip()
            wikipedia_info = wikipedia.summary(search_query, sentences=3)

            # Check if the user is asking for images
            if "images" in prompt_text.lower() or "pictures" in prompt_text.lower():
                # Perform image search on Wikipedia
                image_results = wikipedia.page(search_query).images
                if image_results:
                    st.image(image_results[0], caption="Image from Wikipedia", use_column_width=True)

            st.write("ULTRON (Wikipedia 📖):", wikipedia_info)
            speak(wikipedia_info)

        elif "search the web" in prompt_text.lower() or "search the internet" in prompt_text.lower():
            search_query = prompt_text.replace("web browsing", "").strip()
            
            # Check if the user is asking for images
            if "images" in prompt_text.lower() or "pictures" in prompt_text.lower():
                # Perform image search on the web
                image_results = perform_web_image_search(search_query)
                if image_results:
                    st.image(image_results[0], caption="Image from the web", use_column_width=True)

            # Perform a regular web search
            else:
                perform_web_search(search_query)


        elif "email" in prompt_text.lower() and "letter" in prompt_text.lower():
            # Generate email draft using the separate module
            draft_email = generate_email_draft(prompt_text)

            if draft_email:
                st.write("Here's a draft email for your review 🍻:")
                st.write(draft_email)
                st.write("**Note:** This feature only generates email drafts. It cannot send emails.")
            else:
                st.write("Couldn't generate an email draft based on your prompt.")

        elif "nearby places" in prompt_text.lower() and "find places" in prompt_text.lower():
            user_location = input("Enter your current location 📍: ")
            place_type = input("Enter the type of place you're looking for (e.g., restaurant, landmark): ")
            nearby_places = get_nearby_places(user_location, place_type)
            st.write(f"Nearby {place_type}s:")
            for index, place in enumerate(nearby_places, start=1):
                st.write(f"{index}. {place['name']} (Latitude: {place['latitude']}, Longitude: {place['longitude']})")
                speak(f"{place['name']} is nearby.")

        else:
            st.write('User:', prompt_text)
            output = model.generate(prompt_text, max_tokens=250)
            speak(output)

        st.write('\nYou can enter a new prompt. \n')
        listening_for_prompt = True
        counter += 1

    except Exception as e:
        st.write("Prompt error 🥊: ", e)

def perform_web_image_search(query, num_results=1):
    # Perform image search on the web and return the results
    search_results = google_search(query, num_results=num_results, image_search=True)
    return search_results

# Modify the google_search function to handle image search
def google_search(query, num_results=5, image_search=False):
    search_results = list(search(query, num_results=num_results))
    
    # Filter image search results
    if image_search:
        search_results = [result for result in search_results if result.endswith(('.jpg', '.jpeg', '.png'))]

    return search_results

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.write(f"Error fetching page content: {e}")
        return None

def summarize_text(text):
    summarizer = Summarizer()
    summary = summarizer(text, min_length=50, max_length=200)
    return summary

def is_recipe_widget_open():
    # Use a session state variable to track the widget's state
    if 'recipe_widget_open' not in st.session_state:
        st.session_state['recipe_widget_open'] = False
    return st.session_state['recipe_widget_open']

def toggle_recipe_widget():
    st.session_state['recipe_widget_open'] = not st.session_state['recipe_widget_open']

# Streamlit app
def app():
    st.set_page_config(page_title="Ultron ✨", page_icon="🌌")

    # Load custom CSS from external file (assuming style.css exists)
    with open("style.css") as f:
        st.sidebar.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Sidebar with macOS-style widgets
    st.sidebar.title("Widgets ⚙️")

    # Weather widget
    st.sidebar.header("Weather Widget ☁️")
    location = st.sidebar.text_input("Enter location for weather:", "Bangalore")
    if st.sidebar.button("Get Weather"):
        weather_info = get_weather(location)
        st.sidebar.write(f"Weather in {location.capitalize()}:", weather_info)

    # Recipe widget with button to toggle visibility
    if is_recipe_widget_open():
        st.sidebar.header("Recipe of the Day 🍣")
        if st.sidebar.button("Close Recipe 🍅"):
            toggle_recipe_widget()
        else:
            recipe = get_random_recipe()
            st.sidebar.subheader(recipe["strMeal"])

            # Display rounded image with caption
            st.sidebar.image(recipe["strMealThumb"], caption=recipe["strMeal"], use_column_width=True, output_format="auto")

            st.sidebar.markdown(f"**Category:** {recipe['strCategory']}")
            st.sidebar.markdown(f"**Instructions:** {recipe['strInstructions']}")

    else:
        if st.sidebar.button("Open Recipe 🥑"):
            toggle_recipe_widget()

    # Artist Top Songs widget
    st.sidebar.header("Artist Top Songs 🎵")
    artist_name = st.sidebar.text_input("Enter artist name:")
    if st.sidebar.button("Get Top Songs"):
        get_top_songs(artist_name)

    # Language Translation widget
    st.sidebar.header("Language Translation 🌐")
    # Input text for translation
    text_to_translate = st.sidebar.text_area("Enter text for translation:", "Hello, how are you?")
    # Source language selection
    source_language = st.sidebar.selectbox("Select source language:", ["auto", "en", "es", "fr", "de", "zh-CN"])
    # Target language selection
    target_language = st.sidebar.selectbox("Select target language:", ["en", "es", "fr", "de", "zh-CN"])

    # Button to perform translation
    if st.sidebar.button("Translate"):
        try:
            translator = Translator()
            translated_text = translator.translate(text_to_translate, dest=target_language).text
            st.sidebar.write(f"Translated text: {translated_text}")
        except Exception as e:
            st.sidebar.write(f"Translation error: {e}")


    # Main content with title and prompt input
    st.title("Ultron ✨")
    prompt_text = st.text_input("You:", key=f"unique_key_{counter}")
    if st.button("Submit"):
        prompt_gpt(prompt_text)

if __name__ == "__main__":
    app()
