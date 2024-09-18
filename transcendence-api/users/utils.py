from users.models import CustomUser
from users.serializers import UserInfoSerializer
from urllib.request import urlopen
from django.core.files import File
from io import BytesIO

def get_user_info(nickname):
    try:
        user = CustomUser.objects.get(nickname=nickname)
    except CustomUser.DoesNotExist:
        return None

    user_serializer = UserInfoSerializer(user)
    return user_serializer.data

def save_image_from_url(url):
    try:
        response = urlopen(url)
        if response.status == 200:
            io = BytesIO(response.read())
            return File(io, name=url.split("/")[-1])
        else:
            return None
    except Exception as e:
        return None