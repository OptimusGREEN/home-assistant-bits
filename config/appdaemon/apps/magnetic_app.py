import appdaemon.plugins.hass.hassapi as hass
from globals.modules.magnetic import Magnetic
import globals.modules.my_secrets as secret
import humanize

class MagneticApp(hass.Hass):

    def initialize(self):
        
        self.debug_mode = True

        self.text_input_entity = self.args["text_input_entity"]
        self.search_button = self.args["search_button_entity"]
        self.results_sensor = self.args["results_sensor"]
        self.filters = None
        self.query = None
        self.results = None

        if "use_proxies" in self.args:
            self.magnetic = Magnetic(proxies=secret.digital_ocean_proxies)
        else:
            self.magnetic = Magnetic()

        if "filters" in self.args:
            self.filters = self.args["filters"]
        
        self.listen_state(self.__read_text_box, entity=self.text_input_entity)
        self.listen_state(self.__search_magnets, entity=self.search_button, new='on')

    def logme(self, string, level="info", *args, **kwargs):
        if level == "debug":
            if self.debug_mode:
                import inspect
                frame = inspect.currentframe().f_back
                line = "Line: " + str(frame.f_lineno)
                self.log("[{}] - {}".format(line, string))
        else:
            self.log(string)
    
    def __read_text_box(self, *args, **kwargs):
        self.query = self.get_state(self.text_input_entity)
        self.logme("query = {}".format(self.query))

    def __search_magnets(self, *args, **kwargs):
        self.set_state(entity_id=self.results_sensor, state="Searching")
        mags = self.magnetic.magnetyze(self.query, scrape_limit=50, sites=['rarbg'], filters=self.filters, only_get_largest=False, get_size_magnet_dict=True)
        if mags:
            # res = "**Magnet Results for {}**\n\n\n".format(self.query)
            count = 1
            total_mags = len(mags)
            for size, mag in mags.items():
                id = "sensor.magnetic_magnet_link_{}".format(count)
                # res += "`{}`".format(mag) + "\n\n"
                self.set_state(entity_id=id, state=self.query, attributes={"friendly_name": "Magnet {} {}".format(self.query, count), "quality": self.__get_quality(mag), "size": humanize.naturalsize(size), "results": mag})
                count += 1
                if count == 10:
                    total_mags = 10
                    break
            res = "{} magnets found".format(total_mags)
            self.set_state(entity_id=self.text_input_entity, state="")
            self.set_state(entity_id=self.results_sensor, state=res)
        else:
            res = "Unable to get any magnet links."
            self.set_state(entity_id=self.text_input_entity, state=self.query)
        self.results = res
        self.turn_off(self.search_button)
        self.logme("\n\n###############\n{}\n#################\n\n".format(self.results), level="debug")
        self.__populate_results_text()
    
    def __populate_results_text(self, *args, **kwargs):
        self.set_state(entity_id=self.results_sensor, state=self.results)
    
    def __get_quality(self, mag, *args, **kwargs):
        q = [["2160", "265"],["2160", "hevc"],["1080", "265"],["1080", "hevc"],["1080"]]
        for i in q:
            if all(x in mag.lower() for x in i):
                quality = " ".join(str(x) for x in i)
        return quality
    

# {% for state in states.sensor %}
# {% if state.entity_id.startswith('sensor.magnetic_magnet_link_') %}
# {{ state.name }}
# {{ "Quality" }}: {{ state_attr(state.entity_id, 'quality') }}
# {{ "Size" }}: {{ state_attr(state.entity_id, 'size') }}
# {{ state_attr(state.entity_id, 'results') }}

# -----------------------------

# {% endif %}
# {% endfor %}
