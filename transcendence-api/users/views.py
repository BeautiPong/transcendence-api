from django.http import JsonResponse
from users.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.serializers import *
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# 회원가입
@csrf_exempt
def join (request) :
    if request.method == 'POST' :
        userID = request.POST.get('userID')   # 로그인 시 필요한 아이디 (고유)
        password = request.POST.get('password') # 로그인 시 필요한 비밀번호
        nickname = request.POST.get('nickname') # 사용자 닉네임 (고유)

    # 사용자가 이미 회원가입을 했는지 확인
    user = CustomUser.objects.filter(userID=userID).first()
    if user :
        response = JsonResponse(
            {
                "message": "이미 회원가입 된 회원입니다."
            },
            status = status.HTTP_200_OK
        )

    else :
        # 사용자 생성 후 DB에 저장
        CustomUser.objects.create_user(userID=userID, password=password,nickname=nickname)
        
        response = JsonResponse(
            {
                "message": "회원가입 성공!"
            },
            status = status.HTTP_200_OK
        )
    
    return response

# 자체 로그인
@csrf_exempt
def login (request) :
    if request.method == 'POST' :
        userID = request.POST.get('userID')
        password = request.POST.get('password')

        user = CustomUser.objects.filter(userID=userID).first()

        # user가 DB에 있고 비밀번호가 맞다면
        if user and check_password(password, user.password):
            token = TokenObtainPairSerializer.get_token(user)  # refresh token 생성
            refresh_token = str(token)
            access_token = str(token.access_token)  # access token 생성

            response = JsonResponse (
                {
                    "message": "로그인 성공",
                    "jwt_token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    },
                },
                status = status.HTTP_200_OK
            )
            response.set_cookie("access_token", access_token, httponly=True)
            response.set_cookie("refresh_token", refresh_token, httponly=True)

        else :
            response = JsonResponse (
                {
                    "message": "아이디 또는 비밀번호가 틀렸습니다."
                },
                status = status.HTTP_401_UNAUTHORIZED
            )

        return response

        
# 로그인된 사용자 정보 반환
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        response = JsonResponse(
            {
                "user id" : user.id,
                "username" : user.nickname,
            },
            status = status.HTTP_200_OK
        )
        return response