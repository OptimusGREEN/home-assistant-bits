import appdaemon.plugins.hass.hassapi as hass



class AverageTemperature(hass.Hass):

    def initialize(self):

        self.sensors = ("sensor.bedroom_temperature", "sensor.ben_temperature", "sensor.olivia_temperature", "sensor.lounge_temperature", "sensor.playroom_temperature")
        self.valid_sensors = None
        self.total_temp = None
        self.average = None

        for sensor in self.sensors:
            self.listen_state(self.start, sensor)
        
        self.start()

    def start(self, *args, **kwargs):
        self.get_valid_sensors()
        self.calculate_average_temperature()
        self.update_average_temp()
    
    def update_average_temp(self, *args, **kwargs):
        self.set_state(entity_id='sensor.average_room_temp', state=self.average)
    
    def get_valid_sensors(self, *args, **kwargs):
        v_sensors = 0
        total = 0
        for sensor in self.sensors:
          state = self.get_state(sensor)
          try:
            float(state)
            v_sensors += 1
            total += float(state)
          except:
            pass
        self.valid_sensors = v_sensors
        self.total_temp = total
    
    def calculate_average_temperature(self, *args, **kwargs):
        if self.valid_sensors > 1:
          average = round(self.total_temp / self.valid_sensors, 1)
        elif self.valid_sensors == 1:
          average = round(self.total_temp, 1)
        else:
          average = 'null'
        self.average = average

