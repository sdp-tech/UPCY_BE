from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models.reformer import ReformerEducation, ReformerCertification


class ReformerCertificationDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            certification_uuid = kwargs.get("education_uuid")
            reformer_certification = ReformerCertification.objects.filter(
                certification_uuid=certification_uuid
            ).first()
            if not reformer_certification:
                raise ReformerCertification.DoesNotExist
            document_file = request.FILES.get("document")
            if not document_file:
                raise ValidationError("Document is required")

            reformer_certification.proof_document = document_file
            reformer_certification.save()

            return Response(
                data={"message": "Successfully uploaded document"},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                data={"message": "데이터베이스 무결성 오류"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ReformerCertification.DoesNotExist:
            return Response(
                data={
                    "message": "해당 UUID에 해당하는 리포머 자격증 내역 정보가 존재하지 않습니다."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
