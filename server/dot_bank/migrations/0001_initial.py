# Generated by Django 4.2.5 on 2023-09-13 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PersonModel',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('role', models.IntegerField(choices=[(0, 'Клиент'), (1, 'Сотрудник')], verbose_name='Роль')),
                ('name', models.CharField(max_length=50, verbose_name='Имя')),
                ('phone', models.CharField(max_length=11, verbose_name='Номер телефона')),
                ('authentication', models.BooleanField(default=False, verbose_name='Подтверждение')),
            ],
            options={
                'verbose_name_plural': 'Люди',
            },
        ),
        migrations.CreateModel(
            name='NoteModel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('note_date', models.DateField(auto_now=True, verbose_name='Дата записи')),
                ('note_time', models.TimeField(auto_now=True, verbose_name='Время записи')),
                ('text', models.CharField(max_length=200, verbose_name='Текст записи')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dot_bank.personmodel', verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name_plural': 'Записи сотрудников',
            },
        ),
    ]
