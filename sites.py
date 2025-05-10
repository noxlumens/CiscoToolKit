import getpass
from pick import pick

def site():
    count = 0
    
    while count < 3:
        count += 1
        site = input("Which Site Are you downloading from?\n0: Site1\n1: Site2\n>> ")
        #print(type(site))
        #print(site)
        if site == "0":
            l = "site1"
            return l
        elif site == "1":
            l = "site2"
            return l
        else:
            if count == 3:
                print("You've entered a wrong location 3 times...exiting\n")
                return None
            else:
                print("Please Enter '0' or '1'.\n>> ")
    return site
                
    
def credential():
    binary = input("Enter Binary file name: ")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    return binary, username, password

def c_credential():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    return username, password
    
def targets():
        hosts = [
    "Switch1",
    #"Router1",
    "10.10.10.10"
        ]
        return hosts
    
def targetversions():
        hosts = [
    "Switch1",
    #"Router1",
    "10.10.10.10"
        ]
        return hosts

def choose_hosts():
    title = 'Pick your devices.'
    options = targets()

    options = pick(options, title, indicator='=>', default_index=0, multiselect=True)
    hosts = [host[0] for host in options]
    if hosts:
        print(hosts)
    return hosts

if __name__ == "__main__":
    print("CiscoToolKit Module Information:\nSites.py is used by several CiscoToolKit Modules\n")
