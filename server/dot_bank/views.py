from django.views import View
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from datetime import datetime

from .models import PersonModel, NoteModel, FileDownloadModel


class CheckView(View):
    def get(self, request):
        return HttpResponse("Server is working!!!")


class FileView(APIView):
    def post(self, request: Request) -> Response:
        person = PersonModel.objects.get(user_id=int(request.POST['user_id']))
        # print(type(request.POST['datetime']), request.POST['datetime'])
        cursor = FileDownloadModel(
                user_id=person,
                station_name=request.POST['file_name'][:4],
                file_name=request.POST['file_name'],
                file_date=datetime.strptime(request.POST['datetime'], "%Y-%m-%d %H:%M:%S").date(),
                file_time=datetime.strptime(request.POST['datetime'], "%Y-%m-%d %H:%M:%S").time(),
            )
        cursor.save()
        return Response({'text': 'Data was save'})


class PersonApiView(APIView):
    def get(self, request: Request) -> Response:
        try:
            person = PersonModel.objects.get(user_id=int(request.POST['user_id']))
            return Response({'text': person.authentication})
        except:
            return Response({'text': 3})

    def post(self, request: Request) -> Response:
        try:
            person = PersonModel.objects.get(user_id=int(request.GET.get('user_id')))
            return Response({'text': "Вы уже зарегистрированы. Если вам не открыт доступ то обратитесь к администрации"})
        except:
            cursor = PersonModel(
                user_id=request.POST['user_id'],
                name=request.POST['name'],
                phone=request.POST['phone']
            )
            cursor.save()
            return Response({'text': "Заявка подана. Дождитесь одобрения администрации."})


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


