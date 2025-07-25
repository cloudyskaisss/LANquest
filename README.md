# LANquest
[Work in Progess]

A python-based, LAN-based multiplayer, text-based MUD. Made to be hosted from a Raspberry Pi or similar single-board computer, but it can be hosted from any computer, on any OS with wifi and with Python installed.

# Install & usage instructions:

**Linux:**

  To install prerequisites:
  
    sudo apt install python3 --scope machine

    pip install websockets

    pip install cryptography


**Windows:**
  To install prerequisites:

    Install Python3 from Microsoft store by typing "python" without it installed.

    pip install websockets

    pip install cryptography


**All Machines:**

  Copy and paste the following commands:
  
    git clone https://github.com/cloudyskaisss/LANquest.git
    
    cd LANquest

  **IN SERVER.PY, CHANGE [YOUR IP ADDRESS CHANGE THIS] TO YOUR HOST MACHINE'S IP ADDRESS**

    python3 server.py

  _In another terminal:_

    python3 -m http.server 80


  If _pip install websockets_ gives an error saying you need to use a venv, use the following commands instead:
    
    git clone https://github.com/cloudyskaisss/LANquest.git
    
    cd LANquest

    python3 -m venv venv

    ./venv/bin/pip install websockets

    ./venv/bin/python3 server.py

  _In another terminal:_

    ./venv/bin/python3 -m http.server 80






**To use the webpage:**

  Type in the following URL: http://[HOST MACHINE IP]
    
  Replace [HOST_MACHINE_IP] with the local IP address of the host machine. To find this out, type in ifconfig (linux) or ipconfig (windows), and look for an address like 192.168.1.1 or 10.0.0.1.
