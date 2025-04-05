import getpass

def site():
    count = 0
    
    while count < 3:
        count += 1
        site = input("Which Site Are you downloading from?\n0: location1\n1: location2\n>> ")
        #print(type(site))
        #print(site)
        if site == "0":
            l = "lr"
            return l
        elif site == "1":
            l = "fs"
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
    
def targets():
        hosts = [
            #"core-sw-1",
            "10.200.120.2"
        ]
        return hosts
    
def targetversions():
        hosts = [
            "core-sw-1",
            "10.200.120.2"
        ]
        return hosts

if __name__ == "__main__":
    print("CiscoToolKit Module Information:\nSites.py is used by several CiscoToolKit Modules\n")