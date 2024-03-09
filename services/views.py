from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response

from .models import Service
from .services import ServiceCoordinatorService, ServiceService, ServicePhotoService

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
        ervice = service.create(
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
        
        product_photo_url = ServicePhotoService.create(
            image=data.get('image')
        )
        
        return Response({
            'status':'success',
            'data':{'location': product_photo_url},
        }, status = status.HTTP_201_CREATED)