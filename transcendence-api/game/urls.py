from django.urls import path

from game.views import SaveGameView

urlpatterns = [
    path('', SaveGameView.as_view(), name='save_game'),
]
