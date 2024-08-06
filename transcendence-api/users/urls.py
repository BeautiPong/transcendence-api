from .views import get_code, get_token, UserInfoView, UserRankingView
from django.urls import path
from .views import join, login, UserProfileView

urlpatterns = [
    path('account/join/', join, name='join'),
    path('account/login/', login, name='login'),
    path('api/profile/', UserProfileView.as_view(), name='user_profile'),

    path('login/', get_code, name='get_code'),
    path('get-token/', get_token, name='get_token'),
    path('info/<str:nickname>/', UserInfoView.as_view(), name='get_user_info'),
    path('rank/<str:nickname>/', UserRankingView.as_view(), name='get_user_rank'),
]