from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.views import APIView
from friend.models import Friend
from rest_framework.response import Response
from users.utils import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chattingRoom.models import ChattingRoom
from rest_framework.exceptions import NotFound, ValidationError

# 내 친구 리스트 반환
class FriendList(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        # user1이 현재 유저이고 친구 요청이 수락된 친구 목록을 가져오기
        friend_with_user1 = Friend.objects.filter(user1=user, status=Friend.Status.ACCEPT)
        friend_list = [friend.user2 for friend in friend_with_user1]

        # UserInfoSerializer에 친구 목록 직렬화 및 request context 전달
        friend_info_serializer = UserInfoSerializer(friend_list, many=True, context={'request': request})

        # 닉네임을 기준으로 정렬 (serializer의 'name' 필드를 기준으로)
        sorted_friend_data = sorted(friend_info_serializer.data, key=lambda user_info: user_info["nickname"])

        return Response({'friends': sorted_friend_data}, status=status.HTTP_200_OK)

# 친구 추가
# 프론트에서 친구의 nickname을 주고
# 백에서 받아서 친구 관계 저장 -> DB
# 소켓으로 상대방 nickname group에 메시지 보내기
class AddFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname) :
        user = request.user
        try:
            user2 = CustomUser.objects.get(nickname=friend_nickname)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="Friend does not exist.", code=status.HTTP_404_NOT_FOUND)

        # 나 자신에게 친구 추가를 시도할 경우 예외 처리
        if user == user2:
            raise ValidationError(detail="You cannot add yourself as a friend.", code=status.HTTP_400_BAD_REQUEST)

        # 이미 친구 추가를 요청한 경우 예외 처리
        if check_friend_status(user, user2, Friend.Status.SEND):
            raise ValidationError(detail="You already request friend.", code=status.HTTP_400_BAD_REQUEST)

        # 친구에게 친구 추가를 시도할 경우 예외 처리
        if check_friend_status(user, user2, Friend.Status.ACCEPT):
            raise ValidationError(detail="You cannot add already friend as a friend.", code=status.HTTP_400_BAD_REQUEST)

        # 차단당했는지 확인
        if not check_friend_status(user2, user, Friend.Status.BLOCK):
            # 친구 요청 보낸 사람 = user1
            friend = Friend(
                user1=user,
                user2=user2,
                user1_victory_num=0,
                user2_victory_num=0,
                status=Friend.Status.SEND
            )
            friend.save()

            # 친구 요청 받은 사람 = user1
            friend = Friend(
                user1=user2,
                user2=user,
                user1_victory_num=0,
                user2_victory_num=0,
                status=Friend.Status.PEND
            )
            friend.save()

            # 친구가 온라인에 있으면 소켓으로 보내기
            if user2.is_online:
                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    f"user_{user2.nickname}",
                {
                    'type': 'request_friend',
                    'sender': user.nickname,
                    'message': f"{user.nickname} 님이 친구 요청을 보냈습니다!!",
                    'tag' : 'request'
                }
            )

        return Response({"message": "Friend request sent."}, status=status.HTTP_201_CREATED)


# 친구 수락
class AcceptFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname) :
        user = request.user
        user2 = CustomUser.objects.filter(nickname=friend_nickname).first()

        friend1 = Friend.objects.filter(user1=user, user2=user2).first()
        friend2 = Friend.objects.filter(user1=user2, user2=user).first()

        # 요청오지 않은 유저를 수락한 경우
        if (friend1 is None or friend2 is None) :
            raise ValidationError(detail="You haven't received a friend request from that friend", code=status.HTTP_400_BAD_REQUEST)

        # 이미 수락한 경우
        if (friend1.status == "AC" or friend2.status == "AC") :
            raise ValidationError(detail="You already accept friend", code=status.HTTP_400_BAD_REQUEST)

        friend1.status = Friend.Status.ACCEPT
        friend2.status = Friend.Status.ACCEPT

        friend1.save()
        friend2.save()

        # if user2.is_active :
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"user_{user2.nickname}",
            {
                'type': 'request_friend',
                'sender': user.nickname,
                'message': f"{user.nickname} 님이 친구 요청을 수락했습니다!!",
                'tag' : 'accept'
            }
        )

        # 수락 했으니까 채팅방 만들기
        sorted_names = sorted([user.nickname, user2.nickname])
        room_name = f'chat_{sorted_names[0]}_{sorted_names[1]}'
        chattingRoom = ChattingRoom(user1=user, user2=user2, name=room_name)
        chattingRoom.save()

        return Response({"message": "친구관계 성립~"}, status=status.HTTP_200_OK)

# 친구 차단
class BlockFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname):
        user = request.user
        try:
            user2 = CustomUser.objects.get(nickname=friend_nickname)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="Friend does not exist.", code=status.HTTP_404_NOT_FOUND)

        try:
            friend1 = Friend.objects.get(user1=user, user2=user2)
        except Friend.DoesNotExist:
            raise NotFound(detail="Friend relationship does not exist.", code=status.HTTP_404_NOT_FOUND)

        friend1.status = "BL"
        friend1.save()

        return Response({"message": f"You blocked {friend_nickname}."}, status=status.HTTP_200_OK)

