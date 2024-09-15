from django.shortcuts import get_object_or_404, render
from rest_framework import serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.views import get_paginated_response
from users.models import User

from .models import Category, Detail, Fit, Service, Style, Texture
from .selectors import ServiceSelector
from .services import (ServiceCoordinatorService, ServiceKeywordService,
                       ServicePhotoService, ServiceService)


class ServiceCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ServiceCreateInputSerializer(serializers.Serializer):
        name = serializers.CharField()
        category = serializers.CharField()
        style = serializers.ListField(required=False)
        fit = serializers.ListField(required=False)
        texture = serializers.ListField(required=False)
        detail = serializers.ListField(required=False)
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

class ServiceUpdateApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ServiceUpdateInputSerializer(serializers.Serializer):
        name= serializers.CharField(required=False)
        category=serializers.CharField(required=False)
        style=serializers.ListField(required=False)
        fit=serializers.ListField(required=False)
        texture=serializers.ListField(required=False)
        detail=serializers.ListField(required=False)
        keywords = serializers.ListField(required=False)
        basic_price = serializers.CharField(required=False)
        max_price = serializers.CharField(required=False)
        option = serializers.CharField(required=False)
        service_photos = serializers.ListField(required=False)
        info = serializers.CharField(required=False)
        notice = serializers.CharField(required=False)
        period = serializers.CharField(required=False)
        transaction_direct = serializers.BooleanField(required=False)
        transaction_package = serializers.BooleanField(required=False)
        refund = serializers.CharField(required=False)
        def __init__(self, *args, **kwargs):
            self.service = kwargs.pop('service', None)
            super().__init__(*args, **kwargs)

    def patch(self,request,service_id):
        try:
            service=Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            return Response({
                'status':'failure',
                'message':'Service is not found',
            },status=status.HTTP_404_NOT_FOUND)
        
        serializer=self.ServiceUpdateInputSerializer(service=service,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        
        service=ServiceService.update(service,data)
        return Response({
            'status': 'success',
            'data': {'id': service.id},
        }, status=status.HTTP_200_OK)

class StyleSerializer(serializers.Serializer):
    name=serializers.CharField()
    
class ReformerServiceListApi(APIView):
    permission_classes=(AllowAny,)  
    class Pagination(PageNumberPagination):
        page_size=4
        page_size_query_param='page_size'
    class ReformerServiceListFilterSerializer(serializers.Serializer):
        reformer_filter=serializers.ListField(required=False)

    class ServiceListOutputSerializer(serializers.Serializer):
        id=serializers.IntegerField()
        name=serializers.CharField()
        style=serializers.ListField(child=StyleSerializer())
        basic_price=serializers.CharField()
        user_likes=serializers.BooleanField()

    def get(self, request):
        reformer_id=request.query_params.get('reformer_filter')
        print(reformer_id)
        user = request.user  # 요청한 사용자
        reformer = get_object_or_404(User, id=reformer_id)  # 조회하려는 리포머

        if not reformer.is_reformer:
            return Response({"error": "This user is not a reformer."}, status=status.HTTP_400_BAD_REQUEST)

        services = Service.objects.filter(reformer=reformer).select_related(
            'reformer', 'category'
        ).prefetch_related(
            'style', 'fit', 'texture', 'detail'
        )

        # DTO 
        services_dtos = [{
            'id': service.id,
            'name': service.name,
            'basic_price': service.basic_price,
            'style': [{'id': s.id, 'name': s.name} for s in service.style.all()],
            'user_likes': user in service.likeuser_set.all()
        } for service in services]

        serializer = self.ServiceListOutputSerializer(services_dtos, many=True)

        return Response({
            'status': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)        