import appdaemon.plugins.hass.hassapi as hass
import random
import time



class HolidayMode(hass.Hass):

    def initialize(self):
      
      self.trigger_switch = "input_boolean.holiday_mode"
      self.someone_home = "input_boolean.someone_home"
      
      self.listen_state(self.start_holiday_mode, self.trigger_switch, new='on')
      self.listen_state(self.end_holiday_mode, self.trigger_switch, new='off')
      self.listen_state(self.end_holiday_mode, self.someone_home, new='on')
      
      self.common_lights = ("switch.landing_light_switch_top", "switch.hall_light_switch_back", "switch.bathroom_light_switch")
      self.ensuite_lights = ("light.bedroom_lamp_1", "light.bedroom_lamp_2", "light.ensuite_light", "switch.olivias_lamp")
      self.living_area = ("light.dining_room_lamp_1", "light.dining_room_lamp_2", "light.standing_lamp", "light.living_room_lamp_1", "light.living_room_lamp_2", "light.living_room_lamp_3")
      self.outside_lights = ("switch.front_outside_light", "switch.back_outside_light_switch")
      self.playroom_lights = ("group.play_room_tv", "group.play_room_centre", "group.play_room_sofa", "group.playroom_lights")
    
    def start_holiday_mode(self, *args, **kwargs):
      pass
    
    def end_holiday_mode(self, *args, **kwargs):
      pass