import logging
from typing import Union
import os
import shutil
import subprocess
import shlex

import pandas as pd

logger = logging.getLogger(__name__)


class FileWriter:
    """Class for work with coord files"""

    base_path = "./bot_4_files/base"
    projects_path = "./bot_4_files/projects"

    def __init__(self):
        self.file_data_list = self.open_input_file().split("\n")

    # global logic
    def create_all_files(self, df: pd.DataFrame, efemeride_year: int, project_name: str):
        """MAIN navigate method"""
        try:
            # check coords
            check_coords = self.validate_all_coords(df=df)
            if not check_coords["success"]:
                return check_coords
            logger.info(f"Coords it's OK")
            # check year
            check_year = self.validate_all_time_b(df=df, efemeride_year=efemeride_year)
            if not check_year["success"]:
                return check_year
            logger.info(f"Year it's OK")

            # create input and enter .exe
            for index in df.index:
                self.create_one_input_txt(
                    coord_x=str(df["X"][index]),
                    coord_y=str(df["Y"][index]),
                    coord_z=str(df["Z"][index]),
                    name=str(df["№"][index]),
                    mask=str(df["mask"][index]),
                    time_b=str(df["Time B"][index]),
                    time_e=str(df["Time E"][index]),
                    time_interval=str(df["Int"][index]),
                    dh=str(df["dh"][index]),
                    project_name=project_name
                )
                self.use_exe_file(project_name=project_name)
            return {"success": True}
        except Exception as _ex:
            logger.error(f"Ошибка excel файла. Повторите отправку -> {_ex}")
            return {"success": False, "info": "Ошибка в .xlsx файле"}

    def create_all_files_without_efem(self, df: pd.DataFrame, project_name: str):
        """MAIN navigate method"""
        try:
            # check coords
            check_coords = self.validate_all_coords(df=df)
            if not check_coords["success"]:
                return check_coords
            logger.info(f"Coords it's OK")

            # create input and enter .exe
            for index in df.index:
                self.create_one_input_txt(
                    coord_x=str(df["X"][index]),
                    coord_y=str(df["Y"][index]),
                    coord_z=str(df["Z"][index]),
                    name=str(df["№"][index]),
                    mask=str(df["mask"][index]),
                    time_b=str(df["Time B"][index]),
                    time_e=str(df["Time E"][index]),
                    time_interval=str(df["Int"][index]),
                    dh=str(df["dh"][index]),
                    project_name=project_name
                )
                self.use_exe_file(project_name=project_name)
            return {"success": True}
        except Exception as _ex:
            logger.error(f"Ошибка excel файла. Повторите отправку -> {_ex}")
            return {"success": False, "info": "Ошибка excel файла. Повторите отправку"}

    # logic with work to dirs
    def create_dir(self, dir_name: str):
        logger.info(f"Create directory: {dir_name}")
        if not os.path.exists("./bot_4_files/projects"):
            os.mkdir("./bot_4_files/projects")
        os.mkdir(f"{self.projects_path}/{dir_name}")

    def copy_files_from_base(self, target_dir: str):
        """This method copy all files from base dir
        in target directory
        """
        for file in os.listdir(self.base_path):
            shutil.copy(f"{self.base_path}/{file}", f"{self.projects_path}/{target_dir}")

    def get_generate_files_path(self, project_name: str) -> list:
        try:
            files_list = os.listdir(f"{self.projects_path}/{project_name}")
            total_list = []
            for file_name in files_list:
                if file_name.strip(".")[-1][-1] == "O":
                    total_list.append(f"{self.projects_path}/{project_name}/{file_name}")
            logger.info(f"File path list: {total_list}")
            return total_list
        except Exception as _ex:
            logger.error(f'Error to get generate file path: {_ex}')
            return []

    def use_exe_file(self, project_name: str):
        """This method use .exe file
        wine abc/info.exe
        """
        logger.info(f"Activate .exe file. Project: {project_name}")
        os.chmod(f'{self.projects_path}/{project_name}/wine.sh', 0o754)
        subprocess.call(shlex.split(f'{self.projects_path}/{project_name}/wine.sh {project_name}'))
        logger.info(f"Work .exe file is End. Project: {project_name}")

    def save_file_in_project_dir(self, project_name: str, file_name: str, file_data):
        logger.info(f"Save file: {file_name} in project: {project_name}")
        with open(f"{self.projects_path}/{project_name}/{file_name}", 'wb') as f:
            f.write(file_data)


    # logic to work with .xlsx files
    def read_pandas_file(self, file_path) -> pd.DataFrame:
        logger.info(f"Read data from Excel file: {file_path}")
        df = pd.read_excel(f"{file_path}")
        return df

    @staticmethod
    def read_pandas_from_data(data) -> pd.DataFrame:
        logger.info(f"Read data from data")
        df = pd.read_excel(data)
        logger.info(f"Pandas dataframe: {df}")
        return df

    @staticmethod
    def get_date_list(df: pd.DataFrame) -> set:
        total_set = set()
        for index in df.index:
            tmp_list = df["Time B"][index].split()
            total_set.add(f"{tmp_list[0]}_{tmp_list[1]}_{tmp_list[2]}")
        return total_set

    def validate_all_time_b(self, df: pd.DataFrame, efemeride_year: int) -> dict:
        try:
            success = True
            info = None
            for index in df.index:
                logger.info(f"Validate row: {index + 1}")
                if not self.validate_one_time_b(efemeride_year=efemeride_year, time_b=df["Time B"][index]):
                    info = f"Ошибка. строка №{index + 1}. " \
                           f"Эфемерид: {efemeride_year} год. Прислан: {df['Time B'][index][:4]} год"
                    success = False
                    break
        except Exception as _ex:
            logger.error("Error to validate time b")
            success = False
            info = "Ошибка при проверке полей Time B"
        finally:
            return {"success": success, "info": info}

    def validate_one_time_b(self, efemeride_year: int, time_b: str):
        try:
            str_year = time_b.split()[0][-2:]
            if int(str_year) != efemeride_year:
                logger.error(f"Time_b year: {str_year} != efemeride_year {efemeride_year}")
                return False
            return True
        except Exception as _ex:
            logger.error(f"Error to validate: {time_b}")
            return False

    def validate_all_coords(self, df: pd.DataFrame) -> dict:
        """This method validate one
        Args:
            df: dataframe with data
        """
        try:
            success = True
            info = None
            for index in df.index:
                logger.info(f"Validate row: {index + 1}")
                if not self.validate_coord(coord=str(round(df["X"][index], 7))):
                    info = f"Ошибка. строка №{index + 1} колонка X"
                    raise ValueError
                if not self.validate_coord(coord=str(round(df["Y"][index], 7))):
                    info = f"Ошибка. строка №{index + 1} колонка Y"
                    raise ValueError
                if not self.validate_coord(coord=str(round(df["Z"][index], 7))):
                    info = f"Ошибка. строка №{index + 1} колонка Z"
                    raise ValueError
        except ValueError:
            success = False
        finally:
            return {"success": success, "info": info}

    def validate_coord(self, coord: str) -> bool:
        """This method validate coordination data"""
        try:
            div_coord = coord.split(".")
            if len(div_coord) != 2:
                raise ValueError
            if len(div_coord[0]) > 6 or len(div_coord[0]) < 1:
                raise ValueError
            logger.info(f"Coord: {coord} have a need format")
            return True
        except Exception as _ex:
            logger.error(f"Coord: {coord} haven't a need format")
            return False



    # logic to work with .txt files
    def open_input_file(self):
        logger.info(f"Open input.txt")
        with open(f"{self.base_path}/input.txt") as f:
            return f.read()

    def create_new_file(self, path: str, data: str):
        """This method create new input.txt file
        and write in data
        """
        with open(path, "w+") as f:
            f.write(data)

    def create_one_input_txt(
            self,
            coord_x: str,
            coord_y: str,
            coord_z: str,
            name: str,
            mask: str,
            time_b: str,
            time_e: str,
            time_interval: str,
            dh: str,
            project_name: str
    ):
        """
        This method create new file input.txt
        with args
        """
        self.paste_need_coord(coord_x, coord_y, coord_z)
        self.past_need_name(name)
        self.past_need_mask(mask)
        self.past_need_time_b(time_b)
        self.past_need_time_e(time_e)
        self.past_need_time_interval(time_interval)
        self.past_need_dh(dh)
        self.create_new_file(
            path=f"{self.projects_path}/{project_name}/input.txt",
            data="\n".join(self.file_data_list)
        )

    def paste_need_coord(
            self,
            coord_x: str,
            coord_y: str,
            coord_z: str
    ) -> None:
        """This method past coord in one string"""
        x_before = coord_x.strip().split(".")[0]
        if len(x_before) > 6:
            x_before = x_before[:6]
        x_after = coord_x.strip().split(".")[-1]
        if len(x_after) > 7:
            x_after = x_after[:7]
        y_before = coord_y.strip().split(".")[0]
        if len(y_before) > 6:
            y_before = y_before[:6]
        y_after = coord_y.strip().split(".")[-1]
        if len(y_after) > 7:
            y_after = y_after[:7]
        z_before = coord_z.strip().split(".")[0]
        if len(z_before) > 6:
            z_before = z_before[:6]
        z_after = coord_z.strip().split(".")[-1]
        if len(z_after) > 7:
            z_after = z_after[:7]

        x_whole = self.add_symbol_before(data=x_before, symbol=" ", count=6)
        x_fract = self.add_symbol_after(data=x_after, symbol="0", count=7)
        y_whole = self.add_symbol_before(data=y_before, symbol=" ", count=6)
        y_fract = self.add_symbol_after(data=y_after, symbol="0", count=7)
        z_whole = self.add_symbol_before(data=z_before, symbol=" ", count=6)
        z_fract = self.add_symbol_after(data=z_after, symbol="0", count=7)
        self.file_data_list[18] = f"**{x_whole}.{x_fract} {y_whole}.{y_fract} {z_whole}.{z_fract}" \
                                  f"  station coordinates (km)"

    def past_need_name(self, name: str):
        """This method past name in need string"""
        need_name = self.add_symbol_after(data=f"**{name.strip()}  C1P1P2L1L2", symbol=" ", count=48)
        self.file_data_list[19] = need_name + "station name and observations to simulate"

    def past_need_mask(self, mask: str):
        """This method past mast in need string"""
        need_mask = self.add_symbol_after(data=f"**{mask} S", symbol=" ", count=48)
        self.file_data_list[20] = need_mask + "elevation mask (degrees) AND tropospheric delay simulation (S/N)"

    def past_need_time_b(self, time_b: str):
        """This method past time_b in need string"""
        need_time_b = self.add_symbol_after(data=f"**{time_b.strip()}", symbol=" ", count=48)
        self.file_data_list[21] = need_time_b + "date and initial epoch"

    def past_need_time_e(self, time_e: str):
        """This method past time_e in need string"""
        need_time_e = self.add_symbol_after(data=f"**{time_e.strip()}", symbol=" ", count=48)
        self.file_data_list[22] = need_time_e + "final epoch"

    def past_need_time_interval(self, time_interval: str):
        time_interval_whole = self.add_symbol_before(
            data=time_interval.strip().split(".")[0],
            symbol=" ",
            count=5
        )
        time_interval_fract = self.add_symbol_after(
            data=time_interval.strip().split('.')[-1],
            symbol=" ",
            count=40
        )
        self.file_data_list[23] = f"**{time_interval_whole}.{time_interval_fract}" + "time interval between observations"

    def past_need_dh(self, dh: str):
        dh_whole = self.add_symbol_before(
            data=dh.strip().split(".")[0],
            symbol=" ",
            count=9
        )
        dh_fract = self.add_symbol_after(
            data=dh.strip().split('.')[-1],
            symbol=" ",
            count=6
        )
        self.file_data_list[25] = f"**{dh_whole}.{dh_fract}" + "0.0000   0.0000               antenna parameters."

    def add_symbol_before(self, data: str, symbol: str, count: int):
        if len(data) < count:
            return self.add_symbol_before(data=f"{symbol}{data}", symbol=symbol, count=count)
        return data

    def add_symbol_after(self, data: str, symbol: str, count: int):
        if len(data) < count:
            return self.add_symbol_after(data=f"{data}{symbol}", symbol=symbol, count=count)
        return data


if __name__ == '__main__':
    obj = FileWriter()
    x = "3436.71043"
    y = "2655.503361"
    z = "4655.367117"
    name = "mmm"
    time_b = "2023 07 05 03 00 00.00000000"
    time_e = "08 02 00.00000000"
    time_interval = "8.00"
    mask = "08.0"
    dh = "1.7808"

    pandas_name = "excel.xlsx"

    # obj.create_one_input_txt(
    #     coord_x=x,
    #     coord_y=y,
    #     coord_z=z,
    #     name=name,
    #     time_b=time_b,
    #     time_e=time_e,
    #     time_interval=time_interval,
    #     mask=mask,
    #     dh=dh,
    #     project_name="test"
    # )
    obj.use_exe_file(project_name="test")
