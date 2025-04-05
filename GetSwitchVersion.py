import time
from netmiko import ConnectHandler
import getpass
import re
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import curses
import sites

# Function to display the initial block of text and prompt for credentials
def display_initial_text():
    print("""
======================================================================
======================================================================
|                                                                    |
|  This script will log into numerous network devices and return the |
|  current software version every 10 seconds. If you have the        |
|  correct permissions, your domain account will be used to provide  |
|  this output. To continue, please input your domain credentials.   |
|                                                                    |
======================================================================
======================================================================
""")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    return username, password

# Function to verify credentials on a single device
def verify_credentials(hosts, cisco_router):
    try:
        cisco_router['host'] = hosts[0]
        ssh = ConnectHandler(**cisco_router)
        ssh.disconnect()
    except Exception as e:
        print("""
                         !!! 
                    !!!!!!!!!!!!!
   ************************************************   
 ***************************************************** 
***                                                 ***
***        Initial Authentication Failed            ***
***                Exiting Script                   ***
***                                                 ***
 ***************************************************** 
   ************************************************   
                    !!!!!!!!!!!!!
                         !!!
    """)
        exit()

# Function to check the device version
def check_device(host):
    try:
        log_time = datetime.datetime.now().strftime("%H:%M:%S")
        if host not in ssh_connections:
            cisco_router['host'] = host
            ssh = ConnectHandler(**cisco_router)
            ssh_connections[host] = ssh
        else:
            ssh = ssh_connections[host]
        
        version = ssh.send_command("sh ver")
        regex = r"Version\s+(.+?),"
        match = re.search(regex, version)
        current_version = match.group(1).rstrip(',')
        version_match = f"{host:<30} {current_version}"
        
        # Check if the version has changed
        if host in previous_versions:
            if previous_versions[host] != current_version:
                version_match += " ***"
                previous_versions[host] = current_version
        else:
            previous_versions[host] = current_version
        
        failed_hosts.discard(host)
        return version_match
    except Exception as error:
        error_message = "<-= Failed to connect =->"
        version_match = f"{host:<30} {error_message}"
        
        # Remove the SSH connection if it fails
        if host in ssh_connections:
            del ssh_connections[host]
        
        failed_hosts.add(host)
        return version_match

# Main function for the curses interface
def curses_main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.clear()
    
    # Get the dimensions of the window
    height, width = stdscr.getmaxyx()
    
    # Check if the window size is sufficient
    if len(hosts) + 5 > height:
        stdscr.addstr(0, 0, "Error: Not enough room to display all servers. Please expand the window size.")
        stdscr.refresh()
        time.sleep(5)  # Give the user time to read the message
        return
    
    # Check credentials on a single device
    try:
        initial_output = check_device(hosts[0])
        stdscr.addstr(3, 0, initial_output)  # Start from line 3 to leave a blank line after the spinner line
        stdscr.refresh()
    except Exception as e:
        stdscr.addstr(3, 0, """
                             !!! 
                        !!!!!!!!!!!!!
       ************************************************   
     ***************************************************** 
    ***                                                 ***
    ***        Initial Authentication Failed            ***
    ***                Exiting Script                   ***
    ***                                                 ***
     ***************************************************** 
       ************************************************   
                        !!!!!!!!!!!!!
                             !!!
        """)
        stdscr.refresh()
        log.close()
        return

    spinner = ['-', '\\', '|', '/']
    spinner_index = 0

    # Main loop to run the script every 10 seconds
    try:
        while True:
            for _ in range(10):  # Update spinner every second for 10 seconds
                stdscr.addstr(0, 0, f"Version check loop is running... {spinner[spinner_index]}")
                stdscr.addstr(1, 0, "")  # Add a blank line under the spinner line
                stdscr.refresh()
                spinner_index = (spinner_index + 1) % len(spinner)
                
                # Check for user input
                stdscr.nodelay(True)
                key = stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    stdscr.addstr(len(hosts) + 5, 0, "\nScript terminated by user.")  # Adjusted for blank line after last host
                    stdscr.refresh()
                    log.close()
                    # Close all SSH connections
                    for ssh in ssh_connections.values():
                        ssh.disconnect()
                    return
                
                time.sleep(1)
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_host = {executor.submit(check_device, host): host for host in hosts}
                for future in as_completed(future_to_host):
                    host = future_to_host[future]
                    try:
                        result = future.result()
                        line_number = hosts.index(host) + 3  # Adjusted for blank line after spinner line
                        stdscr.addstr(line_number, 0, result)
                        stdscr.clrtoeol()
                        stdscr.refresh()
                    except Exception as exc:
                        line_number = hosts.index(host) + 3  # Adjusted for blank line after spinner line
                        stdscr.addstr(line_number, 0, f'{host:<30} <-= Failed to connect =->')
                        stdscr.clrtoeol()
                        stdscr.refresh()
    except KeyboardInterrupt:
        stdscr.addstr(len(hosts) + 5, 0, "\nScript terminated by user.")  # Adjusted for blank line after last host
        stdscr.refresh()
        log.close()
        # Close all SSH connections
        for ssh in ssh_connections.values():
            ssh.disconnect()

# Global variables
previous_versions = {}
ssh_connections = {}
failed_hosts = set()
log = None
hosts = sites.targets()
cisco_router = {}

# Function to initialize global variables
def initialize_globals(username, password):
    global hosts, cisco_router
    hosts = sites.targetversions()  
    print("We will begin in 5 seconds...\nCancel Now? 'CTRL+C'\n")
    time.sleep(5)
    cisco_router = {
        'device_type': 'cisco_ios',
        'username': f'{username}',
        'password': f'{password}',
    }

def run_curses_interface():
    curses.wrapper(curses_main)

if __name__ == "__main__":
    print("Run from CiscoToolKit.py with -V option")
   """ 
    username, password = display_initial_text()
    initialize_globals(username, password)
    verify_credentials(hosts, cisco_router)
    curses.wrapper(curses_main)
    """