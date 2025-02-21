"""
Show Description Script

This script fetches and displays the description of a Jira ticket.
It formats the output nicely and includes the ticket summary.

Usage:
    python show_description.py TICKET-123

Example:
    python show_description.py EXMP-152
"""

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import sys
import textwrap

# Load environment variables from .env file
load_dotenv()

# Jira API details
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
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

def format_description(description):
    """Format the description text for better readability."""
    if not description:
        return "No description available."
    
    # Wrap text at 80 characters
    wrapped_text = textwrap.fill(description, width=80)
    return wrapped_text

def main():
    if len(sys.argv) != 2:
        print("Usage: python show_description.py TICKET-123")
        sys.exit(1)
    
    ticket_key = sys.argv[1].upper()
    issue = get_issue_details(ticket_key)
    
    if issue:
        print(f"\nTicket: {ticket_key}")
        print(f"Summary: {issue['fields']['summary']}")
        print("\nDescription:")
        print("-" * 80)
        description = issue['fields'].get('description', '')
        print(format_description(description))
        print("-" * 80)
    else:
        print(f"Could not find ticket {ticket_key}")

if __name__ == "__main__":
    main() 