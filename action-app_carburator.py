#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import requests
import googlemaps

CONFIG_INI = "config.ini"
CARBURATOR_API_URL = "http://carburator.fr/api/"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def getLonLat(gmaps, city):
    try:
        if gmaps:
            geocode_result = gmaps.geocode(city)
            return (geocode_result[0]['geometry']['location']['lng'],geocode_result[0]['geometry']['location']['lat'])
        else:
            raise Exception('No API key specified');
    except Exception as e:
        raise e

class Carburator(object):
    """
    Class used to wrap action code with mqtt connection
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
            self.gmaps = None
            try:
                if self.config.get("secret").get("google_maps_api_key"):
                    self.gmaps = googlemaps.Client(key=self.config.get("secret").get("google_maps_api_key"))
            except Exception as e:
                print(e)
                self.gmaps = None
        except :
            self.config = None
        self.longitude = 0
        self.latitude = 0
        self.city = ''
        self.oil_type = ''

        # start listening to MQTT
        self.start_blocking()


    # --> Sub callback function, one per intent
    def setOilType_callback(self, hermes, intent_message):
        oil_types = ['gasoline','diesel']
        oil_type = None
        if intent_message.slots.oilType:
            oil_type = intent_message.slots.oilType.first().value
            # check if the category is valide
            if oil_type.encode("utf-8") not in oil_types:
                oil_type = None
            else:
                self.oil_type = oil_type.encode("utf-8")

        if oil_type is None:
            hermes.publish_start_session_notification(intent_message.site_id, "Error: no oil type was specified.", "")
            return
        hermes.publish_start_session_notification(intent_message.site_id, "Your oil is now " + self.oil_type + ".", "")

    def setCity_callback(self, hermes, intent_message):
        if intent_message.slots.city:
            try:
                city = intent_message.slots.city.first().value.encode("utf-8")
                lon, lat = getLonLat(self.gmaps, city)
                self.longitude = lon
                self.latitude = lat
                self.city = city
            except Exception as e:
                print(e)
                hermes.publish_start_session_notification(intent_message.site_id, "Error finding location", "")
                return
            hermes.publish_start_session_notification(intent_message.site_id, "Your city is now " + self.city + ".", "")

        return

    def getServices_callback(self, hermes, intent_message):
        # get location (lon lat)
        if self.city != '':
            longitude, latitude = self.longitude, self.latitude
        else:
            hermes.publish_start_session_notification(intent_message.site_id, 'Error: no location specified. Say "I live in" and then your city to specify your location.', "")
            return

        try:
            station_data = requests.get(CARBURATOR_API_URL+'stations/lon/'+str(longitude)+'/lat/'+str(latitude)+'?limit=1').json()
            list_services = []
            for service in station_data[0]['services']:
                list_services.append(service)
            services = ", ".join(list_services)
        except Exception as e:
            print(e)
            hermes.publish_start_session_notification(intent_message.site_id, "Error: impossible to find services.", "")
            return
        hermes.publish_start_session_notification(intent_message.site_id, "The services are: " + services + ".", "")


    def getStationAddress_callback(self, hermes, intent_message):
        # get location (lon lat)
        if self.city != '':
            longitude, latitude = self.longitude, self.latitude
        else:
            hermes.publish_start_session_notification(intent_message.site_id, 'Error: no location specified. Say "I live in" and then your city to specify your location.', "")
            return

        try:
            station_data = requests.get(CARBURATOR_API_URL+'stations/lon/'+str(longitude)+'/lat/'+str(latitude)+'?limit=1').json()
            address = station_data[0]['address'] + ', ' + station_data[0]['postcode'] + ', ' + station_data[0]['city']
        except Exception as e:
            print(e)
            hermes.publish_start_session_notification(intent_message.site_id, "Error: impossible to find address.", "")
            return
        hermes.publish_start_session_notification(intent_message.site_id, "The gas station is at " + address + ".", "")



    def askPrice_callback(self, hermes, intent_message):
        # Find oil type
        oil_type = None
        if intent_message.slots.oilType:
            oil_types = ['gasoline','diesel']
            oil_type = intent_message.slots.oilType.first().value
            # check if the category is valide
            if oil_type.encode("utf-8") not in oil_types:
                oil_type = None
        elif self.oil_type != '':
            oil_type = self.oil_type
        else:
            ## trigger setOilType intent
            hermes.publish_continue_session(intent_message.session_id, 'Do you want the price for Gasoline or Diesel?', ['setOilType'])


        # Find location
        longitude, latitude = 0, 0
        if intent_message.slots.city:
            try:
                city = intent_message.slots.city.first().value.encode("utf-8")
                longitude, latitude = getLonLat(self.gmaps, city)
            except:
                hermes.publish_start_session_notification(intent_message.site_id, "Error finding location", "")
                return
        elif self.city != '':
            longitude, latitude = self.longitude, self.latitude
        else:
            ## trigger setCity intent
            hermes.publish_continue_session(intent_message.session_id, 'For which place do you want the prices?', ['setCity'])

        try:
            print(CARBURATOR_API_URL+'stations/lon/'+str(longitude)+'/lat/'+str(latitude)+'?limit=1')
            station_data = requests.get(CARBURATOR_API_URL+'stations/lon/'+str(longitude)+'/lat/'+str(latitude)+'?limit=1').json()
            try:
                prices = station_data[0]['prices']
                if oil_type == 'gasoline':
                    price = prices['2']['value']
                else:
                    price = prices['1']['value']
            except Exception as error:
                hermes.publish_start_session_notification(intent_message.site_id, "Error: impossible to find gas price.", "")
                return
        except:
            hermes.publish_start_session_notification(intent_message.site_id, "Error when fetching gas data.", "")
            return

        hermes.publish_start_session_notification(intent_message.site_id, "The " + str(oil_type) + ' is currently at ' + price + ' euros per liter.', "")

        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        print('[Received] intent: '+ str(intent_message.intent.intent_name))
        if 'askPrice' in coming_intent:
            self.askPrice_callback(hermes, intent_message)
        elif 'setOilType' in coming_intent:
            self.setOilType_callback(hermes, intent_message)
        elif 'setCity' in coming_intent:
            self.setCity_callback(hermes, intent_message)
        elif 'getServices' in coming_intent:
            self.getServices_callback(hermes, intent_message)
        elif 'getStationAddress' in coming_intent:
            self.getStationAddress_callback(hermes, intent_message)

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).subscribe_intent('setOilType', self.setOilType_callback).start()

if __name__ == "__main__":
    Carburator()
