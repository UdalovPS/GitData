from django.urls import path
from .import views


urlpatterns = [
    path("check/", views.CheckView.as_view(), name='check_view'),
    path('person/', views.PersonApiView.as_view(), name='person'),
    path('note/', views.NoteApiView.as_view(), name='note'),
    path('file/', views.FileView.as_view(), name='file'),
]
