from django.views import View
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import PersonModel, NoteModel


class CheckView(View):
    def get(self, request):
        return HttpResponse("Server is working!!!")


class PersonApiView(APIView):
    def post(self, request: Request) -> Response:
        cursor = PersonModel(
            user_id=request.POST['user_id'],
            name=request.POST['name'],
            phone=request.POST['phone']
        )
        cursor.save()
        return Response({'status': 'Person add'})


class NoteApiView(APIView):
    def post(self, request: Request) -> Response:
        person = PersonModel.objects.get(user_id=request.POST['user_id'])
        cursor = NoteModel(
            user_id=person,
            note_type=request.POST['note_type'],
            text=request.POST['text']
        )
        cursor.save()
        return Response({'status': 'Note add'})
