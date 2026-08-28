# Support Rota Automation

## Introduction

To preface, this app is geared towards the way Squad Skellig does their Support Rota.

To start, first create a query group. This will include the link to the grafana dashboard, followed by a number of types of metrics. These will correspond to the 4 elasticsearch queries found in Grafana.

Excluded from this is the DLQ panel. This should be done by a human.

When first using this program a new `.chrome_profile` directory will be created at the root of this project. To populate this with the correct credentials, you will need to sign-in to GitHub to allow access to Grafana. This only needs to be done once. On subsequent runs the program will be fully automatic.

If the program doesn't work after trying for a while, deleting the `.chrome_profile` can help. This shouldn't be necessary though.

After creating your profile, all that needs to be done is to click `Get Metrics`.

You may copy both the screenshot and also the formatted analytics themselves by clicking the corresponding copy-to clipboard-buttons.

## Installation

First, go to the `backend/` directory and use `pip install -r requirements.txt` to install all python dependencies. Make sure you're on Python >=3.14.0.

Next, go to the `frontend/` directory and make sure you have `rust` installed. Then, using `cargo install` in the `frontend/src-tauri/` directory install the necessary Rust Crates.

Lastly, go to the `frontend/src` directory, and run making sure you have both `node` and `npm` installed, run `npm install`.

Now that everything is installed, just run `npm run tauri dev` in the `frontend/` directory and you're good to go.

I am too lazy to make a build.

__Note:__ There is probably something missing here so just message yours truly if there is an issue

## Important Notes

### Maximum Number of Logs

This program can get up to 10,000 logs at a time for any given query. This means 40,000 logs split evenly among the elasticsearch queries. This should be more than enough.

### Only Production and Sandbox

Due to the way Grafana API queries work with the data source endpoint `POST /api/ds/query`. A UID must be given to get the correct environment. For `production` this is 00000007, and for `sandbox` this is 00000006. This is currently matched based off of the `orgId=N` parameter you can see at the end of the Grafana URLS. Other environments can be achieved, but for now it is just production and sandbox.

### Error Handling

Yeah, it could just be better at this point.

### Closing The App

Following from this, if you have metrics stored in the app, restarting it will lose all your metrics. Not a big deal as it takes so little time to get them again, but just something to keep in mind.

## Pro Tip

After pasting into Slack, press `ctrl + shift + f` to format the metrics.
