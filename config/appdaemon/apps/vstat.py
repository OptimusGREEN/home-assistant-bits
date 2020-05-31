import appdaemon.plugins.hass.hassapi as hass



class Vstat(hass.Hass):

    def initialize(self):
        
        self.debug_mode = False

        self.areas_dict ={"Average": "sensor.average_room_temp",
                          "Lounge": "sensor.lounge_temperature", 
                          "Bedroom": "sensor.bedroom_temperature",
                          "Olivia's Room": "sensor.olivia_temperature",
                          "Ben's Room": "sensor.ben_temperature",
                          "Playroom": "sensor.playroom_temperature"}
        
        self.target_area = None
        self.target_area_temp = None
        self.target_area_sensor = None

        self.listen_state(self.__set_target_area, "input_select.heating_area")
        self.listen_state(self.__set_target_area_temp, self.target_area_sensor)

        self.__set_target_area()
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)

    def __set_target_area(self, *args, **kwargs):
        self.logme("", level="debug")
        self.target_area = self.get_state("input_select.heating_area")
        self.logme("Setting Target Area to: {}".format(self.target_area), level="info")
        self.target_area_sensor = self.areas_dict.get(self.target_area)
        self.logme("Area: {} - Sensor: {}".format(self.target_area, self.target_area_sensor), level="debug")
        self.__set_target_area_temp()
    
    def __set_target_area_temp(self, *args, **kwargs):
        self.logme("", level="debug")
        if not self.target_area_sensor:
            self.logme("No Sensor!!!, Setting to Average...", level="warning")
            self.set_state(entity_id="input_select.heating_area", state="Average")

        else:
            sensor_state = self.get_state(self.target_area_sensor)
            self.logme("Sensor State: {}".format(sensor_state), level="debug")

        try:
            self.logme("", level="debug")
            float(sensor_state)
            self.target_area_temp = sensor_state
            self.__update_vstat_current_temp()
        except Exception as e:
            self.logme("", level="debug")
            self.log(e)
            self.set_state(entity_id="input_select.heating_area", state="Average")
    
    def __update_vstat_current_temp(self, *args, **kwargs):
        self.logme("", level="debug")
        self.set_state(entity_id='sensor.virtual_stat_current_temp', state=self.target_area_temp)

