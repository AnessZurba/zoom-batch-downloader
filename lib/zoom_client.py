from urllib.parse import parse_qs, urlparse

import requests

import lib.oauth_server as oauth_server
import lib.urls as urls
import lib.utils as utils


class zoom_client:
	def __init__(self, credentials, refresh_tokens_path, use_oauth_server, oauth_port, oauth_timeout, verbose_output, PAGE_SIZE: int = 300):
		if type(credentials).__name__ == "server_to_server":
			self.account_id = credentials.ACCOUNT_ID
			self.client_id = credentials.CLIENT_ID
			self.client_secret = credentials.CLIENT_SECRET
			self.is_oauth = False
		elif type(credentials).__name__ == "oauth":
			self.client_id = credentials.CLIENT_ID
			self.client_secret = credentials.CLIENT_SECRET
			self.auth_identifier = credentials.auth_identifier
			self.is_oauth = True

		self.refresh_tokens = utils.persistent_dict(refresh_tokens_path)

		self.use_oauth_server = use_oauth_server
		self.oauth_port = oauth_port
		self.oauth_timeout = oauth_timeout
		self.verbose_output = verbose_output
		self.PAGE_SIZE = PAGE_SIZE
		self.cached_token = None

	def credentials_description(self):
		if self.is_oauth and self.use_oauth_server:
			return f'OAuth Credentials with OAuth server for automatic authentication. Authentication identifier: {self.auth_identifier}'
		elif self.is_oauth and not self.use_oauth_server:
			return f'OAuth Credentials with manual authentication. Authentication identifier: {self.auth_identifier}'
		else:
			return 'Server to Server Credentials'
	
	def get(self, url):
		return self._get_with_token(lambda t: requests.get(url=url, headers=self._get_headers(t))).json()

	def _get_with_token(self, get):
		if self.cached_token:
			response = get(self.cached_token)
		
		if not self.cached_token or response.status_code == 401:
			self.cached_token = self._fetch_token()
			response = get(self.cached_token)

		if not response.ok:
			raise Exception(f'{response.status_code} {response.text}')
		
		return response

	def prefetch_token(self):
		self._fetch_token()

	def _fetch_token(self):
		used_refresh_token = False
		if self.is_oauth:
			refresh_token = self.refresh_tokens.load(self.auth_identifier)
			if refresh_token is not None:
				used_refresh_token = True
				data = {
					'grant_type': 'refresh_token',
					'refresh_token' : refresh_token
				}
			else:
				authorization_code = _get_auth_code(
					self.auth_identifier, self.client_id, self.use_oauth_server, self.oauth_port, self.oauth_timeout
				)
				data = {
					'grant_type': 'authorization_code',
					'code' : authorization_code,
					'redirect_uri': urls.oauth_redirect(self.oauth_port)
				}
		else:
			data = {
				'grant_type': 'account_credentials',
				'account_id': self.account_id
			}
		response = requests.post(
			urls.token(), auth=(self.client_id, self.client_secret), data=data
		).json()

		if self.verbose_output:
			utils.print_dim(f'Fetching access token with grant_type: {data["grant_type"]}.')

		if 'access_token' not in response:
			if used_refresh_token:
				self.refresh_tokens.store(self.auth_identifier, None)
				return self._fetch_token()
			raise Exception(f'Unable to fetch access token: {response["reason"]} - verify your credentials.')

		if 'refresh_token' in response and self.is_oauth:
			self.refresh_tokens.store(self.auth_identifier, response['refresh_token'])
		
		if self.verbose_output and 'scope' in response:
			utils.print_dim(f'Got token with scope: {response["scope"]}.')
			utils.print_dim('')
			
		return response['access_token']  
	
	def _get_headers(self, token):
		return {
			'Authorization': f'Bearer {token}',
			'Content-Type': 'application/json'
		}

	def paginate(self, url):
		class __paginate_iter:
			def __init__(self, client, url):
				self.url = utils.add_url_params(url, {'page_size': client.PAGE_SIZE})
				self.client = client
				self.page = client.get(self.url)
				self.page_count = self.page['page_count'] or 1
			
			def __iter__(self): return self

			def __len__(self): return self.page_count

			def __next__(self):
				page = self.page
				if not page and self.page_token:
					page = self.client.get(utils.add_url_params(self.url, {'next_page_token': self.page_token}))

				if not page:
					raise StopIteration()

				self.page, self.page_token = None, page['next_page_token']
				return page
			
		return __paginate_iter(self, url)
	
	def do_with_token(self, do):
		def do_as_get(token):
			test_response = requests.get(urls.test(), headers=self._get_headers(token))
			if test_response.ok:
				try:
					do(token)
				except:
					test_response = requests.get(urls.test(), headers=self._get_headers(token))
					if test_response.ok:
						raise

			return test_response
			
		self._get_with_token(lambda t: do_as_get(t))

def _get_auth_code(auth_identifier, client_id, use_oauth_server, port, timeout):
	utils.print_bright_blue('')
	utils.print_bright_blue('---------------------------------------------')
	utils.print_bright_blue(f'Refresh Token for {auth_identifier} is missing or expired.')
	if use_oauth_server:
		utils.print_bright_blue('Please authenticate by clicking "Allow" in this link:')
		utils.print_bright_blue(urls.ouath_user_consent(client_id, port))
		auth_code = oauth_server.get_auth_code(port, timeout)
	else:
		utils.print_bright_blue(f'Manual authentication is enabled.')
		utils.print_bright_blue(f'Please authenticate by clicking "Allow" in the link below, then provide the URL you get directed to.')
		utils.print_bright_blue(urls.ouath_user_consent(client_id, port))
		
		auth_code = None
		while auth_code is None:
			utils.print_bright('REDIRECT URL: ', end='')
			url = input('')
			auth_code = parse_qs(urlparse(url).query).get('code')
			if auth_code is None:
				utils.print_dim_red('Invalid URL. Please try again.')

	utils.print_bright_blue('Authorization code received!')
	utils.print_bright_blue('---------------------------------------------')
	utils.print_bright_blue('')

	return auth_code