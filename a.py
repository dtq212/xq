from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
import geopy
import redis
from geopy import adapters
print(geopy.__version__, redis.__version__)

geolocator = Nominatim(user_agent = "myGeocodeApp_v1")