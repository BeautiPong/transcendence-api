from django.http import JsonResponse

import requests
import urllib.parse
from users.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.serializers import *
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from users.serializers import UserInfoSerializer


# Create your views here.

def get_code(request): 
    client_id = 'u-s4t2ud-5165cfc59957b2a5cd674a6fc909e1e94378eff8b68d30144cbf571ed0b80ea1'
    redirect_uri = 'http://localhost:8000/'
    response_type = 'code'
    
    oauth_url = f'https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type={response_type}'
    
    return HttpResponseRedirect(oauth_url) # redirect to 42 login page



import requests
from django.http import JsonResponse

def get_token(request):
    code = 'dbcc26b5ec2f01b58cb7ed741d4c08058ef728b36227c5872fa0fdf6204020ed'  # 유저가 받은 코드를 여기에 입력합니다.
    client_id = 'u-s4t2ud-5165cfc59957b2a5cd674a6fc909e1e94378eff8b68d30144cbf571ed0b80ea1'  # 42에서 제공한 클라이언트 ID
    client_secret = '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'  # 42에서 제공한 클라이언트 시크릿
    redirect_uri = 'http://localhost:8000/'  # 이전에 사용한 리디렉션 URL
    grant_type = 'authorization_code'
    scope = 'public profile'  # 42에서 제공한 스코프

    token_url = 'https://api.intra.42.fr/oauth/token'
    
    # 액세스 토큰 요청을 위한 데이터
    data = {
        'grant_type': grant_type,
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'scope': scope,
    }

    # POST 요청을 통해 액세스 토큰 요청
    response = requests.post(token_url, data=data)
    
    # 응답 데이터 처리
    if response.status_code == 200:
        access_token = response.json().get('access_token')
    #     return JsonResponse({'access_token': access_token})
    # else:
    #     return JsonResponse({'error': 'Failed to obtain access token'}, status=response.status_code)

    # response_data = response.json()
    # return JsonResponse(response_data)

    user_url = 'https://api.intra.42.fr/v2/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(user_url, headers=headers)
    response_data = response.json()
    return JsonResponse(response_data)

def get_user_info(request):
    access_token = request.headers.get('accessToken')
    user_url = 'https://api.intra.42.fr/v2/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(user_url, headers=headers)
    response_data = response.json()
    return JsonResponse(response_data)


# 회원가입
@csrf_exempt
def join (request) :
    if request.method == 'POST' :
        userID = request.POST.get('userID')   # 로그인 시 필요한 아이디 (고유)
        password = request.POST.get('password') # 로그인 시 필요한 비밀번호
        nickname = request.POST.get('nickname') # 사용자 닉네임 (고유)
        email = request.POST.get('email')  # 이메일

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
        CustomUser.objects.create_user(userID=userID, password=password,nickname=nickname, email=email)
        
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

        
# 사용자 정보 반환
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        image_url = user.image.url if user.image else None
        win_rate = user.win_cnt / user.match_cnt * 100 if user.match_cnt != 0 else 0

        response = JsonResponse(
            {
                "username" : user.nickname,
                "email" : user.email,
                "profile_img" : image_url,
                "match_cnt" : user.match_cnt,
                "win_cnt" : user.win_cnt,
                "win_rate" : win_rate,
            },
            status = status.HTTP_200_OK
        )
        return response

# 사용자 정보 수정
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def put(self, request):
        # 현재 로그인된 사용자의 UserProfile을 가져옵니다.
        serializer = UserInfoSerializer(request.user, data=request.data, partial=True)  # partial=True allows partial updates

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)