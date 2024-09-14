from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers.reformer_profile_serializer import ReformerProfileSerializer
from users.serializers.user_login_serializer import UserLoginSerializer
from users.serializers.user_signup_serializer import UserSignUpSerializer
from users.services import UserService
from users.selectors import ReformerSelector, UserSelector


class UserSignUpApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        requested_data = UserSignUpSerializer(data=request.data)
        if requested_data.is_valid(raise_exception=True):
            data = requested_data.validated_data

            UserService.user_sign_up(
                email=data.get('email'),
                password=data.get('password'),
                agreement_terms=bool(data.get('agreement_terms')),
                address=data.get('address'),
            )
            return Response(
                {
                    'message': 'success',
                },
                status=status.HTTP_201_CREATED
            )


class UserLoginApi(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        requested_data = UserLoginSerializer(data=request.data)
        if requested_data.is_valid(raise_exception=True):
            data = requested_data.validated_data
            service = UserService()
            try:
                login_data = service.login(
                    email=data.get('email'),
                    password=data.get('password'),
                )
                return Response(
                    data=login_data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'status': 'fail', 'message': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'status': 'fail', 'message': 'Invalid input data'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLogoutApi(APIView):
    """
    로그아웃 처리 Class
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        service = UserService()
        service.logout(user=request.user)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class UserProfileImageApi(APIView):
    permission_classes = (IsAuthenticated,)

    class UserProfileInputSerializer(serializers.Serializer):
        img = serializers.ImageField()

    class UserProfileOutputSerializer(serializers.Serializer):
        email = serializers.CharField()
        nickname = serializers.CharField()
        img = serializers.URLField()

    def post(self, request):
        serializers = self.UserProfileInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data

        service = UserService()
        profile_data = service.user_profile_image_register(
            user=request.user,
            img=data.get('img')
        )
        output_serializer = self.UserProfileOutputSerializer(data=profile_data)
        output_serializer.is_valid(raise_exception=True)
        try:
            # data=service.user_profile_image_register(
            #     user=request.user,
            #     img=data.get('img'),
            # )
            return Response({'status': 'succes',
                             'data': output_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Failed to upload img to s3:{e}")
            return None

class ReformerProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ReformerProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
