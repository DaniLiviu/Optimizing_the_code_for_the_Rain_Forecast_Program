import requests
import datetime
import json
import geocoder

# Define constants
API_URL = "https://api.open-meteo.com/v1/forecast"
weather_cache_file = 'weather_data.txt'

# Custom User-Agent header for geocoding
headers = {
    'User-Agent': 'Weather App (example@example.com)'  # Use a real app name and contact email
}

# Define the WeatherForecast class
class WeatherForecast:
    def __init__(self):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data.get(key, None)

    def __iter__(self):
        return iter(self.data)

    def items(self):
        return ((key, value) for key, value in self.data.items())

# Create a WeatherForecast object to manage cached data
weather_forecast = WeatherForecast()

# Load cached data from the file if it exists
try:
    with open(weather_cache_file, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            date = list(data.keys())[0]
            weather_forecast[date] = data[date]
except FileNotFoundError:
    pass


def get_lat_lon(city_name=None):
    if city_name:
        # Geocode with custom User-Agent header
        g = geocoder.osm(city_name, headers=headers)
        if g.ok:
            return g.latlng
    # Default to a predefined location (e.g., London)
    return [51.5074, -0.1278]


# Weather forecast retrieval loop
while True:
    searched_date = input("Enter date (YYYY-mm-dd) or leave blank for tomorrow: ")

    if not searched_date:
        searched_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        try:
            datetime.datetime.strptime(searched_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-mm-dd format.")
            continue

    city_name = input("Enter city name or leave blank for default location: ")
    lat_lon = get_lat_lon(city_name)

    # Check if the data is already cached
    if searched_date in weather_forecast:
        weather_data = weather_forecast[searched_date]
        print("Using cached data...")
    else:
        latitude, longitude = lat_lon
        url = f"{API_URL}?latitude={latitude}&longitude={longitude}&daily=precipitation_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}"

        response = requests.get(url)

        if response.status_code == 200:
            weather_data = response.json()
            weather_forecast[searched_date] = weather_data  # Add to cache
        else:
            print("API request failed.")
            continue

    # Extract and display precipitation information
    try:
        daily_data = weather_data['daily']
        precipitation_sum = daily_data['precipitation_sum'][0]

        if precipitation_sum > 0.0:
            print(f"It will rain. Precipitation value: {precipitation_sum} mm")
        elif precipitation_sum == 0.0:
            print("It will not rain.")
        else:
            print("I don't know! (No data or negative value)")
    except KeyError:
        print("Unexpected data format.")

    # Save the data to the cache file
    with open(weather_cache_file, 'a') as f:
        f.write(json.dumps({searched_date: weather_data}) + '\n')

    # Ask the user if they want to continue
    continuation = input("Do you want to check another date (yes/no)? ").strip().lower()
    if continuation != 'yes':
        break
