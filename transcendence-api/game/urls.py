from django.urls import path
from .views import SaveGameView, RecentGamesView, InviteGameView, AcceptGameView, MatchingView, OfflineGameView, \
    GamePageView

urlpatterns = [
    path('', SaveGameView.as_view(), name='save_game'),
    path('info/<str:nickname>/', RecentGamesView.as_view(), name='recent_games'),
    path('invite/<str:nickname>/', InviteGameView.as_view(), name='invite'),
    path('accept/<str:friend_nickname>/', AcceptGameView.as_view(), name='accept_invite'),
    path('match/', MatchingView.as_view(), name='match'),
    path('online/<str:room_name>/', GamePageView.as_view(), name='match'),
    path('offline/', OfflineGameView.as_view(), name='match'),
]
