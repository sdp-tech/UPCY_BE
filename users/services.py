import os
import string
import random
import datetime

import io
import time
import uuid

from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.utils.encoding import force_str, force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.template.loader import render_to_string

from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_jwt.settings import api_settings
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from users.models import User
# from core.exceptions import ApplicationError


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class UserService:
    def __init__(self):
        pass

    def reformer_sign_up(
            email: str, 
            password: str, 
            nickname:str, 
            phone:str, 
            profile_image: InMemoryUploadedFile,
            agreement_terms:bool,
            school:str,
            is_enrolled:str,
            area:str,
            career:str,
            work_style:list[str],
            bios:str,
            certificate_studentship: InMemoryUploadedFile,
            ):

        # ext = certificate_studentship.name.split(".")[-1]
        # file_path = '{}.{}'.format(str(time.time())+str(uuid.uuid4().hex), ext)
        # certificate_studentship = ImageFile(io.BytesIO(certificate_studentship.read()), name=file_path)

        user = User(
            email = email,
            nickname = nickname,
            password = password,
            phone = phone,
            profile_image = profile_image,
            is_reformer=True,
            agreement_terms=agreement_terms,
            school = school,
            is_enrolled = is_enrolled,
            area = area,
            career = career,
            bios = bios,
            certificate_studentship=certificate_studentship,
        )

        user.set_password(password)
        user.is_active = False
        user.save()

        user.work_style.set(work_style)