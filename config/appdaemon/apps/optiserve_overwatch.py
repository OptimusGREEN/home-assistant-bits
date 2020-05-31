import appdaemon.plugins.hass.hassapi as hass

class Overwatch(hass.Hass):

    def initialize(self):

        self.debug_mode = False

        self.listen_event(self.__log_mqtt_message, "MQTT_MESSAGE", namespace="mqtt")
        self.listen_event(self.__check_and_execute, "MQTT_MESSAGE", namespace="mqtt")

        # self.__logme(self.get_plugin_config())

    def __log_mqtt_message(self, event_name, data, kwargs):
        # self.__logme("Event Name: {} \n".format(event_name), level='debug')
        self.__logme("\nTopic: {} \nPayload: {}\n".format(data["topic"], data["payload"]), level='debug')

    def __logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)
    
    def __check_and_execute(self, event_name, data, kwargs):
        topic = data["topic"]
        cb = self.__get_callback(topic)
        if cb:
            cb(data["payload"])


    def __get_callback(self, topic, *args, **kwargs):
        self.__logme("topic: {}".format(topic), level="debug")
        cb_dict = {"OptiSERVE/system2mqtt/LWT": self.__restart_system2mqtt}
        for k, v in cb_dict.items():
            if k == topic:
                return v
        return

    ############## Callbacks #################

    def __restart_system2mqtt(self, payload, *args, **kwargs):
        self.__logme("", level="debug")
        if payload == "offline":
            self.__logme("Restarting System2Mqtt Script")
            self.call_service("shell_command/start_system2mqtt")
