# LANquest
[Work in Progess]

A python-based, LAN-based multiplayer, text-based MUD. Made to be hosted from a Raspberry Pi or similar single-board computer, but it can be hosted from any computer, on any OS with Python installed.

# Install & usage instructions:

Make sure git and python are installed, with the websockets prerequisite for python installed.

Copy and paste the following commands:

  git clone https://github.com/cloudyskaisss/LANquest.git
  
  cd LANquest
  
  python3 ./server.py

**In another terminal:**

  python3 -m 8080

**To use the webpage:**

  Type in the following URL: https://[HOST MACHINE IP]:8080
    
  Replace [HOST_MACHINE_IP] with the local IP address of the host machine. To find this out, type in ifconfig, and look for an address like 192.168.1.1 or 10.0.0.1.
