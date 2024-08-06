from django.urls import path
from game.views import RecentGamesView
from game.views import SaveGameView

urlpatterns = [
    path('', SaveGameView.as_view(), name='save_game'),
    path('<str:nickname>/', RecentGamesView.as_view(), name='recent_games'),
]
