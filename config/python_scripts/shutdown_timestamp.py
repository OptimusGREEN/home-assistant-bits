now = time.time()
mqtt_topic = "home-assistant/timestamp/stopped"
mqtt_payload = now
retain = "true"
blocking = True
service_data = {"topic": mqtt_topic, "payload": mqtt_payload, "retain": retain}
hass.services.call("mqtt", "publish", service_data, blocking)