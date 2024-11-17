import os

from boto3 import client
from botocore import errorfactory
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import ReformerFreelancer
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerFreelancerSerializer,
)


class ReformerFreelancerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        try:
            freelancer_uuid = kwargs.get("freelancer_uuid")
            reformer_freelancer = ReformerFreelancer.objects.filter(
                freelancer_uuid=freelancer_uuid
            ).first()
            if not reformer_freelancer:
                raise ReformerFreelancer.DoesNotExist

            serializer = ReformerFreelancerSerializer(instance=reformer_freelancer)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ReformerFreelancer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 프리랜서/외주 경력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs):
        try:
            freelancer_uuid = kwargs.get("freelancer_uuid")
            reformer_freelancer = ReformerFreelancer.objects.filter(
                freelancer_uuid=freelancer_uuid
            ).first()
            if not reformer_freelancer:
                raise ReformerFreelancer.DoesNotExist

            serializer = ReformerFreelancerSerializer(
                instance=reformer_freelancer, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data={"message": "successfully updated"}, status=status.HTTP_200_OK
                )
            else:
                raise ValueError(f"{serializer.errors}")
        except (AttributeError, ValueError) as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except ReformerFreelancer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 프리랜서/외주 경력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, **kwargs):
        try:
            freelancer_uuid = kwargs.get("freelancer_uuid")
            reformer_freelancer = ReformerFreelancer.objects.filter(
                freelancer_uuid=freelancer_uuid
            ).first()
            if not reformer_freelancer:
                raise ReformerFreelancer.DoesNotExist

            with transaction.atomic():
                if reformer_freelancer.proof_document:  # 증명 서류가 존재한다면, 삭제
                    s3 = client("s3")
                    s3.delete_object(
                        Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                        Key=reformer_freelancer.proof_document.name,
                    )

                reformer_freelancer.delete()
                return Response(
                    data={"message": "successfully deleted"}, status=status.HTTP_200_OK
                )
        except IntegrityError:
            return Response(
                data={"message": "데이터베이스 무결성 오류"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except errorfactory.ClientError:
            return Response(
                data={"message": "백엔드에서 설정한 버킷이 존재하지 않습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ReformerFreelancer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 프리랜서/외주 경력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
