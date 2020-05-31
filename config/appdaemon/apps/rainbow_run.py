import appdaemon.plugins.hass.hassapi as hass
import random
import time



class RainbowRun(hass.Hass):

    def initialize(self):
        
        self.debug_mode = False

        # for a in self.args:
        #     self.__logme("\n\n{}\n\n".format(a), 'debug')
        if "entities" in self.args:
            self.entities = self.args["entities"]
        if "switch" in self.args:
            self.switch = self.args["switch"]
        self.end_state = 'on'
        self.keep_running = False
        self.logme(self.entities)

        if 'master_switch' in self.args:
            self.logme('', 'debug')
            self.master_switch = self.args["master_switch"]
        else:
            self.logme('', 'debug')
            self.master_switch = None

        if "end_state" in self.args:
            if self.args["end_state"] in ['on', 'off']:
                self.end_state = self.args["end_state"]

        self.start_listener = self.listen_state(self.start, self.switch, new='on')
        self.stop_listener = self.listen_state(self.stop, self.switch, new='off')


        if self.master_switch:
            self.logme("Rainbow Run Master Switch In Use: {}".format(self.master_switch), 'debug')
            self.master_stop_listener = self.listen_state(self.master_switch_stop, self.master_switch, new='off')


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
        if not self.master_switch:
            self.logme('', 'debug')
            self.keep_running = True
            self.change_engine()
        else:
            self.logme('', 'debug')
            if self.get_state(self.master_switch) == 'off':
                self.logme('', 'debug')
                self.turn_on(self.master_switch)
                self.keep_running = True
                self.change_engine()
            else:
                self.logme('', 'debug')
                self.keep_running = True
                self.change_engine()

    def change_engine(self, *args, **kwargs):
        self.logme('in change engine', 'debug')
        self.logme(self.get_state(self.master_switch), 'debug')
        colour_index = 0
        colours = ["red", "green", "blue", "gold", "deeppink", "cyan"]
        random.shuffle(colours)

        if self.keep_running:
            for l in self.entities:
                self.l = l
                self.logme("master = {}".format(self.get_state(self.master_switch)), 'debug')
                if self.keep_running:
                    self.rc = colours[colour_index]
                    # self.__logme("{} is {}".format(l, rc), 'debug')
                    # self.turn_on(l, brightness='250', color_name=rc)
                    self.run_in(self.run_in_callback, delay=1)
                    if colours[colour_index] == colours[-1]:
                        colour_index = 0
                    else:
                        colour_index += 1
                else:
                    if self.get_state(self.master_switch) == 'off':
                        self.stop()
        if self.get_state(self.switch) == 'on' and self.keep_running:
            self.logme("", 'debug')
            self.change_engine()
    
    def run_in_callback(self, *args, **kwargs):
        self.turn_on(self.l, brightness='250', color_name=self.rc)

    def stop(self, *args, **kwargs):
        self.logme('in stop', 'debug')
        self.keep_running = False
        self.run_in(callback=self.set_end_state, delay=2)

    def set_end_state(self, *args, **kwargs):
        if self.end_state == 'on':
            for l in self.entities:
                self.turn_on(l, color_name="white")
        else:
            for l in self.entities:
                self.turn_off(l)

    def master_switch_stop(self, *args, **kwargs):
        self.logme('in master stop', 'debug')
        self.cancel_listen_state(self.stop_listener)
        self.keep_running = False
        self.end_state = 'off'
        self.stop()

    def random_colour(self, amount=3, *args, **kwargs):
        l = []
        for a in range(3):
            l.append(random.choice(range(256)))
        return l

    def random_colour_name(self, *args, **kwargs):
        colours = ["red", "green", "blue", "yellow", "purple", "pink", "orange", "lime"]
        out = random.choice(colours)
        return out

