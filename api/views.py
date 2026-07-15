from rest_framework.decorators import api_view
from rest_framework.response import Response

from health_records.models import HealthRecord
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from .serializers import HealthRecordSerializer
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from .serializers import ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def health_records(request):

    if request.method == 'GET':

        records = HealthRecord.objects.filter(
            user=request.user
        )

        # Search
        search = request.GET.get('search')

        if search:
            records = records.filter(
                Q(risk__icontains=search) |
                Q(blood_pressure__icontains=search)
            )

        # Filters
        risk = request.GET.get('risk')
        min_glucose = request.GET.get('min_glucose')
        max_glucose = request.GET.get('max_glucose')

        if risk:
            records = records.filter(risk=risk)

        if min_glucose:
            records = records.filter(glucose_level__gte=min_glucose)

        if max_glucose:
            records = records.filter(glucose_level__lte=max_glucose)

        # Ordering
        ordering = request.GET.get('ordering')

        if ordering:
            records = records.order_by(ordering)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 5

        result_page = paginator.paginate_queryset(
            records,
            request
        )

        serializer = HealthRecordSerializer(
            result_page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    elif request.method == 'POST':

        serializer = HealthRecordSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(user=request.user)

            return Response(serializer.data)

        return Response(serializer.errors)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_record(request, id):

    record = get_object_or_404(
        HealthRecord,
        id=id,
        user=request.user
    )

    serializer = HealthRecordSerializer(
        record,
        data=request.data
    )

    if serializer.is_valid():

        serializer.save(user=request.user)

        return Response(serializer.data)

    return Response(serializer.errors)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_record(request, id):

    record = get_object_or_404(
        HealthRecord,
        id=id,
        user=request.user
    )

    record.delete()

    return Response({
        "message": "Health record deleted successfully."
    })

@api_view(['POST'])
def register(request):

    serializer = RegisterSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            {
                "message": "User registered successfully."
            },
            status=201
        )

    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):

    user = request.user

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "date_joined": user.date_joined
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):

    serializer = ChangePasswordSerializer(
        data=request.data
    )

    if serializer.is_valid():

        user = request.user

        if not user.check_password(
            serializer.validated_data['old_password']
        ):

            return Response(
                {
                    "error": "Old password is incorrect."
                },
                status=400
            )

        user.set_password(
            serializer.validated_data['new_password']
        )

        user.save()

        return Response(
            {
                "message": "Password changed successfully."
            }
        )

    return Response(serializer.errors)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):

    try:

        refresh_token = request.data["refresh"]

        token = RefreshToken(refresh_token)

        token.blacklist()

        return Response(
            {
                "message": "Logout successful."
            },
            status=200
        )

    except Exception:

        return Response(
            {
                "error": "Invalid or expired refresh token."
            },
            status=400
        )