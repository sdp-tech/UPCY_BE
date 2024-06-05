from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from core.views import get_paginated_response
from users.models import User

from .models import Service, Category, Style, Fit, Texture, Detail
from .services import ServiceCoordinatorService, ServiceService, ServicePhotoService, ServiceKeywordService
from .selectors import ServiceSelector

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class ServiceCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ServiceCreateInputSerializer(serializers.Serializer):
        name= serializers.CharField()
        
        category=serializers.CharField()
        style=serializers.ListField(required=False)
        fit=serializers.ListField(required=False)
        texture=serializers.ListField(required=False)
        detail=serializers.ListField(required=False)
        keywords = serializers.ListField(required=False)

        basic_price = serializers.CharField()
        max_price = serializers.CharField()
        option = serializers.CharField()
        service_photos = serializers.ListField(required=False)
        info = serializers.CharField()
        notice = serializers.CharField()
        period = serializers.CharField()
        transaction_direct = serializers.BooleanField()
        transaction_package = serializers.BooleanField()
        refund = serializers.CharField()
    
    @swagger_auto_schema(
        request_body=ServiceCreateInputSerializer,
        security=[],
        operation_id='서비스 생성 API',
        operation_description="서비스를 생성하는 API입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "name":"서비스 이름",
                        "category":"1",
                        "style":[1,2],
                        "fit":[1],
                        "texture":[1],
                        "detail":[],
                        "keywords":[],
                        "basic_price":'8000',
                        "max_price":'12000',
                        "option":'단추',
                        "service_photos":'~~~.img',
                        "info":"서비스 정보",
                        "notice":'서비스 관련 공지사항',
                        "period":"3",
                        "trasaction_direct":"true",
                        "trasaction_package":'true',
                        "refund":"환불 관련 정보",
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            )
        }
    )
    def post(self,request):
        serializers = self.ServiceCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
        
        service = ServiceCoordinatorService(user=request.user)
        service = service.create(
            name=data.get('name'),
        
            category = data.get('category'),
            style=data.get('style',[]),
            fit=data.get('fit',[]),
            texture=data.get('texture',[]),
            detail=data.get('detail',[]),
                            
            keywords=data.get('keywords', []),
            basic_price=data.get('basic_price'),
            max_price=data.get('max_price'),
            option=data.get('option'),
            service_photos=data.get('service_photos', []),
            info=data.get('info'),
            notice=data.get('notice'),
            period=data.get('period'),
            transaction_direct=data.get('transaction_direct'),
            transaction_package=data.get('transaction_package'),
            refund=data.get('refund'),
            )

        if service is not None:
            return Response({
                'status' : 'success',
                'data' : {'id': service.id},
            },status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status':'failure','message':'Service 생성 실패',
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
            
class ServicePhotoCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ServicePhotoCreateInputSerializer(serializers.Serializer):
        image = serializers.ImageField()
        
    @swagger_auto_schema(
        request_body=ServicePhotoCreateInputSerializer,
        security=[],
        operation_id='서비스 사진 등록 API',
        operation_description="서비스 사진을 등록하는 API 입니다.",
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
        serializers = self.ServicePhotoCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data

        image_file = data.get('image')


        service_photo_service = ServicePhotoService(file=image_file)

        service_photo_url = service_photo_service.upload()
        
        #service_photo_url = ServicePhotoService.upload(
        #    image=data.get('image')
        #)
        
        return Response({
            'status':'success',
            'data':{'location': service_photo_url},
        }, status = status.HTTP_201_CREATED)
    
class ServiceDetailApi(APIView):
    permission_classes=(AllowAny,)

    class ServiceDetailOuputSerialier(serializers.Serializer):
        id=serializers.IntegerField()
        market=serializers.CharField()
        nickname=serializers.CharField()

        style=serializers.ListField(child=serializers.DictField())
        texture=serializers.ListField(child=serializers.DictField())
        fit=serializers.ListField(child=serializers.DictField())
        detail=serializers.ListField(child=serializers.DictField())
        category=serializers.DictField()
        option=serializers.CharField()
                    
        name=serializers.CharField()
        reformer=serializers.CharField()
        basic_price=serializers.CharField()
        info=serializers.CharField()
        notice=serializers.CharField()
        period=serializers.CharField()
        user_likes=serializers.BooleanField()
        like_cnt=serializers.IntegerField()
        category=serializers.DictField()
        photos=serializers.ListField()

        transaction_direct=serializers.BooleanField()
        transaction_package=serializers.BooleanField()
        
    @swagger_auto_schema(
        security=[],
        operation_id='서비스 글 조회 API',    
        operation_description='''
            전달된 id에 해당하는 서비스 글 디테일을 조회합니다.<br/>
            photos 배열 중 0번째 원소가 대표 이미지(rep_pic)입니다.<br/>
        ''',
        responses={ 
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "name":'services_test_240106',
                        "category":'1',
                        "style":[1,2],
                        "fit":[1],
                        "texture":[1,2,3],
                        "detail":[],
                        "keywords":['후드티','후드'],
                        "basic_price":1000,
                        "info":'product no 1',
                        "notice":'noticesssss',
                        "option":'긴팔',
                        "period":3,
                        "transaction_direct":'true',
                        "transaction_package":'true',
                        "refund":'환불정책',
                        "reformer":"sdptech@gmail.com",
                        "likeuserset":['user1@gmail.com','user2@gmail.com',],
                        'likecnt':2,
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
      
    def get(self,request,service_id):
        service=ServiceSelector.detail(service_id=service_id, user=request.user)
        serializer=self.ServiceDetailOuputSerialier(service)

        return Response({
            'status':'success',
            'data':serializer.data,
        }, status=status.HTTP_200_OK)

class ServiceListApi(APIView):
    permission_classes=(AllowAny,)

    class Pagination(PageNumberPagination):
        page_size=4
        page_size_query_param='page_size'

    class ServiceListFilterSerializer(serializers.Serializer):
        search=serializers.CharField(required=False)
        order=serializers.CharField(required=False)

        category_filter=serializers.CharField(required=False)
        style_filter=serializers.ListField(required=False)
        fit_filter=serializers.ListField(required=False)
        texture_filter=serializers.ListField(required=False)
        detail_filter=serializers.ListField(required=False)

    class ServiceListOutputSerializer(serializers.Serializer):
        id=serializers.IntegerField()
        name=serializers.CharField()
        reformer=serializers.CharField()
        basic_price=serializers.CharField()
        user_likes=serializers.BooleanField()
        category=serializers.DictField()
        photos=serializers.ListField()
        style=serializers.ListField(child=serializers.DictField())
        texture=serializers.ListField(child=serializers.DictField())
        fit=serializers.ListField(child=serializers.DictField())
        detail=serializers.ListField(child=serializers.DictField())

    @swagger_auto_schema(
        security=[],
        operation_id='서비스 목록 조회 API',
        operation_description='''
            전달된 쿼리 파라미터에 부합하는 서비스 글 리스트를 반환합니다.<br/>
            photos 배열 중 0번째 원소가 대표 이미지(rep_pic)입니다.<br/>
            <br/>
            search : name, info 내 검색어<br/>
            order : 정렬 기준(latest, hot)<br/>
            category_filter: 카테고리 id <br/>
            style_filter: 스타일 id <br/>
            fit_filter: 핏 id <br/>
            texture_filter : 텍스쳐 id <br/>
            detail_filter: 디테일 id <br/>
        ''',
        responses={ 
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json": {
                    "status": "success",
                    "data": {
                        "count": 1,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "name":'services_test_240106',
                                "category":'1',
                                "style":[1,2],
                                "fit":[1],
                                "texture":[1,2,3],
                                "detail":[],
                                "keywords":['후드티','후드'],
                                "basic_price":1000,
                                "info":'product no 1',
                                "notice":'noticesssss',
                                "option":'긴팔',
                                "period":3,
                                "transaction_direct":'true',
                                "transaction_package":'true',
                                "refund":'환불정책',
                                "reformer":"sdptech@gmail.com",
                                "likeuserset":['user1@gmail.com','user2@gmail.com',],
                                'likecnt':2,                   
                                },
                            ]
                        }
                    }
                }
            ),
            
            "400":openapi.Response(
                description="Bad Request",
            ),
        }    
    )
    
    def get(self,request):
        filters_serializer=self.ServiceListFilterSerializer(
            data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        filters=filters_serializer.validated_data

        services=ServiceSelector.list(
            search=filters.get('search',''),
            order=filters.get('order','latest'),
            category_filter=filters.get('category_filter',''),
            style_filters = filters.get('style_filter',[]),
            fit_filters=filters.get('fit_filter',[]),
            texture_filters=filters.get('texture_filter',[]),
            detail_filters=filters.get('detail_filter',[]),
            user=request.user,
        )

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ServiceListOutputSerializer,
            queryset=services,
            request=request,
            view=self
        )

class ServiceLikeApi(APIView):
    permission_classes=(IsAuthenticated, )

    @swagger_auto_schema(
        operation_id='서비스 좋아요 또는 좋아요 취소',
        operation_description='''
            입력한 id를 가지는 서비스에 대한 사용자의 좋아요/좋아요 취소를 수행합니다.<br/>
            결과로 좋아요 상태(TRUE:좋아요, FALSE:좋아요X)가 반환됩니다.
        ''',
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json": {
                        "status": "success",
                        "data": {"likes": True}
                    }
                }
            ),
            "400": openapi.Response(
                description="Bad Request",
            ),
        },
    )
    
    def post(self, request, service_id):
        likes=ServiceService.like_or_dislike(
            service=get_object_or_404(Service,pk=service_id),
            user=request.user
        )

        return Response({
            'status':'success',
            'data':{'likes':likes},
        },status=status.HTTP_200_OK)



