import appdaemon.plugins.hass.hassapi as hass
import random
import time

class XmasLamp(hass.Hass):

    def initialize(self):
        
        self.debug_mode = True
        self.logme("initializing xmas lamp", 'debug')
        self.stop = False

        # for a in self.args:
        #     self.__logme("\n\n{}\n\n".format(a), 'debug')
        if "entities" in self.args:
            self.entities = self.args["entities"]
        else:
          self.entities = ["light.standing_lamp"]
          
        if "switch" in self.args:
            self.switch = self.args["switch"]
        else:
          self.switch = "input_boolean.xmas_standing_lamp"
        self.logme(self.entities)
        
        if "time" in self.args:
            self.time = self.args["time"]
        else:
          self.time = 30
        
        if "colours" in self.args:
            self.colours = self.args["colours"]
        else:
          self.colours = ["red", "green", "blue"]
        
        self.listen_state(self.start, self.switch, new='on')
    
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
        self.logme('in start', 'debug')
        self.logme('', 'debug')
        self.keep_running = True
        self.logme('in change engine', 'debug')
        self.colour_index = 0
        self.change_engine()
        
    def change_engine(self, *args, **kwargs):
        if self.get_state(self.switch) == 'on':
            for l in self.entities:
                if not self.stop:
                    self.l = l
                    self.rc = self.colours[self.colour_index]
                    self.logme("{} is {}".format(l, self.rc), 'debug')
                    # self.turn_on(l, brightness='250', color_name=rc)
                    self.turn_on(self.l, brightness='250', color_name=self.rc)
                    self.run_in(self.run_in_callback, delay=self.time)
                    if self.colours[self.colour_index] == self.colours[-1]:
                        self.colour_index = 0
                    else:
                        self.colour_index += 1
        else:
          for e in self.entities:
            self.turn_off(e)
    
    def run_in_callback(self, *args, **kwargs):
        self.turn_on(self.l, brightness='250', color_name=self.rc)
        self.change_engine()

