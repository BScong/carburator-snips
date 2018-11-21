# Carburator Snips App
Snips app to fetch the current gas prices of the nearest gas station (currently the data is only available in France).
Based on [Snips App Template](https://github.com/snipsco/snips-app-template-py).

Calling the [Carburator API](https://github.com/BScong/carburator-backend) (one of my personal projects), which is based on French open data.


## Intents
| Intent            | Slots          | Description                                    |
|-------------------|----------------|------------------------------------------------|
| askPrice          | oil_type, city | Fetch the gas price for oil_type               |
| getServices       |                | Get possible services from last gas station    |
| getStationAddress |                | Get the address for last gas station           |
| setCity           | **city**       | Set or change city to find nearest gas station |
| setOilType        | **oil_type**   | Set or change oil type                         |

The `oil_type` slots contains `['gasoline','diesel']`. The `city` is a default (String) slot.
The slots in bold are required.

### askPrice
If `oil_type` was not set before, it triggers the `setCity` action to ask the user for it.
If `city` was not set before, it triggers the `setOilType` action to ask the user for it.

The user can also call askPrice with a `oil_type` and `city`, but those won't be saved (for example, an user can ask the price for another oil type without re-setting its preferences).

The askPrice action is calling the [Carburator API](https://github.com/BScong/carburator-backend).
It fetches the nearest gas station and tries to fetch the price for the corresponding saved `oil_type`.

### getServices
The getServices action is calling the [Carburator API](https://github.com/BScong/carburator-backend).
It fetches the nearest gas station and tries to list the different services from this station.

### getStationAddress
The getServices action is calling the [Carburator API](https://github.com/BScong/carburator-backend).
It fetches the nearest gas station and returns the station address.

### setCity
Set the city for the current user. The slot is required.
The location is converted to longitude/latitude by calling the [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/intro). A Google Maps API key is required (set in `config.ini` or asked when the app is deployed). We use the [Google Maps Python library](https://github.com/googlemaps/google-maps-services-python).

### setOilType
Set the oil type for the current user. The slot is required.

## Examples


## Todo list and improvements
 - ✓ Return gas price for an oil_type and location (hardcoded then user based)
 - ✓ Ask the user for its location (and convert it to longitude/latitude)
 - ✓ Save preferences for user (oil_type, location)
 - ✓ Being able to ask for the gas station precise address (provided by API)
 - X Being able to ask for the gas station opening hours (provided by API / Update: not provided anymore by API)
 - ✓ Being able to ask for the gas station services (provided by API)
 - Add custom slot type for French Cities for setCity intent
 - Maybe convert setCity intent to setAddress to be more precise and accurate?
 - Add analytics
