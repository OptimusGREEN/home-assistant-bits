
l1 = "light.playroom_tv1"
l2 = "light.playroom_centre1"
l3 = "light.playroom_sofa1"
l4 = "light.playroom_sofa2"
l5 = "light.playroom_centre2"
l6 = "light.playroom_tv2"

sw = "input_boolean.chaser_switch"

def random_colour(amount=3):
    if amount == 1:
        return random.choice(range(256))
    else:
        l = []
        for a in range(amount):
            l.append(random.choice(range(256)))
        return l

liv_lights = [l1, l2, l3, l4, l5, l6]

# count = 0
# while count <= 10:
sw_state = hass.states.is_state(sw, "on")
logger.info(sw_state)
while sw_state:
    for l in liv_lights:
        rc = random_colour()
        logger.info("{} is {}".format(l,rc))
        hass.services.call('light', 'turn_on', {"entity_id": l, "brightness": '250', "transition": 0.01, "rgb_color": rc})
        time.sleep(0.5)
        hass.services.call('light', 'turn_on', {"entity_id": l, "brightness": "0", "transition": 0.01})
    sw_state = hass.states.is_state(sw, "on")
    # count = count + 1
    logger.info(sw_state)