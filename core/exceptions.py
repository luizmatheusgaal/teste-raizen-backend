from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)


MESSAGE_OVERRIDES = {
    'authentication_failed': 'Você precisa fazer login para acessar este recurso.',
    'not_authenticated': 'Você precisa fazer login para acessar este recurso.',
    'permission_denied': 'Você não tem permissão para realizar esta ação.',
    'invalid': 'Sua sessão é inválida. Faça login novamente.',
    'no_active_account': 'E-mail ou senha incorretos.',
    'unable_to_login': 'E-mail ou senha incorretos.',
}


def friendly_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        response.data = {'detail': MESSAGE_OVERRIDES['authentication_failed']}
        return response

    if isinstance(exc, PermissionDenied):
        response.data = {'detail': MESSAGE_OVERRIDES['permission_denied']}
        return response

    if isinstance(exc, ValidationError):
        response.data = _translate_validation_errors(response.data)

    if 'detail' in response.data:
        detail = response.data['detail']
        if isinstance(detail, list):
            detail = detail[0]
        if isinstance(detail, str):
            response.data['detail'] = _translate_detail(detail)

    return response


def _translate_detail(detail):
    lower = detail.lower()
    if 'authentication credentials were not provided' in lower:
        return MESSAGE_OVERRIDES['not_authenticated']
    if 'invalid token' in lower:
        return MESSAGE_OVERRIDES['invalid']
    if 'impossível fazer login' in lower or 'unable to log in' in lower:
        return MESSAGE_OVERRIDES['unable_to_login']
    if 'not found' in lower or 'não encontrado' in lower:
        return 'Recurso não encontrado.'
    return detail


def _translate_validation_errors(data):
    if isinstance(data, dict):
        translated = {}
        for key, value in data.items():
            translated[key] = _translate_validation_errors(value)
        return translated
    if isinstance(data, list):
        return [_translate_validation_errors(item) for item in data]
    if isinstance(data, str):
        lower = data.lower()
        if 'already exists' in lower or 'já existe' in lower:
            return 'Já existe um registro com este valor.'
        if 'this field' in lower:
            return 'Este campo é obrigatório.'
        if 'enter a valid email' in lower:
            return 'Informe um e-mail válido.'
        return data
    return data
