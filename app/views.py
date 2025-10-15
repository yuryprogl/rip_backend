from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .calc import calc
from .serializers import *


def get_draft_forecast():
    return Forecast.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


def identity_user(request):
    return get_user()


@api_view(["GET"])
def search_elements(request):
    element_name = request.GET.get("element_name", "")

    elements = Element.objects.filter(status=1)

    if element_name:
        elements = elements.filter(name__icontains=element_name)

    serializer = ElementsSerializer(elements, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_element_by_id(request, element_id):
    if not Element.objects.filter(pk=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    element = Element.objects.get(pk=element_id)
    serializer = ElementSerializer(element)

    return Response(serializer.data)


@api_view(["PUT"])
def update_element(request, element_id):
    if not Element.objects.filter(pk=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    element = Element.objects.get(pk=element_id)

    serializer = ElementSerializer(element, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_element(request):
    serializer = ElementSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Element.objects.create(**serializer.validated_data)

    elements = Element.objects.filter(status=1)
    serializer = ElementSerializer(elements, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_element(request, element_id):
    if not Element.objects.filter(pk=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    element = Element.objects.get(pk=element_id)
    element.status = 2
    element.save()

    elements = Element.objects.filter(status=1)
    serializer = ElementSerializer(elements, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_element_to_forecast(request, element_id):
    if not Element.objects.filter(pk=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    element = Element.objects.get(pk=element_id)

    draft_forecast = get_draft_forecast()

    if draft_forecast is None:
        draft_forecast = Forecast.objects.create()
        draft_forecast.owner = get_user()
        draft_forecast.save()

    if ElementForecast.objects.filter(forecast=draft_forecast, element=element).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = ElementForecast.objects.create(
        forecast=draft_forecast,
        element=element
    )
    item.save()

    serializer = ForecastSerializer(draft_forecast)
    return Response(serializer.data["elements"])


@api_view(["POST"])
def update_element_image(request, element_id):
    if not Element.objects.filter(pk=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    element = Element.objects.get(pk=element_id)

    image = request.data.get("image")
    if image is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    element.image = image
    element.save()

    serializer = ElementSerializer(element)
    return Response(serializer.data)


@api_view(["GET"])
def search_forecasts(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    forecasts = Forecast.objects.exclude(status__in=[1, 5])

    if status > 0:
        forecasts = forecasts.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        forecasts = forecasts.filter(date_formation__gt=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        forecasts = forecasts.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = ForecastsSerializer(forecasts, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_cart_info(request):
    resp = {
        "elements_count": 0,
        "draft_forecast": 0
    }

    draft_forecast = get_draft_forecast()
    if draft_forecast:
        elements = ElementForecast.objects.filter(forecast=draft_forecast)
        resp = {
            "elements_count": elements.count(),
            "draft_forecast": draft_forecast.pk
        }

    return Response(resp)


@api_view(["GET"])
def get_forecast_by_id(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)
    serializer = ForecastSerializer(forecast, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_forecast(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)
    serializer = ForecastSerializer(forecast, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return Response({
                "error": "прогноз не найден"
        }, status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)

    if forecast.status != 1:
        return Response({
                "error": "прогноз не в том статусе"
        },status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not forecast.volume:
        return Response({
            "error": "поле volume не заполнено"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecast.status = 2
    forecast.date_formation = timezone.now()
    forecast.save()

    serializer = ForecastSerializer(forecast)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return Response({
                "error": "прогноз не найден"
            }, status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])
    if request_status not in [3, 4]:
        return Response({
                "error": "некорректный status"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecast = Forecast.objects.get(pk=forecast_id)

    if forecast.status != 2:
        return Response({
                "error": "прогноз не в том статусе"
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        for item in ElementForecast.objects.filter(forecast=forecast):
            item.weight = calc(forecast, item)
            item.save()

    forecast.date_complete = timezone.now()
    forecast.status = request_status
    forecast.moderator = get_moderator()
    forecast.save()

    serializer = ForecastSerializer(forecast)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_forecast(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)

    if forecast.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecast.status = 5
    forecast.save()

    serializer = ForecastSerializer(forecast, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_element_from_forecast(request, forecast_id, element_id):
    if not ElementForecast.objects.filter(forecast_id=forecast_id, element_id=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ElementForecast.objects.get(forecast_id=forecast_id, element_id=element_id)
    item.delete()

    items = ElementForecast.objects.filter(forecast_id=forecast_id)
    data = [ElementItemSerializer(item.element, context={"temperature": item.temperature}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_element_in_forecast(request, forecast_id, element_id):
    if not ElementForecast.objects.filter(element_id=element_id, forecast_id=forecast_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)
    if forecast.status != 1:
        return Response({
            "error": "Некорректный статус прогноза"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = ElementForecast.objects.get(element_id=element_id, forecast_id=forecast_id)

    serializer = ElementForecastSerializer(item, data=request.data, partial=True)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def user_info(request):
    user = identity_user(request)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request):
    user = identity_user(request)

    serializer = UserUpdateProfileSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)