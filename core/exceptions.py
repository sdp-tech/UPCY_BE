from functools import wraps

from botocore.exceptions import ParamValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db import IntegrityError


def view_exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return Response(
                data={"error": "ValueError", "error_message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError as e:
            return Response(
                data={"error": "IntegrityError", "error_message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ValidationError as e:
            return Response(
                data={
                    "error": "Validation Error",
                    "error_message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist as e:
            return Response(
                data={
                    "error": "Object Does Not Exist",
                    "error_message": str(e),
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except ParamValidationError as e:
            return Response(
                data={
                    "error": "S3: Parameter Validation Error",
                    "error_message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                data={
                    "error": "Internal Server Error",
                    "error_message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return wrapper
