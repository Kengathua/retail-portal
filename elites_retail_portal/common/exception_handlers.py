from __future__ import unicode_literals

import logging
import six
import sys

from django.core import exceptions
from django.db.models import ProtectedError
from rest_framework.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status


LOGGER = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Django Restframework fails silently to the errors it doesn't handle.
    This handler will bubble up errors that are not handled by DRF.
    Users of this handler will have to catch the error themselves..
    ..NOTE : ValidationErrors esp django model errors are context specific
    hence handling them here will provide a generic message that won't
    be helpful for that context..therefore they are better handled by the
    users themselves.
    """

    # log the exception so that sentry picks it up
    # to receive/process these logs in django requires that
    # `sil_custom_exception_handler` be added to django logging i.e
    # `settings.LOGGING['loggers']`
    LOGGER.error(
        "Internal API Error: {}".format(exc),
        extra={'exception': exc, 'context': context},
        exc_info=True)

    if isinstance(exc, exceptions.ValidationError):
        try:
            # handles field errors
            data = exc.message_dict
        except AttributeError:
            # handle non_field errors
            data = {'detail': exc.messages}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    elif isinstance(exc, exceptions.ObjectDoesNotExist):
        data = {'detail': str(exc)}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    elif isinstance(exc, ProtectedError):
        view = context['view']
        # this exception is raised off an instance; therefore the assumption
        # that an instance will be found is a safe bet
        instance = view.get_object()
        msg = (
            "You cannot delete {} because you have other "
            "records using it.".format(str(instance)))
        data = {"detail": msg}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    elif isinstance(exc, ValidationError):
        msg = "Internal Server Error. Kindly Contact Admin"
        error = exc.__dict__['detail']
        field = list(error.keys())[0]
        field_name = field.replace('_', ' ').title()
        error_message = str(error[field][0])
        if error_message == "This field must be unique.":
            msg = 'The {} field must be unique. Kindly select another {}'.format(
                field_name, field_name.lower())

        data = {"detail": msg}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    response = exception_handler(exc, context)
    if not response:
        six.reraise(*sys.exc_info())
    return response
