import os

from boto3 import client
from botocore import errorfactory
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import ReformerCareer
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerCareerSerializer,
)


class ReformerCareerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        try:
            career_uuid = self.kwargs.get("career_uuid")
            reformer_career = ReformerCareer.objects.filter(
                career_uuid=career_uuid
            ).first()
            if not reformer_career:
                raise ReformerCareer.DoesNotExist

            serializer = ReformerCareerSerializer(instance=reformer_career)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ReformerCareer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 경력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, **kwargs):
        try:
            career_uuid = kwargs.get("career_uuid")
            reformer_career = ReformerCareer.objects.filter(
                career_uuid=career_uuid
            ).first()
            if not reformer_career:
                raise ReformerCareer.DoesNotExist

            serializer = ReformerCareerSerializer(
                instance=reformer_career, data=request.data, partial=True
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
        except ReformerCareer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 경력 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"message": f"예상치 못한 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, **kwargs):
        try:
            career_uuid = kwargs.get("career_uuid")
            reformer_career = ReformerCareer.objects.filter(
                career_uuid=career_uuid
            ).first()
            if not reformer_career:
                raise ReformerCareer.DoesNotExist

            with transaction.atomic():
                if reformer_career.proof_document:  # 증명 서류가 존재한다면, 삭제
                    s3 = client("s3")
                    s3.delete_object(
                        Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                        Key=reformer_career.proof_document.name,
                    )

                reformer_career.delete()
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
        except ReformerCareer.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 경력 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
