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

from multiprocessing import Pool

from settings import *


def db_connection(dbname):
    try:
        global conn
        conn = psycopg2.connect("dbname='" + dbname + "' user='postgres' host="+db_ip2+" password='postgres'")
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
            values_string += "'" + str(value) + "')"
        else:
            values_string += "'" + str(value) + "', "

    SQLtext = ""
    SQLtext += "INSERT INTO public." + str(tablename) + str(labels_string) + "VALUES " + values_string + ";"
    return SQLtext


# def sqlquery_make_string(tablename, value):
#     SQLtext = ""
#     SQLtext += "INSERT INTO public." + str(tablename) + " (message_string, lab_ts) " + \
#                "VALUES ('" + value + "' , '" + str(datetime.utcnow()) + "');"
#     return SQLtext


def on_message_writetodb(client, userdata, message):

    # print("Received: " + str(userdata))
    lab_ts_utc = datetime.utcnow()
    json1_str = message.payload.decode("utf-8")

    try:
        json1_data = json.loads(json1_str)
    except json.decoder.JSONDecodeError as e:
        logging.error(" When: " + str(datetime.now()) + " --- " + 'Json decode error: ' + str(e))
        json1_data = None

    if userdata == "irl001":
        trialsite_settings = irl001_settings
        json_to_sqlreq_irl(json1_data, trialsite_settings, lab_ts_utc)
    elif userdata == "ita005":
        trialsite_settings = ita005_settings
        json_to_sqlreq_ita(json1_data, trialsite_settings, lab_ts_utc)
    elif userdata == "ita006":
        trialsite_settings = ita006_settings
        json_to_sqlreq_ita(json1_data, trialsite_settings, lab_ts_utc)
    elif userdata == "ita007":
        trialsite_settings = ita007_settings
        json_to_sqlreq_ita(json1_data, trialsite_settings, lab_ts_utc)
    elif userdata == "ita008":
        trialsite_settings = ita008_settings
        json_to_sqlreq_ita(json1_data, trialsite_settings, lab_ts_utc)
    else:
        logging.warning(" When: " + str(datetime.now()) + " --- " + "Unrecognized userdata! :" + str(userdata))
        return


def json_to_sqlreq_irl(json1_data, trialsite_settings, lab_ts_utc):

    # calculate latency
    smx_ts = json1_data["SMXtimestamp"]
    # lab_ts_dt = datetime.strptime(str(lab_ts), '%Y-%m-%d %H:%M:%S.%f')
    smx_ts_dt = datetime.strptime(str(smx_ts), '%Y/%m/%d %H:%M:%S:%f')
    latency = lab_ts_utc - smx_ts_dt
    latency_sec = latency.microseconds / 10e5

    if 'wallya1' in json1_data:
        which_wally = 'wallya1'
        wally_idx = 0
    elif 'wallya2' in json1_data:
        which_wally = 'wallya2'
        wally_idx = 1
    else:
        logging.warning(" When: " + str(datetime.now()) + " --- " +
                        "No wallyXX label detected in the irish data.")
        return

    SQLtext = ""

    msg_label = trialsite_settings['msg_labels'][wally_idx]
    values = []
    for l in range(len(msg_label)):
        key = msg_label[l]
        if key == 'SMXtimestamp' or key == 'SysDateTimeUTC':
            value = json1_data[key]
        else:
            value = json1_data[which_wally][key]['value']

        values.append(value)
    values.append(str(lab_ts_utc))
    values.append(str(latency_sec))


    SQLtext += sqlquery_make(trialsite_settings['db_tables'][wally_idx], trialsite_settings['db_labels'][wally_idx], values)
    # the request below to store the whole received string as backup
    # SQLtext += sqlquery_make_string(trialsite_settings['db_tables_string'][ml], str(json1_str))

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
    print("Data (" + trialsite_settings['name'] + ") written in DB. SMX ts=" + str(smx_ts))
    return


