https://stackoverflow.com/questions/9270734/ssh-permissions-are-too-open

#from lm5050
Windows 10 ssh into Ubuntu EC2 “permissions are too open” error on AWS

I had this issue trying to ssh into an Ubuntu EC2 instance using the .pem file from AWS.

In windows this worked when I put this key in a folder created under the .ssh folder

C:\Users\USERNAME\.ssh\private_key
To change permission settings in Windows 10 :

File Settings > Security > Advanced

Disable inheritance

Convert Inherited Permissions Into Explicit Permissions

Remove all the permission entries except for Administrators

Could then connect securely.

# Connect MQTT Client Devices to AWS IoT Greengrass V2
## Good reference by Michael:
https://www.youtube.com/watch?v=tN0DQlQy2kM&ab_channel=Michael