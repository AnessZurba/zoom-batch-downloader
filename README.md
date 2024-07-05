# zoom-batch-downloader

Download all your Zoom cloud recordings for accounts with [paid plans](https://zoom.us/pricing#personal).

This script requires [server-to-server app](https://developers.zoom.us/docs/internal-apps/create/)/[oauth app](https://developers.zoom.us/docs/integrations/create/) credentials from [Zoom App Marketplace](https://marketplace.zoom.us/user/build). There is no need to publish any apps to the marketplace. All usage of the app will be through the credentials you get from Zoom website and provide to the script.

## Choosing your App type

### Server-to-Server app

Recommended for individual users (not part of an organization), or Zoom account admins/owners. The app creation process is straightforward, and the authentication process is seamless once you provide the credentials to the script.

In this app, the app creator and user are always one and the same. The credentials can be used to access data within the account they were created in.

### OAuth App (Advanced)

Recommended for users within an organization where they don't have admin access.

**Important:** When creating the app, be sure to set "Redirect URL for OAuth" and "Add Allow List" to `http://localhost:8000` (You can change the port in the config file if you want).

In this app, the app creator and user can be different. The credentials you get when creating the app are not enough to access the data of your account, and another authentication process will be initiated by the script when using it. You can also autheticate multiple users/accounts using the same app and switch between them using `auth_identifier` in the config file. each `auth_identifier` will have its refresh_token (Basically a temporary password allowing you to access that user resource) in the file `refresh_tokens.json` and will get updated when needed, which might require in some cases a new authentication process by the user.

You can read more about the authentication process [here](https://developers.zoom.us/docs/api/rest/using-zoom-apis/).

## Required Scopes

These are the scopes your app needs to have in order for the script to work.

- `cloud_recording:read:list_user_recordings:admin` or `cloud_recording:read:list_user_recordings` .
- `cloud_recording:read:list_recording_files:admin` or `cloud_recording:read:list_recording_files`.
- (Optional) `user:read:list_users:admin`: if you want the script to iterate over all users in the account (default behavior).

If you are using classic scopes then these would be:

- `recording:read:admin` or  `recording:read` to download the recordings.
- `user:read:admin` if you want the script to iterate over all users in the account.

## Instructions

1. Read "Choosing your App type" section above and decide on your application type.

1. [Create](https://marketplace.zoom.us/user/build) your app with the needed scopes and activate it (no need to publish).

1. Clone/[Download](https://github.com/AnessZurba/zoom-batch-downloader/archive/refs/heads/master.zip) this repository.

1. Copy `config_template.py` to a new file called `config.py` in the same directory and edit it to include your credentials. In addition to the target path and date range for your recording downloads.

1. (Optional) Go over `config.py` to see if you wish to change any other settings.

1. **(Experimental - Windows 10+ only)** If you are not familiar with the concept of a terminal, click the file `run_windows.bat` to run the script directly and skip the rest of these steps - If you are familiar with it, it's recommended you keep reading.

1. Install [Python 3](https://wiki.python.org/moin/BeginnersGuide/Download).

1. Open up a terminal and install the requirements listed in `requirements.txt` using [pip](https://pip.pypa.io/en/stable/reference/requirement-specifiers/).

    ```bash
    python -m pip install -r requirements.txt
    ```

1. Run `zoom_batch_downloader.py`.

    ```bash
    python zoom_batch_downloader.py
    ```

1. (Optional) You can run the app with a custom configuration or override one configuration by fields of another one.

   ``` bash
   python zoom_batch_downloader.py -c config_1.py config_2.py
   ```

Code written by Georg Kasmin, Lane Campbell and Aness Zurba.
