import netmiko
import getpass
from netmiko import ConnectHandler
# This file needs to have the IPs of the devices you're running the
# script against.
devicefile = "voipswitches.txt"
# Prompt for cisco login information.
username = getpass.getpass("What is your Username? ")
password = getpass.getpass("What is your password? ")
secret = getpass.getpass("What is the enable password?")

if __name__ == '__main__':
 # Open devicefile, and save into variable devices 
 f1 = open(devicefile,"r")
 devices = f1.readlines()
 # Open file where output of the program will be stored
 results = open("intconfig_output.txt", "w")
 # Loop through device file for each device
 for device in devices:
  device = device.rstrip()
  # Add device info into output file.
  results.write("\n\nFor device: "+device+"\n")
  # Create netmiko object with appropriate parameters
  ciscodevice = {
   'device_type':'cisco_ios',
   'ip':device,
   'username':username,
   'password':password,
   'secret':secret,
   }
  net_connect = ConnectHandler(**ciscodevice)
  # Let user know which device the session is with
  print("Interactive SSH session established to " + device)
  # Send the int status command
  net_connect.enable()
  net_connect.config_mode()
  # Store basic configs in globalcommand variable 
  globalcommand = ["lldp run", "network-policy profile 126", "voice vlan 211"]
  #  Send globalcommand
  net_connect.send_config_set(globalcommand)
  #  Send show int status command, and store results to sipb
  sipb = net_connect.send_command("show int status")
  # Split the lines of sipb.
  lines = sipb.splitlines()
  # initiate 2 lists.
  trunk_lines = []
  no_trunk_lines = []
  # Loop through each of the objects in lines
  for line in lines:
   # If the word trunk is not present, add to the list of non trunks
   if 'trunk' not in line:
    no_trunk_lines.append(line)
   # If not, it means trunk is present.  Add to list of trunks.
   else:
    trunk_lines.append(line)

  #---OLD CODE---
  #results.write("Here are the non-trunk ports")
  #results.write(str(no_trunk_lines))
  #results.write("Here are the trunk ports")
  #results.write(str(trunk_lines))
  #---Old Code---

  #  Trunk Logic!!!
  #separates the ouput with a comma for every space in the ouput
  #and then grabs the interface
  trunk_list = []
  trunk_lines_string = str(trunk_lines)
  trunkwords = trunk_lines_string.split()
  # results.write(trunk_lines_string)
  
  # Go through trunkwords, get rid of "'" and "["
  for trunkword in trunkwords:
   trunkword = trunkword.replace("'", "")
   trunkword = trunkword.replace("[", "")
   #results.write(trunkword)
   #  Filter for Fa and Gi (remove VLAN interfaces)
   #  & Add to trunk_list
   if 'Fa' in trunkword or 'Gi' in trunkword:
    trunk_list.append(trunkword)
  results.write(str(trunk_list))

  #  Interface Logic!!!
  #  Logic here is repeated, this time for non trunk interfaces
  interface_list = []
  no_trunk_lines_string = str(no_trunk_lines)
  words = no_trunk_lines_string.split()
  for word in words:
   word = word.replace("'", "")
   word = word.replace("[", "")
   if 'Fa' in word or 'Gi' in word:
    interface_list.append(word)
  results.write(str(interface_list))

# -- Old testing code --
#  print(net_connect.find_prompt())
# enters in VoIP config for every access interface
#  for trunk in trunk_list:
#   print("Allowing VoIP Vlan on " + trunk + ".")
#   trunkcommands = ["int " + trunk, "switchport trunk allow vlan add 211-214"]
#   net_connect.send_config_set(trunkcommands)
# -- Old testing code --

  # Cycle through interface list, and add voip configuration
  for interface in interface_list:
   print("Configuring " + interface + " for VoIP.")
   #  Define commands to send
   intcommands = ["int " + interface, "network-policy 126"]
   #  Send commands
   net_connect.send_config_set(intcommands)
  print("Completed changes for " + device + ".")
  net_connect.disconnect()
#f1.close()
results.close()

