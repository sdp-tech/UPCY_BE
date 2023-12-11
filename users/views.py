from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from users.models import User
from users.services import UserService

# Create your views here.

class ReformerSignUpApi(APIView):
    permission_classes = (AllowAny,)

    class ReformerSignupInputSerializer(serializers.Serializer):
        #TODO재학증명서, 전화번호 인증 구현 필요
        email = serializers.EmailField()
        password = serializers.CharField()
        nickname = serializers.CharField()
        phone = serializers.CharField()
        agreement_terms = serializers.BooleanField()
        school = serializers.CharField()
        is_enrolled = serializers.CharField()
        area = serializers.CharField()
        career = serializers.CharField()
        work_style = serializers.ListField()
        bios = serializers.CharField()
        certificate_studentship = serializers.ImageField()

    def post(self, request):
        serializer = self.ReformerSignupInputSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        UserService.reformer_sign_up(
            email = data.get('email'),
            password = data.get('password'),
            nickname = data.get('nickname'),
            phone = data.get('phone'),
            agreement_terms= data.get('agreement_terms'),
            school = data.get('school'),
            is_enrolled = data.get('is_enrolled'),
            area = data.get('area'),
            career = data.get('career'),
            work_style=data.get('work_style'),
            bios = data.get('bios'),
            certificate_studentship = data.get('certificate_studentship'),
        )

        return Response({
            'stauts': 'success',
        },status = status.HTTP_201_CREATED)