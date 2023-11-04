# Cloudflare Dynamic DNS Updater

This Python script automates the process of updating a DNS A record on Cloudflare with the current WAN IP address of the machine it's run from. This is particularly useful if you have a dynamic IP address and are hosting services that need to be accessed from the internet.

## Features

- Fetches the current WAN IP of the machine.
- Checks the current IP against the configured A record on Cloudflare.
- Updates the A record if the WAN IP has changed.
- Uses exponential backoff to handle retries for network-related exceptions.

## Requirements

- Python 3.x
- `requests>=2.31.0` module
- `backoff>=2.2.1` module
- `python-dotenv>=1.0.0` module (for environment variable management)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/pedroanisio/scripts.git
cd scripts
```

2. Install the required Python packages:

```bash
virtualenv venv
source venv/bin/activate && cd venv
pip install -r cloudflare_updater.txt
```

## Configuration

1. Rename the provided `cloudflare.env.example` to `cloudflare.env`.

2. Fill in your Cloudflare API token, zone ID, record ID, and the domain you're updating in the `cloudflare.env` file.

```plaintext
CLOUDFLARE_API_TOKEN=your_api_token
CLOUDFLARE_ZONE_ID=your_zone_id
CLOUDFLARE_RECORD_ID=your_record_id
CLOUDFLARE_DOMAIN=your_domain
```

## Usage

Simply run the script:

```bash
python cloudflare_updater/main.py
```

## Automating with Crontab

To keep your DNS record up to date without manual intervention, you can schedule the script to run at regular intervals using `crontab` on Unix-like systems.

1. Open your crontab configuration:

```bash
crontab -e
```

2. Add a new line to schedule the script to run at your desired frequency. For example, to run the script every hour, you would add:

```plaintext
0 * * * * /your_path/virtualenv/bin/python /your_path/cloudflare_updater/main.py >> /path/to/your/logfile.log 2>&1

```

Make sure to replace `/usr/bin/python` with the path to your Python interpreter (you can find this with `which python` or `which python3`), `/path/to/your/cloudflare_updater/main.py` with the actual path to the script, and `/path/to/your/logfile.log` with the path to where you want to store the log output.

3. Save and close the crontab. The cron daemon will automatically install your crontab entry, and your script will be executed at the schedule you've set.

**Note**: The `>> /path/to/your/logfile.log 2>&1` at the end of the crontab entry will redirect both stdout and stderr to a logfile of your choosing, so you can monitor the script's output.

4. To ensure that your environment variables are accessible by the cron job, you can source your `.env` file at the start of the script or use the `env` command in your crontab. Here's how you might modify the crontab entry to source the `.env` file:

```plaintext
0 * * * * /bin/bash -c 'source /path/to/your/cloudflare.env && /usr/bin/python /path/to/your/cloudflare_updater/main.py' >> /path/to/your/logfile.log 2>&1
```

Ensure you replace `/path/to/your/cloudflare.env` with the actual path to your `.env` file.

---

Please adjust the instructions according to the user's environment and make sure the paths and filenames are correct for their setup. It's also a good idea to inform users that they should verify the execution of cron jobs to ensure that everything is running as expected.

The script will log its actions to the console. If the WAN IP and the subdomain's IP address are different, it will update the DNS record.

## Error Handling

The script uses the `backoff` library to retry requests in case of `ConnectionError` or `Timeout`. It will retry 5 times with an exponential backoff strategy.

## Logging

Logs are output to the console with informational messages about the script's operations and errors.

## Contributions

Contributions are welcome! If you would like to contribute to this project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.