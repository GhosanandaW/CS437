# commands needed to run firewall, adapted from https://www.digitalocean.com/community/questions/how-to-reset-the-firewall-on-ubuntu

sudo apt install ufw #install ufw in the system
sudo ufw allow 65432,9000/tcp #allow TCP connection for 65432 for lab2 PicarX telemetry and control and for 9000 for PicarX video streaming
sudo ufw allow from 192.168.1.0/24 #always allow connection from local
sudo ufw default allow outgoing #always allow outgoing connection 
sudo ufw allow VNC #allow VNC by default
sudo ufw allow SSH #allow SSH by default
sudo ufw allow OpenSSH #allow SSH by default
sudo ufw allow 22/tcp #allow TCP connection for SSH - Port 22
sudo ufw allow 80/tcp #allow TCP connection for HTTP - Port 80
sudo ufw allow 443/tcp #allow TCP connection for HTTPS - port 443
sudo ufw enable #enable the ufw firewall
