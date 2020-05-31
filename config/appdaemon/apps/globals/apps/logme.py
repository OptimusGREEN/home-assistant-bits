
import appdaemon.plugins.hass.hassapi as hass

class LogMe(hass.Hass):

    def initialize(self):
        pass
    
    def logme(self, string, level="info", *args, **kwargs):
        if not level == "debug":
            self.log(string)
        else:
            self.debug(string, level)
            
    
    def debug(self, string, level="info", *args, **kwargs):
        import inspect
        frame = inspect.currentframe().f_back.f_back
        line = "Line: " + str(frame.f_lineno)
        module = str(inspect.getframeinfo(frame, context=1)[0].split("/")[-1])
        self.log("[{}]:[{}] - {}".format(module, line, string))