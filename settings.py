IP_irl001 = "10.12.0.18"

db_ip = "10.12.0.1" # "137.226.133.186"

wallya1_topic = "SUCCESS/NORM/ESB001/wally1/Values"
wallya2_topic = "SUCCESS/NORM/ESB001/wally2/Values"

log_inf = False

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

