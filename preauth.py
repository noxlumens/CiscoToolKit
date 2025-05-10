from netmiko import ConnectHandler
from sites import targets

def authcheck(username,password,hosts):
    # Define the device details template
    device_template = {
        'device_type': 'cisco_ios',
        'username': username,
        'password': password,
    }
    try:
        device = device_template.copy()
        device['host'] = hosts[0]
        output = ""
        ssh = ConnectHandler(**device)
        ssh.disconnect()
        return True
    except Exception as e:
        print("""
        ==================================================== 
       ===         Initial Authentication Failed          ===
       ===                 Exiting Script                 ===
        ====================================================   
        """)
        print(f"{e}")
        exit()
        return False

if __name__ == "__main__":
    print("Authentication Detection happens at the beginning of the CiscoToolKit.")
