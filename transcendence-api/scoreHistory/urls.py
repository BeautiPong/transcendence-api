from .views import OverallRankingsView, UserScoreHistoryView
from django.urls import path

urlpatterns = [
    path('all/', OverallRankingsView.as_view(), name='get_overall_rankings'),
    path('graph/<str:nickname>/', UserScoreHistoryView.as_view(), name='get_user_graph'),
]
