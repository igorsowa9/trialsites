import copy

db_ip = "10.12.0.1"  # "137.226.133.186"

log_inf = True

ita005_settings = {"name": "ita005",
                   "ip": "10.12.0.202",
                   "mqtt_topics": [('#', 0)],
                   "msg_labels":
                       [
                           [
                               ".REQUEST_TIME",
                                ".SERVER_TIME",
                                "Active Power 3-Phase",
                                "Apparent Energy",
                                "Apparent Power 3-Phase",
                                "Delivered Active Energy",
                                "Frequency",
                                "InstFrequency",
                                "Non-Active Power 3-Phase",
                                "PF 3-Phase",
                                "Received Active Energy",
                                "Rms Current L1-N",
                                "Rms Voltage L1-N"
                            ]
                       ],
                   "db_name": "itadb",
                   "db_tables": ["ita005"],
                   "db_tables_string": ["ita005_string"],
                   "db_labels":
                       [
                           [
                                "request_time",
                                "server_time",
                                "p_3phase",
                                "apparent_energy",
                                "s_3phase",
                                "delivered_active_energy",
                                "frequency",
                                "inst_frequency",
                                "nonactive_power_3phase",
                                "pf_3phase",
                                "received_active_energy",
                                "rms_current_l1n",
                                "rms_voltage_l1n",
                                "lab_ts",
                                "latency"
                            ]
                       ]
                   }

ita006_settings = copy.deepcopy(ita005_settings)
ita006_settings.update({'ip': "10.12.0.206"})
ita006_settings.update({"name": "ita006"})
ita006_settings.update({"db_tables": ["ita006"]})
ita006_settings.update({"db_tables_string": ["ita006_string"]})

ita007_settings = copy.deepcopy(ita005_settings)
ita007_settings.update({'ip': "10.12.0.210"})
ita007_settings.update({"name": "ita007"})
ita007_settings.update({"db_tables": ["ita007"]})
ita007_settings.update({"db_tables_string": ["ita007_string"]})

irl001_settings = {"name": "irl001",
                   "ip": "10.12.0.18",
                   "mqtt_topics": [('SUCCESS/NORM/ESB001/wally1/Values', 0),
                                   ('SUCCESS/NORM/ESB001/wally2/Values', 0)],
                   "msg_labels":
                       [
                           [
                                "SMXtimestamp",
                                "SysDateTimeUTC",
                                "Frequency",
                                "InstFrequency",
                                "Rms Voltage L1-L2",
                                "Rms Voltage L1-N",
                                "Rms Voltage L2-L3",
                                "Rms Voltage L2-N",
                                "Rms Voltage L3-L1",
                                "Rms Voltage L3-N",
                                "Rms Voltage L4-N"
                            ],
                           [
                                "SMXtimestamp",
                                "SysDateTimeUTC",
                                "Frequency",
                                "InstFrequency",
                                "Rms Voltage L1-L2",
                                "Rms Voltage L1-N",
                                "Rms Voltage L2-L3",
                                "Rms Voltage L2-N",
                                "Rms Voltage L3-L1",
                                "Rms Voltage L3-N",
                                "Rms Voltage L4-N"
                           ]
                   ],
                   "db_name": "irldb",
                   "db_tables": ["irldata_wallya1", "irldata_wallya2"],
                   "db_labels":
                       [
                           [
                               "smx_ts",
                               "smx_utc",
                               "frequency",
                               "instfrequency",
                               "v_l1l2_rms",
                               "v_l1n_rms",
                                "v_l2l3_rms",
                               "v_l2n_rms",
                                "v_l3l1_rms",
                               "v_l3n_rms",
                               "v_l4n_rms",

                                "lab_ts",
                               "latency"
                           ],
                            [
                               "smx_ts",
                               "smx_utc",
                               "frequency",
                               "instfrequency",
                               "v_l1l2_rms",
                               "v_l1n_rms",
                                "v_l2l3_rms",
                               "v_l2n_rms",
                                "v_l3l1_rms",
                               "v_l3n_rms",
                               "v_l4n_rms",

                                "lab_ts",
                               "latency"
                           ]
                       ]}

test_message = """
{

    "SMXtimestamp":"2018/03/04 20:09:54:018",
    "SysDateTimeUTC":"03/04/2018 20:09:54",
    "wallya1":{
        "Frequency":{
            "unit":"Hz",
            "value":"049.973"
        },
        "InstFrequency":{
            "unit":"Hz",
            "value":"049.977"
        },
        "Rms Voltage L1-L2":{
            "unit":"V",
            "value":"388.791"
        },
        "Rms Voltage L1-N":{
            "unit":"V",
            "value":"223.972"
        },
        "Rms Voltage L2-L3":{
            "unit":"V",
            "value":"390.539"
        },
        "Rms Voltage L2-N":{
            "unit":"V",
            "value":"225.551"
        },
        "Rms Voltage L3-L1":{
            "unit":"V",
            "value":"389.523"
        },
        "Rms Voltage L3-N":{
            "unit":"V",
            "value":"225.366"
        },
        "Rms Voltage L4-N":{
            "unit":"V",
            "value":"000.000"
        }
    }

}
"""

test_message2 = '{"Frequency":{"unit":"Hz","value":"049.947"},"Rms Voltage L1-L2":{"unit":"V","value":"385.302"},"Rms Voltage L1-N":{"unit":"V","value":"222.537"},"Rms Voltage L2-L3":{"unit":"V","value":"387.723"},"Rms Voltage L2-N":{"unit":"V","value":"223.412"},"Rms Voltage L3-L1":{"unit":"V","value":"387.416"},"Rms Voltage L3-N":{"unit":"V","value":"224.093"},"Rms Voltage L4-N":{"unit":"V","value":"000.000"}}'

