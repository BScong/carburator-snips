#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import requests

CONFIG_INI = "config.ini"
CARBURATOR_API_URL = "http://carburator.fr/api/"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class Carburator(object):
    """
    Class used to wrap action code with mqtt connection
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        # start listening to MQTT
        self.start_blocking()

    # --> Sub callback function, one per intent
    def askPrice_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        print('[Received] intent: '+ str(intent_message.intent.intent_name))

        longitude = self.config.get("secret").get("longitude")
        latitude = self.config.get("secret").get("latitude")
        if longitude is not None and latitude is not None:
            station_data = requests.get(CARBURATOR_API_URL+'stations/lon/'+str(longitude)+'/lat/'+str(latitude)+'?limit=1').json()
        else:
            hermes.publish_start_session_notification(intent_message.site_id, "Error: no location was specified.", "")
            return

        # action code goes here...
        oil_types = ['gasoline','diesel']
        oil_type = None
        if intent_message.slots.oil_type:
            oil_type = intent_message.slots.oil_type.first().value
            # check if the category is valide
            if oil_type.encode("utf-8") not in oil_types:
                oil_type = None

        if oil_type is None:
            hermes.publish_start_session_notification(intent_message.site_id, "Error: no oil type was specified.", "")
            return

        try:
            prices = station_data[0]['prices']
            if oil_type == 'gasoline':
                price = prices['2']['value']
            else:
                price = price['1']['value']
        except Exception as error:
            hermes.publish_start_session_notification(intent_message.site_id, "Error: impossible to find gas price.", "")
            return
        hermes.publish_start_session_notification(intent_message.site_id, "The " + str(oil_type) + ' is currently at ' + price + ' euros per liter.', "")


    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'askPrice':
            self.askPrice_callback(hermes, intent_message)
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Carburator()
