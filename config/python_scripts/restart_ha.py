# hass.services.call('input_boolean', 'turn_off', {"entity_id": "input_boolean_restart_homeassistant")
hass.services.call('homeassistant', 'restart')