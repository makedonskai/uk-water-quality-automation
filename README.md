UK Water Quality Automation
An automated water level monitoring system for UK rivers, built with n8n. Tracks 5 stations on the Thames and Lee rivers in real time, logs all readings to Google Sheets, and sends instant Telegram alerts when water levels exceed warning or critical thresholds.

What it does
Every time the workflow runs, it:

Loads a list of 5 monitoring stations with their custom warning/critical thresholds
Fetches the latest water level reading from each station via the UK Environment Agency Flood Monitoring API
Logs every reading to a Google Sheets spreadsheet for historical analysis
Compares each reading against the station's specific thresholds
Sends a Telegram alert if any station exceeds its warning level
Sends an emergency Telegram alert if any station exceeds its critical level
Why this project
The UK government provides free flood warnings, but they are tuned for general public safety. Small businesses near rivers — B&Bs, fish farms, golf courses, campsites — often need custom thresholds and custom alert routing. This project demonstrates how to build that on top of public open data, with no infrastructure cost beyond a laptop running n8n locally.

Stack
n8n (self-hosted, npm install) — workflow automation
UK Environment Agency Flood Monitoring API — real-time water levels (15-min updates)
Google Sheets API — historical data logging
Telegram Bot API — instant alerts
Node.js 20 LTS — runtime
Git + GitHub — version control
Architecture
[Manual Trigger]
|
v
[Code: Define stations] <- 5 station configs with thresholds
|
v
[HTTP Request] <- Fetches readings from EA API
|
v
[Edit Fields] <- Merges API data with station config
|
+----> [Google Sheets: Append row] <- All readings logged here
|
v
[Switch] <- Routes by status
|
+-- Output 0 (current_level >= critical) -> [Telegram: Critical Alert]
+-- Output 1 (current_level >= warning) -> [Telegram: Warning Alert]
+-- Output 2 (normal) -> (no action)
Stations monitored
Station ID Name River Warning Critical
2200TH Reading Thames 7.0 m 7.3 m
3400TH Kingston Thames 3.97 m 4.2 m
5380TH Walthamstow Low Hall Lee 1.35 m 1.50 m
3404TH Sunbury Lock Thames 0.17 m 0.30 m
4150TH Merton Wandle 0.38 m 0.60 m
Threshold values are stored in data/reference/thresholds.csv and were derived from the EA API's stageScale (typical range high) and the public flood warning service.

How to run this yourself
Prerequisites
macOS, Linux, or Windows
Node.js 20 LTS or newer
A Google account (for Sheets)
A Telegram account (for alerts)
Git
Setup
Clone the repository

git clone https://github.com/makedonskai/uk-water-quality-automation.git
cd uk-water-quality-automation
Install n8n globally

npm install -g n8n
Start n8n

n8n start
Then open http://localhost:5678 in your browser and create a local account.

Create a Google Sheets spreadsheet

Create a new Google Sheet named uk-water-monitoring
Rename the first sheet to All_Readings
Add these column headers in row 1: timestamp, station_id, station_name, current_level, warning_level, critical_level, reading_time, status
Set up Google OAuth credentials

Go to Google Cloud Console → create a new project
Enable the Google Sheets API
OAuth consent screen → External, Testing mode
Credentials → OAuth client ID → Web application
Add http://localhost:5678/rest/oauth2-credential/callback to authorized redirect URIs
Copy the Client ID and Client Secret into the n8n Google Sheets credential
Set up Telegram bot

Open Telegram, message @BotFather
Send /newbot, follow prompts to create a bot
Copy the bot token
Start a chat with your new bot (send any message)
Visit https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates to find your chat ID
In n8n, create a Telegram credential using the bot token
Import the workflow

In n8n, go to Workflows → Import from file
Select workflows/02-fetch-all-stations.json
Open the workflow and re-link credentials in:
Google Sheets node (your Sheets credential)
Telegram nodes (your Telegram credential)
Update the chat ID in Telegram nodes to your own
Update the spreadsheet ID in the Google Sheets node
Test

Click Execute workflow
Verify rows appear in your Google Sheet
Force a Telegram alert by temporarily lowering a threshold
Reliability features
HTTP retry — the HTTP Request node retries up to 3 times on failure, with exponential backoff. The UK EA API is generally reliable but occasional 5xx responses do happen.
Per-station thresholds — each station has its own warning and critical values, configured in the Code node. No assumptions about a "global" alert level.
Full audit trail — every reading is logged to Google Sheets regardless of status, so historical trends can be analysed even when no alerts fired.
What's not in V1 (planned for V2)
Schedule trigger (currently runs only on manual trigger)
AI-generated breach explanations via Anthropic Claude API
Trend detection (rising vs. falling water levels)
Multi-channel routing (different stations → different Telegram groups)
Slack output for business clients
Web dashboard (visualisation of historical data from Sheets)
Security notes
No credentials are stored in this repository. All API keys, OAuth tokens, and bot tokens live only inside n8n's local encrypted database (~/.n8n/database.sqlite).
Workflow exports include only credential references (IDs), not the credentials themselves. Importing this workflow on a different machine requires re-authenticating with your own accounts.
The .gitignore blocks any accidental commits of .env, OAuth tokens, or n8n local data files.
Data licensing
Water level data is provided by the UK Environment Agency under the Open Government Licence v3.0. This project is non-commercial and demonstrative.

Author
Built by Inna Makedonska as part of a hands-on n8n + API integration learning project. Contact: see GitHub profile.
