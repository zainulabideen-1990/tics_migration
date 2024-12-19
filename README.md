# Install Python
 - Click on link (https://www.python.org/downloads/) and download the 3.13.1 version of python

# Run the Command (to install packages)
  - pip install requests tenacity python-dotenv

## Sequence to run scripts ##

1. contacts_migration.py
    - Fetch Contacts from AutoTask, post contacts on atera, and save the extracted contacts in a file locally.

2. fetch_atera_contacts.py
    - Fetch Contacts from Atera, and save the extracted contacts in a file locally.

3. fetch_resources.py
    - Fetch all the resources from AutoTask, and save the extracted resources locally

4. script1_tickets.py
    - Fetch all tickets from Auto Task priority wise, and save the extracted tickets locally

5. script2_tickets.py
    - Fetch ticket notes against each ticket, make seperate call for each ticket. 
    - Append the tickets notes against each ticket. Then save the updated data in a new file

6. script3_tickets.py
    - Map the final payload to final hit on Atera.
    - It includes matching database entries of Atera with AutoTask

7. script4_tickets.py
    - Final Script to post tickets, and comments on Atera

## Note:
    - All the relevant files are saved in json_files folder.
    - Logs of each script will be maintained in log_info folder.

## List of Pre-saved JSON Files:
    -> all_priority.json
    -> all_status.json
    -> atera_technicians.json (--I have fetched this data from Network Request, as there is noexposed API available in swagger doc)
