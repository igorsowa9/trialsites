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


from settings import IP_irl001, test_message, db_ip, wallya1_topic, wallya2_topic, test_message2, log_inf


def db_connection(dbname):
    try:
        global conn
        conn = psycopg2.connect("dbname='" + dbname + "' user='postgres' host="+db_ip+" password='postgres'")
        logging.info(" When: " + str(datetime.now()) + " --- " + " DB: " + dbname + " connected.")
        return(conn)
    except:
        logging.error(" When: " + str(datetime.now()) + " --- " + "I am unable to connect to the database.")
        print("I am unable to connect to the database. STOP.")


def sqlquery_wite_data_all(ts, message):

    SQLtext = ""
    SQLtext += "INSERT INTO public.irldata_all (time, string) VALUES ('"+str(ts)+"', '"+str(message)+"')"
    return SQLtext


def sqlquery_wite_data_wally(wally_name, lab_ts, field1, field2, field3, field4, field5, field6, field7, field8, field9, smx_ts, smx_utc):

    SQLtext = ""
    SQLtext += "INSERT INTO public.irldata_"+wally_name+" (lab_ts, frequency, instfrequency, V_L1L2_rms, V_L1N_rms, " \
                                                        "V_L2L3_rms, V_L2N_rms, V_L3L1_rms, V_L3N_rms, V_L4N_rms, smx_ts, smx_utc) " \
               "VALUES ('"+str(lab_ts)+"', '"+str(field1)+"', '"+str(field2)+"', '"+str(field3)+"', '"+str(field4)+"', " \
                "'"+str(field5)+"', '"+str(field6)+"', '"+str(field7)+"', '"+str(field8)+"', '"+str(field9)+"', " \
                "'"+str(smx_ts)+"', '"+str(smx_utc)+"'); "
    return SQLtext


def on_message_writetodb(client, userdata, message):

    if message.topic == wallya1_topic:
        wally_name = 'wallya1'
    elif message.topic == wallya2_topic:
        wally_name = 'wallya2'

    json1_str = message.payload.decode("utf-8")
    try:
        json1_data = json.loads(json1_str)
    except json.decoder.JSONDecodeError as e:
        logging.error(" When: " + str(datetime.now()) + " --- " + 'Json decode error: ' + str(e))
        json1_data = None
        wally_name = None

    lab_ts = datetime.now()

    SQLtext_write_wally = sqlquery_wite_data_wally(wally_name, lab_ts,
                                                    str(json1_data[wally_name]["Frequency"]["value"]), #field1 etc.
                                                    str(json1_data[wally_name]["InstFrequency"]["value"]),
                                                    str(json1_data[wally_name]["Rms Voltage L1-L2"]["value"]),
                                                    str(json1_data[wally_name]["Rms Voltage L1-N"]["value"]),
                                                    str(json1_data[wally_name]["Rms Voltage L2-L3"]["value"]),
                                                    str(json1_data[wally_name]["Rms Voltage L2-N"]["value"]),
                                                    str(json1_data[wally_name]["Rms Voltage L3-L1"]["value"]),
                                                    str(json1_data[wally_name]["Rms Voltage L3-N"]["value"]),
                                                    str(json1_data[wally_name]["Rms Voltage L4-N"]["value"]), # field9
                                                    str(json1_data["SMXtimestamp"]),
                                                    str(json1_data["SysDateTimeUTC"]))

    conn = db_connection("irldb")
    cursor = conn.cursor()

    try:
        cursor.execute(SQLtext_write_wally)
        conn.commit()
    except psycopg2.OperationalError as e:
        logging.warning(" When: " + str(datetime.now()) + " --- " + "Unable to execute query! " + format(e))
    finally:
        if log_inf == True: logging.info(" When: " + str(datetime.now()) + " --- " + 'Data written in DB.')
        print('Data written in DB.')
        conn.close()


def storedataAttempt(topic):

    vm = mqttcli.Client()
    vm.on_message = on_message_writetodb
    vm.connect(IP_irl001)
    vm.loop_start()
    vm.subscribe([(topic, 0)])

    print("Waiting for data...")
    if log_inf == True: logging.info(" When: " + str(datetime.now()) + " --- " + "Waiting for data...")
    time.sleep(2.5)
    vm.loop_stop()

def storedataOnce():
    while True:
        try:
            # run in parallel both mqtt subscriptions
            with Pool(5) as p:
                storedataAttempt(p.map(storedataAttempt, [wallya1_topic, wallya2_topic]))

        except:
            logging.info(" When: " + str(datetime.now()) + " --- " + "Except in storedataOnce()")
            pass
        else:
            break

def storedataRepeatedly():
    while True:
        storedataOnce()
        time.sleep(1)

archive_name = "logarchive_" + str(datetime.now().isoformat()) + ".log"
shutil.copy("logfile.log", archive_name)

#shutil.make_archive(archive_name, "zip")
#os.remove(archive_name)

logging.basicConfig(filename='logfile.log', level=logging.INFO)
logging.warning(" When: " + str(datetime.now()) + " --- " + "Initiate logfile")

storedataRepeatedly()