import appdaemon.plugins.hass.hassapi as hass

class CoverControl(hass.Hass):

    def initialize(self):

        self.debug_mode = False

        self.open_switch = self.args["open_switch"]
        self.close_switch = self.args["close_switch"]
        self.current_position_sensor = self.args["current_position_sensor"]
        self.mqtt_sensor_topic = self.args["mqtt_sensor_topic"] # required for a retained value to currentz position sensor after restart

        self.logme("open_switch: {}".format(self.open_switch), level="debug")
        self.logme("close_switch: {}".format(self.close_switch), level="debug")
        self.logme("current_position_sensor: {}".format(self.current_position_sensor), level="debug")
        self.logme("mqtt_sensor_topic: {}".format(self.mqtt_sensor_topic), level="debug")

        if "full_transition_time" in self.args:
            self.full_transition_time = float(self.args["full_transition_time"])
        else:
            self.full_transition_time = 10
        self.logme("full_transition_time: {}".format(self.full_transition_time), level="debug")

        if "overrun_time" in self.args: # useful if timings stray to fully open or close cover
            self.overrun_time = float(self.args["overrun_time"])
        else:
            self.overrun_time = 0
        self.logme("overrun_time: {}".format(self.overrun_time), level="debug")

        if "nudge" in self.args: # a list with numeric value in % at index 0, nudge_open_switch entity_id at index 1, nudge_close_switch entity_id at index 2 
            self.nudge_percent = float(self.args["nudge"][0])
            self.nudge_open_switch = self.args["nudge"][1]
            self.nudge_close_switch = self.args["nudge"][2]
            self.listen_state(self.__nudge_open, entity=self.nudge_open_switch, new='on', amount=self.nudge_percent)
            self.listen_state(self.__nudge_close, entity=self.nudge_close_switch, new='on', amount=self.nudge_percent)
        
        if "pre_pos_1" in self.args: # a list with numeric value in % at index 0 and switch entity_id at index 1
            self.pre_pos_1 = float(self.args["pre_pos_1"][0])
            self.pre_pos_1_switch = self.args["pre_pos_1"][1]
            self.listen_state(self.__callback_buffer, entity=self.pre_pos_1_switch, new='on', position=self.pre_pos_1)
            self.logme("pre_pos_1: {}".format(self.pre_pos_1), level="debug")
            self.logme("pre_pos_1_switch: {}".format(self.pre_pos_1_switch), level="debug")

        
        if "pre_pos_2" in self.args: # a list with numeric value in % at index 0 and switch entity_id at index 1
            self.pre_pos_2 = float(self.args["pre_pos_2"][0])
            self.pre_pos_2_switch = self.args["pre_pos_2"][1]
            self.listen_state(self.__callback_buffer, entity=self.pre_pos_2_switch, new='on', position=self.pre_pos_2)
            self.logme("pre_pos_2: {}".format(self.pre_pos_2), level="debug")
            self.logme("pre_pos_2_switch: {}".format(self.pre_pos_2_switch), level="debug")
        
        if "pre_pos_3" in self.args: # a list with numeric value in % at index 0 and switch entity_id at index 1
            self.pre_pos_3 = float(self.args["pre_pos_3"][0])
            self.pre_pos_3_switch = self.args["pre_pos_3"][1]
            self.listen_state(self.__callback_buffer, entity=self.pre_pos_3_switch, new='on', position=self.pre_pos_3)
            self.logme("pre_pos_3: {}".format(self.pre_pos_3), level="debug")
            self.logme("pre_pos_3_switch: {}".format(self.pre_pos_3_switch), level="debug")
        
        if "pre_pos_4" in self.args: # a list with numeric value in % at index 0 and switch entity_id at index 1
            self.pre_pos_4 = float(self.args["pre_pos_4"][0])
            self.pre_pos_4_switch = self.args["pre_pos_4"][1]
            self.listen_state(self.__callback_buffer, entity=self.pre_pos_4_switch, new='on', position=self.pre_pos_4)
            self.logme("pre_pos_4: {}".format(self.pre_pos_4), level="debug")
            self.logme("pre_pos_4_switch: {}".format(self.pre_pos_4_switch), level="debug")
        
        if "pre_pos_5" in self.args: # a list with numeric value in % at index 0 and switch entity_id at index 1
            self.pre_pos_5 = float(self.args["pre_pos_5"][0])
            self.pre_pos_5_switch = self.args["pre_pos_5"][1]
            self.listen_state(self.__callback_buffer, entity=self.pre_pos_5_switch, new='on', position=self.pre_pos_5)
            self.logme("pre_pos_5: {}".format(self.pre_pos_5), level="debug")
            self.logme("pre_pos_5_switch: {}".format(self.pre_pos_5_switch), level="debug")
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)
    
    def __callback_buffer(self, entity, attribute, old, new, kwargs):
        position = kwargs.get('position')
        self.__set_position(entity, position)
    
    def __set_position(self, entity, position, *args, **kwargs):
        self.logme("{}".format(kwargs), level="debug")
        self.logme("position: {}".format(position), level="debug")
        t = self.__position_time(position)
        c = self.__get_current_position()
        self.turn_off(entity)
        if float(position) > float(c):
            self.__open()
            self.run_in(callback=self.__stop, delay=t, position=position)
        elif float(position) < float(c):
            self.__close()
            self.run_in(callback=self.__stop, delay=t, position=position)
        else:
            self.logme("Requested position was neither greater or less than current position: Current: {} - Requested: {}".format(c, position))
    
    def __position_time(self, position, *args, **kwargs):
        self.logme("", level="debug")
        full_time = self.full_transition_time
        c = float(self.__get_current_position())
        self.logme("Current Position: {}".format(c), level="debug")
        self.logme("New Position: {}".format(position), level="debug")
        d = abs((c) - (float(position)))
        self.logme("Difference in Position: {}".format(d), level="debug")
        # t = float(d) / float(full_time)
        if position == 0 or position == 100:
            t = ((float(full_time) / 100) * float(d)) + float(self.overrun_time)
            self.logme("transition_time: (({}/100) * {}) + {} = {}".format(full_time, d, self.overrun_time, t), level="debug")
        else:
            t = (float(full_time) / 100) * float(d)
            self.logme("transition_time: ({}/100) * {} = {}".format(full_time, d, t), level="debug")
        return float(t)
    
    def __nudge_open(self, entity, attribute, old, new, kwargs):
        a = kwargs.get("amount")
        self.logme("Nudge Open Amount: {}".format(a), level="debug")
        c = self.__get_current_position()
        n = float(c) + float(a)
        self.logme("Nudge Open New Position: {}".format(n), level="debug")
        self.__set_position(entity, n)

    def __nudge_close(self, entity, attribute, old, new, kwargs):
        a = kwargs.get("amount")
        self.logme("Nudge Close Amount: {}".format(a), level="debug")
        c = self.__get_current_position()
        n = float(c) - float(a)
        self.logme("Nudge Close New Position: {}".format(n), level="debug")
        self.__set_position(entity, n)

    def __open(self, *args, **kwargs):
        self.logme("", level="debug")
        self.turn_off(self.close_switch)
        self.turn_on(self.open_switch)
    
    def __close(self, *args, **kwargs):
        self.logme("", level="debug")
        self.turn_off(self.open_switch)
        self.turn_on(self.close_switch)

    def __stop(self, kwargs):
        position = kwargs.get("position")
        self.logme("", level="debug")
        self.turn_off(self.open_switch)
        self.turn_off(self.close_switch)
        self.__update_position(position)
    
    def __update_position(self, position, *args, **kwargs):
        self.logme("position: {}".format(position), level="debug")
        if float(position) > 100:
            self.logme("position is more than 100, tweaking....", level="debug")
            position = 100
        elif float(position) < 0:
            self.logme("position is less than 0, tweaking....", level="debug")
            position = 0
        else:
            pass
        self.call_service("mqtt/publish", topic=self.mqtt_sensor_topic, payload=int(position), retain=True)
        self.logme("Recliner Position: {}".format(position), level="info")
    
    def __get_current_position(self, *args, **kwargs):
        null_states = ["unknown", None, False]
        c = self.get_state(self.current_position_sensor)
        if c in null_states:
            self.call_service("mqtt/publish", topic=self.mqtt_sensor_topic, payload=0, retain=True)
        c = self.get_state(self.current_position_sensor)
        return c
        
