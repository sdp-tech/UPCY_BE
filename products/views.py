from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from core.views import get_paginated_response
from users.models import User

from .models import Product, Category, Style, Fit, Texture, Detail
from .services import ProductCoordinatorService, ProductPhotoService, ProductKeywordService, ProductService
from .selectors import ProductSelector

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class ProductCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ProductCreateInputSerializer(serializers.Serializer):
        name = serializers.CharField()
        
        category = serializers.CharField(required=False)
        style = serializers.ListField(required=False)
        fit = serializers.ListField(required=False)
        texture = serializers.ListField(required=False)
        detail=serializers.ListField(required=False)
        
        keywords = serializers.ListField(required=False)
        basic_price = serializers.CharField()
        option = serializers.CharField()
        product_photos = serializers.ListField(required=False)
        info = serializers.CharField()
        notice = serializers.CharField()
        period = serializers.CharField()
        transaction_direct = serializers.BooleanField()
        transaction_package = serializers.BooleanField()
        refund = serializers.CharField()
    
    @swagger_auto_schema(
        request_body=ProductCreateInputSerializer,
        security=[],
        operation_id='상품 생성 API',
        operation_description="리포머의 상품을 등록하는 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "name":"상품이름",
                        "category":"1",
                        "style":[1,2],
                        "fit":[1],
                        "texture":[1],
                        "detail":[],
                        "keywords":[],
                        "basic_price":'8000',
                        "option":'단추',
                        "product_photos":'~~~.img',
                        "info":"상품 정보",
                        "notice":'상품 관련 공지사항',
                        "period":"3",
                        "trasaction_direct":"true",
                        "trasaction_package":'true',
                        "refund":"환불 관련 정보",
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
    
    def post(self,request):
        serializers = self.ProductCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
        
        service=ProductCoordinatorService(user=request.user)
        
        product = service.create(
            name=data.get('name'),
            
            category = data.get('category'),
            style=data.get('style',[]),
            fit=data.get('fit',[]),
            texture=data.get('texture',[]),
            detail=data.get('detail',[]),
                        
            keywords=data.get('keywords', []),
            basic_price=data.get('basic_price'),
            option=data.get('option'),
            product_photos=data.get('product_photos', []),
            info=data.get('info'),
            notice=data.get('notice'),
            period=data.get('period'),
            transaction_direct=data.get('transaction_direct'),
            transaction_package=data.get('transaction_package'),
            refund=data.get('refund'),
            )
        if product is not None:
            return Response({
                'status' : 'success',
                'data' : {'id': product.id},
            },status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status':'failure','message':'Product생성 실패',
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ProductPhotoCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ProductPhotoCreateInputSerializer(serializers.Serializer):
        image = serializers.ImageField()
        
    @swagger_auto_schema(
        request_body=ProductPhotoCreateInputSerializer,
        security=[],
        operation_id='상품 사진 등록 API',
        operation_description="상품 사진을 등록하는 API 입니다.",
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
        serializers = self.ProductPhotoCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
        
        product_photo_url = ProductPhotoService.create(
            image=data.get('image')
        )
        
        return Response({
            'status':'success',
            'data':{'location': product_photo_url},
        }, status = status.HTTP_201_CREATED)
        
class ProductDetailApi(APIView):
    permission_classes=(AllowAny,)
    
    class ProductDetailOuutputSerializer(serializers.Serializer):
        id=serializers.IntegerField()
        market=serializers.CharField()
        nickname=serializers.CharField()
        
        style = serializers.ListField(child=serializers.DictField())
        texture = serializers.ListField(child=serializers.DictField())
        fit = serializers.ListField(child=serializers.DictField())
        detail = serializers.ListField(child=serializers.DictField())
        category=serializers.DictField()
        option = serializers.CharField()
                    
        name = serializers.CharField()
        reformer = serializers.CharField()
        basic_price = serializers.CharField()
        info = serializers.CharField()
        notice = serializers.CharField()
        period = serializers.CharField()
        user_likes = serializers.BooleanField()
        like_cnt=serializers.IntegerField()
        category = serializers.DictField()
        photos = serializers.ListField()
    
        transaction_direct = serializers.BooleanField()
        transaction_package = serializers.BooleanField()
        
    @swagger_auto_schema(
        security=[],
        operation_id='상품 글 조회 API',    
        operation_description='''
            전달된 id에 해당하는 상품 글 디테일을 조회합니다.<br/>
            photos 배열 중 0번째 원소가 대표 이미지(rep_pic)입니다.<br/>
        ''',
        responses={ 
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "name":'products_test_240106',
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
    
    def get(self,request,product_id):
        product= ProductSelector.detail(product_id=product_id, user=request.user)
        serializer=self.ProductDetailOuutputSerializer(product)
        
        return Response({
            'status': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
        

class ProductListApi(APIView):
    permission_classes = (AllowAny,)
    
    class Pagination(PageNumberPagination):
        page_size= 4
        page_size_query_param = 'page_size'
    
    class ProductListFilterSerializer(serializers.Serializer):
        search = serializers.CharField(required=False)
        order = serializers.CharField(required=False)
        ## 필터 
        category_filter = serializers.CharField(required=False)
        style_filter = serializers.ListField(required=False)
        fit_filter = serializers.ListField(required=False)
        texture_filter = serializers.ListField(required=False)
        detail_filter = serializers.ListField(required=False)
        #금액 & 수선기간 필터링 추가
        
    
    class ProductListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        reformer = serializers.CharField()
        basic_price = serializers.CharField()
        user_likes = serializers.BooleanField()
        category = serializers.DictField()
        photos = serializers.ListField()
        style = serializers.ListField(child=serializers.DictField())
        texture = serializers.ListField(child=serializers.DictField())
        fit = serializers.ListField(child=serializers.DictField())
        detail = serializers.ListField(child=serializers.DictField())
     
    @swagger_auto_schema(
        security=[],
        operation_id='상품 목록 조회 API',
        operation_description='''
            전달된 쿼리 파라미터에 부합하는 상품 글 리스트를 반환합니다.<br/>
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
                                "name":'products_test_240106',
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
        filters_serializer = self.ProductListFilterSerializer(
            data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        filters = filters_serializer.validated_data
        
        products = ProductSelector.list(
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
            serializer_class=self.ProductListOutputSerializer,
            queryset=products,
            request=request,
            view=self
        )
        
        

class ProductLikeApi(APIView):
    permission_classes = (IsAuthenticated, )
    
    @swagger_auto_schema(
        operation_id='상품 좋아요 또는 좋아요 취소',
        operation_description='''
            입력한 id를 가지는 상품에 대한 사용자의 좋아요/좋아요 취소를 수행합니다.<br/>
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
    def post(self, request, product_id):
        likes = ProductService.like_or_dislike(
            product=get_object_or_404(Product,pk=product_id),
            user=request.user
        )

        return Response({
            'status' : 'success',
            'data':{'likes':likes},
        },status=status.HTTP_200_OK)