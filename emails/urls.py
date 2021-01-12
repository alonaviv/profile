from . import views
from django.urls import path


urlpatterns = [
    path('cancel_subscription', views.cancel_subscription, name='cancel_subscription'),
    path('restore_subscription', views.restore_subscription, name='restore_subscription')
]
