import appdaemon.plugins.hass.hassapi as hass

"""
    App to turn lights on when motion detected then off again after a delay while updating sensor for timer status
    
    Use with constrints to activate only for the hours of darkness
    
    Args:
    
    sensor: binary sensor to use as trigger
    entity_on : entity to turn on when detecting motion, can be a light, script, scene or anything else that can be turned on
    entity_off : entity to turn off when detecting motion, can be a light, script or anything else that can be turned off. Can also be a scene which will be turned on
    light_on_time: amount of time after turning on to turn off again. If not specified defaults to 60 seconds.
    countdown: Name of a sensor to be used to show the remaining time before the light is turned off (does not need to exist in HASS will be created automatically)
    
    Release Notes
    
    Version 1.2:
      Add sensor countdown
    
    Version 1.1:
      Add ability for other apps to cancel the timer
    
     Version 1.0:
       Initial Version
"""

class MotionLights(hass.Hass):

  def initialize(self, *args, **kwargs):
    
    self.light_on_handle = None
    self.light_delay_handle = None
    self.snapshot_delay_handle = None
    self.use_take_snapshot = False
    self.use_send_snapshot = False
    
    # Check some Params

    # Zero out the countdown
    self.set_countdown("-")
    # Subscribe to sensors
    if "sensor" in self.args:
      self.listen_state(self.motion, self.args["sensor"])
    else:
      self.log("No sensor specified, doing nothing")

    if "light_on_time" in self.args:
      self.light_on_time = self.args["light_on_time"]
    else:
      self.light_on_time = 60
    
    if "light_delay_time" in self.args:
      self.light_delay_time = self.args["light_delay_time"]
    else:
      self.light_delay_time = 10
    
    if "snapshot_delay_time" in self.args:
      self.snapshot_delay_time = self.args["snapshot_delay_time"]
    else:
      self.snapshot_delay_time = 30
    
    if "take_snapshot" in self.args:
      self.use_take_snapshot = True
      if "send_snapshot" in self.args:
        self.use_send_snapshot = True

    self.snapshot_delay_count = self.snapshot_delay_time
    self.light_on_count = self.light_on_time
    self.light_delay_count = self.light_delay_time
    
  def motion(self, entity, attribute, old, new, *args, **kwargs):
    if new == "on":
      self.snapshot_delay_count = self.snapshot_delay_time
      self.light_on_count = self.light_on_time
      self.light_delay_count = self.light_delay_time
      # turn light on
      if self.light_delay_time == 0:
        self.light_on()
      else:
        now = self.datetime()
        self.light_delay_handle = self.run_every(self.light_delay, now, 1)
      if self.use_take_snapshot:
        now = self.datetime()
        self.snapshot_delay_handle = self.run_every(self.snapshot_delay, now, 1)
    elif new == "off":
      self.cancel_timer(self.snapshot_delay_handle)
      self.cancel_timer(self.light_delay_handle)
      # self.cancel_timer(self.light_on_handle)
  
  def light_delay(self, *args, **kwargs):
    self.light_delay_count -= 1
    self.log("Light Delay Count: {}".format(self.light_delay_count))
    self.set_countdown(self.light_delay_count)
    if self.light_delay_count <= 0:
      self.light_on()
  
  def light_on(self, *args, **kwargs):
    if "entity_on" in self.args:
      if self.get_state("input_boolean.getting_dark").lower() == "on":
        self.log("Motion detected: turning {} on".format(self.args["entity_on"]))
        self.light_on_count = self.light_on_time
        self.turn_on(self.args["entity_on"])
    now = self.datetime()
    self.light_on_handle = self.run_every(self.light_check, now, 1)
  
  def light_check(self, *args, **kwargs):
    self.light_on_count -= 1
    self.log("Light On Count: {}".format(self.light_on_count))
    self.set_countdown(self.light_on_count)
    if self.light_on_count <= 0:
      self.cancel_timer(self.light_on_handle)
      if "entity_off" in self.args:
          self.log("Turning {} off".format(self.args["entity_off"]))
          self.turn_off(self.args["entity_off"])
      
  
  def snapshot_delay(self, *args, **kwargs):
    self.snapshot_delay_count -= 1
    self.log("Snapshot Count: {}".format(self.snapshot_delay_count))
    self.set_countdown(self.snapshot_delay_count)
    if self.snapshot_delay_count <= 0:
      self.cancel_timer(self.snapshot_delay_handle)
      self.take_snapshot()
  
  def take_snapshot(self, *args, **kwargs):
    self.call_service("camera.snapshot", entity_id="camera.backcam1", filename="/config/tmp/snapshot.jpg")
    if self.use_send_snapshot:
      self.send_snapshot()
  
  def send_snapshot(self, *args, **kwargs):
    self.call_service("notify/john", title="BackCam1", message="Motion Detected", data={"photo":{"file": "/config/tmp/snapshot.jpg"}})

    self.set_countdown("-")

  def set_countdown(self, value, *args, **kwargs):
    if "countdown" in self.args:
        self.set_state(self.args["countdown"], state = value)