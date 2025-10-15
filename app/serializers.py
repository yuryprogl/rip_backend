from rest_framework import serializers

from .models import *


class ElementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = ("id", "name", "status", "formula", "image")


class ElementSerializer(ElementsSerializer):
    class Meta(ElementsSerializer.Meta):
        fields = "__all__"


class ForecastsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Forecast
        fields = "__all__"


class ForecastSerializer(ForecastsSerializer):
    elements = serializers.SerializerMethodField()
            
    def get_elements(self, forecast):
        items = ElementForecast.objects.filter(forecast=forecast)

        if forecast.status == 3:
            return [ElementItemSerializerWithCalc(item.element, context={"temperature": item.temperature, "weight": item.weight}).data for item in items]

        return [ElementItemSerializer(item.element, context={"temperature": item.temperature}).data for item in items]


class ElementItemSerializer(ElementSerializer):
    temperature = serializers.SerializerMethodField()

    def get_temperature(self, _):
        return self.context.get("temperature")


class ElementItemSerializerWithCalc(ElementItemSerializer):
    weight = serializers.SerializerMethodField()

    def get_weight(self, _):
        return self.context.get("weight")


class ElementForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementForecast
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        instance = super().update(instance, validated_data)

        if password and password.strip() and not self.instance.check_password(password):
            instance.set_password(password)
            instance.save()

        return instance