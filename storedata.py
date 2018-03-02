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


from settings import IP_irl001, test_message, db_ip, wally_topic, test_message2, log_inf


def db_connection(dbname):
    try:
        global conn
        conn = psycopg2.connect("dbname='" + dbname + "' user='postgres' host="+db_ip+" password='postgres'")
        logging.warning(" When: " + str(datetime.now()) + " --- " + " DB: " + dbname + " connected.")
        return(conn)
    except:
        logging.error(" When: " + str(datetime.now()) + " --- " + "I am unable to connect to the database.")
        print("I am unable to connect to the database. STOP.")


def sqlquery_wite_data_all(ts, message):

    SQLtext = ""
    SQLtext += "INSERT INTO public.irldata_all (time, string) VALUES ('"+str(ts)+"', '"+str(message)+"')"
    return SQLtext


def sqlquery_wite_data_wally(time, field1, field2, field3, field4, field5, field6, field7, field8, smx_ts):

    SQLtext = ""
    SQLtext += "INSERT INTO public.irldata_wally (time, frequency, V_L1L2_rms, V_L1N_rms, V_L2L3_rms, V_L2N_rms, " \
               "V_L3L1_rms, V_L3N_rms, V_L4N_rms, smx_ts) " \
               "VALUES ('"+str(time)+"', '"+str(field1)+"', '"+str(field2)+"', '"+str(field3)+"', '"+str(field4)+"', " \
                "'"+str(field5)+"', '"+str(field6)+"', '"+str(field7)+"', '"+str(field8)+"', '"+str(smx_ts)+"')"
    return SQLtext


def on_message_writetodb(client, userdata, message):

    json1_str = message.payload.decode("utf-8")
    try:
        json1_data = json.loads(json1_str)
    except json.decoder.JSONDecodeError as e:
        logging.error(" When: " + str(datetime.now()) + " --- " + 'Json decode error: ' + str(e))

    ts = datetime.now()

    SQLtext_write_wally = sqlquery_wite_data_wally(ts,
                                                    str(json1_data["wallya1"]["Frequency"]["value"]), #field1 etc.
                                                    str(json1_data["wallya1"]["Rms Voltage L1-L2"]["value"]),
                                                    str(json1_data["wallya1"]["Rms Voltage L1-N"]["value"]),
                                                    str(json1_data["wallya1"]["Rms Voltage L2-L3"]["value"]),
                                                    str(json1_data["wallya1"]["Rms Voltage L2-N"]["value"]),
                                                    str(json1_data["wallya1"]["Rms Voltage L3-L1"]["value"]),
                                                    str(json1_data["wallya1"]["Rms Voltage L3-N"]["value"]),
                                                    str(json1_data["wallya1"]["Rms Voltage L4-N"]["value"]), # field8
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


def storedataAttempt():

    vm = mqttcli.Client()
    vm.on_message = on_message_writetodb
    vm.connect(IP_irl001)
    vm.loop_start()
    vm.subscribe([(wally_topic, 0)])

    print("Waiting for data...")
    if log_inf == True: logging.info(" When: " + str(datetime.now()) + " --- " + "Waiting for data...")
    time.sleep(0.6)
    vm.loop_stop()


def storedataOnce():
    while True:
        try:
            storedataAttempt()
        except:
            logging.warning(" When: " + str(datetime.now()) + " --- " + "Except in storedataOnce()")
            pass
        else:
            break

def storedataRepeatedly():
    while True:
        storedataOnce()
        time.sleep(0.4)

archive_name = "logarchive_" + str(datetime.now().isoformat()) + ".log"
shutil.copyfile("logfile.log", archive_name)
shutil.make_archive(archive_name, "zip")
os.remove(archive_name)

logging.basicConfig(filename='logfile.log', level=logging.INFO)
logging.warning(" When: " + str(datetime.now()) + " --- " + "Initiate logfile")

storedataRepeatedly()