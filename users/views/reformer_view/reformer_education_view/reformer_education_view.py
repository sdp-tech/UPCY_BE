import os

from boto3 import client
from botocore import errorfactory
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import ReformerEducation
from users.serializers.reformer_serializer.reformer_profile_serializer import \
    ReformerEducationSerializer


class ReformerEducationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        try:
            education_uuid = kwargs.get("education_uuid")
            reformer_education = ReformerEducation.objects.filter(
                education_uuid=education_uuid
            ).first()
            if not reformer_education:
                raise ReformerEducation.DoesNotExist

            serializer = ReformerEducationSerializer(instance=reformer_education)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ReformerEducation.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 학력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, **kwargs):
        try:
            education_uuid = kwargs.get("education_uuid")
            reformer_education = ReformerEducation.objects.filter(
                education_uuid=education_uuid
            ).first()
            if not reformer_education:
                raise ReformerEducation.DoesNotExist

            serializer = ReformerEducationSerializer(
                instance=reformer_education, data=request.data, partial=True
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
        except ReformerEducation.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 학력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, **kwargs):
        try:
            education_uuid = kwargs.get("education_uuid")
            reformer_education = ReformerEducation.objects.filter(
                education_uuid=education_uuid
            ).first()
            if not reformer_education:
                raise ReformerEducation.DoesNotExist

            with transaction.atomic():
                s3 = client("s3")
                s3.delete_object(
                    Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                    Key=reformer_education.proof_document.name,
                )
                reformer_education.delete()
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
        except ReformerEducation.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 학력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
