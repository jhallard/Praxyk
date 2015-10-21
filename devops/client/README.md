#### Overview
The devops_client program is a python script that wraps around the DevOps API and simplifies the task of managing virtual machines and snapshots of them. 

**Requirements**
 * Operating System - POSIX Compliant (I think, haven't actually tested on OSX yet)
 * Account - You need a username and initial password from me, you will use this to log-in the first time.
 * Python 2.7 and the requests library. You should have it by default.

#### Quick Start
Run the following commands in a terminal to get the script up and running.

```sh
curl https://raw.githubusercontent.com/jhallard/praxyk/devops/devops/client/devops_client.py > ~/.devops_client
chmod +x ~/.devops_client 
sudo ln -s ~/.devops_client /usr/bin/devops_client
mkdir -p ~/.praxykdevops/client/
devops_client setup
```

The program will now launch and will start by asking you for your username and password, enter the values I sent you. You will then be prompted to change your password, give a password that is more than 6 characters but otherwise has no restrictions. You will then be prompted to setup SSHKeys. It is highly recommended you do this now, if you can't you can always run this script later and skip the password-change step.

When setting up ssh-keys, it will first look for a key at `~/.ssh/id_rsa`. If one exists, it will ask you if you want to use this one. Choose yes if you are sure you remember the password for this key. Otherwise, you will be asked if you want to generate a new key. It is recommended that you do this, it will generate a new key pair for you (stored in `~/.ssh`) and load the public key into the DevOps database. If you don't choose either of these options, you can give the full path to an already existing key in your system for it to use.

SSHKeys are important because your public key gets uploaded to every VM that you make, which allows you to login immediately using only the password for the key. If you don't have ssh-keys set up, a root password will be emailed to my personal email and I'll have to forward it to you, which is a pain. 

**Note** - If you want to set-up your client so you can work from multiple machines, just do the setup process on the next machine and skip the password changing step. If you create a new SSH key, that one will also be uploaded to any new VMs that you create, it unfortunately will not be added to existing VMs. You can also just copy the keys over to your other compute via flash-drive and you will be able to log right in 

After you have the your ssh-key setup the script will exit and you will be set to make some virtual machines.

#### Commands

All commands have the following structure
```sh
devops_client $action [$noun]
```

Valid actions are [setup, login, create, destroy, get, update]. Valid nouns are [user, users, instance, instances, snapshot, snapshots]. A noun is required for all actions except for login and setup.

**Setup Action**

```sh
devops_client setup
```

This will walk you through the act of setting up your account, you can skip the password changing and jump right to the ssh-key setup if you want to. If you ever need to add another SSH key do it by calling setup.

**Login Action**
```sh
devops_client login
```

Calling the above command will prompt you for your username (or will auto-grab it if it is cached) and your password (never cached obviously), send this info to the server, and will get you an access token. Tokens expire every 24 hours so expect to call this once a day. The token that is returned is auto-saved in your config file so you don't have to worry about doing anything with it.


#### The Good Stuff
Now that you set up your account, changed your password, and added ssh-keys (you did add ssh-keys for your account, right? right??), you can make some VMs!

Let's start with a simple command.

```sh
devops_client get user
```

This will ask you which user you want to view (give your own username), and then will return something like this

```sh
User Shaftoe Info : 
Email : bobby@shaftoe.com 
Instances Running : 2
Instances : [5122149, 67145632]
```

The list of numbers is a list of VM instance IDs owned by that user. Let's get more information on an instance.

```sh
devops_client get instance
```
You will be prompted to select from a list of instance names, choose any one you like. After you choose, you'll see something like 

```sh
Instance Name  : the-test-server-1
Inst ID : 8123394 
Inst IP : 112.109.164.114
Inst Status : active
Inst Creator: root
Created At : 2015-10-02 21:52:12
```

**Making your first VM**

Here's how to make your first virtual machine
```sh
devops_client create instance
```

This will walk you through the steps of choosing an instance name, a VM size, a boot-image, and then will make the VM for you. Name the VM something good, not too short, include your name or initials maybe. Names cannot have underscores, only dashes. For a size, choose '2gb' to start, it's more than enough to mess around with. Save the '4gb' VMs for when we are actually doing real work in the future. For the boot-image, right now it will only show `ubuntu 14.04 x64`. This is a blank, default Ubuntu image. After people start adding custom VM snapshots, the snapshots will show up here as options. If you choose a snapshot as a boot-image, the VM you create will be an exact copy of the VM that the snapshot was taken of.

Once you have selected the above options and confirmed them, the creation process will start. This can take up to 3 minutes, so wait for it to finish. When it is done, you will get a description of the VM you just made.
Note the IP address shown in the description, if you ever lose this value just run
```sh
devops_client get instance
```
And choose your instance name to get a description of the instance including the IP.

**Logging in to the new VM**

Since you did set up ssh-keys earlier, you can log right in to your new vm. Grab the IP address of your VM, and do the following command.
```sh
ssh root@$IP_ADDRESS
```
You will be prompted for the password to your ssh key (or won't if you didn't set a password for it), after which you will see a blank prompt. Congrats, you're logged into your instance as root. You don't normally want to do this though, so start by making a user account and setting the password for it. 

Try running the following to get started 
```sh
useradd $username -m # create a user with name $username, make them a home dir at /home/$username/
sudo adduser $username sudo # add your account to the sudoers file
passwd $username # set a password for your account
su $username # change user to $username
sudo apt-get install vim tmux git build-essential inxi python-pip node nodejs npm
```

In the future, ssh into the VM by doing the following
```sh
ssh $username@IP_ADDRESS
```

#### Help
If you ever need help with the script, you can run 
```sh
devops_client -h
```

Which will output the following
```sh
$ ./devops_client.py -h
usage: devops_client.py [-h] [--root]
                        action [noun] [specifics [specifics ...]]

This script is the client-side bindings for the Praxyk DevOps API. It uses the
requests python library to wrap around the exposed API and simplify the
management of virtual machines and their images on the command line. All calls
to the API must be done with tokens, to get a token, you must log in. The
token will remain valid for about 24 hours when it will then expire requiring
you to log in again. When you get a token by using the login function, the
token will be saved in a json file in your home directory. Do not touch this
file for it is auto-managed by this script. --- Argument Descriptions ---
Actions : Actions describe what you want to do, but not what you want to do
the action to. For instance, if you want to create an instance, you would call
./devops_util create instance. If you wanted to see all of the existing
snapshots, you would call ./devops_util get snapshots. Actions are also used
to initialize a user (setup sshkeys and change the default password) by
calling ./devops_util setup. Nouns : Nouns describe what you want to apply the
action to. Nouns to not have to be submitted if you are logging in or you are
setting-up the account, otherwise one must be given. Nouns can be {user,
users, instance, instances, snapshot, snapshots} Specifics : You can sometimes
throw on arguments here to skip having to type them in at a prompt. For
instance, if getting a user's info, instead of typing `./devops_client get
user` then typing in the user name at a prompt, you can just enter
`./devops_client get user bobby_shaftoe and the users info will be returned
immediately.

positional arguments:
  action      This argument describes what action you want to take.This can be
              one of the following : {setup, login, get, create, destroy,
              update}.
  noun        This argument describes what you want to apply the action to and
              is not required if the action you submitted is 'login' or
              'setup'.Can be one of : {user[s], instance[s], snapshot[s]}
  specifics   You can throw in args that would normally be prompted for, like
              user names of instance names depending on what you are doing

optional arguments:
  -h, --help  show this help message and exit
  --root      This flag will cause the program to look for a different config
              file, one that contains a root token. If you don't have the root
              token, giving this flag will only cause everything to fail.
```
