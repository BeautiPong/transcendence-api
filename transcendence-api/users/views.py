from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication    import JWTAuthentication
from rest_framework_simplejwt.serializers       import *
from rest_framework_simplejwt.exceptions        import InvalidToken, TokenError
from rest_framework_simplejwt.views             import TokenRefreshView
from django.views.decorators.csrf               import csrf_exempt
from django.contrib.auth.hashers                import check_password
from rest_framework.permissions                 import IsAuthenticated
from rest_framework.response                    import Response
from django.core.exceptions                     import ValidationError
from rest_framework.views                       import APIView
from users.serializers                          import UserInfoSerializer, UserRankingSerializer
from rest_framework                             import status
from users.models                               import CustomUser
from django.http                                import HttpResponseRedirect
from django.http                                import JsonResponse
import urllib.parse
from rest_framework.permissions import IsAuthenticated
import requests
import re
import json
from users.utils import get_user_info


# Create your views here.

def get_code(request):
    client_id = 'u-s4t2ud-5165cfc59957b2a5cd674a6fc909e1e94378eff8b68d30144cbf571ed0b80ea1'
    redirect_uri = 'http://localhost:8000/'
    response_type = 'code'
    oauth_url = f'https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type={response_type}'

    return HttpResponseRedirect(oauth_url)  # redirect to 42 login page


def get_token(request):
    code = request.GET.get('code')  # 유저가 받은 코드를 여기에 입력합니다.
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
        ft_access_token = response.json().get('access_token')
    else:
        return JsonResponse({'error': 'Failed to obtain access token'},
                            status=response.status_code)

    user_url = 'https://api.intra.42.fr/v2/me'
    headers = {
        'Authorization': f'Bearer {ft_access_token}',
    }
    response = requests.get(user_url, headers=headers)
    response_data = response.json()
    intra_id = response_data.get('login')
    email = response_data.get('email')
    image = response_data.get('image.list')

    user = CustomUser.objects.filter(oauthID=intra_id).first()
    if user:
        response = JsonResponse({"message": "로그인 성공."}
                                , status=status.HTTP_200_OK)
    else:
        user = CustomUser.objects.create_ft_user(oauthID=intra_id, email=email, image=image)
        response = JsonResponse({"message": "42user 회원가입 성공!"}
                                , status=status.HTTP_201_CREATED)

    token = TokenObtainPairSerializer.get_token(user)  # refresh token 생성
    refresh_token = str(token)
    access_token = str(token.access_token)  # access token 생성
    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)
    return response

