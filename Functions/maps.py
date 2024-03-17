import requests

def get_nearby_places(location, place_type):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "format": "json",
        "limit": 5,
        "q": f"{place_type} near {location}",
    }

    response = requests.get(base_url, params=params)
    results = response.json()

    nearby_places = []
    for place in results:
        name = place.get("display_name", "")
        lat = place.get("lat", "")
        lon = place.get("lon", "")
        nearby_places.append({"name": name, "latitude": lat, "longitude": lon})

    return nearby_places
