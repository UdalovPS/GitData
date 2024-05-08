from django.views import View
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from datetime import datetime

from .models import PersonModel, NoteModel, FileDownloadModel, InstuctionsDownloadModel, FeedBackModel


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
            person = PersonModel.objects.get(user_id=int(request.data["user_id"]))
            print(person.authentication)
            return Response({'text': person.authentication})
        except Exception as _ex:
            print(_ex)
            return Response({'text': 3})

    def post(self, request: Request) -> Response:
        try:
            person = PersonModel.objects.get(user_id=int(request.POST['user_id']))
            if person.authentication == True:
                return Response({'text': "Ваша заявка одобрена. Вам доступен весь функционал."})
            else:
                return Response({'text': "Ваша заявка еще не одобрена. Обратитесь к администрации."})
        except:
            cursor = PersonModel(
                user_id=request.POST['user_id'],
                name=request.POST['name'],
                phone=request.POST['phone'],
                bot_number=request.POST["bot_number"]
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


class InstructionView(APIView):
    def post(self, request: Request) -> Response:
        person = PersonModel.objects.get(user_id=int(request.POST['user_id']))
        cursor = InstuctionsDownloadModel(
                user_id=person,
                file_name=request.POST['file_name'],
            )
        cursor.save()
        return Response({'text': 'Data was save'})


class FeedBackView(APIView):
    def post(self, request: Request) -> Response:
        person = PersonModel.objects.get(user_id=int(request.POST['user_id']))
        cursor = FeedBackModel(
                user_id=person,
                text=request.POST['text'],
                bot_number=request.POST['bot_number']
            )
        cursor.save()
        return Response({'text': 'Data was save'})


class PersonInstructionApiView(APIView):
    def get(self, request: Request) -> Response:
        try:
            person = PersonModel.objects.get(user_id=int(request.data["user_id"]))
            print(person.authentication)
            return Response({'text': person.authentication})
        except Exception as _ex:
            print(_ex)
            return Response({'text': 3})

    def post(self, request: Request) -> Response:
        try:
            person = PersonModel.objects.get(user_id=int(request.POST['user_id']))
            if person.authentication == True:
                return Response({'text': "Ваша заявка одобрена. Вам доступен весь функционал."})
            else:
                return Response({'text': "Ваша заявка еще не одобрена. Обратитесь к администрации."})
        except:
            cursor = PersonModel(
                user_id=request.POST['user_id'],
                name=request.POST['name'],
                phone=request.POST['phone'],
                bot_number=request.POST["bot_number"]
            )
            cursor.save()
            return Response({'text': "Заявка подана. Дождитесь одобрения администрации."})
