from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

app_name = 'api'

urlpatterns = [
   path('users/register/', RegisterView.as_view(), name="user-register"),
   path('users/login/', LoginView.as_view(), name="user-login"),
   path('users/logout/', LogoutView.as_view(), name="user-logout"),
   path('users/google-login/', GoogleLoginView.as_view(), name="user-google-login"),
   
   path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

   path('records/', RecordListView.as_view(), name='record-list'),
   path('records/create/', RecordCreateView.as_view(), name='record-add'),
   path('records/<int:id>/', RecordDetailView.as_view(), name='record-detail'),
   path('records/<int:id>/update/', RecordUpdateView.as_view(), name='record-update'),
   path('records/<int:id>/delete/', RecordDeleteView.as_view(), name='record-delete'),
   path('records/user/<int:user_id>/', UserRecordListView.as_view(), name='records-user'),

   path('genres/', GenreListView.as_view(), name='genres'),

   path('goldmine-conditions-record/', GoldmineConditionRecordListView.as_view(), name='goldmine-conditions-record'),
   path('goldmine-conditions-cover/', GoldmineConditionCoverListView.as_view(), name='goldmine-conditions-cover'),

   path('locations/', LocationListView.as_view(), name='location-list'),
   path('locations/<int:id>/', LocationDetailView.as_view(), name='location-detail'),

   path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
   path('wishlist/add/', WishlistCreateView.as_view(), name='wishlist-add'),
   path('wishlist/<int:id>/delete/', WishlistDeleteView.as_view(), name='wishlist-delete'),

   path('exchanges/', ExchangeListView.as_view(), name='exchange-list'),
   path('exchanges/create/', ExchangeCreateView.as_view(), name='exchange-create'),
   path('exchanges/<int:id>/', ExchangeRetrieveView.as_view(), name='exchange-detail'),
   path('exchanges/<int:id>/update/', ExchangeUpdateView.as_view(), name='exchange-update'),
   path('exchanges/<int:id>/delete/', ExchangeDeleteView.as_view(), name='exchange-delete'), 
   path('exchanges/<int:id>/switch-reviewer/', ExchangeSwitchReviewerView.as_view(), name='exchange-switch-reviewer'),
   path('exchanges/<int:id>/finalize/', ExchangeFinalizeView.as_view(), name='exchange-finalize'),
]
