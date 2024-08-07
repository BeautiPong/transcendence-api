from rest_framework import serializers
from users.models import CustomUser


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['nickname', 'image', 'match_cnt', 'win_cnt', 'score', 'is_active']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    def update(self, instance, validated_data):
        nickname = validated_data.get('nickname', instance.nickname)
        if CustomUser.objects.filter(nickname=nickname).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"nickname": "This nickname is already in use."})
        instance.nickname = nickname

        image = validated_data.get('image', None)
        if image is not None:
            instance.image = image

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