def json_to_sqlreq_ita(json1_data, trialsite_settings, lab_ts_utc):

    # calculate latency
    smx_ts = json1_data[".SERVER_TIME"]
    # lab_ts_dt = datetime.strptime(str(lab_ts), '%Y-%m-%d %H:%M:%S.%f')
    smx_ts_dt = datetime.strptime(str(smx_ts), '%Y-%m-%d %H:%M:%S')
    latency = lab_ts_utc - smx_ts_dt
    latency_sec = latency.microseconds / 10e5

    meter_idx = 0

    SQLtext = ""

    msg_label = trialsite_settings['msg_labels'][meter_idx]
    values = []
    for l in range(len(msg_label)):
        key = msg_label[l]
        if key[0] == ".":
            value = json1_data[key]
        else:
            value = json1_data[key]['value']
        values.append(value)
    values.append(str(lab_ts_utc))
    values.append(str(latency_sec))

    SQLtext += sqlquery_make(trialsite_settings['db_tables'][meter_idx], trialsite_settings['db_labels'][meter_idx], values)
    # SQLtext += sqlquery_make_string(trialsite_settings['db_tables_string'][meter_idx], str(json1_str))

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
    print("Data (" + trialsite_settings['name'] + ") written in DB. SMX ts=" + str(smx_ts))
    return


def storedataAttempt(trialsite_settings):

    # print("storeAttempt: " + str(trialsite_settings['name']))

    if trialsite_settings['name'] == 'irl001':
        vm = mqttcli.Client(userdata="irl001")
    elif trialsite_settings['name'] == 'ita005':
        vm = mqttcli.Client(userdata="ita005")
    elif trialsite_settings['name'] == 'ita006':
        vm = mqttcli.Client(userdata="ita006")
    elif trialsite_settings['name'] == 'ita007':
        vm = mqttcli.Client(userdata="ita007")
    elif trialsite_settings['name'] == 'ita008':
        vm = mqttcli.Client(userdata="ita008")
    else:
        logging.warning(" When: " + str(datetime.now()) + " --- " + "Unrecognized trialsite settings! :")
        return

    # vm.on_message = on_message_writetodb
    vm.connect(trialsite_settings["ip"])
    vm.loop_start()
    vm.subscribe(trialsite_settings["mqtt_topics"])

    for topic in trialsite_settings["mqtt_topics"]:
        vm.message_callback_add(topic[0], on_message_writetodb)

    # print("Waiting for data...")
    if log_inf: logging.info(" When: " + str(datetime.now()) + " --- " + "Waiting for data...")
    time.sleep(2)
    vm.loop_stop()


def storedataOnce():
    while True:
        try:
            # pool = Pool(processes=4)
            # pool.apply_async(storedataAttempt, [irl001_settings])
            # pool.apply_async(storedataAttempt, [ita005_settings])
            # pool.apply_async(storedataAttempt, [ita006_settings])
            # pool.apply_async(storedataAttempt, [ita007_settings])
            # storedataAttempt(irl001_settings)
            # storedataAttempt(ita005_settings)
            storedataAttempt(ita006_settings)
            # storedataAttempt(ita007_settings)
            # storedataAttempt(ita008_settings)
        except:

            print("Unexpected error:", sys.exc_info())
            logging.error(" When: " + str(datetime.now()) + " --- " + "Error in storedataOnce(): ", sys.exc_info())
            pass
        else:
            break

def storedataRepeatedly():
    while True:
        storedataOnce()
        time.sleep(0.1)

# archive_name = "logarchive_" + str(datetime.now().isoformat()) + ".log"
# shutil.copy("logfile.log", archive_name)

#shutil.make_archive(archive_name, "zip")
#os.remove(archive_name)

# logging.basicConfig(filename='logfile.log', level=logging.INFO)
# logging.warning(" When: " + str(datetime.now()) + " --- " + "Initiate logfile")

storedataRepeatedly()
