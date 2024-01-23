import json
import string
import requests
from datetime import datetime, timedelta
import yaml
from requests.auth import HTTPBasicAuth
import random

username='hemanthn@testvagrant.com'
password='ATATT3xFfGF00x8wTLQbCysaq5iojlDm1vo8XjEklEl9zyKKwrlF_PiWphnIoXoW99lx9B7z5gdLZSASzEeGimkJTe-bDpW5DUw2Wya-PrhMeWOPR3sg3LwyoUCg2owN4w2DSFOMCI4Xpvi1OjFlc1Y5UNHAqv4E0catK_HVPsURRadk_9DGrmA=CAE5BF29'
jira_url='https://preetis-testvagrant.atlassian.net/'
createIssueURL= jira_url+"rest/api/2/issue";
priority=['Low','Lowest','Medium','High','Highest']
teams=['Team1','Team2','Team3',"Team4"]
summary=["Application crashes when clicking on a specific button.",
    "Incorrect results are displayed in the search feature.",
    "Login functionality is not working as expected.",
    "Typos in error messages throughout the system.",
    "Unable to upload files through the file attachment feature.",
    "Data inconsistency between the database and the UI.",
    "Error 500 encountered when accessing a particular page.",
    "Missing validation for user input in the registration form.",
    "Performance degradation during heavy data processing.",
    "Graphical glitches in the user interface.",
    "Incorrect date formatting in certain sections of the application.",
    "Email notifications are not being sent upon certain events.",
    "Broken links on the website.",
    "Issues with responsive design on mobile devices.",
    "Inconsistent behavior across different browsers.",
    "Unintuitive error messages confusing users.",
    "Authentication problems for certain user roles.",
    "Issues with session management and user logout.",
    "Unable to save changes in the profile settings.",
    "Search functionality returning incomplete or incorrect results.",
    "Security vulnerability in the password reset functionality.",
    "Incorrect handling of special characters in input fields.",
    "Timeout issues during long-running processes.",
    "Missing error handling for edge cases in the code.",
    "Problems with data synchronization between server and client.",
    "Unexpected behavior when navigating back and forth between pages.",
    "Issues with data validation on form submissions.",
    "Difficulty reproducing intermittent bugs for debugging.",
    "Cross-site scripting (XSS) vulnerability detected.",
    "Accessibility issues for users with disabilities.",
    "Failure to gracefully handle server downtimes or outages.",
    "Unexpected behavior when using keyboard shortcuts.",
    "Incorrect sorting of data in tables or lists."]

def getRequestJson():
    createIssue={
    "fields": {
        "project": {
        "key": "TP"
        },
        "summary": random.choice(summary),
        "description": "Creating an issue via REST API",
        "issuetype": {
        "name": "Bug"
        },
        "priority": {
        "name": random.choice(priority) 
        },
        "assignee": {
        "accountId": "712020:39aad32f-acf7-4658-b0cc-4ff1fd173e33"
        },
        "customfield_10043": {
        "value": random.choice(teams)
        }
    }
    }
    # print(createIssue['fields']['summary'])
    # print(createIssue)
    return createIssue


def get_jira_url_from_config():
    config_file_path = 'config.yml'
    with open(config_file_path, 'r') as file:
        config_data = yaml.safe_load(file)
        jira_base_url = config_data.get('URL', {}).get('base', '')
        jira_jql = config_data.get('URL', {}).get('jql', '')
        return f"{jira_base_url}{jira_jql}"
        
    
def fetch_data_from_api():
    current_datetime = datetime.now()
    four_days_ago = current_datetime - timedelta(days=4)
    end_time = current_datetime.strftime('%Y-%m-%d %H:%M')
    start_time = four_days_ago.strftime('%Y-%m-%d %H:%M')
    with open('config.yml', 'r') as file:
            config = yaml.safe_load(file)
    
    jql_query = f'rest/api/3/search?jql=created >= "{start_time}" AND created <= "{end_time}" OR updated >= "{start_time}" AND updated <= "{end_time}" order by priority DESC,updated DESC'
    config['URL']['jql'] = jql_query
    with open('config.yml', 'w') as file:
        yaml.dump(config, file)
    api_url=get_jira_url_from_config()
    print("URL =",api_url)
    try:
        response = requests.get(api_url, auth=HTTPBasicAuth(username=username, password=password))
        if response.status_code == 200:
            data = response.json()
            result_dict = {issue['id']: issue['fields']['status']['name'] for issue in data['issues']}
            return result_dict;
        else:
            print(f"Error: Unable to fetch data. Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return {}

        
def changeStatus(jsonDict):
    for issue_id, current_status in jsonDict.items():
        if current_status == 'To Do':
            desired_status = 'In Progress'
        elif current_status == 'In Progress':
            desired_status = 'In Review'
        elif current_status == 'In Review':
            desired_status = 'Resolved'
        elif current_status == 'Resolved':
            desired_status = 'In Test'
        elif current_status == 'In Test':
            desired_status = 'Done'
        else:
            # No change for 'Done' status
            continue
        # Jira API endpoint for transitions
        transitions_endpoint = f"{jira_url}/rest/api/2/issue/{issue_id}/transitions"
        print("transitions_endpoint = ",transitions_endpoint)
        # Get available transitions for the issue
        response = requests.get(transitions_endpoint, auth=(username, password))
        transitions_data = response.json()
        print('-----------------------------------')
        # Find the transition ID for the desired status
        transition_id = None
        for transition in transitions_data['transitions']:
            if transition['to']['name'] == desired_status:
                transition_id = transition['id']
                break
        print("transition_id = ", transition_id)

        if transition_id is None:
            print(f"Warning: Transition to '{desired_status}' not found for issue {issue_id}")
            continue

        # Perform the transition
        transition_data = {
            "transition": {"id": transition_id}
        }
        print("transition_data = ",transition_data)
        transition_url = transitions_endpoint;
        print("transition_url = ",transition_url)
        
        response = requests.post(transition_url, json=transition_data, auth=(username, password))

        if response.status_code == 204:
            print(f"Successfully transitioned issue {issue_id} from '{current_status}' to '{desired_status}'")
        else:
            print(f"Failed to transition issue {issue_id} from '{current_status}' to '{desired_status}'. Status code: {response.status_code}")
            print(response.text)
    

def createNewIssue(createIssue):
    requests.post(createIssueURL, json=createIssue, auth=HTTPBasicAuth(username=username, password=password))
    print('-----------------------------------')
    print(createIssue)


issueDict=fetch_data_from_api()
changeStatus(issueDict)
for i in range(10):
    print('---------------------------------')
    requestPayload=getRequestJson()
    createNewIssue(requestPayload)

