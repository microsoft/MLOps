# Setting up VSCode Remote to Azure ML

## 0. Prerequisite (Windows only)
Install an OpenSSH compatible SSH client (https://code.visualstudio.com/docs/remote/troubleshooting#_installing-a-supported-ssh-client) if one is not already present.
Note: PuTTY is not supported on Windows since the ssh command must be in the path.

## (Optional) Create SSH config file with a script

1. Download the [script](https://github.com/danielsc/azureml-debug-training/blob/master/src/create_ssh_config.py) and run the script on your local machine with `python create_ssh_config.py`
2. For your **IP Address**: 
    -  Find VM in https://ml.azure.com/, Click **Compute** and Click the VM you want the SSH into. You should see a page with the title "Compute Details" with all your VM details.
    -  Click the link under "Resource ID" for that VM 
    ![](img/vm_ipaddress.png)
    -  Copy the "Public IP address" (your IP Address value)
    -  Paste value in the terminal
3. For your **Private Key**: 
    -  Find VM in https://ml.azure.com/, Click **Compute** and Click the VM you want the SSH into. You should see a page with the title "Compute Details" with all your VM details.
    ![](img/vm_ssh_config_ws2.png)
    -  Copy the RSA Key "Private key" for that VM 
    -  Paste value in the terminal
    -  Press `Ctrl+z` and Enter(Windows) or `Ctrl+d` and Enter(Mac/Linux) to confirm Private Key
3. Skip to the **Install VS Code and connect to the Notebook VM** section of this document. Your VM should appear in VSCode with the IP     address as the name.

## 1. Save the Notebook VM access information
In the AzureML Workspace in the Azure Portal, go to configuration page of the compute target associated with your Notebook VM and find the IP Adress, ssh port, and ssh private key at the bottom: 
![](img/vm_ssh_config_ws2.png)

Save private key to the ~/.ssh/ directory on your local computer; for instance open an editor for a new file and paste the key in:

Linux:

    vi ~/.ssh/id_mynotebookvm_rsa 

Windows:

    notepad C:\Users\<username>\.ssh\id_mynotebookvm_rsa

The private key will look something like this:
    
    -----BEGIN RSA PRIVATE KEY-----
    KEY
    .....
    KEY==
    -----END RSA PRIVATE KEY-----

Change permissions on file to make sure only you can read the file (not sure if this is needed on Windows)

    chmod 600 ~/.ssh/id_mynotebookvm_rsa  

## 2. Add the Notebook VM as a host
Open the file ~/.ssh/config (C:\Users\<username>\.ssh\config on Windows) in an editor and add a new entry:

    Host mynotebookvm
        HostName 13.69.56.51
        Port 22
        User azureuser
        IdentityFile ~/.ssh/id_mynotebookvm_rsa  
   
Here some details on the fields:

- `Host`: use whatever shorthand you like for the VM
- `HostName`: This is the IP address of the VM pulled from the above configuration page
- `Port`: This is the port shown on the above configuration page.
- `User`: this needs to be `azureuser`
- `IdentityFile`: should point to the file where you saved the privat key

Now you should be able to ssh to your Notebook VM using the shorthand you used above.

```
    MININT-LI90F99:git username$ ssh mynotebookvm
    Welcome to Ubuntu 16.04.6 LTS (GNU/Linux 4.15.0-1041-azure x86_64)

    94 packages can be updated.
    0 updates are security updates.

...

    Last login: Sun Jun 16 18:03:28 2019 from 172.58.43.244
    azureuser@danielsctestc7e12521ac:~$ 
```

## 3. Install VS Code and connect to the Notebook VM
Next install VS Code from here: https://code.visualstudio.com/ and then install the Remote SSH Extension from here: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh.

Now, click on the Remote-SSH icon on the left to show your SSH configurations, then right-click on the SSH host configuration you just created, and select 'Connect to Host in current Window'.

From here on, you are entirely working on the Notebook VM and you can now edit, debug, use git, use extensions, etc. -- just like you can with your local VSCode.

Have fun!
