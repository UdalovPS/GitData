from django.db import models
import datetime


class PersonModel(models.Model):
    ROLE_CHOISES = [
        (0, "Клиент"),
        (1, "Сотрудник"),
    ]
    user_id = models.BigIntegerField(primary_key=True)
    role = models.IntegerField(choices=ROLE_CHOISES, default=0, verbose_name='Роль')
    name = models.CharField(max_length=50, verbose_name='Имя')
    phone = models.CharField(max_length=11, verbose_name='Номер телефона')
    authentication = models.BooleanField(default=False, verbose_name="Подтверждение")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Люди"


class NoteModel(models.Model):
    NOTE_TYPE = [
        (0, "/w"),
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
