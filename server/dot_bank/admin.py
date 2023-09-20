from django.contrib import admin
from .models import *


@admin.register(FileDownloadModel)
class FileDownloadModelAdmin(admin.ModelAdmin):
    list_display = [
        "user_id", "station_name",
        "file_name", "file_date", "file_time",
        "note_date", "note_time"
    ]
    list_filter = ["user_id", "station_name"]
    search_fields = ["file_name"]


@admin.register(PersonModel)
class PersonModelAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'name', 'role', 'phone', 'authentication'
    ]
    list_filter = ['name', 'role', 'authentication']
    search_fields = ['name', 'phone']


@admin.register(NoteModel)
class NoteModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_id', 'username', 'text', 'note_type', 'note_date', 'note_time'
    ]
    list_filter = ['username', 'note_type']
    search_fields = ['username', 'text']

