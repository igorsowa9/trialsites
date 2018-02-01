import sys
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time
import sys, os
from datetime import datetime, timedelta
import psycopg2
import numpy as np
from pprint import pprint as pp
import copy
import json

from settings import IP_irl001, test_message, db_ip

def db_connection(dbname):
    try:
        global conn
        conn = psycopg2.connect("dbname='" + dbname + "' user='postgres' host="+db_ip+" password='postgres'")
        print("DB: " + dbname + " connected.")
        return(conn)
    except:
        print("I am unable to connect to the database. STOP.")
        sys.exit(0)


def sqlquery_wite_data(ts, message):

    SQLtext = ""
    SQLtext += "INSERT INTO public.irldata_all (time, string) VALUES ('"+str(ts)+"', '"+str(message)+"')"
    return SQLtext


def on_message_writetodb(client, userdata, message):
    json1_str = message.payload.decode("utf-8")
    #json1_data = json.loads(json1_str)

    SQLtext_write = sqlquery_wite_data(datetime.now(), json1_str)

    conn = db_connection("irldb")
    cursor = conn.cursor()

    try:
        cursor.execute(SQLtext_write)
        conn.commit()
    except psycopg2.OperationalError as e:
        print('Unable to execute query!\n{0}').format(e)
        sys.exit(1)
    finally:
        print('Data written in DB.')
        conn.close()

def storedata():

    vm = mqttcli.Client()
    vm.on_message = on_message_writetodb
    vm.connect(IP_irl001)
    vm.loop_start()
    vm.subscribe([("#", 0)])

    print("1... waiting for data...")
    time.sleep(2)
    vm.loop_stop()

while True:
    storedata()
    time.sleep(1)