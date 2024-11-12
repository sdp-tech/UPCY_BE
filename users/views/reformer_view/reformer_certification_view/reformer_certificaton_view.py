import os

from boto3 import client
from botocore import errorfactory
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import ReformerCertification, ReformerEducation
from users.serializers.reformer_serializer.reformer_profile_serializer import (
<<<<<<< HEAD
    ReformerCertificationSerializer, ReformerEducationSerializer)
=======
    ReformerCertificationSerializer,
    ReformerEducationSerializer,
)
>>>>>>> c58c23774c09e48cfe239ed971af9fe92c340c29


class ReformerCertificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        try:
            certification_uuid = kwargs.get("certification_uuid")
            reformer_certification = ReformerCertification.objects.filter(
                certification_uuid=certification_uuid
            ).first()
            if not reformer_certification:
                raise ReformerCertification.DoesNotExist

            serializer = ReformerCertificationSerializer(
                instance=reformer_certification
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ReformerCertification.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 자격증 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, **kwargs):
        try:
            certification_uuid = kwargs.get("certification_uuid")
            reformer_certification = ReformerCertification.objects.filter(
                certification_uuid=certification_uuid
            ).first()
            if not reformer_certification:
                raise ReformerCertification.DoesNotExist

            serializer = ReformerCertificationSerializer(
                instance=reformer_certification, data=request.data, partial=True
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
        except ReformerCertification.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 자격증 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, **kwargs):
        try:
            certification_uuid = kwargs.get("certification_uuid")
            reformer_certification = ReformerCertification.objects.filter(
                certification_uuid=certification_uuid
            ).first()
            if not reformer_certification:
                raise ReformerCertification.DoesNotExist

            with transaction.atomic():
                if (
                    reformer_certification.proof_document
                ):  # 증명 서류가 존재한다면, 삭제
                    s3 = client("s3")
                    s3.delete_object(
                        Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                        Key=reformer_certification.proof_document.name,
                    )

                reformer_certification.delete()
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
        except ReformerCertification.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 자격증 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
