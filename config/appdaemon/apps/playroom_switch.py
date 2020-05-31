import appdaemon.plugins.hass.hassapi as hass
import random
import time



class PlayroomSwitch(hass.Hass):

    def initialize(self):
        
        self.debug_mode = False
        
        self.off_flag = True

        self.switch_tl = "switch.playroom_tl"
        self.switch_tr = "switch.playroom_tr"
        self.switch_bl = "switch.playroom_bl"
        self.switch_br = "switch.playroom_br"
        
        self.switch_list = [self.switch_tl, self.switch_tr, self.switch_bl, self.switch_br]

        self.listen_state(self.tl_on, self.switch_tl, new='on')
        self.listen_state(self.tr_on, self.switch_tr, new='on')
        self.listen_state(self.bl_on, self.switch_bl, new='on')
        self.listen_state(self.br_on, self.switch_br, new='on')
        
        self.listen_state(self.tl_off, self.switch_tl, new='off')
        self.listen_state(self.tr_off, self.switch_tr, new='off')
        self.listen_state(self.bl_off, self.switch_bl, new='off')
        self.listen_state(self.br_off, self.switch_br, new='off')
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)

    
    def tl_on(self, *args, **kwargs):
        s = self.switch_tl
        scene = 'scene.dimmed_white_playroom'
        self.logme("activating 'dimmed white' via: {}".format(s))
        self.turn_on(scene)
        for sw in self.switch_list:
            self.logme("s: {} - sw: {}".format(s,sw), 'debug')
            if not sw == s:
                if self.get_state(sw) == 'on':
                    self.logme("turning off: {}".format(sw), 'debug')
                    self.turn_off(sw)
    
    def tr_on(self, *args, **kwargs):
        s = self.switch_tr
        scene = 'scene.white_playroom'
        self.logme("activating 'white playroom' via: {}".format(s))
        self.turn_on(scene)
        for sw in self.switch_list:
            self.logme("s: {} - sw: {}".format(s,sw), 'debug')
            if not sw == s:
                if self.get_state(sw) == 'on':
                    self.logme("turning off: {}".format(sw), 'debug')
                    self.turn_off(sw)
    
    def bl_on(self, *args, **kwargs):
        s = self.switch_bl
        scene = 'scene.cycle_playroom'
        self.logme("activating 'cycle playroom' via: {}".format(s))
        # scene = 'scene.celtic_playroom'
        # self.__logme("activating 'celtic playroom' via: {}".format(s))
        self.turn_on(scene)
        for sw in self.switch_list:
            self.logme("s: {} - sw: {}".format(s,sw), 'debug')
            if not sw == s:
                if self.get_state(sw) == 'on':
                    self.logme("turning off: {}".format(sw), 'debug')
                    self.turn_off(sw)
    
    def br_on(self, *args, **kwargs):
        s = self.switch_br
        scene = 'scene.coloured_playroom'
        self.logme("activating 'coloured_playroom' via: {}".format(s))
        self.turn_on(scene)
        for sw in self.switch_list:
            self.logme("s: {} - sw: {}".format(s,sw), 'debug')
            if not sw == s:
                if self.get_state(sw) == 'on':
                    self.logme("turning off: {}".format(sw), 'debug')
                    self.turn_off(sw)
    
    def tl_off(self, *args, **kwargs):
        s = self.switch_tl
        self.switch_off(sw=s)
    
    def tr_off(self, *args, **kwargs):
        s = self.switch_tr
        self.switch_off(sw=s)
    
    def bl_off(self, *args, **kwargs):
        s = self.switch_bl
        self.switch_off(sw=s)
    
    def br_off(self, *args, **kwargs):
        s = self.switch_br
        self.switch_off(sw=s)
    
    def switch_off(self, sw, *args, **kwargs):
        if sw in self.switch_list:
            self.logme("€€ switch list - {}".format(self.switch_list), 'debug')
            # self.__logme("€€€ switch in list", 'debug')
            self.switch_list.remove(sw)
            other_switches = self.switch_list
            self.logme("€€ other switches - {}".format(other_switches), 'debug')
        else:
            self.logme("€€€€ switch NOT in list", 'debug')
            other_switches = self.switch_list
        # self.__logme("€###€#€#€€#€€#€ - {} - €##€#€#€#€#€#€#€".format(other_switches), 'debug')
        for s in other_switches:
            if self.get_state(s) == "on":
                self.off_flag = False
        self.logme("flag: {}".format(self.off_flag), 'debug')
        if self.off_flag:
            group_item = self.get_state("group.play_room_lights", attribute="all")
            entity_list = group_item['attributes']['entity_id']
            for e in entity_list:
                self.logme("TURNING OFF LIGHT:\n\n{}\n\n".format(e))
                self.turn_off(e)
        self.off_flag = True
        self.switch_list = [self.switch_tl, self.switch_tr, self.switch_bl, self.switch_br]