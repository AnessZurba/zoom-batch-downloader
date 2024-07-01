# This file defines the configuration for zoom_batch_downloader.
# Lines starting with # are comment lines and will be ignored by the script.

# Authentication classes definition. DO NOT DELETE.
from dataclasses import dataclass


@dataclass
class server_to_server: CLIENT_ID: str; CLIENT_SECRET: str; ACCOUNT_ID: str

@dataclass
class oauth: CLIENT_ID: str; CLIENT_SECRET: str; auth_identifier: str

########################################################
#               Zoom API credentials                   #
# Pick one of the following as explained in the README #
########################################################

# Server to server Credentials - Comment it out if you don't want to use it.
CREDENTIALS = server_to_server(
    CLIENT_ID = R"############",
    CLIENT_SECRET = R"###########",
    ACCOUNT_ID = R"############"
)

# OAUTH Credentials - Uncomment to use.
# CREDENTIALS = oauth(
#     CLIENT_ID = R"############",
#     CLIENT_SECRET = R"############",
#     auth_identifier = R"############" # user-defined string. Can be left empty if you don't need multiple user/account support.
# )

########################################################

# Put your own download path here, no need to escape backslashes but avoid ending with one.
OUTPUT_PATH = R"C:\Test\Zoom"

# Date range (inclusive) for downloads, None value for Days gets replaced by first/last day of the month.
START_DAY, START_MONTH, START_YEAR = None, 5, 2020
END_DAY, END_MONTH, END_YEAR = None, 3, 2022

# Put here emails of the users you want to check for recordings. If empty, all users under the account will be checked.
USERS = [
    # R"####@####.####",
    # R"####@####.####",
]

# Put here the topics of the meetings you wish to download recordings for. If empty, no topic filtering will happen.
TOPICS = [
    # R"############",
    # R"############",
]

# Put here the file types you wish to download. If empty, no file type filtering will happen.
RECORDING_FILE_TYPES = [
    # R"MP4",            # Video file of the recording.
    # R"M4A",            # Audio-only file of the recording.
    # R"TIMELINE",       # Timestamp file of the recording in JSON file format.
    # R"TRANSCRIPT",     # Transcription file of the recording in VTT format.
    # R"CHAT",           # A TXT file containing in-meeting chat messages that were sent during the meeting.
    # R"CC",             # File containing closed captions of the recording in VTT file format.
    # R"CSV",            # File containing polling data in CSV format.
    # R"SUMMARY",        # Summary file of the recording in JSON file format.
]

# Determines the folder structure of the downloaded files, the first folder contains the second and so on.
GROUP_BY = [
    "USER",         # Group by owning user
    "TOPIC",        # Group by meeting topic
    "RECORDING",    # Group by Recording (might contain multiple files).
]

# Path to contain the refresh tokens for oauth, this file contains API secrets and shouldn't be shared.
REFRESH_TOKENS_PATH = "refresh_tokens.json"

# If True, participant audio files will be downloaded as well.
# This works when "Record a separate audio file of each participant" is enabled.
INCLUDE_PARTICIPANT_AUDIO = True

# Set to True for more verbose output.
VERBOSE_OUTPUT = False

# If True, OAuth server will be used to streamline the OAuth process.
# If False, the user will have to copy the authentication code manually back to the script.
USE_OAUTH_SERVER = True

# Port to use for OAuth server at http://localhost.
OAUTH_PORT = 8000

# Timeout in seconds to be used when waiting for user input.
USER_INPUT_TIMEOUT = 3600

# Constants used for indicating size in bytes.
B = 1
KB = 1024 * B
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB

# Minimum free disk space in bytes for downloads to happen, downloading will be stalled if disk space is
# expected to get below this amount as a result of the new file.
MINIMUM_FREE_DISK = 1 * GB

# Tolerance for recording files size mismatch between the declared size in Zoom Servers and the files 
# actually downloaded from the server.
# This was observed to happen sometimes on google drive mounted storage (mismatches of < 300 KBs).
# Note: High tolerance might cause issues like corrupt downloads not being recognized by script.
FILE_SIZE_MISMATCH_TOLERANCE = 0 * KB
