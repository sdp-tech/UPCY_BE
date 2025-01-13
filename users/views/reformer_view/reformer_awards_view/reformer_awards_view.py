import os

from boto3 import client
from botocore import errorfactory
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import ReformerAwards
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerAwardsSerializer,
)


class ReformerAwardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        try:
            award_uuid = self.kwargs.get("award_uuid")
            reformer_awards = ReformerAwards.objects.filter(
                award_uuid=award_uuid
            ).first()
            if not reformer_awards:
                raise ReformerAwards.DoesNotExist

            serializer = ReformerAwardsSerializer(instance=reformer_awards)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ReformerAwards.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 수상 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, **kwargs):
        try:
            award_uuid = kwargs.get("award_uuid")
            reformer_awards = ReformerAwards.objects.filter(
                award_uuid=award_uuid
            ).first()
            if not reformer_awards:
                raise ReformerAwards.DoesNotExist

            serializer = ReformerAwardsSerializer(
                instance=reformer_awards, data=request.data, partial=True
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
        except ReformerAwards.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 수상 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, **kwargs):
        try:
            award_uuid = kwargs.get("award_uuid")
            reformer_awards = ReformerAwards.objects.filter(
                award_uuid=award_uuid
            ).first()
            if not reformer_awards:
                raise ReformerAwards.DoesNotExist

            with transaction.atomic():
                s3 = client("s3")
                s3_key = reformer_awards.proof_document.name
                if s3_key:  # 키가 비어있지 않을 때만 삭제 시도
                    s3.delete_object(
                        Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                        Key=s3_key,
                    )
                else:
                    print("Warning: S3 Key가 비어 있어 삭제를 건너뜁니다.")

                reformer_awards.delete()
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
        except ReformerAwards.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 수상 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
