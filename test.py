import sys
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time
import sys, os
from datetime import datetime
import psycopg2
import json

cli = mqttcli.Client()
cli.connect("localhost")

def test_message():

    cli.publish("test/topic", "test message from the server")

while(True):
    test_message()
    time.sleep(2)

