from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import Reformer, ReformerAwards
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerAwardsSerializer,
)


class ReformerAwardsCreateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            reformer_awards = ReformerAwards.objects.filter(
                reformer=request.user.reformer_profile
            )
            if not reformer_awards:
                raise Reformer.DoesNotExist

            serializer = ReformerAwardsSerializer(instance=reformer_awards, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except AttributeError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Reformer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 User가 생성한 Reformer 프로필 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        try:
            reformer = Reformer.objects.filter(user=request.user).first()
            if not reformer:
                raise Reformer.DoesNotExist

            serializer = ReformerAwardsSerializer(
                data=request.data, context={"reformer": reformer}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    data={"message": "successfully created"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                raise ValueError(f"{serializer.errors}")
        except (AttributeError, ValueError) as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as e:
            return Response(
                data={"message": "데이터베이스 무결성 오류"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Reformer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 User가 생성한 Reformer 프로필 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
