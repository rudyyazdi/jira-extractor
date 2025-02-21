import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import sys
import json

# Load environment variables from .env file
load_dotenv()

# Jira API details
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
ISSUE_API_URL = f"https://{JIRA_DOMAIN}/rest/api/2/issue"
ISSUE_LINK_URL = f"https://{JIRA_DOMAIN}/rest/api/2/issueLink"

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

def check_existing_links(issue_key):
    """Check if the issue already has a mirror link."""
    issue = get_issue_details(issue_key)
    if not issue:
        return False
    
    links = issue.get('fields', {}).get('issuelinks', [])
    for link in links:
        if link.get('type', {}).get('name') in ['Relates', 'Mirrors']:
            linked_issue = link.get('outwardIssue') or link.get('inwardIssue')
            if linked_issue and linked_issue.get('key', '').startswith('PET-'):
                print(f"Mirror link already exists: {linked_issue['key']}")
                return True
    return False

def create_mirror_issue(source_issue, project_key="PET"):
    """Create a mirror issue in the target project."""
    fields = source_issue['fields']
    
    # Prepare the payload for the new issue
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": fields['summary'],
            "description": fields.get('description', ''),
            "issuetype": {"name": "Task"}  # You might want to adjust this based on available issue types
        }
    }
    
    response = requests.post(
        ISSUE_API_URL,
        headers=HEADERS,
        auth=AUTH,
        json=payload
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create mirror issue. Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def create_issue_link(source_key, target_key):
    """Create a link between two issues."""
    payload = {
        "type": {
            "name": "Relates"  # or "Mirrors" if available in your Jira instance
        },
        "inwardIssue": {
            "key": source_key
        },
        "outwardIssue": {
            "key": target_key
        }
    }
    
    response = requests.post(
        ISSUE_LINK_URL,
        headers=HEADERS,
        auth=AUTH,
        json=payload
    )
    
    if response.status_code == 201:
        return True
    else:
        print(f"Failed to create issue link. Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def process_ticket(source_key):
    """Process a single ticket to create its mirror."""
    print(f"\nProcessing ticket: {source_key}")
    
    # Check if mirror already exists
    if check_existing_links(source_key):
        print("Mirror ticket already exists. Skipping creation.")
        return False
    
    # Get source issue details
    source_issue = get_issue_details(source_key)
    if not source_issue:
        print(f"Failed to process {source_key}")
        return False
    
    # Create mirror issue
    print(f"Creating mirror issue for {source_key}...")
    mirror_issue = create_mirror_issue(source_issue)
    if not mirror_issue:
        print(f"Failed to process {source_key}")
        return False
    
    mirror_key = mirror_issue['key']
    print(f"Created mirror issue: {mirror_key}")
    
    # Create link between issues
    print("Creating link between issues...")
    if create_issue_link(source_key, mirror_key):
        print(f"Successfully created mirror ticket {mirror_key} and linked it to {source_key}")
        return True
    else:
        print("Failed to create link between issues")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_mirror.py TICKET-123 [TICKET-456 TICKET-789 ...]")
        sys.exit(1)
    
    # Process all tickets provided as arguments
    source_keys = [key.upper() for key in sys.argv[1:]]
    
    results = []
    for key in source_keys:
        success = process_ticket(key)
        results.append((key, success))
    
    # Print summary
    print("\nSummary:")
    print("-" * 50)
    for key, success in results:
        status = "✓ Success" if success else "✗ Skipped/Failed"
        print(f"{key}: {status}")

if __name__ == "__main__":
    main() 