from sqlite3 import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import ReformerProfile
from users.selectors import ReformerSelector
from users.serializers.reformer_profile_serializer import ReformerProfileSerializer
from users.services import UserService


class ReformerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    selector = ReformerSelector()
    user_service = UserService()

    def get(self, request):
        user = request.user
        try:
            reformer_profile = self.selector.get_reformer_profile_by_user(user)
            self.user_service.update_user_role(user=user, role="reformer") # Reformer 프로필 등록 -> user role 변경 필요
            serializer = ReformerProfileSerializer(instance=reformer_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReformerProfile.DoesNotExist:
            return Response(
                data={
                    "message": "Cannot find reformer profile that belongs to the user"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={
                    "message": f"{str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        user = request.user
        try:
            # 1. ReformerProfile 객체 생성
            reformer_profile = ReformerProfile(user=user)
            reformer_profile.save()

            # 2. 요청 데이터 파싱해서 시리얼라이저로 넘겨줌 (검증 및 create 메소드 사용하기 위함)
            data = self.parse_querydict(request.data)
            serializer = ReformerProfileSerializer(
                instance=reformer_profile,
                data=data,
                context={'request': request}
            )

            if serializer.is_valid(): # 3. 검증이 성공적이라면, save() 호출해서 Serializer의 create()메소드 호출
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                     data={
                         'details': serializer.errors
                     },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except IntegrityError as e:
            return Response({'error': '데이터베이스 무결성 오류', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': '예기치 못한 오류 발생', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def parse_querydict(self, querydict):
        data = {}
        for key, value in querydict.lists():
            if '[' in key and ']' in key:
                base_key, index, sub_key = self.split_key(key)
                if base_key not in data:
                    data[base_key] = []
                while len(data[base_key]) <= index:
                    data[base_key].append({})
                data[base_key][index][sub_key] = value[0] if len(value) == 1 else value
            else:
                data[key] = value[0] if len(value) == 1 else value
        return data

    def split_key(self, key):
        base_key, sub = key.split('[', 1)
        index, sub_key = sub.split(']', 1)
        index = int(index)
        sub_key = sub_key.strip('[]')
        return base_key, index, sub_key
