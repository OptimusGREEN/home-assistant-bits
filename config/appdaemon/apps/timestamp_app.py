import appdaemon.plugins.hass.hassapi as hass
import time


class TimestampApp(hass.Hass):

    def initialize(self, *args, **kwargs):
        
        self.debug_mode = False

        self.trigger = self.args["trigger"]
        self.trigger_state = self.args["trigger_state"]
        self.timestamp_sensor = self.args["timestamp_sensor"]
        self.output_time_format = "timestamp"

        self.logme("trigger: {}".format(self.trigger), level="debug")
        self.logme("trigger_state: {}".format(self.trigger_state), level="debug")
        self.logme("timestamp_sensor: {}".format(self.timestamp_sensor), level="debug")

        otf = ("timestamp", "readable")

        if "output_time_format" in self.args:
            if self.output_time_format in otf:
                self.output_time_format = self.args["output_time_format"]
        self.logme("output_time_format: {}".format(self.output_time_format), level="debug")

        self.listen_state(self.start, self.trigger, new=self.trigger_state)
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)
    
    def start(self, *args, **kwargs):
        self.logme("", level="debug")
        output = ""
        if self.output_time_format == "timestamp":
            output = self.__get_timestamp()
        elif self.output_time_format == "readable":
            output = self.__get_readable()
        else:
            raise Exception("output_time_format not recognised")
        self.update_sensor(new_state=output)

    def update_sensor(self, new_state, *args, **kwargs):
        self.logme("New '{}' State: {}".format(self.timestamp_sensor, new_state))
        self.set_state(entity_id=self.timestamp_sensor, state=new_state)
    
    def __get_timestamp(self, *args, **kwargs):
        self.logme("", level="debug")
        return time.time()
    
    def __get_readable(self, *args, **kwargs):
        self.logme("", level="debug")
        return time.strftime("%d %b %Y %H:%M:%S", time.gmtime())