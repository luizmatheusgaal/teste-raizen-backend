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
    'unable_to_login': 'E-mail ou senha incorretos.',
}


def friendly_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        response.data = {'msg': MESSAGE_OVERRIDES['authentication_failed']}
        return response

    if isinstance(exc, PermissionDenied):
        response.data = {'msg': MESSAGE_OVERRIDES['permission_denied']}
        return response

    if isinstance(exc, ValidationError):
        response.data = {'msg': _flatten_validation_errors(response.data)}
        return response

    detail = response.data.get('detail') if isinstance(response.data, dict) else None
    if isinstance(detail, list):
        detail = detail[0]
    if isinstance(detail, str):
        response.data = {'msg': _translate_detail(detail)}
        return response

    if isinstance(response.data, dict):
        response.data = {'msg': _flatten_validation_errors(response.data)}

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


def _flatten_validation_errors(data, prefix=''):
    messages = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                messages.append(_flatten_validation_errors(value, f'{prefix}{key}: '))
            elif isinstance(value, str):
                messages.append(f'{prefix}{_translate_validation_message(value)}')
    elif isinstance(data, list):
        for item in data:
            messages.append(_flatten_validation_errors(item, prefix))
    elif isinstance(data, str):
        messages.append(f'{prefix}{_translate_validation_message(data)}')

    cleaned = [m for m in messages if m]
    return ' '.join(cleaned) if cleaned else 'Ocorreu um erro de validação.'


def _translate_validation_message(message):
    lower = message.lower()
    if 'already exists' in lower or 'já existe' in lower:
        return 'Já existe um registro com este valor.'
    if 'this field' in lower and 'required' in lower:
        return 'Este campo é obrigatório.'
    if 'enter a valid email' in lower:
        return 'Informe um e-mail válido.'
    return message
