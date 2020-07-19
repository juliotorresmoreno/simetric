from django.urls import path

from api.views import get_index

urlpatterns = [
    path('<str:table>/', get_index, name='index'),
]