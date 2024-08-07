from users.models import CustomUser
from users.serializers import UserInfoSerializer

def get_user_info(nickname):
    try:
        user = CustomUser.objects.get(nickname=nickname)
    except CustomUser.DoesNotExist:
        return None

    user_serializer = UserInfoSerializer(user)
    return user_serializer.data
