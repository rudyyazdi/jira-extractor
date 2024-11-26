import requests
from requests.auth import HTTPBasicAuth

# Jira API details
JIRA_DOMAIN = "honeyinsurance.atlassian.net"  # Replace with your Jira domain
BOARD_ID = "45"  # Replace with your board ID
EMAIL = "rudy@rudy.com"  # Replace with your Jira email
API_TOKEN = "your-api-token"  # Replace with your Jira API token

# Jira API endpoint for fetching board issues
URL = f"https://{JIRA_DOMAIN}/rest/agile/1.0/board/{BOARD_ID}/issue"

# Headers
HEADERS = {
    "Accept": "application/json"
}

# Make the request
try:
    response = requests.get(
        URL,
        headers=HEADERS,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN)
    )

    # Check the response status
    if response.status_code == 200:
        issues = response.json()
        print("Issues retrieved successfully!")
        for issue in issues.get("issues", []):
            print(f"- {issue['key']}: {issue['fields']['summary']}")
    else:
        print(f"Failed to retrieve issues. Status code: {response.status_code}")
        print(f"Error message: {response.text}")

except Exception as e:
    print(f"An error occurred: {e}")