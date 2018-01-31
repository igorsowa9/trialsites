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

from settings import IP_irl001

def db_connection(dbname):
    """
    Connection to the database of SAU
    :param: str of db name
    :return: instance pf connection from psycopg2 pointing at dbname from input.
    """
    try:
        global conn
        conn = psycopg2.connect("dbname='" + dbname + "' user='postgres' host='134.130.169.25' password='postgres'")
        print("DB: " + dbname + " connected.")
        return(conn)
    except:
        print("I am unable to connect to the database. STOP.")
        sys.exit(0)


def sqlquery_wite_data(mtype, phaseid, nodeid, time1, measurementvalue):
    """
    Writes measurement values to the DB
    :param mtype: 1-33, 28-Pup, 29-Plow, 30-Qup, 31-Qlow
    :param phaseid:
    :param nodeid:
    :param time1:
    :param measurementvalue:
    :param accuracyvalue:
    :return:
    """

    SQLtext = ""
    SQLtext += "INSERT INTO measurecommand.measurement_historian (scl_measurement_id, timestamp,value,quality) VALUES (\n"
    SQLtext += "(SELECT scl_measurement_id FROM measurecommand.physicaldevice NATURAL JOIN measurecommand.logicaldevice NATURAL JOIN measurecommand.logicalnode NATURAL JOIN measurecommand.dataobject NATURAL JOIN measurecommand.dataattribute NATURAL JOIN\n"
    SQLtext += "measurecommand.measurement NATURAL JOIN  bridge.cim_scl_measurement NATURAL JOIN  networktopology.cim_measurement NATURAL JOIN networktopology.nodes\n"
    SQLtext += "WHERE measurement_type='" + mtype + "' \n"
    SQLtext += "AND measurecommand.measurement.dattribute_id_value = measurecommand.dataattribute.dattribute_id\n"
    SQLtext += "AND ldevice_id != '1' AND ldevice_id != '2' \n"
    SQLtext += "AND phase='" + phaseid + "' \n"
    SQLtext += "AND id='" + nodeid + "'  \n"
    SQLtext += "LIMIT 1),'" + time1 + "','" + measurementvalue + "','1');\n"
    SQLtext += "INSERT INTO measurecommand.measurement_accuracy (scl_measurement_id, acc_timestamp, accuracy) VALUES (\n"
    SQLtext += "(SELECT scl_measurement_id FROM measurecommand.physicaldevice NATURAL JOIN measurecommand.logicaldevice NATURAL JOIN measurecommand.logicalnode NATURAL JOIN measurecommand.dataobject NATURAL JOIN measurecommand.dataattribute NATURAL JOIN\n"
    SQLtext += "measurecommand.measurement NATURAL JOIN  bridge.cim_scl_measurement NATURAL JOIN  networktopology.cim_measurement NATURAL JOIN networktopology.nodes\n"
    SQLtext += "WHERE measurement_type='" + mtype + "' \n"
    SQLtext += "AND measurecommand.measurement.dattribute_id_value = measurecommand.dataattribute.dattribute_id\n"
    SQLtext += "AND ldevice_id != '1' AND ldevice_id != '2' \n"
    SQLtext += "AND phase='" + phaseid + "' \n"
    SQLtext += "AND id='" + nodeid + "'  \n"
    SQLtext += "LIMIT 1),'" + time1 + "','" + accuracyvalue + "');\n"
    return SQLtext


msgs_from_trialsite = {}
def on_message(client, userdata, message):
    #print("Following message received: ", str(message.payload.decode("utf-8")), ": full topic: ", message.topic)
    tup = {message.topic : str(message.payload.decode("utf-8"))}
    msgs_from_trialsite.update(tup)


def storedata():

    vm = mqttcli.Client()
    vm.on_message = on_message
    vm.connect(IP_irl001)
    vm.loop_start()
    vm.subscribe([("#", 0)])

    print("1... waiting for data...")
    time.sleep(2)
    vm.loop_stop()
    print("...no more waiting... data received: ", msgs_from_trialsite)

    if msgs_from_trialsite=={}:
        print("no data received. Waiting until the next loop...")
        time.sleep(2)
        return

    sys.exit()

    #json1_data = json.loads(json1_str)[0]

    current_time = datetime.now()
    SQLtext_write = ""
    for i in range(0, len(res['gen'])): # includes slack generator, that cannot be controlled!!
        g = res['gen'][i,:]
        g_static = orig_gen[i,:]
        Ppm = g[1]/(g_static[8]-g_static[9])
        Qpm = g[2]/((g_static[3]-g_static[4])/2)

        # nodeid, resource_id, controltype...
        control = np.array([int(g[0] - 1), int(s[i, 0]), np.round(Ppm, 4), np.round(Qpm, 4)])
        print('Gens/floads settings extracted from OPF results: ', control)
        # nodeid just by subtracting 1 - should be refactored!!!
        SQLtext_write += sqlquery_wite_data(str(int(control[0])),
                                                  str(int(control[1])),
                                                  str(2),
                                                  str(current_time),
                                                  str(control[2]))
        SQLtext_write += " "
        SQLtext_write += sqlquery_wite_data(str(int(control[0])),
                                                  str(int(control[1])),
                                                  str(4),
                                                  str(current_time),
                                                  str(control[3]))
        SQLtext_write += " "

    # --4.2-- # Write new control values to the DB
    conn = db_connection("irland")
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

