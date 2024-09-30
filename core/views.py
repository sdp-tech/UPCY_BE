from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


def get_paginated_response(
    *, pagination_class, serializer_class, queryset, request, view
):
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True, context={"request": request})
    else:
        serializer = serializer_class(queryset, many=True, context={"request": request})

    return Response(
        {
            "status": "success",
            "data": paginator.get_paginated_response(serializer.data).data,
        },
        status=status.HTTP_200_OK,
    )


class HealthCheckView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(
            {
                "message": "hello",
            },
            status=status.HTTP_200_OK,
        )
