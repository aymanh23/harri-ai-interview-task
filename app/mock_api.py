import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.settings import settings



def _load_json(filename: str) -> List[Dict[str, Any]]:
    """Reads and parses a JSON file from the data directory."""
    data_path = settings.data_path / filename
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_employee_info(
    query: Optional[str] = None,
    id: Optional[str] = None,
    name: Optional[str] = None,
    team: Optional[str] = None,
    role: Optional[str] = None,
    jira_username: Optional[str] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    
    employees = _load_json("employees.json")
    results = []
    for emp in employees:
        if (
            (id is None or emp.get("id") == id) and
            (name is None or emp.get("name").lower() == name.lower()) and
            (email is None or emp.get("email").lower() == email.lower()) and
            (role is None or emp.get("role").lower() == role.lower()) and
            (team is None or emp.get("team").lower() == team.lower()) and 
            (jira_username is None or emp.get("jira_username").lowe() == jira_username.lower())
        ):
            results.append(emp)

    return {
        "source": "employees.json",
        "fetched_at": datetime.now().isoformat(),
        "data": results or employees
    }

def get_jira_tickets(
    query: Optional[str] = None,
    id: Optional[str] = None,
    assignee: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:

    tickets = _load_json("jira_tickets.json")
    results = []
    for t in tickets:
        if (
            (id is None or t.get("id").lower() == id.lower()) and
            (assignee is None or t.get("assignee").lower() == assignee.lower()) and
            (status is None or t.get("status").lower() == status.lower()) and
            (priority is None or t.get("priority").lower() == priority.lower())
        ):
            results.append(t)
    

    return {
        "source": "jira_tickets.json",
        "fetched_at": datetime.now().isoformat(),
        "data": results or tickets,
    }

def get_deployments(
    query: Optional[str] = None,
    service: Optional[str] = None,
    version: Optional[str] = None,
    status: Optional[str] = None,
    date: Optional[str] = None
) -> Dict[str, Any]:

    deployments = _load_json("deployments.json")
    results = []
    for dep in deployments:
        if (
            (service is None or dep.get("service").lower() == service.lower()) and
            (version is None or dep.get("version").lower() == version.lower()) and
            (date is None or dep.get("date") == date) and
            (status is None or dep.get("status").lower() == status.lower())
        ):
            results.append(dep)

    return {
        "source": "deployments.json",
        "fetched_at": datetime.now().isoformat(),
        "data": results or deployments,
    }


