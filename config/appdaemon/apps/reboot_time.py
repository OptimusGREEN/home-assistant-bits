import appdaemon.plugins.hass.hassapi as hass
# from globals.modules.database import DataBase


class GetRestartTime(hass.Hass):

    def initialize(self):
        
        self.debug_mode = False

        self.use_db = False

        # if "use_db" in self.args:
        #     self.use_db = True
        #     self.user = self.args["user"]
        #     self.password = self.args["password"]

        #     self.db_cnx = DataBase(self.user, self.password)

        #     self.listen_state(self.db_set_shutdown_time, "input_boolean.restart_homeassistant", new="on")

        self.update_sensor()
    
    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)
    
    def last_shutdown_time(self, *args, **kwargs):
        if not self.use_db:
            sensor = "sensor.timestamp_stopped"
            last_shutdown = self.get_state(sensor)
            self.logme("Last Shutdown: {}".format(last_shutdown), 'debug')
            return last_shutdown
        
        # try:
        #     last_shutdown = self.db_cnx.read(table="timestamps", known_col="name", row_id="last_shutdown", target_col="timestamp")
        #     return last_shutdown
        # except Exception as e:
        #     self.__logme("Error: {}".format(e))
        #     return
        
    def startup_time(self, *args, **kwargs):
        import time
        return time.time()
        # if not self.use_db:
        #     sensor = "sensor.timestamp_started"
        #     startup = self.get_state(sensor)
        #     self.__logme("Startup: {}".format(startup), 'debug')
        #     return startup
        # else:
        #     try:
        #         startup = self.db_cnx.read("timestamps", "name", "start_time", "timestamp")
        #         return startup
        #     except Exception as e:
        #         self.__logme("Error: {}".format(e))
        #         return
    
    def duration(self, *args, **kwargs):

        import datetime
        import dateutil.relativedelta
        try:
            dt1 = datetime.datetime.fromtimestamp(float(self.last_shutdown_time()))
        except:
            return "N/A"
        dt2 = datetime.datetime.fromtimestamp(float(self.startup_time()))
        rd = dateutil.relativedelta.relativedelta (dt2, dt1)
        
        if rd.minutes > 1:
            return "%d mins %d secs" % (rd.minutes, rd.seconds)
        elif rd.minutes < 1:
            return "%d secs" % (rd.seconds)
        else:
            return "%d min %d secs" % (rd.minutes, rd.seconds)
    
    def update_sensor(self, *args, **kwargs):
        dur = self.duration()
        self.logme("Restart Duration: {}".format(dur))
        self.set_state(entity_id="sensor.restart_duration", state=dur)
    
    # def db_set_startup_time(self, *args, **kwargs):
    #     import time
    #     self.db_cnx.write(table="timestamps", headings=("name", "timestamp"), data=("start_time", time.time()))

    # def db_set_shutdown_time(self, *args, **kwargs):
    #     import time
    #     self.db_cnx.write("timestamps", ("name", "timestamp"), ("last_shutdown", time.time()))