from .views import get_code, get_token, UserInfoView, UserRankingView, login_and_redirect, login_success
from django.urls import path
from .views import join, login, LogoutView, UserProfileView, UserProfileUpdateView, check_user
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('account/pre-login/', check_user, name='pre-login'),
    path('account/join/', join, name='join'),
    path('account/login/', login, name='login'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),

    path('login/', get_code, name='get_code'),
    path('get-token/', get_token, name='get_token'),
    path('info/<str:nickname>/', UserInfoView.as_view(), name='get_user_info'),
    path('rank/<str:nickname>/', UserRankingView.as_view(), name='get_user_rank'),
    path('token/reissue', TokenRefreshView.as_view()),
    path('login/success', login_success, name='login_success'),

    path('test/', login_and_redirect),
    # path("<str:nickname>/", WebSocketLoginView.as_view(), name="login"),
]