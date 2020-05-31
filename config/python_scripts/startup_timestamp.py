now = time.time()
# hass.states.set("sensor.timestamp_started", now)

mqtt_topic = "home-assistant/timestamp/started"
mqtt_payload = now
retain = "true"
blocking = False
service_data = {"topic": mqtt_topic, "payload": mqtt_payload, "retain": retain}
hass.services.call("mqtt", "publish", service_data, blocking)