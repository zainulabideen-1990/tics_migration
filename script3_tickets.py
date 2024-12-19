import json
import os

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

all_contacts = load_json(os.path.join("json_files", "all_contacts.json"))
all_priorities = load_json(os.path.join("json_files", "all_priority.json"))
all_statuses = load_json(os.path.join("json_files", "all_status.json"))
all_resources = load_json(os.path.join("json_files", "all_resources.json"))
all_technicians = load_json(os.path.join("json_files", "atera_technicians.json"))
atera_contacts = load_json(os.path.join("json_files", "atera_contacts.json"))

def get_ticket_priority(priority_id):
    for priority in all_priorities:
        if priority['id'] == priority_id:
            return priority['name']
    return "Low"

def get_ticket_status(status_id):
    for status in all_statuses:
        if status['id'] == status_id:
            return status['name']
    return "New"

def get_ticket_impact(issue_type):
    impacts = {
        1: 'NoImpact',
        2: 'Minor',
        3: 'Major',
        4: 'Crisis',
        5: 'SiteDown',
    }
    return impacts.get(issue_type, 'Minor')

def get_ticket_type(ticket_type_id):
    ticket_type_dict = {
        1: "Request",
        2: "Incident",
        3: "Problem",
        4: "Change"
    }
    return ticket_type_dict.get(ticket_type_id, "Incident")

def get_end_user(contact_id):
    for contact in all_contacts:
        if contact['id'] == contact_id:
            return {
                'EndUserID': contact['id'],
                'EndUserFirstName': contact['firstName'],
                'EndUserLastName': contact['lastName'],
                'EndUserEmail': contact['emailAddress']
            }
    return {}

def get_assigned_resource(resource_id):
    for resource in all_resources:
        if resource['id'] == resource_id:
            return {
                'resourceID': resource['id'],
                'resourceFirstName': resource['firstName'],
                'resourceLastName': resource['lastName'],
                'resourceEmail': resource['email']
            }
    return {}

def get_technician_id(resource_email):
    for technician in all_technicians:
        if technician['Email'] == resource_email:
               return technician['$id']
        
def get_enduser_id(enduser_email):
    for enduser in atera_contacts:
        if enduser['Email'] == enduser_email:
               return enduser['EndUserID']

def get_ticket_comments(comments):
    result = []
    for comment in comments:
        if (comment["noteType"] == 1):
            comment_data = {
                "CommentTimestampUTC": comment["createDateTime"],
                "CommentText": comment["description"],
            }
            if comment["creatorResourceID"] is None:
                comment_data["TechnicianCommentDetails"] = {
                    "TechnicianId": get_technician_id(get_end_user(comment["createdByContactID"]).get("EndUserEmail")),
                    "IsInternal": False
                }
            else:
                comment_data["EnduserCommentDetails"] = {
                    "EnduserId": get_enduser_id(get_assigned_resource(comment["creatorResourceID"]).get("resourceEmail"))
                }
            result.append(comment_data)
    return result

def create_ticket_payload(ticket):
    priority = get_ticket_priority(ticket['priority'])
    comments = get_ticket_comments(ticket['notes'])
    status = get_ticket_status(ticket['status'])
    impact = get_ticket_impact(ticket['issueType'])
    ticket_type = get_ticket_type(ticket['ticketType'])
    end_user = get_end_user(ticket['contactID'])
    assigned_resource = get_assigned_resource(ticket['assignedResourceID'])
    technician_contact_id = get_technician_id(assigned_resource.get('resourceEmail'))
    end_user_id = get_enduser_id(end_user.get('EndUserEmail'))

    payload = {
        "TicketTitle": ticket["title"],
        "Description": ticket["description"],
        "TicketPriority": priority,
        "TicketImpact": impact,
        "TicketStatus": status,
        "TicketType": ticket_type,
        "TechnicianContactID": technician_contact_id,
        "comments": comments
    }

    if end_user_id:
        payload["EndUserID"] = end_user_id
    else:
        payload.update({
            "EndUserFirstName": end_user.get("EndUserFirstName"),
            "EndUserLastName": end_user.get("EndUserLastName"),
            "EndUserEmail": end_user.get("EndUserEmail"),
        })

    return payload

def process_tickets(ticket_data):
    new_payloads = []
    for ticket in ticket_data:
        payload = create_ticket_payload(ticket)
        new_payloads.append(payload)
    return new_payloads

if __name__ == "__main__":
    tickets = load_json('result2.json')
    new_ticket_payloads = process_tickets(tickets)

    with open(os.path.join("json_files", "result3.json"), 'w') as f:
        json.dump(new_ticket_payloads, f, indent=4)

    print(f"Processed {len(new_ticket_payloads)} tickets and saved to 'result3.json'.")
