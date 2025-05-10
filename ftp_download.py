from netmiko import ConnectHandler
import time
from concurrent.futures import ThreadPoolExecutor
import logging

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
        logging.info(f"{host} => Searching for Binary")
        print(f"{host} => Searching for Binary => {time.strftime('%m/%d/%Y %H:%M:%S')}")

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
                    logging.info(f"{host} => Cleaned Up Unused Files")
                    print(f"{host} => Cleaned Up Unused Files => {time.strftime('%m/%d/%Y %H:%M:%S')}")
                    break
            logging.info(f"{host} => Downloading")
            print(f"{host} => Downloading => {time.strftime('%m/%d/%Y %H:%M:%S')}")
            output = net_connect.send_command_timing(f"copy ftp://{site}ftp/{binary} flash:/{binary}", strip_prompt=False, strip_command=False, read_timeout=0)

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
                    logging.info(f"{host} => Download Successful => {binary}")
                    print(f"{host} => Download Successful => {binary} => {time.strftime('%m/%d/%Y %H:%M:%S')}")
                    net_connect.send_command_timing("copy running-config startup-config",read_timeout=0)
        else:
            logging.warning(f"{host} => Binary Exists")
            print(f"{host} => Binary Exists => {time.strftime('%m/%d/%Y %H:%M:%S')}")
            return True

    except Exception as e:
        logging.error(f"{host} => {e} => {time.strftime('%m/%d/%Y %H:%M:%S')}")
        print(f"Exception on {host}: {e}")

def download_multiple_devices(site, binary, username, password, hosts):
    logging.basicConfig(filename=f"{time.strftime('Maintenance_%m-%d-%Y_%H-%M-%S')}", filemode='w', format='%(asctime)s => ', level=logging.INFO)
    with ThreadPoolExecutor(max_workers=len(hosts)) as executor:
        futures = [executor.submit(ftp_downloading, site, binary, username, password, host) for host in hosts]
        for future in futures:
            future.result()

if __name__ == "__main__":
    print("CiscoToolKit Module Information:\nftp_download is a module for the CiscoToolKit application and should be run with the following:\npython CiscoToolKit.py -d\n")