class CustomPasswordValidator:
    def validate(self, password):
        if len(password) < 8:
            raise ValidationError(f"비밀번호는 최소 8글자 이상이어야 합니다.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("비밀번호는 대문자를 하나 이상 포함해야 합니다.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("비밀번호는 소문자를 하나 이상 포함해야 합니다.")
        if not re.search(r'\d', password):
            raise ValidationError("비밀번호는 숫자를 하나 이상 포함해야 합니다.")
        if not re.search(r'[@$!%*?&]', password):
            raise ValidationError("비밀번호는 특수 문자를 하나 이상 포함해야 합니다.")

    def get_help_text(self):
        return "비밀번호는 대문자, 소문자, 숫자 및 특수 문자를 포함해야 합니다."

# 회원가입
@csrf_exempt
def join (request) :
    if request.method == 'POST' :
        data = json.loads(request.body)
        userID = data.get('userID')   # 로그인 시 필요한 아이디 (고유)
        password = data.get('password')  # 로그인 시 필요한 비밀번호 (null X)
        nickname = data.get('nickname')  # 사용자 닉네임 (고유)
        email = data.get('email')  # 이메일 (고유))

    # 유효성 검사
    user = CustomUser.objects.filter(nickname=nickname).first()
    if user :
        return JsonResponse({"message": "이미 존재하는 닉네임입니다."},
            status = status.HTTP_400_BAD_REQUEST)
    
    user = CustomUser.objects.filter(email=email).first()
    if user :
        return JsonResponse({"message": "이미 존재하는 이메일입니다."},
            status = status.HTTP_400_BAD_REQUEST)
    
    try:
        validator = CustomPasswordValidator()
        validator.validate(password=password)
    except ValidationError as e:
        return JsonResponse({"errors": e.messages}, 
            status=status.HTTP_400_BAD_REQUEST)


    # 사용자가 이미 회원가입을 했는지 확인
    user = CustomUser.objects.filter(userID=userID).first()
    if user :
        return JsonResponse({"message": "이미 가입 된 회원입니다."},
            status = status.HTTP_202_ACCEPTED)
    else :
        # 사용자 생성 후 DB에 저장
        CustomUser.objects.create_user(userID=userID, password=password,nickname=nickname, email=email)
        return JsonResponse({"message": "회원가입 성공!"},
            status = status.HTTP_200_OK)

#아이디비번 확인
@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        userID = data.get('userID')
        password = data.get('password')

        user = CustomUser.objects.filter(userID=userID).first()

        if user is None:
            return JsonResponse(
                {"message": "존재하지 않는 아이디입니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif not check_password(password, user.password):
            return JsonResponse(
                {"message": "비밀번호가 틀렸습니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            # 2FA를 위한 임시 JWT 토큰 발급
            temp_token = AccessToken.for_user(user)
            temp_token.set_exp(lifetime=timedelta(minutes=10))  # 토큰 유효 기간을 10분으로 설정

            return JsonResponse(
                {"message": "아이디 비번 확인되었습니다.", "temp_token": str(temp_token)},
                status=status.HTTP_200_OK
            )

# 자체 로그인
# @csrf_exempt
# def login (request) :
#     if request.method == 'POST' :
#         data = json.loads(request.body)
#         userID = data.get('userID')
#         password = data.get('password')

#         user = CustomUser.objects.filter(userID=userID).first()

#         if user is None :
#             response = JsonResponse(
#                 {"message": "존재하지 않는 아이디입니다."},
#                 status=status.HTTP_401_UNAUTHORIZED)
#         elif check_password(password, user.password) == False :
#             response = JsonResponse(
#                 {"message": "비밀번호가 틀렸습니다."},
#                 status=status.HTTP_401_UNAUTHORIZED)
#         else :
#             token = TokenObtainPairSerializer.get_token(user)  # refresh token 생성
#             refresh_token = str(token)
#             access_token = str(token.access_token)  # access token 생성
#             response = JsonResponse(
#                 {
#                     "message": "로그인 성공",
#                     "jwt_token": {
#                         "access_token": access_token,
#                         "refresh_token": refresh_token
#                     },
#                 },
#                 status=status.HTTP_200_OK
#             )
#             response.set_cookie("access_token", access_token, httponly=True)
#             response.set_cookie("refresh_token", refresh_token, httponly=True)
#         return response

# 로그아웃
class LogoutView(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request) :
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        token = RefreshToken(token=refresh_token)
        token.blacklist()

        return JsonResponse({"message": "로그아웃 성공!"},
            status = status.HTTP_200_OK)


# 사용자 정보 반환
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        serializer = UserInfoSerializer(user, context={'request': request})

        win_rate = user.win_cnt / user.match_cnt * 100 if user.match_cnt != 0 else 0
        response_data = serializer.data
        response_data['win_rate'] = win_rate

        return Response(response_data, status=status.HTTP_200_OK)


# 사용자 정보 수정
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        # 현재 로그인된 사용자의 UserProfile을 가져옵니다.
        serializer = UserInfoSerializer(request.user, data=request.data,
                                        partial=True)  # partial=True allows partial updates

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, nickname):
        user_data = get_user_info(nickname)
        if user_data is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(user_data, status=status.HTTP_200_OK)


class UserRankingView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        users = CustomUser.objects.all().order_by('-score')
        user_rank = None

        for idx, u in enumerate(users):
            rank = idx + 1
            if u.id == user.id:
                if u.match_cnt == 0:
                    user_rank = {
                        'rank': 'null'
                    }
                else:
                    user_rank = {
                        'rank': rank
                    }
                break

        user_rank_serializer = UserRankingSerializer(user_rank)
        return Response(user_rank_serializer.data, status=status.HTTP_200_OK)

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import urllib.parse

@csrf_exempt
def login_and_redirect(request):
    if request.method == 'GET':
        token = request.GET.get('token')

        if token:
            # `user/test.html`로 토큰 전달
            return render(request, 'users/test.html', {'jwt_token': token})
        else:
            return redirect('/login_page/')  # 토큰이 없을 경우 로그인 페이지로 리다이렉트

    else:
        return redirect('/login_page/')  # POST 요청이 아닐 경우 로그인 페이지로 리다이렉트
