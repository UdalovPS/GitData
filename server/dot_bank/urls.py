from django.urls import path
from .import views


urlpatterns = [
    path("check/", views.CheckView.as_view(), name='check_view'),
    path('person/', views.PersonApiView.as_view(), name='person'),
    path('note/', views.NoteApiView.as_view(), name='note'),
    path('file/', views.FileView.as_view(), name='file'),
    path('instruction/', views.InstructionView.as_view(), name="instruction"),
    path('feedback/', views.FeedBackView.as_view(), name="feedback"),
    path('/person/instruction/', views.PersonInstructionApiView.as_view(), name="person_instruction"),
]
