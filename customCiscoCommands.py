import time
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.ERROR)

def device(username, password, host, commands):    
    device_template = {
        'device_type': 'cisco_ios',
        'username': username,
        'password': password,
        'host': host,
    }

    try:
        net_connect = ConnectHandler(**device_template)
        logging.info(f"{host} => Running Commands")
        print(f"{host} => Running Command => {time.strftime('%m/%d/%Y %H:%M:%S')}")
        output = []
        for command in commands:
            output.append(net_connect.send_command(command))
        net_connect.disconnect()
        return "\n".join(output)
    except Exception as e:
        logging.error(f"Exception on {host}: {e}")
        return f"Exception on {host}: {e}"

def command_multiple_devices(username, password, hosts):
    commands = []
    while True:
        user_input = input("Command: ")
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "":
            break
        commands.append(user_input)
    print(f"\n\nSending the following commands!:\n{commands}\nCancel Now? CTRL+c\nHosts: {hosts}\n\n")
    time.sleep(5)

    def run_commands_on_host(device_template, commands):
        try:
            net_connect = ConnectHandler(**device_template)
            output = []
            for command in commands:
                time.sleep(1)
                output.append(net_connect.send_command_timing(command))
            net_connect.disconnect()
            return "\n".join(output)
        except Exception as e:
            logging.error(f"Failed to connect to {device_template['host']}: {e}")
            return f"Failed to connect to {device_template['host']}: {e}"

    with ThreadPoolExecutor(max_workers=len(hosts)) as executor:
        futures = [executor.submit(run_commands_on_host, {'device_type': 'cisco_ios', 'username': username, 'password': password, 'host': host}, commands) for host in hosts]
        for index, future in enumerate(futures):
            print(f"\nHost: {hosts[index]}\n" + f"=" * 20)
            print(future.result())
            print(f"_" * 20 + "\n")

if __name__ == "__main__":
    print("This script should not run directly.")
