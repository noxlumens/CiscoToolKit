from netmiko import ConnectHandler
import time

def ftp_downloading(site,binary,username,password,host):
    # Define the device details template
    device_template = {
        'device_type': 'cisco_ios',
        'username': username,
        'password': password,
    }
    device = device_template.copy()
    device['host'] = host
    output = ""
    try:
        net_connect = ConnectHandler(**device)
        print(f"Checking for the binary file on {host}...")

        # Check if the binary file exists on the switch
        bin_check = net_connect.send_command(f"dir flash: | include {binary}")
        time.sleep(1)

        if binary not in bin_check:
            #print(f"{binary} not found on {host}. Starting download from FTP server...")
            output = net_connect.send_command_timing("install remove inactive")
            while 'SUCCESS: install_remove' not in output:
                time.sleep(5)
                if 'Do you want to remove the above files?' in output:
                    output += net_connect.send_command_timing('y\n', read_timeout=0)
                output += net_connect.read_channel()
                if 'SUCCESS: install_remove' in output:
                    print(f"Unnecessary package files cleaned up for {host}...")
                    break
            print(f"{host} - Downloading - {time.strftime('%m/%d/%Y %H:%M:%S')}")
            output = net_connect.send_command_timing(f"copy ftp://{site}dhcp1/{binary} flash:/{binary}", strip_prompt=False, strip_command=False, read_timeout=0)
            # Handle interactive prompts
            counter = 0
            while 'bytes copied' not in output and counter < 100:
                time.sleep(10)
                if 'Address or name of remote host' in output:
                    output += net_connect.send_command_timing('\n', read_timeout=0)
                if 'Source filename' in output:
                    output += net_connect.send_command_timing('\n', read_timeout=0)
                if 'Destination filename' in output:
                    output += net_connect.send_command_timing('\n', read_timeout=0)
                output += net_connect.read_channel()
                counter += 1
                if 'No such file or directory' in output:
                    print("The file does not exist")
                    break
                if 'bytes copied' in output:
                    print(f"{host} - Download Successful - {binary}")
                    net_connect.send_command_timing("copy running-config startup-config",read_timeout=0)
        else:
            return True

    except Exception as e:
        print(f"Exception on {host}: {e}")

if __name__ == "__main__":
    print("CiscoToolKit Module Information:\nftp_download is a module for the CiscoToolKit application and should be run with the following:\npython CiscoToolKit.py -d\n")