from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsReformer
from market.models import Service
from market.serializers.service_serializers.service_create_retrieve_serializer import ServiceRetrieveSerializer
from rest_framework import status

from market.serializers.service_serializers.service_update_serializer import ServiceUpdateSerializer


class MarketServiceCrudView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsReformer()]
        return super().get_permissions()

    def get(self, request, **kwargs) -> Response:
        try:
            market_service = Service.objects.filter(
                market__market_uuid=kwargs.get('market_uuid'),
                service_uuid=kwargs.get('service_uuid')
            ).select_related('market').first()
            if not market_service:
                raise Service.DoesNotExist

            serializer = ServiceRetrieveSerializer(instance=market_service)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Service.DoesNotExist:
            return Response(
                data={'message': 'market service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs):
        try:
            market_service = Service.objects.filter(
                market__market_uuid=kwargs.get('market_uuid'),
                service_uuid=kwargs.get('service_uuid')
            ).select_related('market').first()
            if not market_service:
                raise Service.DoesNotExist

            serializer = ServiceUpdateSerializer(instance=market_service, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={'message': 'market service updated'},
                    status=status.HTTP_200_OK
                )
        except (ValidationError, KeyError) as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Service.DoesNotExist:
            return Response(
                data={'message': 'market service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, **kwargs):
        try:
            market_service = Service.objects.filter(
                market__market_uuid=kwargs.get('market_uuid'),
                service_uuid=kwargs.get('service_uuid')
            ).select_related('market').first()
            if not market_service:
                raise Service.DoesNotExist

            market_service.delete()
            return Response(
                data={'message': 'market service deleted'},
                status=status.HTTP_200_OK
            )
        except Service.DoesNotExist:
            return Response(
                data={'message': 'market service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
