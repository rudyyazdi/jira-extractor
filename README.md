# Jira Tools

A collection of scripts to help with Jira ticket management.

## Setup

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your Jira details:

```bash
cp .env.example .env
```

Then edit `.env` with your details:

## Available Scripts

### 1. Show Description (`show_description.py`)

Shows the description of a Jira ticket.

**Usage:**

```bash
python show_description.py TICKET-123
```

### 2. Create Mirror (`create_mirror.py`)

Creates a mirror ticket in a specified board and links it to the original ticket.

**Usage:**

```bash
python create_mirror.py -b TARGET_BOARD TICKET-123 [TICKET-456 ...]
```

**Arguments:**

- `-b, --board`: (Required) Target board/project key where mirror tickets will be created (e.g., EXMP, DEV)
- `tickets`: One or more ticket keys to mirror

**Features:**

- Creates a mirror ticket with the same title and description
- Links the mirror ticket to the original
- Prevents duplicate mirrors
- Can handle multiple tickets at once
- Configurable target board

**Examples:**

```bash
# Create mirror in EXMP board for one ticket
python create_mirror.py -b EXMP EXMP-152

# Create mirrors in DEV board for multiple tickets
python create_mirror.py -b DEV EXMP-152 EXMP-153 EXMP-154
```

### 3. My TODOs (`my_todos.py`)

Lists all TODO tickets assigned to you in a specific board.

**Usage:**

```bash
python my_todos.py BOARD_NUMBER
```

**Example:**

```bash
# Show your TODO tickets from EXMP board (69)
python my_todos.py 69
```

## Chaining Commands

You can combine these scripts to automate workflows. Here are some useful combinations:

### Create mirrors for all your TODO tickets

```bash
# Get all your TODO tickets from EXMP board and create mirrors in EXMP board
python my_todos.py 69 | xargs python create_mirror.py -b EXMP
```

### Show descriptions for all your TODO tickets

```

```
