import requests
def askPrice(oil_type):

    CARBURATOR_API_URL = "http://carburator.fr/api/"
    longitude = 4.879310
    latitude = 45.769100
    station_data = requests.get(CARBURATOR_API_URL+'stations/lon/'+str(longitude)+'/lat/'+str(latitude)+'?limit=1').json()

    oil_types = ['gasoline','diesel']
    if oil_type not in oil_types:
        oil_type = None
    if oil_type is None:
        return "Error: no oil type was specified."
    else:
        try:
            prices = station_data[0]['prices']
            #print(prices)
            if oil_type == 'gasoline':
                price = prices['2']['value']
            else:
                price = prices['1']['value']
        except Exception as error:
            return "Error: " + str(error)
    return "The " + str(oil_type) + ' is currently at ' + price + ' euros per liter.'

print(askPrice('gasoline'))
print(askPrice('diesel'))
print(askPrice('unknown'))
