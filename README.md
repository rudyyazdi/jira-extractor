# JIRA Extractor

This script extracts data from JIRA using the JIRA REST API and given a sprint ID, it performs the following tasks:

1. Extracts the tickets in the sprint.
2. For each ticket if there are sub-tasks, it extracts the sub-tasks and removes the main ticket from the list.
3. For each ticket, it prints the ticket name.
4. For each status sums up the story points and prints the total story points for each status.

This README provides instructions on how to set up and run the JIRA Extractor on a Mac, including setting up a virtual environment.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Setup

1. **Get the api token from JIRA:**

- Go to [Atlassian Account](https://id.atlassian.com/manage-profile/security/api-tokens) and create an API token.
- Copy `.env.example` to `.env`: `cp .env.example .env`
- Replace the `JIRA_API_TOKEN` in the .env file with the generated API token.
- Replace the `JIRA_EMAIL` in the .env file with the email address associated with the JIRA account.
- Replace the `JIRA_DOMAIN` in the .env file with the JIRA domain.

2. **Create a virtual environment:**

```sh
python3 -m venv venv
```

3. **Activate the virtual environment:**

```sh
source venv/bin/activate
```

4. **Install the required dependencies:**

```sh
pip install -r requirements.txt
```

## Running the JIRA Extractor

1. **Ensure the virtual environment is activated:**

```sh
source venv/bin/activate
```

2. **Run the extractor script:**

```sh
python extract.py
```

## Deactivating the Virtual Environment

To deactivate the virtual environment, simply run:

```sh
deactivate
```
