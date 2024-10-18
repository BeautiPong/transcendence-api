from rest_framework import serializers
from scoreHistory.models import ScoreHistory
from users.models import CustomUser  # CustomUser 모델을 import하세요.

class ScoreHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreHistory
        fields = ['score', 'create_time']

class OverallRankingSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    image_url = serializers.SerializerMethodField()  # 이미지 URL 필드 추가
    rank = serializers.IntegerField(allow_null=True)

    def get_image_url(self, obj):
        request = self.context.get('request')
        user = CustomUser.objects.filter(nickname=obj['nickname']).first()  # 사용자를 nickname으로 가져오기
        if user and user.image:
            return request.build_absolute_uri(user.image.url)
        return None  # 기본 이미지 경로

