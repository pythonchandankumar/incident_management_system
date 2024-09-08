from django.urls import path
from.views import *

urlpatterns = [
    path('register/',UserRegisterView.as_view(),name="register"),
    path('login/',UserLoginView.as_view(),name="login"),
    path('incidents/', IncidentListCreateAPIView.as_view(), name='incident-list-create'),
    path('incidents/<int:pk>/', IncidentDetailAPIView.as_view(), name='incident-detail'),
    path('incidents/search/', IncidentSearchView.as_view(), name='incident-search'),

]
