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

#     class ReformerSignupInputSerializer(serializers.Serializer):
#         #TODO전화번호 인증 구현 필요, 테스트 후 required=False 삭제 필요
#         email = serializers.EmailField()
#         password = serializers.CharField()
#         nickname = serializers.CharField()
#         phone = serializers.CharField()
#         profile_image = serializers.ImageField(required = False)
#         thumbnail_image = serializers.ImageField(required = False)
#         agreement_terms = serializers.BooleanField(required = False)
#         market_name = serializers.CharField(required = False)
#         market_intro = serializers.CharField(required = False)
#         links = serializers.CharField(required = False)
#         area = serializers.CharField(required = False)
#         work_style = serializers.ListField(required = False)
#         school_ability = serializers.CharField(required = False)
#         school_certification = serializers.FileField(required = False)
#         career_ability = serializers.CharField(required = False)
#         career_certification = serializers.FileField(required = False)
#         license_ability =serializers.CharField(required = False)
#         license_certification = serializers.FileField(required = False)
#         freelancer_ability =serializers.CharField(required = False)
#         freelancer_certification = serializers.FileField(required = False)
#         contest_ability =serializers.CharField(required = False)
#         contest_certification = serializers.FileField(required = False)
#         etc_ability =serializers.CharField(required = False)
#         etc_certification = serializers.FileField(required = False)
#         special_material = serializers.ListField(required = False)

#     def post(self, request):
#         serializer = self.ReformerSignupInputSerializer(data = request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data

#         UserService.reformer_sign_up(
#             email = data.get('email'),
#             password = data.get('password'),
#             nickname = data.get('nickname'),
#             phone = data.get('phone', None),
#             profile_image = data.get('profile_image'),
#             thumbnail_image = data.get('thumbnail_image'),
#             agreement_terms= data.get('agreement_terms', False),
#             market_name = data.get('market_name', None),
#             market_intro = data.get('market_intro', None),
#             links = data.get('links', None),
#             area = data.get('area', None),
#             work_style = data.get('work_style', []),
#             school_ability = data.get('school_ability', None),
#             school_certification = data.get('school_certification', None),
#             career_ability = data.get('career_ability', None),
#             career_certification = data.get('career_certification', None),
#             license_ability =data.get('license_ability', None),
#             license_certification = data.get('license_certification', None),
#             freelancer_ability =data.get('license_ability', None),
#             freelancer_certification = data.get('license_certification', None),
#             contest_ability =data.get('license_ability', None),
#             contest_certification = data.get('license_certification', None),
#             etc_ability =data.get('license_ability', None),
#             etc_certification = data.get('license_certification', None),
#             special_material = data.get('special_material', []),
#         )

#         return Response({
#             'stauts': 'success',
#         },status = status.HTTP_201_CREATED)
    

# class ConsumerSignUpApi(APIView):
#     permission_classes = (AllowAny, )

#     class ConsumerSignUpInputSerializer(serializers.Serializer):
#         #TODO전화번호인증필요
#         email = serializers.EmailField()
#         password = serializers.CharField()
#         nickname = serializers.CharField()
#         phone = serializers.CharField(required = False)
#         profile_image = serializers.ImageField(required = False)
#         agreement_terms = serializers.BooleanField(required = False)
#         area = serializers.CharField(required = False)
#         prefer_style = serializers.ListField(required = False)

#     def post(self, request):
#         serializers = self.ConsumerSignUpInputSerializer(data = request.data)
#         serializers.is_valid(raise_exception=True)
#         data = serializers.validated_data

#         UserService.consumer_sign_up(
#             email = data.get('email'),
#             password = data.get('password'),
#             nickname = data.get('nickname',),
#             phone = data.get('phone', None),
#             profile_image = data.get('profile_image'),
#             agreement_terms= data.get('agreement_terms', False),
#             area = data.get('area', None),
#             prefer_style = data.get('prefer_style',[]),
#         )

#         return Response({ 
#             'stauts': 'success',
#         },status = status.HTTP_201_CREATED)

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

