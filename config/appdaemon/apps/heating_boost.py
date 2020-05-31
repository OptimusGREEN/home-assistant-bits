import appdaemon.plugins.hass.hassapi as hass
import datetime



class HeatingBoost(hass.Hass):

    def initialize(self):

        self.debug_mode = True

        self.thermostat = "climate.virtual_stat"

        self.switch = "input_boolean.heating_boost"
        self.selected_time = "input_select.heating_boost_duration"
        self.switch_on_time = None
        self.timer = None
        self.count = None

        self.reset_timer_sensor()

        self.listen_state(self.boost, self.switch, new='on')
        self.listen_state(self.turn_off_boost_switch, self.switch, new='off')
        self.listen_state(self.timer_change, self.selected_time)
        
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)
    
    def boost(self, *args, **kwargs):
        self.logme("", level='debug')
        self.turn_on("switch.heating")
        self.switch_on_time = self.datetime()
        self.start_timer()

    def start_timer(self, *args, **kwargs):
        self.logme("", level='debug')
        mins = int(self.get_state(self.selected_time))
        secs = mins*60
        self.count = secs
        now = self.datetime()
        t = now + datetime.timedelta(seconds=5)
        self.timer = self.run_every(self.countdown_loop, t, 1)
    
    def countdown_loop(self, *args, **kwargs):
        if self.get_state("switch.heating") == "off": # hacky thing as switch keeps turning off
            self.turn_on("switch.heating")
        self.count -= 1
        if self.count <= 0:
            self.log("Turning {} off".format(self.switch))
            self.turn_off_boost_switch()
            self.stop_timer()
        self.update_timer_sensor()
        
    
    def stop_timer(self, *args, **kwargs):
        self.logme("", level='debug')
        self.cancel_timer(self.timer)
        self.reset_timer_sensor()
    
    def turn_off_boost_switch(self, *args, **kwargs):
        self.logme("", level='debug')
        if self.get_state(self.switch) == 'on':
            self.logme("", level='debug')
            self.turn_off(self.switch)
        if not self.stat_state_active():
            self.logme("", level='debug')
            self.turn_off("switch.heating")
        self.stop_timer()
        self.switch_on_time = None
    
    def timer_change(self, *args, **kwargs):
        self.logme("", level='debug')
        if self.get_state(self.switch) == 'off':
            return
        self.stop_timer()
        self.start_timer()
    
    def update_timer_sensor(self, *args, **kwargs):
        t = datetime.timedelta(seconds=self.count)
        d = datetime.datetime(1,1,1) + t
        t = "{}:{}".format(d.minute, d.second)
        self.set_state(entity_id="sensor.heating_boost_timer", state=t)
        self.logme(t, level='debug')
    
    def reset_timer_sensor(self, *args, **kwargs):
        self.logme("", level='debug')
        self.set_state(entity_id="sensor.heating_boost_timer", state="-")
    
    def stat_state_active(self, *args, **kwargs):
        self.logme("", level='debug')
        target = self.get_state(entity_id=self.thermostat, attribute="temperature")
        current = self.get_state(entity_id=self.thermostat, attribute="current_temperature")
        if target > current:
            self.logme("Target: {} - Current: {}".format(target, current), level='debug')
            return True
        else:
            self.logme("Target: {} - Current: {}".format(target, current), level='debug')
            return False