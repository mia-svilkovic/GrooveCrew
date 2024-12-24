from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GoldmineConditionCoverListView, GoldmineConditionRecordListView
from .views import LoginView, LogoutView, RegisterView
from .views import oauth_login_success, oauth_logout_success
from .views import RecordCreateView, RecordDetailView, RecordListView
from .views import UserRecordListView, GenreListView
from .views import WishlistCreateView, WishlistDeleteView, WishlistListView

app_name = 'api'

urlpatterns = [
   path('users/register/', RegisterView.as_view(), name="user-register"),
   path('users/login/', LoginView.as_view(), name="user-login"),
   path('users/logout/', LogoutView.as_view(), name="user-logout"),
   
   path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

   # Google OAuth 2.0 Based Authentication (Redirect Endpoints)
   path('oauth/login-success/', oauth_login_success, name='oauth-login-success'),
   path('oauth/logout-success/', oauth_logout_success, name='oauth-logout-success'),

   path('records/', RecordListView.as_view(), name='record-list'),
   path('records/<int:id>/', RecordDetailView.as_view(), name='record-detail'),
   path('records/user/<int:user_id>/', UserRecordListView.as_view(), name='user-records'),
   path('records/add/', RecordCreateView.as_view(), name='record-add'),

   path('genres/', GenreListView.as_view(), name='genres'),

   path('goldmine-conditions-record/', GoldmineConditionRecordListView.as_view(), name='goldmine-conditions-record'),
   path('goldmine-conditions-cover/', GoldmineConditionCoverListView.as_view(), name='goldmine-conditions-cover'),

   path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
   path('wishlist/add/', WishlistCreateView.as_view(), name='wishlist-add'),
   path('wishlist/delete/<int:pk>/', WishlistDeleteView.as_view(), name='wishlist-delete'),
]
