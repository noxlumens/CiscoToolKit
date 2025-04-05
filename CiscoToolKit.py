import argparse
from ftp_download import ftp_downloading
import GetSwitchVersion
import ciscoupgradedevice
import sites
import time

def main():
    
    parser = argparse.ArgumentParser(
        prog="CiscoToolKit",
        description="A group of tools for managing Cisco network hardware",
        epilog="Version 0.1"
    )

    parser.add_argument('-d', '--download', action='store_true', help="Download the binary file used for upgrading the device.")
    parser.add_argument('-u', '--upgrade', action='store_true', help="Upgrade the Cisco Device; Binary File must already be installed")
    parser.add_argument('-A', '--letsdoitlive', action='store_true', help="Do IT ALL; download, upgrade, show version currently not working")
    parser.add_argument('-V', '--versions', action='store_true', help="Show Persistent Version Information")
    args = parser.parse_args()

    if args.upgrade:
        hosts = sites.targets()
        site = sites.site()
        print(hosts)
        print("Upgrade\nCancel Now? 'CTRL+C'")
        binary, username, password = sites.credential()
        ciscoupgradedevice.upgrade_multiple_devices(site,binary,username,password,hosts)
    elif args.download:
        hosts = sites.targets()
        site = sites.site()
        binary, username, password = sites.credential()
        print(hosts)
        print("Download\nCancel Now? 'CTRL+C'")
        time.sleep(3)
        for host in hosts:
            ftp_downloading(site,binary,username,password,host)
    elif args.versions:
        username, password = GetSwitchVersion.display_initial_text()
        GetSwitchVersion.initialize_globals(username, password)
        GetSwitchVersion.verify_credentials(GetSwitchVersion.hosts, GetSwitchVersion.cisco_router)
        GetSwitchVersion.run_curses_interface()
    elif args.letsdoitlive:
        print(hosts)
        print("LETS DO IT LIVE!\nCancel Now? 'CTRL+C'")
        time.sleep(3)
        ciscoupgradedevice.upgrade_multiple_devices(site,binary,username,password,hosts)
    else:
        parser.print_help()
        

main()