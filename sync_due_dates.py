"""
Sync Due Dates Script

This script syncs due dates between related Jira tickets.
For each provided ticket, it:
1. Checks if the ticket has any 'Relates' type links
2. If the original ticket has a due date and the linked ticket doesn't
3. Updates the linked ticket's due date to match the original

Usage:
    python sync_due_dates.py TICKET-123 [TICKET-456 TICKET-789 ...]

Example:
    python sync_due_dates.py EXMP-152
    python sync_due_dates.py EXMP-152 EXMP-153 EXMP-154
"""

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import sys
import json
import argparse

# Load environment variables from .env file
load_dotenv()

# Jira API details
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
ISSUE_API_URL = f"https://{JIRA_DOMAIN}/rest/api/2/issue"

# Headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

AUTH = HTTPBasicAuth(os.getenv('JIRA_EMAIL'), os.getenv("JIRA_API_TOKEN"))

def get_issue_details(issue_key):
    """Fetch detailed information for an issue by its key."""
    url = f"{ISSUE_API_URL}/{issue_key}"
    response = requests.get(url, headers=HEADERS, auth=AUTH)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch details for issue {issue_key}. Status code: {response.status_code}")
        return None

def update_issue_due_date(issue_key, due_date):
    """Update the due date of an issue."""
    url = f"{ISSUE_API_URL}/{issue_key}"
    payload = {
        "fields": {
            "duedate": due_date
        }
    }
    
    response = requests.put(
        url,
        headers=HEADERS,
        auth=AUTH,
        json=payload
    )
    
    if response.status_code == 204:  # 204 is success with no content
        return True
    else:
        print(f"Failed to update due date for {issue_key}. Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def process_ticket(source_key):
    """Process a single ticket to sync due dates with related tickets."""
    print(f"\nProcessing ticket: {source_key}")
    
    # Get source issue details
    source_issue = get_issue_details(source_key)
    if not source_issue:
        print(f"Failed to fetch {source_key}")
        return False
    
    # Check if source issue has a due date
    source_due_date = source_issue['fields'].get('duedate')
    if not source_due_date:
        print(f"{source_key} has no due date. Skipping.")
        return False
    
    # Get all issue links
    links = source_issue.get('fields', {}).get('issuelinks', [])
    updated_count = 0
    
    for link in links:
        if link.get('type', {}).get('name') == 'Relates':
            # Get the linked issue (could be either inward or outward)
            linked_issue = link.get('outwardIssue') or link.get('inwardIssue')
            if not linked_issue:
                continue
                
            linked_key = linked_issue['key']
            print(f"Checking related ticket: {linked_key}")
            
            # Get full details of linked issue
            linked_details = get_issue_details(linked_key)
            if not linked_details:
                continue
            
            # Check if linked issue has no due date
            if not linked_details['fields'].get('duedate'):
                print(f"Updating due date for {linked_key}")
                if update_issue_due_date(linked_key, source_due_date):
                    print(f"Successfully updated due date for {linked_key}")
                    updated_count += 1
                else:
                    print(f"Failed to update due date for {linked_key}")
    
    return updated_count > 0

def main():
    parser = argparse.ArgumentParser(description='Sync due dates between related Jira tickets.')
    parser.add_argument('tickets', nargs='+', help='One or more ticket keys to process')
    
    args = parser.parse_args()
    source_keys = [key.upper() for key in args.tickets]
    
    results = []
    for key in source_keys:
        success = process_ticket(key)
        results.append((key, success))
    
    # Print summary
    print("\nSummary:")
    print("-" * 50)
    for key, success in results:
        status = "✓ Updates made" if success else "- No updates needed/failed"
        print(f"{key}: {status}")

if __name__ == "__main__":
    main() 