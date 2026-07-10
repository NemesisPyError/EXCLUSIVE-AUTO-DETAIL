import logging
from flask import request, has_request_context

logger = logging.getLogger(__name__)


def _remote():
    if has_request_context():
        return request.remote_addr or 'unknown'
    return 'system'


def log_login_success(user_email):
    logger.info(f'AUTH LOGIN OK | user={user_email} | ip={_remote()}')


def log_login_failed(user_email):
    logger.warning(f'AUTH LOGIN FAIL | user={user_email} | ip={_remote()}')


def log_login_locked(user_email):
    logger.warning(f'AUTH LOCKED | user={user_email} | ip={_remote()}')


def log_logout(user_email):
    logger.info(f'AUTH LOGOUT | user={user_email} | ip={_remote()}')


def log_admin_action(user_email, action, detail=''):
    logger.info(f'ADMIN ACTION | user={user_email} | action={action} | detail={detail} | ip={_remote()}')


def log_error(endpoint, error_msg):
    logger.error(f'ERROR | endpoint={endpoint} | error={error_msg} | ip={_remote()}')


def log_reset_token_sent(user_email):
    logger.info(f'AUTH RESET TOKEN | user={user_email} | ip={_remote()}')


def log_password_reset(user_email):
    logger.info(f'AUTH PASSWORD RESET | user={user_email} | ip={_remote()}')


def log_session_invalidated(user_email, reason):
    logger.info(f'SESSION INVALIDATED | user={user_email} | reason={reason} | ip={_remote()}')
