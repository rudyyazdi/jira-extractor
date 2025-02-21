import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

# Jira API details
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
AUTH = HTTPBasicAuth(JIRA_EMAIL, os.getenv("JIRA_API_TOKEN"))

# Headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_board_info(board_id):
    """Get board configuration and project key."""
    # First try to get board info
    board_url = f"https://{JIRA_DOMAIN}/rest/agile/1.0/board/{board_id}"
    response = requests.get(board_url, headers=HEADERS, auth=AUTH)
    
    if response.status_code == 200:
        board_data = response.json()
        # The project key is usually in the location or the first project
        if 'location' in board_data and 'projectKey' in board_data['location']:
            return board_data['location']['projectKey']
        elif 'projects' in board_data and len(board_data['projects']) > 0:
            return board_data['projects'][0]['key']
    
    # If that fails, try getting it from the configuration
    config_url = f"https://{JIRA_DOMAIN}/rest/agile/1.0/board/{board_id}/configuration"
    response = requests.get(config_url, headers=HEADERS, auth=AUTH)
    
    if response.status_code == 200:
        config = response.json()
        if 'location' in config and 'projectKey' in config['location']:
            return config['location']['projectKey']
        
    print(f"Failed to fetch board info. Status code: {response.status_code}")
    print(f"Error: {response.text}")
    return None

def get_todo_issues(board_id):
    """Get all TODO issues assigned to the current user."""
    project_key = get_board_info(board_id)
    if not project_key:
        print("Could not determine project key from board ID")
        sys.exit(1)
    
    # JQL query to find TODO issues assigned to current user
    jql = f'project = {project_key} AND assignee = currentUser() AND status in ("To Do", "Open", "TODO", "BACKLOG") ORDER BY created DESC'
    
    # First, get configuration to ensure we have the right status names
    config_url = f"https://{JIRA_DOMAIN}/rest/agile/1.0/board/{board_id}/configuration"
    config_response = requests.get(config_url, headers=HEADERS, auth=AUTH)
    
    if config_response.status_code == 200:
        # Add any additional status names from the board configuration
        config = config_response.json()
        todo_columns = [col['name'] for col in config.get('columnConfig', {}).get('columns', [])
                       if any(word.lower() in col['name'].lower() for word in ['todo', 'to do', 'open', 'backlog'])]
        if todo_columns:
            status_clause = 'status in (' + ', '.join(f'"{s}"' for s in todo_columns) + ')'
            jql = f'project = {project_key} AND assignee = currentUser() AND {status_clause} ORDER BY created DESC'

    # Search for issues
    search_url = f"https://{JIRA_DOMAIN}/rest/api/2/search"
    payload = {
        "jql": jql,
        "maxResults": 50,
        "fields": [
            "summary",
            "status",
            "created",
            "priority",
            "issuetype"
        ]
    }
    
    response = requests.post(search_url, headers=HEADERS, auth=AUTH, json=payload)
    
    if response.status_code == 200:
        return project_key, response.json()
    else:
        print(f"Failed to fetch issues. Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return None, None

def format_issue(issue):
    """Format a single issue for display."""
    fields = issue['fields']
    return {
        'key': issue['key'],
        'type': fields['issuetype']['name'],
        'priority': fields['priority']['name'],
        'status': fields['status']['name'],
        'summary': fields['summary']
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python my_todos.py BOARD_NUMBER")
        print("Example: python my_todos.py 69")
        sys.exit(1)

    try:
        board_id = sys.argv[1]
        int(board_id)  # Validate it's a number
    except ValueError:
        print("Error: Board number must be a number", file=sys.stderr)
        sys.exit(1)
    
    print(f"Fetching TODO issues for {JIRA_EMAIL} from board {board_id}...", file=sys.stderr)
    project_key, issues_data = get_todo_issues(board_id)
    
    if not issues_data:
        sys.exit(1)
        
    issues = issues_data['issues']
    if not issues:
        print("No TODO issues found! 🎉", file=sys.stderr)
        sys.exit(0)
    
    # Print just the ticket numbers, space-separated
    print(" ".join(issue['key'] for issue in issues))

if __name__ == "__main__":
    main() 