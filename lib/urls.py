import lib.utils as utils


def token():
    return 'https://api.zoom.us/oauth/token'

def oauth_redirect(port):
    return f'http://localhost:{port}'

def ouath_user_consent(client_id, port):
    return f'https://zoom.us/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={oauth_redirect(port)}'

def active_users():
    return 'https://api.zoom.us/v2/users?status=active'

def inactive_users():
    return 'https://api.zoom.us/v2/users?status=inactive'

def user_recordings(user_id, start_date, end_date):
    return f'https://api.zoom.us/v2/users/{user_id}/recordings?from={_date_to_str(start_date)}&to={_date_to_str(end_date)}'

def meeting_recordings(meeting_uuid):
    return f'https://api.zoom.us/v2/meetings/{utils.double_encode(meeting_uuid)}/recordings'

def test():
    return 'https://api.zoom.us/v2/users/me/recordings'

def _date_to_str(date):
	return date.strftime('%Y-%m-%d')