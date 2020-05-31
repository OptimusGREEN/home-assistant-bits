import appdaemon.plugins.hass.hassapi as hass
import random
import time



class OutsideLux(hass.Hass):

    def initialize(self):
        self.solar_elevation = None
        self.solar_daylight = None
        self.lux = None
        # self.run_in(callback=self.start, delay=30)
        self.start()

    def start(self, *args, **kwargs):
        azimuth = self.get_state("sun.sun", attribute="azimuth")
        elevation = self.get_state("sun.sun", attribute="elevation")
        self.solar_elevation = elevation
        self.calculate()
    
    def calculate(self, *args, **kwargs):
        import math
        cloud_coverage = self.get_state("sensor.dark_sky_cloud_coverage", attribute="state")
        cloud_factor = 1 - (0.75 * ( float(cloud_coverage) / 100) ** 3 )
        if self.solar_elevation > 1:
          self.solar_daylight = 172278 * (0.271 + 0.706 * math.pow(0.6,math.sqrt(1229+math.pow(614*math.sin(0.01745*self.solar_elevation),2))-614*math.sin(0.01745*self.solar_elevation))) * math.sin(0.01745*self.solar_elevation)
        elif self.solar_elevation > -7:
          self.solar_daylight = 6 - (1-self.solar_elevation)/8*6   
        else:
          self.solar_daylight = 0
        
        # self.log("LUX = {}".format(round(self.solar_daylight)))
        # self.log("cloud_coverage = {}".format(cloud_coverage))
        # self.log("cloud_factor = {}".format(cloud_factor))
        # self.log("Final Lux = {}".format(cloud_factor * self.solar_daylight))
        # self.log("WF Final Lux = {}".format(cloud_factor * self.solar_daylight * self.weather_factor()))
        self.lux = round(cloud_factor * self.solar_daylight * self.weather_factor())
        self.set_lux()
        self.wait()
    
    def set_lux(self, *args, **kwargs):
        self.set_state(entity_id="sensor.outside_lux", state=self.lux)
    
    def weather_factor(self, *args, **kwargs):
        weather = self.get_state("sensor.dark_sky_icon", attribute="state")
        factor = 1
        factors_dict = {
            "clear-day": 1,
            "clear-night": 1,
            "rain": 0.3,
            "snow": 0.7,
            "sleet": 0.5,
            "wind": 1,
            "fog": 0.1,
            "cloudy": .6,
            "partly-cloudy-day": .8,
            "partly-cloudy-night": 1,
            "hail": 0.4,
            "lightning": 0.3
        }
        try:
            factor = factors_dict.get(weather)
        except Exception as e:
            self.log(e)
        self.log("Weather Factor = {}: {}".format(weather, factor))
        return factor
    
    def wait(self, *args, **kwargs):
        self.run_in(callback=self.start, delay=300)

        

