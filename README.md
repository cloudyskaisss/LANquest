# LANquest
[Work in Progess]

A python-based, LAN-based multiplayer, text-based MUD. Made to be hosted from a Raspberry Pi or similar single-board computer, but it can be hosted from any computer, on any OS with Python installed.

# Install & usage instructions:

**Linux:**
  
  Copy and paste the following commands:
  
    git clone https://github.com/cloudyskaisss/LANquest.git
    
    cd LANquest
    
    ./install
  
    ./serve


**Windows:**
  **Make sure git and python are installed.**
  
  Copy and paste the following commands:

    Terminal 1:
      pip install websockets
      
      git clone https://github.com/cloudyskaisss/LANquest.git
      
      cd LANquest

      python3 server.py
      
      
    Terminal 2:
      
      python3 -m http.server 80


**To use the webpage:**

  Type in the following URL: http://[HOST MACHINE IP]
    
  Replace [HOST_MACHINE_IP] with the local IP address of the host machine. To find this out, type in ifconfig (linux) or ipconfig (windows), and look for an address like 192.168.1.1 or 10.0.0.1.
