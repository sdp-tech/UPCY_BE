from sqlite3 import IntegrityError

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import Reformer
from users.serializers.reformer_serializer.reformer_profile_serializer import \
    ReformerProfileSerializer
from users.serializers.reformer_serializer.reformer_update_serializer import \
    ReformerUpdateSerializer
from users.services import UserService


class ReformerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    user_service = UserService()

    def get(self, request) -> Response:
        user = request.user
        try:
            reformer_profile = Reformer.objects.filter(user=user).first()
            if not reformer_profile:
                raise Reformer.DoesNotExist

            serializer = ReformerProfileSerializer(instance=reformer_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reformer.DoesNotExist:
            return Response(
                data={
                    "message": "Cannot find reformer profile that belongs to the user"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request) -> Response:
        user = request.user
        try:
            serializer = ReformerProfileSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                self.user_service.update_user_role(
                    user=user, role="reformer"
                )  # Reformer 프로필 등록 -> user role 변경
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
                data={"message": "데이터베이스 무결성 오류", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                data={"message": "예기치 못한 오류 발생", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request) -> Response:
        try:
            user = request.user
            reformer_profile = Reformer.objects.filter(user=user).first()
            if not reformer_profile:
                raise Reformer.DoesNotExist

            serializer = ReformerUpdateSerializer(
                instance=reformer_profile, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                print(serializer.validated_data)
                serializer.save()
                return Response(
                    data={"message": "successfully updated"}, status=status.HTTP_200_OK
                )
        except Reformer.DoesNotExist:
            return Response(
                data={
                    "message": "Cannot find reformer profile that belongs to the user"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except (AttributeError, serializers.ValidationError) as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):
        user = request.user
        try:
            reformer_profile = Reformer.objects.filter(user=user).first()
            if not reformer_profile:
                raise Reformer.DoesNotExist

            with transaction.atomic():
                reformer_profile.delete()
                self.user_service.update_user_role(
                    user=user, role="user"
                )  # reformer 프로필 삭제 -> user role 변경
                return Response(
                    data={"message": "successfully deleted"}, status=status.HTTP_200_OK
                )
        except Reformer.DoesNotExist:
            return Response(
                data={
                    "message": "Cannot find reformer profile that belongs to the user"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": f"{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
