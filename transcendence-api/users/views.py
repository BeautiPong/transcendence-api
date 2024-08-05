from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.http import JsonResponse
import requests
import urllib.parse



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






