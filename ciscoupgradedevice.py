import ftp_download
import time
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor



def upgrade_device(site,binary,username,password,host):    
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
        print(f"{host} - Start Time -  {time.strftime('%m/%d/%Y %H:%M:%S')}")

        # Check if the binary file exists on the switch
        bin_check = net_connect.send_command(f"dir flash: | include {binary}")

        if binary not in bin_check:
            ftp_download.ftp_downloading(site,binary,username,password,host)  # Call the correct function from ftp_download module
            print(f"{host} - Download Complete - {time.strftime('%m/%d/%Y %H:%M:%S')}")
            #net_connect.send_command("copy running-config startup-config",read_timeout=30)
            print(f"{host} - Upgrading - {time.strftime('%m/%d/%Y %H:%M:%S')}")
            output = net_connect.send_command_timing(f"install add file flash:{binary} activate commit prompt-level none", strip_prompt=False, strip_command=False, read_timeout=0)
            #print(output)
            #print(net_connect.read_channel())
            counter = 0
            while 'SUCCESS: install_add_activate_commit' not in output and counter < 100:
                time.sleep(10)
                if 'This operation may require a reload of the system. Do you want to proceed?' in output:
                    print(output)
                    output += net_connect.send_command_timing('y\n', read_timeout=0)
                output += net_connect.read_channel()
                counter += 1
                if 'SUCCESS: install_add_activate_commit' in output:
                    print(f"{host} - Rebooting - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                    break
                if f'install_engine: Failed to install_add_activate_commit package flash:{binary}, Error: FAILED: install_add exit(1)' in output:
                    print(f"!!!!!!\nFAILURE-{host}-install_engine: Failed to install_add_activate_commit package flash:{binary}, Error: FAILED: install_add exit(1)-{time.strftime('%m/%d/%Y %H:%M:%S')}\n!!!!!!\n\n")
                    break
                if 'Failed to install add_activate_commit' in output:
                    print(f"{host} - Failed to install add_activate_commit - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                    output = net_connect.send_command_timing(f"install add file flash:{binary} activate commit prompt-level none", strip_prompt=False, strip_command=False, read_timeout=0)
                    break
#                print(f"{host} - Download Completed - {time.strftime('%m/%d/%Y %H:%M:%S')}\n")
#                print(f"{host} - Upgrade Failed - {time.strftime('%m/%d/%Y %H:%M:%S')}\n")
        elif binary in bin_check:
            #net_connect.send_command_timing("copy running-config startup-config", strip_command=False, strip_prompt=False,read_timeout=0)
            output = net_connect.send_command_timing(f"install add file flash:{binary} activate commit prompt-level none", strip_prompt=False, strip_command=False, read_timeout=0)
            #print(output)
            print(f"{host} - Upgrading - {time.strftime('%m/%d/%Y %H:%M:%S')}")
            #print(net_connect.read_channel())
            # Handle interactive prompts
            counter = 0
            while 'SUCCESS: install_add_activate_commit' not in output and counter < 100:
                time.sleep(10)
                if 'This operation may require a reload of the system. Do you want to proceed?' in output:
                    print(output)
                    output += net_connect.send_command_timing('y\n', read_timeout=0)
                output += net_connect.read_channel()
                counter += 1
                if 'SUCCESS: install_add_activate_commit' in output:
                    print(f"{host} - Rebooting - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                    break
                if f'install_engine: Failed to install_add_activate_commit package flash:{binary}, Error: FAILED: install_add exit(1)' in output:
                    print(f"!!!!!!\nFAILURE-{host}-install_engine: Failed to install_add_activate_commit package flash:{binary}, Error: FAILED: install_add exit(1)-{time.strftime('%m/%d/%Y %H:%M:%S')}\n!!!!!!\n\n")
                    break
                if 'Failed to install add_activate_commit' in output:
                    print(f"{host} - Failed to install add_activate_commit - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                    output += net_connect.send_command_timing(f"reload", strip_prompt=False, strip_command=False, read_timeout=0)
                    if 'Proceed with reload? [confirm]' in output:
                        print(f"{host} - Attempting to reload and will try again - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                        output += net_connect.send_command_timing('y\n', read_timeout=0)
                        print(f"{host} - Available Space Less than required for upgrade REBOOTING NOW - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                        output = net_connect.send_command_timing(f"install add file flash:{binary} activate commit prompt-level none", strip_prompt=False, strip_command=False, read_timeout=0)
                    else:
                        print(f"{host} - Attempting to Commit Again - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                        output += net_connect.send_command_timing(f"install add file flash:{binary} activate commit prompt-level none", strip_prompt=False, strip_command=False, read_timeout=0)
                        if 'SUCCESS: install_add_activate_commit' in output:
                            print(f"{host} - Rebooting - {time.strftime('%m/%d/%Y %H:%M:%S')}")
                        if f'install_engine: Failed to install_add_activate_commit package flash:{binary}, Error: FAILED: install_add exit(1)' in output:
                            print(f"!!!!!!\nFAILURE-{host}-install_engine: Failed to install_add_activate_commit package flash:{binary}, Error: FAILED: install_add exit(1)-{time.strftime('%m/%d/%Y %H:%M:%S')}\n!!!!!!\n\n")
                            break
        else:
            print(f"{binary} failed to install on {host}.")

    except Exception as e:
        print(f"Exception on {host}: {e}")

def upgrade_multiple_devices(site, binary, username, password, hosts):
    with ThreadPoolExecutor(max_workers=len(hosts)) as executor:
        futures = [executor.submit(upgrade_device, site, binary, username, password, host) for host in hosts]
        for future in futures:
            future.result()


if __name__ == "__main__":
    print("Script should only run from CiscoToolKit.")
