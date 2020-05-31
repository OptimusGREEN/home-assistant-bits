
from bs4 import BeautifulSoup
from json import loads
import re, requests
import logging, time
# from libs.magnetic import mglobals

# logging.basicConfig(level=logging.DEBUG,
#                     format="[%(levelname)s] [%(module)s:%(lineno)d] " + " - %(asctime)s - %(message)s")

# path = mglobals.base_path

class Magnetic(object):
    
    def __init__(self, proxies=None):
        logging.info("Initializing Magnetic")
        
        self.query = None
        self.limit = None
        self.max_size = None
        self.get_largest = False
        self.magnets = []
        self.filters = []
        self.proxies = proxies

        self.retries_count = 0

    def __rarbg(self):
        logging.debug("magnetizing rarbg")
        print(self.query)
        try:
            main_link = 'https://torrentapi.org/pubapi_v2.php?mode=search&search_string=' + self.query + '&token=lnjzy73ucv&format=json_extended&app_id=lol'
            main_request = requests.get(main_link, headers={'User-Agent': 'Mozilla/5.0'}, proxies=self.proxies)
            logging.debug("request: {}".format(main_request.json()))
            main_source = loads(main_request.content)
            if 'torrent_results' in main_source:
                logging.debug("rarbg: source: type: {}  {}".format(type(main_source), main_source))
                tor_list = main_source["torrent_results"]
                titles = []
                seeders = []
                leechers = []
                sizes = []
                dates = []
                size_magnet_dict = {}
                tor_list = self.__filter_magnet_list(tor_list)
                self.limit_counter = 0
                for i in tor_list:
                    if self.limit_counter < self.limit:
                        seeders.append(i["seeders"])
                        leechers.append(i["leechers"])
                        sizes.append(i["size"])
                        dates.append(i["pubdate"].split(" +")[0])
                        size_magnet_dict[i["size"]] = i["download"]
                        self.magnets.append(i["download"])
                        self.limit_counter = + 1
                if self.get_largest:
                    self.magnets = []
                    largest = self.__filterOnlyLargest(size_magnet_dict)
                    self.magnets.append(largest)
        except Exception as e:
            logging.warning(e, stack_info=True, exc_info=True)

    def __tpb(self):
        logging.debug("magnetizing tpb")
        try:
            main_link = 'https://tpb.party/search/' + self.query + '/1/99/0/'
            main_request = requests.get(main_link, headers={'User-Agent': 'Mozilla/5.0'}, proxies=self.proxies)
            main_source = main_request.content
            # print(main_request.json())
            logging.debug("tpb: source: type: {}  {}".format(type(main_source), main_source))
            main_soup = BeautifulSoup(main_source, 'lxml')
            sizes_soup = main_soup.findAll('font', class_="detDesc")
            magnets_soup = main_soup.findAll('a', attrs={'href': re.compile("^magnet")})
            self.limit_counter = 0
            for magnet in magnets_soup:
                if self.limit_counter < self.limit:
                    self.magnets.append(magnet.get('href'))
                    self.limit_counter = self.limit_counter + 1
        except Exception as e:
            logging.warning(e, stack_info=True, exc_info=True)


    def __rerun(self, search_query, sites, scrape_limit, max_file_size_gb, filters, only_get_largest):
        time.sleep(5)
        self.retries_count += 1
        self.magnetyze(search_query, sites, scrape_limit, max_file_size_gb, filters, only_get_largest)


    def __filterOnlyLargest(self, dict):
        key_list = []
        for size, magnet in dict.items():
            logging.debug(size)
            key_list.append(size)
        largest = sorted(key_list, reverse=True)[0]
        logging.debug(largest)
        result = dict.get(largest)
        logging.debug(result)
        return result

    def __filter_magnet_list(self, tor_list):
        if not self.filters:
            return tor_list
        new_tor_list = []
        filter_match = False
        for tor in tor_list:
            magnet_title = tor["title"]
            for l in self.filters:
                # print(l)
                if filter_match:
                    l = filter_match
                if isinstance(l, str):
                    if "," in l:
                        l = l.split(",")
                    elif " " in l:
                        l = l.split(" ")
                if all(x in magnet_title.lower() for x in l):
                    print("* MATCH * Filter: {} is in {}".format(l, magnet_title))
                    new_tor_list.append(tor)
                    filter_match = l
                    break
                else:
                    print("Filter: {} is Not in {}".format(l, magnet_title))
        return new_tor_list

    def magnetyze(self, search_query, sites=None, scrape_limit=None, max_file_size_gb=None, filters=None, only_get_largest=False, retries=4):
        search_query = search_query.translate({ord(i):None for i in '\'"!@#$'})
        logging.info("Magnetizing [{}], this might take a few minutes...".format(search_query))
        print("Magnetizing [{}], this might take a few minutes...".format(search_query))
        if not sites:
            sites = ("rarbg")
        if not scrape_limit:
            scrape_limit = 10
        if not max_file_size_gb:
            max_file_size_gb = 3
        if only_get_largest:
            self.get_largest = True
        self.magnets = []
        self.filters = filters
        func_dict = {"tpb": self.__tpb,
                     "rarbg": self.__rarbg}
        self.limit = scrape_limit
        self.query = search_query
        self.max_size = max_file_size_gb
        if isinstance(sites, (list, tuple)):
            for site in sites:
                scrape = func_dict[site]
                scrape()
        else:
            scrape = func_dict[sites]
            scrape()
        if len(self.magnets) > 0:
            self.retries_count = 0
            return self.magnets
        if self.retries_count >= retries:
            return
        else:
            self.__rerun(search_query, sites, scrape_limit, max_file_size_gb, filters, only_get_largest)



# import libs.my_secrets as secret
# magnetic = Magnetic(proxies=secret.pia_proxies)
#
# magnet_query_filters = [["2160", "265"],
#                         ["2160", "hevc"],
#                         ["1080", "265"],
#                         ["1080", "hevc"],
#                         ["1080"]]
# mags = magnetic.magnetyze("Manhunt s02e01", scrape_limit=50, sites=['rarbg'], filters=magnet_query_filters, only_get_largest=False)
# if mags:
#     print("\n")
#     for mag in mags:
#         print(mag)