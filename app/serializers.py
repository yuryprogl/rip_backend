from rest_framework import serializers
from django.conf import settings

from .models import *


class ElementsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Element
        fields = ("id", "name", "status", "formula", "image")

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):

            if obj.image.url.startswith('http'):
                return obj.image.url
            
            # Собираем URL из настроек
            scheme = "https" if settings.MINIO_EXTERNAL_ENDPOINT_USE_HTTPS else "http"
            return f"{scheme}://{settings.MINIO_EXTERNAL_ENDPOINT}/images/{obj.image.url}"
        return None


class ElementSerializer(ElementsSerializer):
    class Meta(ElementsSerializer.Meta):
        fields = "__all__"


class ElementAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = ("name", "description", "formula", "image")


class ForecastBaseSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Forecast
        fields = "__all__"


class ForecastsSerializer(ForecastBaseSerializer):
    elements_count = serializers.SerializerMethodField()
    # Добавляем вычисляемое поле (НЕ В БД)
    calculated_elements_count = serializers.SerializerMethodField()

    def get_elements_count(self, forecast):
        """Возвращает ОБЩЕЕ количество элементов в прогнозе."""
        return ElementForecast.objects.filter(forecast=forecast).count()
        

    def get_calculated_elements_count(self, forecast):
        """
        Возвращает количество элементов в прогнозе, 
        для которых рассчитан результат (поле weight не является NULL).
        """
        return ElementForecast.objects.filter(forecast=forecast, weight__isnull=False).count()
    
    class Meta(ForecastBaseSerializer.Meta):
        # Явно перечисляем поля, чтобы включить calculated_elements_count
        fields = ('id', 'status', 'date_created', 'date_formation', 'date_complete', 
                  'owner', 'moderator', 'volume', 'elements_count', 'calculated_elements_count')


class ForecastSerializer(ForecastBaseSerializer):
    elements = serializers.SerializerMethodField()

    def get_elements(self, forecast):
        items = ElementForecast.objects.filter(forecast=forecast)

        if forecast.status == 3:
            return [ElementItemSerializerWithCalc(item.element, context={"temperature": item.temperature,
                                                                         "weight": item.weight}).data for item in items]

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