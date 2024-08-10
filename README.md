# Zoom Batch Downloader

Download your Zoom cloud recordings.

This script requires [server-to-server app](https://developers.zoom.us/docs/internal-apps/create/)/[oauth app](https://developers.zoom.us/docs/integrations/create/) credentials from [Zoom App Marketplace](https://marketplace.zoom.us/user/build). There is no need to publish any apps to the marketplace. All usage of the app will be through the credentials you get from Zoom website and provide to the script.

## Choosing your App type

### Server-to-Server app (Default choice)

**Recommended for admins/owners of paid Zoom accounts.** The app creation process is straightforward, and the authentication process is seamless once you provide the credentials to the script.

With this app type, the app creator and user are always one and the same. The credentials can be used to access data within the account they were created in.

This app type can only be used for an account-level app - thus the recommendation above.

### OAuth App (Advanced)

**Recommended for users with free accounts, or those within an organization where they don't have admin access.**

**Important:** When creating the app, be sure to set "Redirect URL for OAuth" and "Add Allow List" to `http://localhost:8000` (You can change the port in the config file if you want).

With this app type, the app creator and user can be different. The credentials you get when creating the app are not enough to access the data of your account, and another authentication process will be initiated by the script when using it. You can also autheticate multiple users/accounts using the same app and switch between them using `auth_identifier` in the config file. Each `auth_identifier` will have its refresh_token (Basically a temporary password allowing you to access that user resource) in the file `refresh_tokens.json` and will get updated when needed, which might require in some cases a new authentication process by the user.

You can read more about the authentication process [here](https://developers.zoom.us/docs/api/rest/using-zoom-apis/).

This app type can be used for an account-level or user-level app (Depends on the permissions given to you by your organization).

## Required Scopes

These are the scopes your app needs to have in order for the script to work:

### For account-level apps (Default choice)

- `cloud_recording:read:list_user_recordings:admin`.
- `cloud_recording:read:list_recording_files:admin`.
- (Optional) `user:read:list_users:admin`: if you want the script to iterate over all users in the account (default behavior).

<details>
<summary>Classic Scopes (Deprecated)</summary>

- `recording:read:admin` to download the recordings.
- `user:read:admin` to iterate over all users in the account.
  
</details>

### For user-level apps

- `cloud_recording:read:list_user_recordings`.
- `cloud_recording:read:list_recording_files`.

<details>
<summary>Classic Scopes (Deprecated)</summary>

- `recording:read`

</details>

**Note:** user-level apps can't access other users' data, so it's recommended that you set the users array in the config file to contain only the string "me".

## Instructions

1. Read [Choosing your App type](#choosing-your-app-type) section above and decide on your application type.

1. [Create](https://marketplace.zoom.us/user/build) your app with the [required scopes](#required-scopes) and activate it (no need to publish).

1. Clone/[Download](../../archive/refs/heads/master.zip) this repository.

1. Copy `config_template.py` to a new file called `config.py` in the same directory and edit it to include your credentials. In addition to the target path and date range for your recording downloads.

1. (Optional) Go over `config.py` to see if you wish to change any other settings.

1. **(For Beginners - Windows 10+ only)** If you are not familiar with the concept of a terminal, double-click the file `run_windows.bat` to run the script directly and skip the rest of these steps. For users familiar with terminals, it's recommended you keep reading.

1. Install [Python 3](https://wiki.python.org/moin/BeginnersGuide/Download).

1. Open up a terminal and install the requirements listed in `requirements.txt` using [pip](https://pip.pypa.io/en/stable/reference/requirement-specifiers/).

    ```bash
    python -m pip install -r requirements.txt
    ```

1. Run `zoom_batch_downloader.py`.

    ```bash
    python zoom_batch_downloader.py
    ```

1. (Optional) You can run the app with a custom configuration or override a configuration by the fields of another one using `--config` parameter

   ``` bash
   python zoom_batch_downloader.py --config config_1.py config_2.py
   ```

Code written by Georg Kasmin, Lane Campbell and Aness Zurba.
