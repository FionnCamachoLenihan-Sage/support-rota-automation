# Usage

When first using this program a new `.chrome_profile` directory will be created at the root of this project. To populate this with the correct credentials, you will need to sign-in to GitHub to allow access to Grafana. This only needs to be done once. On subsequent runs the program will be fully automatic.

`python main.py <grafana_url> <HHh>`

Where `<grafana_url>` is the URL to the Grafana dashboard containing "Errors", "Timeouts", "Very Slow Queries", "DLQ Messages - Standard", and "500's".

and `<HHh>` is the time range in hours. Usually 24h or 72h.

There is an example in `notification-service.sh` on how to use this script.

The output will be generated to `output.txt` and screenshots will be saved to the `screenshots/` directory.

All temporary files are cleared per interpretation of `main.py`.

This program is a bit lacking in error messages, so it is wise to compare the screenshot numbers with the numbers of errors given in output.txt. If these totals match (+- a few), then the program worked.

## Important Note

This program does not yet deal with DLQ messages whatsoever.
