import re
import time
import logging
from typing import Union
import datetime
import os
import gzip

from bs4 import BeautifulSoup
from curl_cffi.requests import Session

logger = logging.getLogger(__name__)



class EfemerideDownloadrer:
    impersonate = "chrome110"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    @staticmethod
    def remove_file(path: str):
        logger.info(f"Remove file for path: {path}")
        os.remove(path=path)

    def get_one_efemeride(self, str_date_list: list):
        logger.info(f"get one archive: {str_date_list}")
        archive_list = self.download_archive(str_data_list=str_date_list)
        logger.info(f"Get archives_list: {archive_list}")
        file_path = self.unzip_archive(archive_path=archive_list[0])
        logger.info(f"Get file_path: {file_path}. Remove archives")
        # remove archive file
        self.remove_file(path=archive_list[0])
        return file_path

    def download_archive(self, str_data_list: list[datetime.date], save_path: str = "./tmp_archives") -> Union[list, bool]:
        logger.info(f"Need download efemeride with date: {str_data_list}")

        url_list = []
        for one_date in str_data_list:
            year = one_date.year
            day_of_year = one_date.timetuple().tm_yday
            if day_of_year < 100:
                day_of_year = f"0{day_of_year}"
            logger.info(day_of_year)
            short_year = str(year)[2:]
            url_list.append(f"https://cddis.nasa.gov/archive/gnss/data/daily/{year}/brdc/brdc{day_of_year}0.{short_year}n.gz")

        # download achive
        self.download_file_helper(
            file_urls=url_list, save_path=save_path
        )
        return [f"{save_path}/{one_url.split('/')[-1]}" for one_url in url_list]


    @staticmethod
    def unzip_archive(archive_path: str, save_path: str = "./tmp_efemerides"):
        file_name = os.path.splitext(archive_path)[0].split("/")[-1]

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        with gzip.open(archive_path, 'rb') as f_in:
            with open(f"{save_path}/{file_name}", 'wb') as f_out:
                f_out.write(f_in.read())

        return f"{save_path}/{file_name}"

    @staticmethod
    def get_date_from_str(str_date: set) -> Union[list[datetime.date], None]:
        try:
            total_list = []
            for data in str_date:
                tmp_list = data.split("_")
                total_list.append(datetime.date(
                    year=int(tmp_list[0]),
                    month=int(tmp_list[1]),
                    day=int(tmp_list[2])
                ))
            return total_list
        except Exception as _ex:
            logger.error(f"Error to formate date: {str_date} -> {_ex}")

    def download_file_helper(self, file_urls: list[str], save_path: str) -> bool:
        try:
            with Session() as session:
                self.login(session, self.username, self.password)
                for file_url in file_urls:
                    self.download_file(session, file_url, save_path)
                    time.sleep(1)
            return True
        except Exception as _ex:
            logger.error(f"Error to download efemeride to url: {file_url} -> {_ex}")
            return False


    def download_file(self, session: Session, file_url: str, save_path: str):
        logger.info(f"downloading {file_url}")

        response = session.get(
            file_url,
            impersonate=self.impersonate,
        )
        response.raise_for_status()

        logger.info(f"Content-Type: {response.headers['Content-Type']}")

        if response.headers["Content-Type"] == "text/html; charset=utf-8":
            redirect_url = self.extract_redirect_url(response.text)
            logger.info("redirecting...")
            time.sleep(3)
            response = session.get(
                redirect_url,
                impersonate=self.impersonate,
            )
            response.raise_for_status()

        if response.headers["Content-Type"] != "application/x-gzip":
            raise Exception(
                "Unexpected file content type: " + response.headers["Content-Type"]
            )
        filename = file_url.split("/")[-1]
        logger.info(f"saving '{filename}'")

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        with open(f"{save_path}/{filename}", "wb") as f:
            f.write(response.content)


    def login(self, session: Session, username: str, password: str):
        logger.info("logging in NASA")

        index_page = self.get_index_page(session)
        auth_token = self.extract_auth_token(index_page)

        data = f"utf8=%E2%9C%93&authenticity_token={auth_token}&username={username}&password={password}&client_id=&redirect_uri=&commit=Log+in"

        response = session.post(
            "https://urs.earthdata.nasa.gov/login",
            data=data,
            impersonate=self.impersonate,
        )
        # with open("login-response.html", "w") as f:
        #     f.write(response.text)

        response.raise_for_status()

    def get_index_page(self, session: Session):
        response = session.get(
            "https://urs.earthdata.nasa.gov/",
            impersonate=self.impersonate,
        )
        response.raise_for_status()
        return response.text

    @staticmethod
    def extract_auth_token(index_page: str):
        soup = BeautifulSoup(index_page, "lxml")
        auth_token_elem = soup.select_one("form input[name=authenticity_token]")
        if auth_token_elem is None:
            raise Exception("authenticity_token not found")
        auth_token = auth_token_elem.get("value")
        return str(auth_token)

    @staticmethod
    def extract_redirect_url(check_page: str):
        matches = re.search('redirectURL = "(.*)"', check_page)
        if matches is None:
            raise Exception("redirectURL not found")
        return matches.group(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    USERNAME = "udalovps"
    PASSWORD = "Udalopasha!4"
    obj = EfemerideDownloadrer(username=USERNAME, password=PASSWORD)
    # obj.download_archive(["2024_06_10", "2024_06_12"])
    # obj.unzip_archive(archive_path="./tmp_archives/brdc1620.24n.gz")
    efem_path = obj.get_one_efemeride(str_date="2024_06_12")
    print(efem_path)
