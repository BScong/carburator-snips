# Carburator Snips App
Snips app to fetch the current gas prices of the nearest gas station (currently the data is only available in France).
Based on [Snips App Template](https://github.com/snipsco/snips-app-template-py).

Calling the [Carburator API](https://github.com/BScong/carburator-backend) (one of my personal projects), which is based on French open data.


## Intents
| Intent   | Slots    | Description                      |
|----------|----------|----------------------------------|
| askPrice | oil_type | Fetch the gas price for oil_type |

The `oil_type` slots contains `['gasoline','diesel']`. It is a required slot.

### askPrice
The askPrice action is calling the [Carburator API](https://github.com/BScong/carburator-backend).
It fetches the nearest gas station and tries to fetch the price for the corresponding `oil_type`.

## Todo list and improvements
 - Ask the user for its location (and convert it to longitude/latitude)
 - Save preferences for user (oil_type, location)
 - Being able to ask for the gas station precise address (provided by API)
 - Being able to ask for the gas station opening hours (provided by API)
 - Being able to ask for the gas station services (provided by API)
