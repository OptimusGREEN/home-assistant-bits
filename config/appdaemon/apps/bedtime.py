import appdaemon.plugins.hass.hassapi as hass
import random
import time



class Bedtime(hass.Hass):

    def initialize(self):

        self.debug_mode = False

        self.switch = "input_boolean.bedtime_switch"
        self.delayed_func = None
        self.delayed_light = ["light.hall_front", "switch.kitchen_light_switch"]

        self.delay1_time = 300
        self.delay2_time = 720

        self.listen_state(self.turn_off_instantly, self.switch, new='on')
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)
    
    def turn_off_instantly(self, *args, **kwargs):
        group_item = self.get_state("group.bedtime_downstairs_lights", attribute="all")
        entity_list = group_item['attributes']['entity_id']

        self.turn_on("input_boolean.no_recline")

        for i in entity_list:
            self.logme("\n{}\n".format(i), level='debug')
            if self.get_state(i) == 'on':
                self.turn_off(i)
        self.logme("", level="debug")
        # self.turn_off("media_player.playroom_tv")
        self.turn_off("media_player.lounge_tv")
        # if self.get_state("media_player.samsung_tv") == "on":
        #     self.call_service("remote/send_command", command="PowerToggle", device="Samsung TV", entity_id="remote.harmony_hub")
        
        # self.turn_on_req_light
        # if self.get_state(self.switch) == 'on' and self.get_state(self.delayed_light[0]) == 'on':
        self.run_in(callback=self.turn_on_req_light, delay=0.5)
        if self.get_state(self.switch) == 'on':
            self.run_in(callback=self.turn_off_delayed, delay=self.delay1_time)
            self.run_in(callback=self.turn_off_floor_lighting, delay=self.delay2_time)
        else:
            self.end()
    
    def turn_on_req_light(self, *args, **kwargs):
        self.logme("", level="debug")
        self.turn_on(self.delayed_light[0], brightness='100')
        self.turn_on("switch.under_bed_light")

    def turn_off_delayed(self, *args, **kwargs):
        self.logme("", level="debug")
        if self.get_state(self.switch) == 'on':
            self.logme("")
            for i in self.delayed_light:
                self.logme("\n{}\n".format(i), level="debug")
                self.turn_off(i)
            self.end()
        else:
            self.logme("", level="debug")
            self.end()
    
    def turn_off_floor_lighting(self, *args, **kwargs):
        self.logme("", level="debug")
        self.turn_off("switch.under_bed_light")

    def end(self, *args, **kwargs):
        if self.get_state(self.switch) == 'on':
            self.turn_off(self.switch)

