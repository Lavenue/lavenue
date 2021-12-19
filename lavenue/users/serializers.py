from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(validators=[UniqueValidator(queryset=get_user_model().objects.all())])

	class Meta:
		model = get_user_model()
		fields = ('username', 'email', 'password')
		extra_kwargs = {
			'password': {'write_only': True},
		}

	def create(self, validated_data):
		password = validated_data.pop('password')
		user = self.Meta.model(**validated_data)
		user.set_password(password)
		user.save()
		return user
