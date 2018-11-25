import json
import requests

# In case you don't have a valid cert
requests.packages.urllib3.disable_warnings()

# Setup your hec server, token, and the PurpleAir Sensors in pas_config.py
import pas_config as conf


# "Stats": // Statistics for PM2.5
# "{
# \"v\":1.07, // Real time or current PM2.5 Value
# \"v1\":1.3988595758168765, // Short term (10 minute average)
# \"v2\":10.938131480857114, // 30 minute average
# \"v3\":15.028685608345926, // 1 hour average
# \"v4\":6.290537580116773, // 6 hour average
# \"v5\":1.8393146177050788, // 24 hour average
# \"v6\":0.27522764912064507, // One week average
# \"pm\":1.07, // Real time or current PM2.5 Value
# \"lastModified\":1490309930933, // Last modified time stamp for calculated average statistics
# \"timeSinceModified\":69290 // Time between last two readings in milliseconds
# }"
# }


def log_to_splunk(sensor_json, hec_server, hec_token):
    print "logging to splunk..."
    url = "%s/services/collector/event" % hec_server
    authHeader = {'Authorization': "Splunk %s" % hec_token}

    jsonDict = {"index": "purpleair",
                "host": "test_host",
                "event": sensor_json}
    r = requests.post(url, headers=authHeader, json=jsonDict, verify=False)
    print r.text


def get_purpleair_sensor_data(sensor_id):
    readings = []
    response = requests.get('https://www.purpleair.com/json?show=%d' % sensor_id)
    if response.status_code == 200:
        sensor_json = json.loads(response.text)
        print json.dumps(sensor_json)

        for reading in sensor_json['results']:
            print reading
            reading['Stats'] = json.loads(reading['Stats'])
            readings.append(reading)
        return readings
    else:
        print "Error: %s" % response.status_code
        exit(1)


if __name__ == "__main__":

    for sensor_id in conf.sensors:
        readings = get_purpleair_sensor_data(sensor_id)
        for reading in readings:
            log_to_splunk(reading, conf.hec_server, conf.hec_token)