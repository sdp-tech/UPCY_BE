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
    
    def post(self, request):
        serializers = self.ServicePhotoCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
        
        service_photo_url = ServicePhotoService.create(
            image=data.get('image')
        )
        
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

    def post(self, request, service_id):
        likes=ServiceService.like_or_dislike(
            service=get_object_or_404(Service,pk=service_id),
            user=request.user
        )

        return Response({
            'status':'success',
            'data':{'likes':likes},
        },status=status.HTTP_200_OK)



