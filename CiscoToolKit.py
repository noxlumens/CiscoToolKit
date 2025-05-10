import argparse
import ftp_download
import GetSwitchVersion
import ciscoupgradedevice
import sites
import customCiscoCommands
import time
from preauth import authcheck
def main():
    
    parser = argparse.ArgumentParser(
        prog="CiscoToolKit.py",
        description="A group of tools for managing Domain network hardware",
        epilog="Version 1.0",
        
    )

    parser.add_argument('-d', '--download', action='store_true', help="Download the binary file used for upgrading the device.")
    parser.add_argument('-u', '--upgrade', action='store_true', help="Upgrade the Cisco Device; Binary File must already be installed")
    parser.add_argument('-V', '--versions', action='store_true', help="Show Persistent Version Information")
    parser.add_argument('-C', '--command', action='store_true', help="Run Custom Cisco Device Commands on hosts in sites.py")
    args = parser.parse_args()

    if args.upgrade:
        try:
            hosts = sites.choose_hosts()
            site = sites.site()
            binary, username, password = sites.credential()
            print(hosts)
            if not hosts:
                print("You've selected no hosts.\n\n")
                exit()
            #hosts = sites.targets()
            else:
                try:
                    authchecking = authcheck(username,password,hosts)
                    #print(authchecking)
                    if authchecking == True:
                        print("Initiating Download...\nCancel Now? 'CTRL+C'")
                        time.sleep(2)
                        ciscoupgradedevice.upgrade_multiple_devices(site,binary,username,password,hosts)
                except:
                    print("oh well goes the goose")
                    exit()
        except Exception as e:
            print(e)
    elif args.download:
        try:
            hosts = sites.choose_hosts()
            site = sites.site()
            binary, username, password = sites.credential()
            print(hosts)
            if not hosts:
                print("You've selected no hosts.\n\n")
                exit()
        #hosts = sites.targets()
            else:
                try:
                    authchecking = authcheck(username,password,hosts)
                    #print(authchecking)
                    if authchecking == True:
                        print("Initiating Download...\nCancel Now? 'CTRL+C'")
                        time.sleep(2)
                        ftp_download.download_multiple_devices(site,binary,username,password,hosts)
                except Exception as e:
                    print(f"oh well goes the goose\n{e}")
                    exit()
        except Exception as e:
            print(e)
    elif args.versions:
        username, password = GetSwitchVersion.display_initial_text()
        GetSwitchVersion.initialize_globals(username, password)
        GetSwitchVersion.verify_credentials(GetSwitchVersion.hosts, GetSwitchVersion.cisco_router)
        GetSwitchVersion.run_curses_interface()      # Assuming GetSwitchVersion has a main function to show versions
    elif args.command:
        try:
            hosts = sites.choose_hosts()
            if not hosts:
                print("You've selected no hosts.\n\n")
                exit()
        #hosts = sites.targets()
            else:
                username, password = sites.c_credential()
                print(hosts)
                try:
                    authchecking = authcheck(username,password,hosts)
                    #print(authchecking)
                    if authchecking == True:
                        print("Preparing The Command Module...\nCancel Now? 'CTRL+C'")
                        time.sleep(2)
                    customCiscoCommands.command_multiple_devices(username, password, hosts)
                except Exception as e:
                    print(f"oh well goes the goose: {e}")
                    exit()
        except Exception as e:
            print(f"An Error Occurred While trying to select devices.\n\n{e}")
            exit()

    else:
        parser.print_help()
        

main()
