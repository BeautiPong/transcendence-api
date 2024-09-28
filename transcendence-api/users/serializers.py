from rest_framework import serializers
from users.models import CustomUser


class UserInfoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # image_url 필드 추가
    
    class Meta:
        model = CustomUser
        fields = ['nickname', 'image','image_url', 'match_cnt', 'win_cnt', 'score', 'is_active']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            # 이미지가 존재하면 절대 URL을 반환
            return request.build_absolute_uri(obj.image.url)
        return request.build_absolute_uri('/path/to/default/image.jpg')  # 기본 이미지 경로

    def update(self, instance, validated_data):
        # 닉네임 중복 체크
        nickname = validated_data.get('nickname', instance.nickname)
        if CustomUser.objects.filter(nickname=nickname).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"nickname": "This nickname is already in use."})
        instance.nickname = nickname

        print("rotorRL")
        # 이미지 업데이트
        image = validated_data.get('image', None)
        print(image)
        if image is not None:
            instance.image = image

        # 다른 필드 업데이트
        instance.match_cnt = validated_data.get('match_cnt', instance.match_cnt)
        instance.win_cnt = validated_data.get('win_cnt', instance.win_cnt)
        instance.score = validated_data.get('score', instance.score)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()
        return instance

class UserRankingSerializer(serializers.Serializer):
    rank = serializers.IntegerField()

class UserScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['match_cnt', 'win_cnt', 'score']

    def update(self, instance, validated_data):
        instance.match_cnt = validated_data.get('match_cnt', instance.match_cnt)
        instance.win_cnt = validated_data.get('win_cnt', instance.win_cnt)
        instance.score = validated_data.get('score', instance.score)
        instance.save()
        return instance
