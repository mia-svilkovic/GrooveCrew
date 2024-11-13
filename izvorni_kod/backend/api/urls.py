from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
   path('home/', views.frontend_view, name='frontend_login'),      # Homepage

   path('home/loginAuth/', views.userLogin, name="loginAuth"),
   path('home/registerAuth/', views.userRegister, name="registerAuth"),
   
   path('add_record/', views.add_vinyl_record, name="add_record"), # Endpoint za dodavanje ploce
   path('get_records/', views.get_records, name="get_records"),    # Endpoint za dohvacanje svih ploca u obliku JSON
   
   path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Endpoint za dobijanje access i refresh tokena
   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Endpoint za osvežavanje access tokena

   path('test_token/', views.test_token, name="test_token"),
]