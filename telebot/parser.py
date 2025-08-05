import bs4
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import logging

logger = logging.getLogger(__name__)


class Parser:
    """This class need for parsing data for telegram bot"""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
    }

    def __init__(self, url: str):
        self.url = url

    def get_data(self) -> requests.models.Response:
        """This method scrap data from web site"""
        logger.info(f"get request to url: {self.url}")
        return requests.get(url=self.url, headers=self.headers)

    def open_index_file(self, path: str) -> str:
        """This is testing developer method"""
        with open(path) as file:
            src = file.read()
        return src

    def create_bs4_obj(self, src) -> bs4.BeautifulSoup:
        """This method create bs4 object"""
        return BeautifulSoup(src, "lxml")

    def get_href_list(self) -> list:
        """This method find href in the page on form list with hrefs"""
        src = self.get_data().text
        soup = self.create_bs4_obj(src)
        item_links = soup.find_all("div", class_="item-link")
        href_list = [link.find('a').get("href") for link in item_links]
        return href_list

    def get_datetime(self) -> list:
        """This method find datetime in the page on form list with datetime"""
        src = self.get_data().text
        soup = self.create_bs4_obj(src)
        item_ts = soup.find_all("span", class_="item-ts")
        # for item in item_ts:
        #     print(f"item: {item}, text: <{item.text}>")
        # dates_and_times = [datetime.strptime(item.text, " %Y.%m.%d %H:%M") for item in item_ts]
        dates_and_times = [datetime.strptime(item.text, " %d.%m.%Y %H:%M") for item in item_ts]
        # print(f"dates and times: {dates_and_times}")
        return dates_and_times

    def get_date_href_dict(self) -> dict:
        """This method create dict. Key - integer date, value - href from href_list"""
        href_list = self.get_href_list()
        date_list = [int(date.split('(')[0]) for date in href_list]
        return dict(zip(date_list, href_list))

    @staticmethod
    def decode_one_node(node: str) -> str:
        """This method decode one node and replace / symbol"""
        if node[-1] == "/":
            return urllib.parse.unquote(node[:-1], encoding='utf-8')
        else:
            return urllib.parse.unquote(node, encoding='utf-8')

    def get_decode_names_list(self, encode_list: list) -> list:
        """This method decode list of byte string to UTF-8"""
        logger.info(f"decode list: {encode_list}")
        return list(map(self.decode_one_node, encode_list))

    @staticmethod
    def get_encode_names_list(decode_list: list) -> list:
        """This methode encode list of string with byte string"""
        logger.info(f"encode list: {decode_list}")
        return [urllib.parse.quote(node, encoding='utf-8') for node in decode_list]

    @staticmethod
    def get_encode_one_node(node: str) -> str:
        """This methode encode one string with byte string"""
        logger.info(f"encode node: {node}")
        return urllib.parse.quote(node, encoding='utf-8')

    @staticmethod
    def check_this_is_file(name: str) -> bool:
        """This method check end of file to need format"""
        logger.info(f"Check name file is are not -> {name}")
        end_files = {"png", "bmp", "pdf", "rtx", "doc", "mp4", "dwg", "las", "laz", "pptx", "rar", "zip", "txt",  "rtf"}
        end_file = name.split(".")[-1]
        logger.info(f"End of file: {end_file}")
        if end_file in end_files:
            return True
        else:
            return False

if __name__ == '__main__':
    # url = "http://212.220.202.105:8080/RINEX/RINEX/2023/"
    # url_2 = "http://212.220.202.105:8080/RINEX/RINEX/2023/001(0101)/"
    # url_3 = "http://212.220.202.105:8080/RINEX/RINEX/2023/001(0101)/TOUR/"
    url_4 = "http://212.220.202.105:8080/GD_data/"

    def use_logic(url: str):
        p = Parser(url=url)
        data = p.get_href_list()
        decode_list = p.get_decode_names_list(encode_list=data)
        print(f"directories -> {decode_list}")
        index = int(input("Choice directory"))
        directory = decode_list[index]
        check_file = p.check_this_is_file(name=directory)
        if check_file:
            print(f"I find file -> {directory}")
        else:
            print(f"This is not file")
            use_logic(url=url + p.get_encode_one_node(node=directory) + "/")

    use_logic(url=url_4)
