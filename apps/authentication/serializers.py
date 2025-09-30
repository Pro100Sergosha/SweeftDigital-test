from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=255,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Username already exists"
            )
        ],
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Email already exists")
        ],
    )
    password = serializers.CharField(write_only=True, max_length=255)
    confirm_password = serializers.CharField(write_only=True, max_length=255)

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()
        return {"message": "User registered successfully."}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid email or password."})
        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        token = RefreshToken.for_user(user)
        return {"access": str(token.access_token), "refresh": str(token)}
