import appdaemon.plugins.hass.hassapi as hass


class Away(hass.Hass):

    def initialize(self):
        
        self.debug_mode = False

        self.switch = "input_boolean.someone_home"

        self.listen_state(self.start_turn_off, self.switch, new='off')
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)

    def start_turn_off(self, *args, **kwargs):
        lights_group = self.get_state("group.all_lights", attribute="all")
        lights_entity_list = lights_group['attributes']['entity_id']
        
        switch_group = self.get_state("group.light_switches", attribute="all")
        switch_entity_list = switch_group['attributes']['entity_id']
        self.logme("{}".format(switch_entity_list), 'debug')
        for i in switch_entity_list:
            self.logme("\n{}\n".format(i))
            self.turn_off(i)
        
        self.logme("{}".format(lights_entity_list), 'debug')
        for i in lights_entity_list:
            self.logme("\n{}\n".format(i))
            if self.get_state(i) == 'on':
                self.turn_off(i)
        
        self.turn_off("media_player.playroom_tv")
        if self.get_state("media_player.samsung_tv") == "on":
            self.call_service("remote/send_command", command="PowerToggle", device="Samsung TV", entity_id="remote.harmony_hub")

