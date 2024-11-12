from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
   path('login/', views.userLogin, name="login"),
   path('register/', views.userRegister, name="register"),
   path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Endpoint za dobijanje access i refresh tokena
   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Endpoint za osvežavanje access tokena
]