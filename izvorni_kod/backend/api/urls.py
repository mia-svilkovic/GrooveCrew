from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
   path('loginAuth/', views.userLogin, name="loginAuth"),
   path('registerAuth/', views.userRegister, name="registerAuth"),
   path('home/', views.frontend_view, name='frontend_login'),
   path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Endpoint za dobijanje access i refresh tokena
   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Endpoint za osvežavanje access tokena
]