#차단 해제
class ReBlockFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname):
        user = request.user
        try:
            user2 = CustomUser.objects.get(nickname=friend_nickname)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="Friend does not exist.", code=status.HTTP_404_NOT_FOUND)

        try:
            friend1 = Friend.objects.get(user1=user, user2=user2)
        except Friend.DoesNotExist:
            raise NotFound(detail="Friend relationship does not exist.", code=status.HTTP_404_NOT_FOUND)

        friend1.status = "AC"
        friend1.save()

        return Response({"message": f"You reblocked {friend_nickname}."}, status=status.HTTP_200_OK)


# 친구 삭제
class DeleteFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname) :
        user = request.user
        try:
            user2 = CustomUser.objects.get(nickname=friend_nickname)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="Friend does not exist.", code=status.HTTP_404_NOT_FOUND)

        try:
            friend1 = Friend.objects.get(user1=user, user2=user2)
            friend2 = Friend.objects.get(user1=user2, user2=user)
        except Friend.DoesNotExist:
            raise NotFound(detail="Friend relationship does not exist.", code=status.HTTP_404_NOT_FOUND)

        friend1.delete()
        friend2.delete()

        return Response({"message": f"You deleted {friend_nickname}."}, status=status.HTTP_200_OK)


def check_friend_status(user, friend_nickname, status):
    friends = Friend.objects.filter(
        user1=user,
        status=status
    ).select_related('user2')

    return friends.filter(user2__nickname=friend_nickname).exists()


def get_my_friends_request(user) :
    test = Friend.objects.filter(
        user2=user,
        status=Friend.Status.SEND,
    ).all()
    return test

class SearchFriend(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, friend_nickname):
        print(f"Received request to find friend with nickname: {friend_nickname}")

        try:
            find_friend = CustomUser.objects.get(nickname=friend_nickname)

            # 이미지가 존재하지 않을 경우 기본 이미지를 설정하거나 None으로 반환
            friend_image_url = find_friend.image.url if find_friend.image else None

            friend_data = {
                "name": find_friend.nickname,
                "image": friend_image_url  # 이미지 URL 또는 None
            }

            return Response(friend_data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            raise NotFound(detail="Friend does not exist.", code=status.HTTP_404_NOT_FOUND)


# 차단된 친구 조회
class GetBlockFriendList(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request) :
        # user1이 나고, status가 BL 인 친구 리스트 뽑아오기

        user = request.user
        blocked_friends = Friend.objects.filter(user1=user, status='BL')

        friend_list = [friend.user2 for friend in blocked_friends]

        friend_info_list = [ ]
        for friend in friend_list :
            friend_info_list.append(get_user_info(friend.nickname))
        friend_info_list_sorted = sorted(friend_info_list, key=lambda user_info: user_info["nickname"])

        # friend_info_serializer = UserInfoSerializer(friend_info_list_sorted, many=True, context={'request': request})
        return Response({'friends': friend_info_list_sorted}, status=status.HTTP_200_OK)

# 아직 읽지 않은 친구 요청 반환
class PendFriendRequest(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request) :
        user = request.user

        # 사용자에게 온 친구 요청 필터링
        pend_request_friends = Friend.objects.filter(user1=user, status='PN')
        friend_list = [friend.user2 for friend in pend_request_friends]

        # UserInfoSerializer에 request를 context로 전달
        friend_info_serializer = UserInfoSerializer(friend_list, many=True, context={'request': request})

        # 친구 정보를 닉네임을 기준으로 정렬
        sorted_friend_data = sorted(friend_info_serializer.data, key=lambda user_info: user_info["nickname"])

        return Response({'friends': sorted_friend_data}, status=status.HTTP_200_OK)


# # 상대방이 나를 차단했는지 조회
# class BlockedMe(APIView) :
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def get(self, request, friend_nickname) :
#         user = request.user  #나

#         friend = Friend.objects.filter(user1=friend_nickname,user2=user, status='BL').first()

#         if friend:
#             return Response({"message": f"You are blocked by {friend_nickname}."}, status=200)

#         return Response({"message": "You are not blocked."}, status=200)

# # 상대방이 나를 차단했을때 바로 메시지 db에 저장
# class saveMessage(APIView) :
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def post(self, request) :

#         data = json.loads(request.body)

#         room_name = data.get("room_name")
#         sender = data.get("sender")
#         message = data.get("message")

#         room = ChattingRoom.objects.filter(name=room_name).first()
#         user = CustomUser.objects.filter(nickname=sender).first()

#         # Save message with current time
#         message = Message.objects.create(
#             room=room,
#             sender=user,
#             content=message,
#             created_at=datetime.now()
#         )

#         return Response({"message": "message 저장 완료"}, status=200)
