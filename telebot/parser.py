import bs4
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# url = "http://212.220.202.105:8080/RINEX/RINEX/2023/"
# responce = requests.get(url=url)
# with open('index.html', 'w') as file:
#     file.write(responce.text)


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
        dates_and_times = [datetime.strptime(item.text, " %Y-%m-%d %H:%M") for item in item_ts]
        # print(f"dates and times: {dates_and_times}")
        return dates_and_times

    def get_date_href_dict(self) -> dict:
        """This method create dict. Key - integer date, value - href from href_list"""
        href_list = self.get_href_list()
        date_list = [int(date.split('(')[0]) for date in href_list]
        return dict(zip(date_list, href_list))


if __name__ == '__main__':
    url = "http://212.220.202.105:8080/RINEX/RINEX/2023/"
    url_2 = "http://212.220.202.105:8080/RINEX/RINEX/2023/001(0101)/"
    url_3 = "http://212.220.202.105:8080/RINEX/RINEX/2023/001(0101)/TOUR/"
    p = Parser(url_3)
    # print(p.get_date_href_dict())
    print(p.get_href_list())
    # http://212.109.197.194/admin/
