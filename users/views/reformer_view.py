from sqlite3 import IntegrityError
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import ReformerProfile
from users.serializers.reformer_profile_serializer import ReformerProfileSerializer


class ReformerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            with transaction.atomic():
                # 중복 생성 방지: 이미 프로필이 있는지 확인
                reformer_profile = ReformerProfile.objects.select_for_update().filter(user=user).first()
                if not reformer_profile:
                    # 새로운 프로필 생성
                    reformer_profile = ReformerProfile(user=user)
                    reformer_profile.save()

                # 요청 데이터 파싱 및 시리얼라이저 적용
                data = self.parse_querydict(request.data)
                serializer = ReformerProfileSerializer(instance=reformer_profile, data=data,
                                                       context={'request': request})

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # 유효성 검사 오류 메시지 확인
                    return Response({'error': '유효성 검사 실패', 'details': serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            return Response({'error': '데이터베이스 무결성 오류', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': '예기치 못한 오류 발생', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def parse_querydict(self, querydict):
        """ Convert QueryDict to a nested dict suitable for serializers """
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
        """ Split a key like 'education[0][school]' into its components """
        base_key, sub = key.split('[', 1)
        index, sub_key = sub.split(']', 1)
        index = int(index)
        sub_key = sub_key.strip('[]')
        return base_key, index, sub_key