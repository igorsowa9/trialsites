import sys
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time
import sys, os
from datetime import datetime
import psycopg2
import json
import logging
import shutil

from settings import *


def db_connection(dbname):
    try:
        global conn
        conn = psycopg2.connect("dbname='" + dbname + "' user='postgres' host="+db_ip+" password='postgres'")
        if log_inf:
            logging.info(" When: " + str(datetime.now()) + " --- " + " DB: " + dbname + " connected.")
        return conn
    except:
        logging.error(" When: " + str(datetime.now()) + " --- " + "I am unable to connect to the database.")
        print("I am unable to connect to the database. STOP.")


def sqlquery_make(tablename, labels, values):

    labels_string = ""
    for l in range(len(labels)):
        label = labels[l]
        if l == 0:
            labels_string += "(" + str(label) + ", "
        elif l == len(labels)-1:
            labels_string += str(label) + ") "
        else:
            labels_string += str(label) + ", "

    values_string = ""
    for v in range(len(values)):
        value = values[v]
        if v == 0:
            values_string += "('" + str(value) + "', "
        elif v == len(values)-1:
            values_string += "'" + str(value) + "', '" + str(datetime.utcnow()) + "')"
        else:
            values_string += "'" + str(value) + "', "

    SQLtext = ""
    SQLtext += "INSERT INTO public." + str(tablename) + str(labels_string) + "VALUES " + values_string + ";"
    return SQLtext


def sqlquery_make_string(tablename, value):
    SQLtext = ""
    SQLtext += "INSERT INTO public." + str(tablename) + " (message_string, lab_ts) " + \
               "VALUES ('" + value + "' , '" + str(datetime.utcnow()) + "');"
    return SQLtext


def on_message_writetodb(client, userdata, message):

    print("Received: " + str(userdata))

    if userdata == "irl001":
        trialsite_settings = irl001_settings
    elif userdata == "ita005":
        trialsite_settings = ita005_settings
    elif userdata == "ita006":
        trialsite_settings = ita006_settings
    else:
        logging.warning(" When: " + str(datetime.now()) + " --- " + "Unrecognized userdata! :" + str(userdata))
        return

    json1_str = message.payload.decode("utf-8")

    try:
        json1_data = json.loads(json1_str)
    except json.decoder.JSONDecodeError as e:
        logging.error(" When: " + str(datetime.now()) + " --- " + 'Json decode error: ' + str(e))
        json1_data = None

    SQLtext = ""
    for ml in range(len(trialsite_settings['msg_labels'])):
        msg_label = trialsite_settings['msg_labels'][ml]
        values = []
        for l in range(len(msg_label)):
            key = msg_label[l]
            if key[0] == "." or key == 'SMXtimestamp' or key == 'SysDateTimeUTC':
                value = json1_data[key]
            elif key[0] == ">":
                try:
                    value = json1_data['wallya1'][key]
                    value = json1_data['wallya2'][key]
                except KeyError:
                    logging.warning(" When: " + str(datetime.now()) + " --- " +
                                    "Message inconsistent with the assumed structure. Do not write to DB.")
                    print("Message inconsistent with the assumed structure. Do not write to DB.")
                    return
            else:
                value = json1_data[key]['value']
            values.append(value)

        SQLtext += sqlquery_make(trialsite_settings['db_tables'][ml], trialsite_settings['db_labels'][ml], values)
        SQLtext += sqlquery_make_string(trialsite_settings['db_tables_string'][ml], str(json1_str))

    if userdata == "irl":  # calculate latency
        lab_ts_utc = datetime.utcnow()
        smx_ts = json1_data["SMXtimestamp"]
        # lab_ts_dt = datetime.strptime(str(lab_ts), '%Y-%m-%d %H:%M:%S.%f')
        smx_ts_dt = datetime.strptime(str(smx_ts), '%Y/%m/%d %H:%M:%S:%f')
        latency = lab_ts_utc - smx_ts_dt
        latency_sec = latency.microseconds / 10e5

    conn = db_connection(trialsite_settings['db_name'])
    cursor = conn.cursor()


    try:
        cursor.execute(SQLtext)
        conn.commit()
    except psycopg2.OperationalError as e:
        logging.warning(" When: " + str(datetime.now()) + " --- " + "Unable to execute query! " + format(e))
    finally:
        conn.close()
    if log_inf: logging.info(" When: " + str(datetime.now()) + " --- " + 'Data written in DB.')
    print("Data written in DB.")
    return


def storedataAttempt(trialsite_settings):

    if trialsite_settings['name'] == 'irl001':
        vm = mqttcli.Client(userdata="irl001")
    elif trialsite_settings['name'] == 'ita005':
        vm = mqttcli.Client(userdata="ita005")
    elif trialsite_settings['name'] == 'ita006':
        vm = mqttcli.Client(userdata="ita006")
    else:
        logging.warning(" When: " + str(datetime.now()) + " --- " + "Unrecognized trialsite settings! :" + str(userdata))
        return

    # vm.on_message = on_message_writetodb
    vm.connect(trialsite_settings["ip"])
    vm.loop_start()
    vm.subscribe(trialsite_settings["mqtt_topics"])

    for topic in trialsite_settings["mqtt_topics"]:
        vm.message_callback_add(topic[0], on_message_writetodb)

    print("Waiting for data...")
    if log_inf: logging.info(" When: " + str(datetime.now()) + " --- " + "Waiting for data...")
    time.sleep(3)
    vm.loop_stop()


def storedataOnce():
    while True:
        try:
            storedataAttempt(irl001_settings)
            storedataAttempt(ita005_settings)
            storedataAttempt(ita006_settings)
        except:

            print("Unexpected error:", sys.exc_info())
            logging.error(" When: " + str(datetime.now()) + " --- " + "Error in storedataOnce(): ", sys.exc_info())
            pass
        else:
            break

def storedataRepeatedly():
    while True:
        storedataOnce()
        time.sleep(0.2)

archive_name = "logarchive_" + str(datetime.now().isoformat()) + ".log"
shutil.copy("logfile.log", archive_name)

#shutil.make_archive(archive_name, "zip")
#os.remove(archive_name)

logging.basicConfig(filename='logfile.log', level=logging.INFO)
logging.warning(" When: " + str(datetime.now()) + " --- " + "Initiate logfile")

storedataRepeatedly()
