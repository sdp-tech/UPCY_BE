from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from users.models import User
from users.services import UserService

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class ReformerSignUpApi(APIView):
    permission_classes = (AllowAny,)

class UserSignUpApi(APIView):
    permission_classes = (AllowAny,)
    
    class UserSignUpInputSerializer(serializers.Serializer):
        #후에 전화번호 인증 구현(근데 이거 찾아보니까 아마 전화번호 문자 보내는 api가 다 유료일걸..?)
        email=serializers.EmailField()
        password=serializers.CharField()
        re_password=serializers.CharField()
        #nickname=serializers.CharField()
        #phone
        #얘도 드롭다운 방식이라서 나중에 필드 형식 변환 필요
        area=serializers.CharField(required=False)

    @swagger_auto_schema(
        request_body=UserSignUpInputSerializer,
        security=[],
        operation_id='유저 회원가입 API',
        operation_description="유저 기본 회원가입 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
    
    def post(self, request):
        serializers = self.UserSignUpInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
        
        UserService.user_sign_up(
            email=data.get('email'),
            password=data.get('password'),
            re_password=data.get('re_password'),
            area=data.get('area',None),
        )
        return Response({
            'status':'success',
        },status=status.HTTP_201_CREATED)
        
class UserLoginApi(APIView):
    permission_classes = (AllowAny, )

    class UserLoginInputSerializer(serializers.Serializer):
        email = serializers.CharField()
        password = serializers.CharField()

    class UserLoginOutputSerializer(serializers.Serializer):
        email = serializers.CharField()
        refresh = serializers.CharField()
        access = serializers.CharField()
        nickname = serializers.CharField(allow_blank = True)
        is_reformer = serializers.BooleanField()
        is_consumer = serializers.BooleanField()

    @swagger_auto_schema(
        request_body=UserLoginInputSerializer,
        security=[],
        operation_description='유저가 로그인하는 API 입니다.',
        operation_id='유저 로그인 API',
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json": {
                        "status": "success",
                        "email":"sdptech@gmail.com",
                        "refresh":"refresh토큰",
                        "access":"access토큰",
                        "nickname":"sdptech",
                        "is_reformer":"true",
                        "is_consumer":"true",
                    }
                }
            ),
            "400": openapi.Response(
                description="Bad Request",
            ),
        },
    
    )
    
    def post(self, request):
        input_serializer = self.UserLoginInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        service = UserService()

        login_data = service.login(
            email = data.get('email'),
            password = data.get('password'),
        )

        output_serializer = self.UserLoginOutputSerializer(data = login_data)
        output_serializer.is_valid(raise_exception=True)

        return Response({
            'status': 'success',
            'data': output_serializer.data,
        }, status = status.HTTP_200_OK)
        
class ReformerProfileApi(APIView):
    permission_classes = (AllowAny,)
    
    class ReformerProfileInputSerializer(serializers.Serializer):
        nickname=serializers.CharField()
        market_name=serializers.CharField()
        market_intro=serializers.CharField()
        links=serializers.CharField()
        area=serializers.CharField()
        
        work_style=serializers.CharField()
        special_material=serializers.CharField()
    
    @swagger_auto_schema(
        request_body=ReformerProfileInputSerializer,
        security=[],
        operation_id='리포머 프로필 등록 API',
        operation_description="리포머의 추가 정보를 등록하는 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success"
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
    
    def post(self,request):
        serializer = self.ReformerProfileInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        
        service = UserService()
        
        service.reformer_profile_register(
            user=request.user,
            nickname=data.get('nickname'),
            market_name=data.get('market_name'),
            market_intro=data.get('market_intro',None),
            links=data.get('links'),
            area=data.get('area'),
            work_style=data.get('work_style',[]),
            special_material=data.get('special_material',[]),
        )
        
        return Response({
            'status':'success',
        },status=status.HTTP_200_OK)
        
class CertificationCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class CertificationCreateInputSerializer(serializers.Serializer):
        name = serializers.CharField()
        issuing_authority = serializers.CharField()
        issue_date = serializers.DateField()
        proof_document = serializers.FileField()
       
    @swagger_auto_schema(
        request_body=CertificationCreateInputSerializer,
        security=[],
        operation_id='자격증 등록 API',
        operation_description="리포머 프로필의 경력 작성 중 하나인 자격증 등록 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success"
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
     
    def post(self,request):
        input_serializer = self.CertificationCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        
        service=UserService()
        
        service.certification_register(
            profile=request.user.reformer_profile,
            name=data.get('name'),
            issuing_authority=data.get('issuing_authority'),
            issue_date=data.get('issue_date'),
            proof_document=data.get('proof_document'),
        )
        
        return Response({
            'status':'success',
        },status=status.HTTP_200_OK)

class CompetitionCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class CompetitionCreateInputSerializer(serializers.Serializer):
        name = serializers.CharField()
        organizer = serializers.CharField()
        award_date = serializers.DateField()
        proof_document = serializers.FileField()
     
    @swagger_auto_schema(
        request_body=CompetitionCreateInputSerializer,
        security=[],
        operation_id='공모전 등록 API',
        operation_description="리포머 프로필의 경력 작성 중 하나인 공모전 등록 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success"
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
        
    def post(self,request):
        input_serializer = self.CompetitionCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        
        service=UserService()
        
        service.competition_register(
            profile=request.user.reformer_profile,
            name=data.get('name'),
            organizer=data.get('organizer'),
            award_date=data.get('award_date'),
            proof_document=data.get('proof_document'),
        )
        
        return Response({
            'status':'success',
        },status=status.HTTP_200_OK)
        
class IntershipCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class IntershipCreateInputSerializer(serializers.Serializer):
        company_name = serializers.CharField()
        department = serializers.CharField(required=False)
        position = serializers.CharField(required=False)
        start_date = serializers.DateField()
        end_date = serializers.DateField()
        proof_document = serializers.FileField()
    
    @swagger_auto_schema(
        request_body=IntershipCreateInputSerializer,
        security=[],
        operation_id='인턴 등록 API',
        operation_description="리포머 프로필 경력 등록 중 하나인 인턴/외주 경력 등록 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success"
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
        
    def post(self,request):
        input_serializer = self.IntershipCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        
        service=UserService()
        
        service.intership_register(
            profile=request.user.reformer_profile,
            company_name=data.get('company_name'),
            department=data.get('department',None),
            position=data.get('position',None),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            proof_document=data.get('proof_document'),
        )
        
        return Response({
            'status':'success',
        },status=status.HTTP_200_OK)

