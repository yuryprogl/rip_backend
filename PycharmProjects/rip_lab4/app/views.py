import uuid
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .calc import calc
from .permissions import IsModerator, IsAuthenticated, IsBuyer
from .redis import session_storage
from .serializers import *
from .utils import get_session, get_draft_forecast, identity_user


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'element_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
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


@swagger_auto_schema(method='put', request_body=ElementSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_element(request, element_id):
    if not Element.objects.filter(pk=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    element = Element.objects.get(pk=element_id)

    serializer = ElementSerializer(element, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=ElementAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def create_element(request):
    serializer = ElementSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Element.objects.create(**serializer.validated_data)

    elements = Element.objects.filter(status=1)
    serializer = ElementSerializer(elements, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
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
@permission_classes([IsBuyer])
def add_element_to_forecast(request, element_id):
    if not Element.objects.filter(pk=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    element = Element.objects.get(pk=element_id)

    draft_forecast = get_draft_forecast(request)

    if draft_forecast is None:
        draft_forecast = Forecast.objects.create()
        draft_forecast.owner = identity_user(request)
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


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
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


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_forecasts(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    forecasts = Forecast.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        forecasts = forecasts.filter(owner=user)

    if status > 0:
        forecasts = forecasts.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        forecasts = forecasts.filter(date_formation__gt=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        forecasts = forecasts.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = ForecastsSerializer(forecasts, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsBuyer])
def get_cart_info(request):
    resp = {
        "elements_count": 0,
        "draft_forecast": 0
    }

    draft_forecast = get_draft_forecast(request)
    if draft_forecast:
        elements = ElementForecast.objects.filter(forecast=draft_forecast)
        resp = {
            "elements_count": elements.count(),
            "draft_forecast": draft_forecast.pk
        }

    return Response(resp)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_forecast_by_id(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)

    user = identity_user(request)
    if not user.is_superuser and forecast.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ForecastSerializer(forecast, many=False)
    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ForecastSerializer)
@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_forecast(request, forecast_id):
    user = identity_user(request)
    if not Forecast.objects.filter(pk=forecast_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)
    serializer = ForecastSerializer(forecast, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_status_user(request, forecast_id):
    user = identity_user(request)
    if not Forecast.objects.filter(pk=forecast_id, owner=user).exists():
        return Response({
            "error": "прогноз не найден"
        }, status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)

    if forecast.status != 1:
        return Response({
            "error": "прогноз не в том статусе"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not forecast.volume:
        return Response({
            "error": "поле volume не заполнено"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecast.status = 2
    forecast.date_formation = timezone.now()
    forecast.save()

    serializer = ForecastSerializer(forecast)
    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

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
    forecast.moderator = identity_user(request)
    forecast.save()

    serializer = ForecastSerializer(forecast)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsBuyer])
def delete_forecast(request, forecast_id):
    user = identity_user(request)
    if not Forecast.objects.filter(pk=forecast_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecast = Forecast.objects.get(pk=forecast_id)

    if forecast.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecast.status = 5
    forecast.save()

    serializer = ForecastSerializer(forecast, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsBuyer])
def delete_element_from_forecast(request, forecast_id, element_id):
    user = identity_user(request)
    if not Forecast.objects.filter(pk=forecast_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ElementForecast.objects.filter(forecast_id=forecast_id, element_id=element_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ElementForecast.objects.get(forecast_id=forecast_id, element_id=element_id)
    item.delete()

    items = ElementForecast.objects.filter(forecast_id=forecast_id)
    data = [ElementItemSerializer(item.element, context={"temperature": item.temperature}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=ElementForecastSerializer)
@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_element_in_forecast(request, forecast_id, element_id):
    user = identity_user(request)
    if not Forecast.objects.filter(pk=forecast_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

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


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@api_view(["GET"])
def user_info(request):
    user = identity_user(request)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=UserUpdateProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = identity_user(request)

    serializer = UserUpdateProfileSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)
