from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from users.models.reformer import ReformerEducation


class ReformerEducationDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pass

    def post(self, request, **kwargs):
        try:
            education_uuid = kwargs.get('education_uuid')
            reformer_education = ReformerEducation.objects.filter(education_uuid=education_uuid).first()
            if not reformer_education:
                raise ReformerEducation.DoesNotExist
            document_file = request.FILES.get("document")
            if not document_file:
                raise ValidationError("Document is required")

            reformer_education.proof_document = document_file
            reformer_education.save()

            return Response(
                data={
                    "message": "Successfully uploaded document"
                },
                status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(
                data={'message': '데이터베이스 무결성 오류'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ReformerEducation.DoesNotExist:
            return Response(
                data={"message": "해당 UUID에 해당하는 리포머 학력 정보가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )