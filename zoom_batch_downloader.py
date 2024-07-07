import argparse
import datetime
import math
import os
import traceback
from calendar import monthrange
from types import ModuleType

import colorama
from colorama import Fore, Style

import lib.urls as urls
import lib.utils as utils
from lib.zoom_client import zoom_client

colorama.init()

def get_parser():
	parser = argparse.ArgumentParser(description="Zoom Batch Downloader - See the README.")
	parser.add_argument(
		'--config', '-c', nargs='+',
		help='List of configuration files. Later configuration files override earlier ones on a value by value basis.'
	)
	return parser

def setup_config():
	args = get_parser().parse_args()
	configs = args.config

	if configs is not None and len(configs) > 0:
		try:
			utils.merge_modules(configs, 'config')
		except Exception as error:
			if utils.is_debug():
				raise
			utils.print_bright_red(f'Error: {error}')
			exit(1)


def create_zoom_client():
	return zoom_client(
		credentials=CONFIG.CREDENTIALS,
		refresh_tokens_path=CONFIG.REFRESH_TOKENS_PATH,
		use_oauth_server=CONFIG.REFRESH_TOKENS_PATH,
		oauth_port=CONFIG.OAUTH_PORT,
		oauth_timeout=CONFIG.USER_INPUT_TIMEOUT,
		verbose_output=CONFIG.VERBOSE_OUTPUT
	)

if __name__ == '__main__':
	setup_config()
	try:
		import config as CONFIG
	except ImportError:
		utils.print_bright_red(
			f'Missing config file, copy config_template.py to config.py and change as needed.\n'
			f'Alternatively, you can provide custom config file(s) as an argument'
		)
		exit(1)

	client = create_zoom_client()

def main():
	CONFIG.OUTPUT_PATH = utils.prepend_path_on_windows(CONFIG.OUTPUT_PATH)

	utils.print_bright(f'Using {client.credentials_description()}.')
	print_filter_warnings()

	from_date, to_date = evaluate_dates()
	file_count, total_size, skipped_count = download_recordings(get_users(), from_date, to_date)

	total_size_str = utils.size_to_string(total_size)

	print(
		f'{Style.BRIGHT}Downloaded {Fore.GREEN}{file_count}{Fore.RESET} files.',
		f'Total size: {Fore.GREEN}{total_size_str}{Fore.RESET}.{Style.RESET_ALL}',
		f'Skipped: {skipped_count} files.'
	)

def print_filter_warnings():
	did_print = False

	if CONFIG.TOPICS:
		utils.print_bright(f'Topics filter is active {CONFIG.TOPICS}')
		did_print = True
	if CONFIG.USERS:
		utils.print_bright(f'Users filter is active {CONFIG.USERS}')
		did_print = True
	if CONFIG.RECORDING_FILE_TYPES:
		utils.print_bright(f'Recording file types filter is active {CONFIG.RECORDING_FILE_TYPES}')
		did_print = True
		
	if did_print:
		print()

def evaluate_dates():
	from_date = datetime.datetime(CONFIG.START_YEAR or 2012, CONFIG.START_MONTH or 1, CONFIG.START_DAY or 1)

	now = datetime.datetime.now()

	if (CONFIG.END_YEAR, CONFIG.END_MONTH, CONFIG.END_DAY) == (None, None, None):
		end_year, end_month, end_day = now.year, now.month, now.day
	else:
		end_year = CONFIG.END_YEAR or now.year
		end_month = CONFIG.END_MONTH or 12
		end_day = CONFIG.END_DAY or monthrange(end_year, end_month)[1]

	to_date = datetime.datetime(end_year, end_month, end_day)

	return from_date, to_date

def get_users():
	if CONFIG.USERS:
		return [(email, '') for email in CONFIG.USERS]

	utils.print_bright('Scanning for users:')
	
	users = []
	pages = utils.chain(client.paginate(urls.active_users()), client.paginate(urls.inactive_users()))
	for page in utils.percentage_tqdm(pages):
			users.extend([(user['email'], get_user_name(user)) for user in page['users']]),

	print()
	return users

def get_user_name(user_data):
	first_name = user_data.get("first_name")
	last_name = user_data.get("last_name")

	if first_name and last_name:
		return f'{first_name} {last_name}'
	else:
		return first_name or last_name
	
def download_recordings(users, from_date, to_date):
	file_count, total_size, skipped_count = 0, 0, 0

	for user_email, user_name in users:
		user_description = get_user_description(user_email, user_name)

		utils.print_bright(
			f'Downloading recordings from user {user_description} - Starting at {date_to_str(from_date)} '
			f'and up to {date_to_str(to_date)} (inclusive).'
		)
	
		meetings = get_meetings(get_meeting_uuids(user_email, from_date, to_date))
		user_file_count, user_total_size, user_skipped_count = download_recordings_from_meetings(meetings, user_email)

		utils.print_bright('######################################################################')
		print()
		
		file_count += user_file_count
		total_size += user_total_size
		skipped_count += user_skipped_count
	
	return (file_count, total_size, skipped_count)

def get_user_description(user_email, user_name):
	return f'{user_email} ({user_name})' if (user_name) else user_email
	
def date_to_str(date):
	return date.strftime('%d/%m/%Y')

def get_meeting_uuids(user_email, start_date, end_date):
	meeting_uuids = []

	local_start_date = start_date
	delta = datetime.timedelta(days=29)
	
	utils.print_bright('Scanning for recorded meetings:')
	estimated_iterations = math.ceil((end_date-start_date) / datetime.timedelta(days=30))
	with utils.percentage_tqdm(total=estimated_iterations) as progress_bar:
		while local_start_date <= end_date:
			local_end_date = min(local_start_date + delta, end_date)

			ids = []
			for page in client.paginate(urls.user_recordings(user_email, local_start_date, local_end_date)):
				ids.extend([meeting['uuid'] for meeting in page['meetings']])

			meeting_uuids.extend(reversed(ids))
			local_start_date = local_end_date + datetime.timedelta(days=1)
			progress_bar.update(1)

	return meeting_uuids

def get_meetings(meeting_uuids):
	meetings = []

	if meeting_uuids:
		utils.print_bright(f'Scanning for recordings:')
		for meeting_uuid in utils.percentage_tqdm(meeting_uuids):
			meetings.append(client.get(urls.meeting_recordings(meeting_uuid)))

	return meetings

def download_recordings_from_meetings(meetings, user_email):
	file_count, total_size, skipped_count = 0, 0, 0

	for meeting in meetings:
		if CONFIG.TOPICS and meeting['topic'] not in CONFIG.TOPICS and utils.slugify(meeting['topic']) not in CONFIG.TOPICS:
			continue
		
		recording_files = meeting.get('recording_files') or []
		participant_audio_files = (meeting.get('participant_audio_files') or []) if CONFIG.INCLUDE_PARTICIPANT_AUDIO else []

		for recording_file in recording_files + participant_audio_files:
			if 'file_size' not in recording_file:
				continue

			if CONFIG.RECORDING_FILE_TYPES and recording_file['file_type'] not in CONFIG.RECORDING_FILE_TYPES:
				continue

			url = recording_file['download_url']
			topic = utils.slugify(meeting['topic'])
			ext = recording_file.get('file_extension') or os.path.splitext(recording_file['file_name'])[1]
			recording_name = utils.slugify(f'{topic}__{recording_file["recording_start"]}')
			file_id = recording_file['id']
			file_name_suffix =  os.path.splitext(recording_file['file_name'])[0] + '__' if 'file_name' in recording_file else ''
			recording_type_suffix =  recording_file['recording_type'] + '__' if 'recording_type' in recording_file else ''
			file_name = utils.slugify(
				f'{recording_name}__{recording_type_suffix}{file_name_suffix}{file_id[-8:]}'
			) + '.' + ext
			file_size = int(recording_file['file_size'])

			if download_recording_file(url, user_email, file_name, file_size, topic, recording_name):
				total_size += file_size
				file_count += 1
			else:
				skipped_count += 1
	
	return file_count, total_size, skipped_count

def download_recording_file(download_url, user_email, file_name, file_size, topic, recording_name):
	if CONFIG.VERBOSE_OUTPUT:
		print()
		utils.print_dim(f'URL: {download_url}')

	file_path = create_path(user_email, file_name, topic, recording_name)

	if os.path.exists(file_path) and abs(os.path.getsize(file_path) - file_size) <= CONFIG.FILE_SIZE_MISMATCH_TOLERANCE:
		utils.print_dim(f'Skipping existing file: {file_name}')
		return False
	elif os.path.exists(file_path):
		utils.print_dim_red(f'Deleting corrupt file: {file_name}')
		os.remove(file_path)

	utils.print_bright(f'Downloading: {file_name}')
	utils.wait_for_disk_space(
		file_size, CONFIG.OUTPUT_PATH, CONFIG.MINIMUM_FREE_DISK, poll_interval=5, timeout=CONFIG.USER_INPUT_TIMEOUT
	)

	tmp_file_path = file_path + '.tmp'
	client.do_with_token(
		lambda t: utils.download_with_progress(
			f'{download_url}?access_token={t}', tmp_file_path, file_size, CONFIG.VERBOSE_OUTPUT,
			CONFIG.FILE_SIZE_MISMATCH_TOLERANCE
		)
	)
	
	os.rename(tmp_file_path, file_path)

	return True

def create_path(user_email, file_name, topic, recording_name):
	folder_path = CONFIG.OUTPUT_PATH

	values = {
		'USER': user_email,
		'TOPIC': topic,
		'RECORDING': recording_name
	}

	for property in CONFIG.GROUP_BY:
		if property in values:
			folder_path = os.path.join(folder_path, values[property])

	os.makedirs(folder_path, exist_ok=True)
	return os.path.join(folder_path, file_name)

if __name__ == '__main__':
	try:
		main()
	except AttributeError as error:
		if isinstance(error.obj, ModuleType) and error.obj.__name__ == 'config':
			print()
			utils.print_bright_red(
				f'Variable {error.name} is not defined in config.py. '
				f'See config_template.py for the complete list of variables.'
			)
		else:
			raise

	except Exception as error:
		print()
		if not getattr(CONFIG, "VERBOSE_OUTPUT"):
			utils.print_bright_red(f'Error: {error}')
		elif utils.is_debug():
			raise
		else:
			utils.print_dim_red(traceback.format_exc())

	except KeyboardInterrupt:
		print()
		utils.print_bright_red('Interrupted by the user')
		exit(1)