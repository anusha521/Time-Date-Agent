from google.adk.agents.llm_agent import Agent
from datetime import datetime
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Initialize helpers
geolocator = Nominatim(user_agent="global_time_agent")
tf = TimezoneFinder()

def get_current_time(location: str) -> dict:
    """
    Returns the current local time in any country or city worldwide.
    Example: 'India', 'France', 'New York', 'Tokyo', etc.
    """
    if not location or not location.strip():
        return {"status": "error", "message": "Please provide a location."}

    try:
        # Step 1: Geocode location -> latitude & longitude
        geocode_result = geolocator.geocode(location, timeout=10)
        if not geocode_result:
            return {"status": "error", "message": f"Could not find location: {location}"}

        lat, lon = geocode_result.latitude, geocode_result.longitude

        # Step 2: Find timezone name
        timezone_name = tf.timezone_at(lat=lat, lng=lon)
        if not timezone_name:
            return {"status": "error", "message": f"Could not find timezone for {location}"}

        # Step 3: Get current time in that timezone
        tz = ZoneInfo(timezone_name)
        current_time = datetime.now(tz)
        formatted_time = current_time.strftime("%Y-%m-%d %I:%M:%S %p")

        return {
            "status": "success",
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "timezone": timezone_name,
            "current_time": formatted_time
        }

    except (GeocoderTimedOut, GeocoderServiceError):
        return {"status": "error", "message": "Geocoding service unavailable. Try again later."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Create the agent
root_agent = Agent(
    model="gemini-2.5-flash",
    name="global_time_agent",
    description="Tells the current time anywhere in the world.",
    instruction="You are a helpful assistant that provides the local time for any country or city using the get_current_time tool.",
    tools=[get_current_time],
)
