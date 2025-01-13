from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import view_exception_handler
from users.models.reformer import Reformer, ReformerEducation
from users.serializers.reformer_serializer.reformer_profile_serializer import (
    ReformerEducationSerializer,
)


class ReformerEducationCreateListView(APIView):
    permission_classes = [IsAuthenticated]

    @view_exception_handler
    def get(self, request):
        reformer = (
            Reformer.objects.select_related("user").filter(user=request.user).first()
        )
        if not reformer:
            raise ObjectDoesNotExist("Cannot found reformer with this user")

        reformer_education = ReformerEducation.objects.filter(reformer=reformer)
        if not reformer_education.exists():
            raise ObjectDoesNotExist("No education data found for the reformer.")

        serializer = ReformerEducationSerializer(instance=reformer_education, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @view_exception_handler
    def post(self, request):
        reformer = (
            Reformer.objects.select_related("user").filter(user=request.user).first()
        )
        if not reformer:
            raise ObjectDoesNotExist("Cannot found reformer with this user")

        serializer = ReformerEducationSerializer(
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
