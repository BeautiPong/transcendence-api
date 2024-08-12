from django.urls import path
from game.views import RecentGamesView, InviteGameView, AcceptGameView
from game.views import SaveGameView

urlpatterns = [
    path('', SaveGameView.as_view(), name='save_game'),
    path('<str:nickname>/', RecentGamesView.as_view(), name='recent_games'),
    path('invite/<str:nickname>/', InviteGameView.as_view(), name='invite'),
    path('accept/<str:friend_nickname>/', AcceptGameView.as_view(), name='accept_invite'),
]
