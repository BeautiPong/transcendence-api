from django.urls import path
from game.views import RecentGamesView

urlpatterns = [
    path('<str:nickname>/', RecentGamesView.as_view(), name='recent_games'),
]
