# Generated by Django 4.2.5 on 2023-09-15 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dot_bank', '0004_notemodel_username_alter_notemodel_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notemodel',
            name='note_type',
            field=models.IntegerField(choices=[(0, '/a'), (1, '/b'), (2, '/c'), (3, '/d'), (4, '/e'), (5, '/f'), (6, '/g'), (7, '/h'), (8, '/i'), (9, '/j'), (10, '/k'), (11, '/l'), (12, '/m'), (13, '/n'), (14, '/o'), (15, '/p'), (16, '/q'), (17, '/r'), (18, '/s'), (19, '/t'), (20, '/u'), (21, '/v'), (22, '/w'), (23, '/x'), (24, '/y'), (25, '/z')], default=0, verbose_name='Тип записи'),
        ),
    ]
