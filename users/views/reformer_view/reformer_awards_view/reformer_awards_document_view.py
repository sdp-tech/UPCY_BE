from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import ReformerAwards


class ReformerAwardsDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pass

    def post(self, request, **kwargs):
        try:
            award_uuid = kwargs.get("award_uuid")
            reformer_awards = ReformerAwards.objects.filter(
                award_uuid=award_uuid
            ).first()
            if not reformer_awards:
                raise ReformerAwards.DoesNotExist
            document_file = request.FILES.get("document")
            if not document_file:
                raise ValidationError("Document is required")

            reformer_awards.proof_document = document_file
            reformer_awards.save()

            return Response(
                data={"message": "Successfully uploaded document"},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                data={"message": "데이터베이스 무결성 오류"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ReformerAwards.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 수상 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
