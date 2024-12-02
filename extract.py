import requests
from requests.auth import HTTPBasicAuth
from collections import defaultdict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Jira API details
JIRA_DOMAIN = "honeyinsurance.atlassian.net"  # Replace with your Jira domain
SPRINT_ID = "750"  # Replace with your board ID
MAX_RESULTS = 50

# URLs
SPRINT_ISSUES_URL = f"https://{JIRA_DOMAIN}/rest/agile/1.0/sprint/{SPRINT_ID}/issue?maxResults={MAX_RESULTS}"
ISSUE_DETAILS_URL = f"https://{JIRA_DOMAIN}/rest/api/2/issue"

# Headers
HEADERS = {
    "Accept": "application/json"
}

AUTH = HTTPBasicAuth(os.getenv('JIRA_EMAIL'), os.getenv("JIRA_API_TOKEN"))

def get_issue_details(issue_key):
    """Fetch detailed information for an issue by its key."""
    url = f"{ISSUE_DETAILS_URL}/{issue_key}"
    response = requests.get(url, headers=HEADERS, auth=AUTH)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch details for issue {issue_key}. Status code: {response.status_code}")
        return None

try:
    # Fetch issues in the sprint
    response = requests.get(
        SPRINT_ISSUES_URL,
        headers=HEADERS,
        auth=AUTH
    )

    if response.status_code == 200:
        issues = response.json()
        print("Issues retrieved successfully!")
        
        final_tickets = []
        story_points_by_status = defaultdict(float)  # Initialize defaultdict for story points aggregation

        for issue in issues.get("issues", []):
            # Get normal ticket information
            story_points = issue["fields"].get("customfield_10016", 0)  # Adjust field ID for story points
            status = issue["fields"]["status"]["name"]

            # Check if there are subtasks
            subtasks = issue["fields"].get("subtasks", [])
            if subtasks:
                for subtask in subtasks:
                    # Fetch detailed information for the subtask
                    subtask_details = get_issue_details(subtask["key"])
                    if subtask_details:
                        subtask_points = subtask_details["fields"].get("customfield_10016", 0)
                        subtask_status = subtask_details["fields"]["status"]["name"]
                        if subtask_points:
                            story_points_by_status[subtask_status] += subtask_points

                        # Add subtasks to final tickets
                        final_tickets.append({
                            "key": subtask["key"],
                            "summary": subtask_details["fields"]["summary"]
                        })
            else:
                # Add story points for the normal ticket
                if story_points:
                    story_points_by_status[status] += story_points

                # Add the normal ticket to final tickets
                final_tickets.append({
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"]
                })

        # Print the processed tickets
        print("Tickets and Subtasks:")
        for ticket in final_tickets:
            print(f"- {ticket['key']}: {ticket['summary']}")

        # Print the total story points by status
        print("\nStory Points by Status:")
        for status, total_points in story_points_by_status.items():
            print(f"- {status}: {total_points} story points")

    else:
        print(f"Failed to retrieve issues. Status code: {response.status_code}")
        print(f"Error message: {response.text}")

except Exception as e:
    print(f"An error occurred: {e}")