from . import views
from django.urls import path


urlpatterns = [
    path('', views.main_dashboard_page, name='index')
]
