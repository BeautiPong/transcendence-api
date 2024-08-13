from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.ChatRoomListCreateView.as_view(), name='chat_rooms'),
    path('<int:room_id>/messages', views.MessageListView.as_view(), name='chat_messages'),
    path('index',views.IndexView.as_view(),name="index"),
]