from django.urls import path
from . import views

app_name = 'rider'

urlpatterns = [

    path('register/', views.RiderRegistration.as_view(), name='rider-registration'),
    path('login/', views.RiderLogin.as_view(), name='rider-login'),
    path('logout/', views.Logout.as_view(), name='rider-logout'),
    path('available_cabs/', views.GetListOfAvailableCab.as_view(), name='getlistofavailablecabs'),
    path('bookcab/', views.BookCab.as_view(), name='bookcab'),
    path('travelhistory/', views.TravelHistoryList.as_view(), name='travelhistory')

]