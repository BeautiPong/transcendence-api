from .views import OverallRankingsView, UserInfoView, UserScoreHistoryView
from django.urls import path

urlpatterns = [
    path('all/', OverallRankingsView.as_view(), name='get_overall_rankings'),
    path('info/<str:nickname>/', UserInfoView.as_view(), name='get_user_info'),
    path('graph/<str:nickname>/', UserScoreHistoryView.as_view(), name='get_user_graph'),
]
