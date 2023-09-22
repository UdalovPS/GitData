from django.db import models
import requests
import os
from dotenv import load_dotenv


load_dotenv()       #load bot token


class PersonModel(models.Model):
    ROLE_CHOISES = [
        (0, "Клиент"),
        (1, "Сотрудник"),
    ]
    user_id = models.BigIntegerField(primary_key=True)
    role = models.IntegerField(choices=ROLE_CHOISES, default=0, verbose_name='Роль')
    name = models.CharField(max_length=50, verbose_name='Имя пользователя')
    phone = models.CharField(max_length=12, verbose_name='Номер телефона')
    authentication = models.BooleanField(default=False, verbose_name="Подтверждение")

    def save(self, *args, **kwargs):
        if self.authentication == True:
            method = "sendMessage"
            print(self.user_id)
            print(os.getenv('TOKEN_2'))
            response = requests.post(
            url='https://api.telegram.org/bot{0}/{1}'.format(os.getenv('TOKEN_2'), method),
            data={'chat_id': self.user_id, 'text': 'Ваша заявка была одобрена'}
            ).json()

        print("[INFO] was been_save", self.user_id, self.authentication)
        #parent method
        super(PersonModel, self).save(*args, **kwargs)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Люди"


class NoteModel(models.Model):
    NOTE_TYPE = [
        (0, "/a"), (1, "/b"), (2, "/c"), (3, "/d"), (4, "/e"), (5, "/f"),
        (6, "/g"), (7, "/h"), (8, "/i"), (9, "/j"), (10, "/k"), (11, "/l"),
        (12, "/m"), (13, "/n"), (14, "/o"), (15, "/p"), (16, "/q"), (17, "/r"),
        (18, "/s"), (19, "/t"), (20, "/u"), (21, "/v"), (22, "/w"), (23, "/x"),
        (24, "/y"), (25, "/z"),
    ]
    id = models.IntegerField(primary_key=True)
    user_id = models.BigIntegerField()
    username = models.CharField(max_length=50, verbose_name="Имя внесшего запись", default="")
    note_type = models.IntegerField(choices=NOTE_TYPE, default=0, verbose_name='Тип записи')
    note_date = models.DateField(auto_now=True, verbose_name='Дата записи')
    note_time = models.TimeField(auto_now=True, verbose_name='Время записи')
    text = models.TextField(verbose_name='Текст записи')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = "Записи сотрудников"


class FileDownloadModel(models.Model):
    user_id = models.ForeignKey("PersonModel", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Имя пользователя")
    station_name = models.CharField(max_length=4, verbose_name="Название станции")
    file_name = models.CharField(max_length=100, verbose_name='Имя файла')
    file_date = models.DateField(verbose_name='Дата файла')
    file_time = models.TimeField(verbose_name='Время файла')
    note_date = models.DateField(auto_now=True, verbose_name='Дата запроса')
    note_time = models.TimeField(auto_now=True, verbose_name='Время запроса')

    class Meta:
        verbose_name_plural = "Запросы станций"
