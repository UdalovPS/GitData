import os

from django.views import View
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
import requests

from .models import PersonModel, NoteModel


class CheckView(View):
    def get(self, request):
        return HttpResponse("Server is working!!!")


class PersonApiView(APIView):
    def post(self, request: Request) -> Response:
        try:
            person = PersonModel.objects.get(user_id=int(request.POST['user_id']))
            return Response({'text': "Вы уже зарегистрированы"})
        except:
            cursor = PersonModel(
                user_id=request.POST['user_id'],
                name=request.POST['name'],
                phone=request.POST['phone']
            )
            cursor.save()
            return Response({'text': "Заявка подана"})


class NoteApiView(APIView):
    def post(self, request: Request) -> Response:
            cursor = NoteModel(
                user_id=request.POST['user_id'],
                username=request.POST['username'],
                note_type=request.POST['note_type'],
                text=request.POST['text']
            )
            cursor.save()
            return Response({'text': 'Запись внесена'})


class FileView(APIView):
    def get(self, request: Request) -> Response:
        file_url = request.GET.get('url')       #URL for download file
        file_name = request.GET.get('file_name')
        file_res = requests.get(url=file_url)

        TOKEN = "1955432392:AAFIKGS33j1DsT-zsWIAc_fs6ckOX4yjLQY"
        method = 'sendDocument'
        chat_id = 1953960185
        file_name = 'dataset_1.zip'
        with open("dataset_1.zip", 'rb') as file:

            response = requests.post(
                url=f'https://api.telegram.org/bot{TOKEN}/{method}',
                data={'chat_id': chat_id, "text": 'text'},
                files={'document': (file_name, file)}
            ).json()        #get file ID
        return Response({'file_id': response['result']['document']['file_id']})

