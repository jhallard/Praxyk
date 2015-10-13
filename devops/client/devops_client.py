#!/usr/bin/python
import requests
import sys, os
import argparse
import datetime
import json
import getpass
import subprocess

from os.path import expanduser

global CONFIG_DIR 
global CLIENT_CONFIG_FILE

CONFIG_DIR = str(expanduser("~"))+'/.praxykdevops/client/'
CLIENT_CONFIG_FILE = CONFIG_DIR + 'config'

ACTIONS = ['setup', 'login', 'create', 'update', 'get', 'destroy']
NOUNS = ['instance', 'instances', 'snapshot', 'snapshots', 'user', 'users']


# BASE_URL = 'http://127.0.0.1:5000/'
BASE_URL = 'http://devops.praxyk.com:5000/'
TOKENS_URL =  BASE_URL+'tokens/'
COMPUTE_URL = BASE_URL+'compute/'
SNAPSHOTS_URL = BASE_URL+'snapshots/'
USERS_URL = BASE_URL+'users/'
SSHKEYS_URL = BASE_URL+'sshkeys/'

DESCRIPTION = """
This script is the client-side bindings for the Praxyk DevOps API. It uses the requests python
library to wrap around the exposed API and simplify the management of virtual machines and their
images on the command line.
All calls to the API must be done with tokens, to get a token, you must log in. The token will
remain valid for about 24 hours when it will then expire requiring you to log in again.
When you get a token by using the login function, the token will be saved in a json file in your home
directory. Do not touch this file for it is auto-managed by this script.
--- Argument Descriptions ---
Actions : Actions describe what you want to do, but not what you want to do the action to. For instance, if
you want to create an instance, you would call ./devops_util create instance. If you wanted to see all of the
existing snapshots, you would call ./devops_util get snapshots. Actions are also used to initialize a user (setup
sshkeys and change the default password) by calling ./devops_util setup. 
Nouns : Nouns describe what you want to apply the action to. Nouns to not have to be submitted if you are logging in
or you are setting-up the account, otherwise one must be given. Nouns can be {user, users, instance, instances, snapshot, snapshots}
Specifics : You can sometimes throw on arguments here to skip having to type them in at a prompt. For instance, if getting a user's info,
instead of typing `./devops_client get user` then typing in the user name at a prompt, you can just enter `./devops_client get user bobby_shaftoe
and the users info will be returned immediately.
"""

# @info - parse command line args into useable dictionary
#         right now we only take a config file as an argument
def parse_args(argv) :
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--root', action='store_true',  help="This flag will cause the program to look for a different config file, one that contains " +\
                                       "a root token. If you don't have the root token, giving this flag will only cause everything to fail.")
    parser.add_argument('action', help="This argument describes what action you want to take." +\
                                       "This can be one of the following : {setup, login, get, create, destroy, update}.")
    parser.add_argument('noun',  nargs='?', default="", help="This argument describes what you want to apply the action to "+\
                                                        " and is not required if the action you submitted is 'login' or 'setup'." +\
                                                        "Can be one of : {user[s], instance[s], snapshot[s]}")

    parser.add_argument('specifics',  nargs='*', default=None, help="You can throw in args that would normally be prompted for, like user names of instance names " +\
                                                             "depending on what you are doing")
    return parser.parse_args()

def get_input(desc, default=None) :
    desc = desc + ("" if not default else " default : (%s)" % str(default))
    print desc
    inp = sys.stdin.readline().strip()
    inp = inp if inp else default
    while not inp :
        inp = sys.stdin.readline().strip()
    return inp


def get_passwd(desc = None) :
    inp = ""
    while not inp :
        inp = getpass.getpass(desc).strip()
    return inp

def get_input_choices(desc, choices) :
    print desc + " : "
    # print "Select One of the Following (by number) : "
    count = 1
    for x in choices :
        print str(count) + ".)  " + str(x)
        count += 1

    inp = None 
    while not inp or not inp.isdigit() or (int(inp) <= 0 or int(inp) > len(choices)) :
        inp = sys.stdin.readline().strip()
        if not inp or not inp.isdigit() or (int(inp) <= 0 or int(inp) > len(choices)) :
            print "Incorrect Choice. Select Again."
    
    return int(inp)-1

# @info - gets a yes/no input from the user, returns true if user chose yes
#         else returns false
def get_yes_no(desc) :
    inp = ""
    print desc + " (Y/n)"
    while inp not in ['y', 'Y', 'n', 'N', 'yes', 'Yes', 'No', 'no'] :
        inp = sys.stdin.readline().strip()

    return inp in ['y', 'Y', 'yes', 'Yes']

# @info - looks at the raw response and prints relevant error messages if necessary
def check_return(r) :
    if not r or not r.text :
        if "404" in r.text :
            sys.stderr.write("Content Not Found. Double check all content-IDs are correct (username, instance id, etc).\n")
        elif "401" in r.text :
            sys.stderr.write("Request Could not be Authorized. If you haven't logged in today, do so. If error persists, contact John.\n")
        elif "500" in r.text :
            sys.stderr.write("The Server had a Hiccup, do you mind forwarding this stack trace to John?\n")
            sys.stderr.write(str(80*'-'+'\n'+r.text+80*'-'+'\n'))
        else :
            sys.stderr.write("Request Could not be Fufilled.\nDetails : %s\n"%r.text)
        return False
    else :
        return True


# @info - grabs the user's current token and username from a local file and return it to be used.
def load_auth_info() :
    if not os.path.isfile(CLIENT_CONFIG_FILE) :
        return {}
    with open(CLIENT_CONFIG_FILE) as fh :
        config_data = json.load(fh)
        return config_data
    return {}


# @info - actually performs the system call to generate  a new ssh key, returns the file name
def gen_ssh_key() :
    data = load_auth_info()
    keyname = get_input("Select a Keyname", "praxyk_%s_key"%data['username'])
    keyfile = os.path.expanduser("~")+"/.ssh/"+keyname
    try :
        subprocess.call(['ssh-keygen', '-f', keyfile])
        subprocess.call(['eval', '$(ssh-agent)'])
        subprocess.call(['ssh-add', keyname])
    except Exception, e :
        pass
    print "Key generation complete. New key : (%s)"%keyfile
    return keyfile


# @info - this will walk the user through the process of creating a new sshkey if they don't have a default one
#         or taking the one they already have and adding it the database through the api for their account.
def setup_ssh_keys() :
    data = load_auth_info()
    if not data :
        sys.stderr.write("Must be logged in (have active token) to setup ssh keys.\n")
        return False

    keyfile = ""
    default_keyfile = os.path.expanduser("~")+"/.ssh/id_rsa"

    if os.path.isfile(default_keyfile) :
        qstr = "You have an existing SSH Key (~/.ssh/id_rsa), would you like to use it? \n" +\
               "Only select this if you remember the password for this key."
        if get_yes_no(qstr) :
            keyfile = default_keyfile

    if not keyfile :
        if get_yes_no("Would you like to generate a new SSH key?") :
            keyfile = gen_ssh_key()
        else :
            if get_yes_no("Is there an existing SSH-key you would like to use?") :
                keyfile = get_input("Enter the path to the ssh key (the private key).")
                if not os.path.isfile(keyfile) :
                    sys.stderr.write("That doesn't seem to be a path to a valid key, double-check and try again.\n")
                    return False
            else :
                sys.stderr.write("Well you need to either give me an existing key or generate a new one. Try again.\n")
                return False
    
    if not keyfile or not os.path.isfile(keyfile) or not os.path.isfile(keyfile+".pub") :
        sys.stderr.write("Something went wrong, keyfile still doesn't exist. Did you login okay?\n")
        return False
    
    with open(keyfile+".pub") as fh :
        pubkey_text = fh.read()
    
    keyname = get_input("Select a DB-name for this key", "praxyk_%s_key"%data['username'])
    
    payload = {'token' : data['token'],
               'username' : data['username'],
                'key_name' : keyname,
                'pubkey_text' : pubkey_text,
                'fingerprint' : ''}

    headers = {'content-type': 'application/json'}
    r = requests.post(SSHKEYS_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)
    
    if not response.get('code') == 200 :
        sys.stderr.write("Bad return code from server. Try again.\n")
        return False
    
    key = response.get('key')
    
    print """SSH Key Added Successfully. When you login to VM's in the future, give the password for the sshkey."""
    print """Key details : user (%s)   keyname (%s)   keyid (%s) """ % (key['username'], key['name'], key['keyid'])
    return response

    
    
    

# @info - this logs the user into the API service by submitting their username and password in return for a temporary access
#         token. This token is stored in a hidden directory and can be loaded automatically when the user makes future requests.
def login_client() :
    config = load_auth_info()
    user = None
    if config.get('username', None) :
        username = config['username']
        if get_yes_no("Username %s detected, would you like to use it?"%username) :
            user = username
    if not user :
        user = get_input("Please enter your username")

    password = get_passwd("Enter the password for your DevOps Account : ")

    if not password :
        sys.stderr.write("Invalid Password Entry")
        sys.exit(1)

    payload = {'username' : user, 'password' : password}
    headers = {'content-type': 'application/json'}
    r = requests.post(TOKENS_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if response['username'] and response['token'] :
        with open(CLIENT_CONFIG_FILE, 'wr+') as fh :
            json.dump(response, fh)

    print "Successfully Logged-in as %s" %response['username']

    return response

# @info - change the users password by using a token and sending a path request to the users url.
def change_password(user=None) :
    data = load_auth_info()
    if not data or not data.get('token') :
        print "You must have a valid token in order to change your password"
        if get_yes_no("would you like to login now and retrieve a token before changing your password?") :
            login_client()
        else :
            sys.stderr.write("You must retrieve a token before changing passwords, or contact sysadmin.")
            return False
    
    data = load_auth_info()
    if not data or not data.get('token')  :
        sys.stderr.write("Failed to login, try again.")
        return False

    username = user if user else data.get('username') # if a username is passed in, use it else use the one
                                                      # associated with the token
    token = data.get('token')

    newpasswd = "1"
    newpasswd2 = "2"
    while newpasswd != newpasswd2:
        newpasswd  = get_passwd("Enter the new password for your account (%s) :"%username)
        newpasswd2 = get_passwd("Confirm the new password for your account (%s) :"%username)
        if newpasswd != newpasswd2 :
            sys.stderr.write("Passwords don't match, try again.\n")
        elif len(newpasswd) < 6 :
            sys.stderr.write("Password must be 6 or more characters..\n")
            newpasswd = "1" 
            newpasswd2 = "2"

    payload = {'token' : token, 'password' : newpasswd}
    headers = {'content-type': 'application/json'}
    r = requests.put(USERS_URL+username, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)
    
    print "Password Changed Succesfully.\n Username : %s \n Email : %s" % (response['username'], response['email'])
    return True

# @info - helper function to let a user change their email address
def change_email(user=None) :
    data = load_auth_info()
    if not data or not data.get('token') :
        print "You must have a valid token in order to change your email"
        return False

    username = user if user else data.get('username') 
    token = data.get('token')

    email = get_input("Enter the new email address for (%s)"%username)
    if not email or not email.split('@') or len(email) >= 100 :
        sys.stderr.write("Invalid input for email address")
        return False
    
    payload = {'token' : token, 'email' : email}
    headers = {'content-type': 'application/json'}
    r = requests.put(USERS_URL+username, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)
    
    print "Email Changed Succesfully.\n Username : %s \n Email : %s" % (response['username'], response['email'])
    return True
    

# @info - walks a new user through the process of logging into their account, changing the
#         existing default password, getting their first token, and setting up their sshkey.
def setup_client(argv=None) :
    print "You will now set up your DevOps Client Account."
    print "Start by logging in with your existing username and password."
    res = login_client()
    
    if not res or not load_auth_info() :
        sys.stderr.write("Something went wrong, your token and username aren't saved.\n Try again or report to sysadmin.\n")
        return False
    
    if get_yes_no("Now that you have logged in and aquired a token, would you like to change your password?") :
        res = change_password()
    
    if get_yes_no("Finally, would you like to setup SSH-keys? Without them you won't be able to access VM's you create.") :
        res = setup_ssh_keys()
    
    print "Setup Process Complete : You now have a valid token and can create virtual-machines." 
    print "Tokens expire every 24 hours"
    print "If you get errors with a code 401, call\n`devops_client login`\nto obtain another token." 
    sys.exit(0)


# @info - can only be run by root user, this function walks the caller through the steps of adding a new user
#         to the devops system.
def create_user(argv=None) :
    data = load_auth_info()
    token = data['token']
    
    username = get_input("Select a name for the new user")
    email = get_input("Enter an email for the new user") 
    password = get_passwd("Enter a default password for the new user : ")
    password2 = get_passwd("Confirm the default password for the new user : ")
    
    if password != password2 :
        sys.stderr.write("Passwords don't match, try again.\n")
        return False
    
    auth = get_input_choices("Select an Auth Level for the new user (2 is root)", ['0', '1', '2'])
    auth = int(auth)

    payload = {'name' : username, 'email' : email, 'password' : password, 'auth' : auth, 'token' : token}
    headers = {'content-type': 'application/json'}
    
    print "New User : Username (%s)  Email (%s)  Passwd (%s)  Auth (%s)"%(username, email, password, auth)
    if not get_yes_no("Confirm this information is correct.") :
        sys.stderr.write("User Creation Canceled, exiting.\n")
        return False

    r = requests.post(USERS_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)
    
    print "User (%s) Created Successfully." % (response['username'])
    return True

def update_user(argv=None) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information,\n Try logging in first.\n")
        return False
    
    username = get_input("Which user do you want to update?", data['username'])
    if username != data['username'] :
        print "Remember, only root users can alter users other than themselves. You can try though."

    if get_yes_no("Do you want to change %s's password?"%username) :
        res = change_password(username)

    if get_yes_no("Do you want to change %s's email?"%username) :
        res = change_email(username)
    
    print "\n Updating User (%s) Finished."%username
    return True


def destroy_user(argv=None) :
    sys.stderr.write("This function isn't yet implemented (and only root can delete users anyways)\n")
    return False

def get_user(argv=None) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information,\n Try logging in first.\n")
        return False

    token = data['token']
    
    if argv and len(argv) > 0 :
        username = argv[0]
    else :
        username = get_input("Which user do you want to view info for?", data['username'])
        
    
    payload = {'token' : token}
    headers = {'content-type': 'application/json'}
    r = requests.get(USERS_URL+username, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)
    
    print ""
    print "-"*80
    print "Username     : %s" % (response['username'])
    print "Email        : %s " % response['email']
    print "VM's Running : %s" % len(response.get('instances', []))
    print "Instance IDs : %s" % str("[" + ', '.join(response.get('instances', [])) + "]")
    print "-"*80
    print ""
    return True

def get_users(argv=None) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information,\n Try logging in first.\n")
        return False

    token = data['token']
    
    payload = {'token' : token}
    headers = {'content-type': 'application/json'}
    r = requests.get(USERS_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    print ""
    print "-"*80
    print "\nNumber of Users : %s\n" % str(len(response.get('users', [])))
    
    for user in response.get('users', []) :
        print "Username     : %s" % (user['username'])
        print "Email        : %s " % user['email']
        print "VM's Running : %s" % len(user.get('instances', []))
        print "Instance IDs : %s" % str("[" + ', '.join(user.get('instances', [])) + "]")
        print ""
    print "-"*80
    print ""

    return response

# @info - walk the user through the steps of creating a new instance
def create_instance(argv=None, ret_json=False) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information, try logging in first.")
        return False

    token = data['token']

    payload = {'token' : token}
    headers = {'content-type': 'application/json'}
    instance_name = ""
    image_id = None
    classslug = ""
    boot_images = [("Ubuntu 14.04 x64", "13089493", "(Default Boot Image)")]
    snapshots = get_snapshots(ret_json=True)['snapshots']
    snapshots = [(snap['name'], snap['id'], "(Custom Snapshot)") for snap in snapshots]
    total_images =  [(x[0], x[1], x[2])  for x in (boot_images+snapshots)]
    image_names = [x[0] + " : " + x[1] for x in total_images]
    classes = ['1gb', '2gb', '4gb']
    slugname = None

    if argv and len(argv) > 0 :
       instance_name = argv[0]
    while not instance_name or len(instance_name) < 6 or len(instance_name) >= 50 or any(i in instance_name for i in '_=+\|/,') :
        instance_name = get_input("Please Enter a Name for the New Instance ([A-Z,a-z,1-9,-])")
    payload['instance_name'] = instance_name

    if argv and len(argv) > 1 :
        image_id = argv[1]
        for image in total_images :
            if image_id == image[1] :
                image_name = image[0]
        if not image_name  :
            sys.stderr.write("Image Id (%s) is not valid. Try another."%str(image_id))
            return False
        
    while image_id is None :
        choice = get_input_choices("Select the Boot Image for your new Instance.", image_names)
        image_id = total_images[choice][1]
        image_name = total_images[choice][0]
    payload['image'] = image_id

    if argv and len(argv) > 2 :
        slugname = argv[2]
        for x in range(len(classes)) :
            if slugname == classes[x] :
                classslug = x
        if not classslug :
            sys.stderr.write("Invalid Class Slug Given (%s)" % str(slugname))
            return False
    while slugname is None or classslug is None  :
        classslug = get_input_choices("Select the Compute Class for your Instance", classes)
        slugname = classes[classslug]

    payload['class'] = slugname
    payload['provider'] = 'DO'

    print "Confirm Instance Details"
    print "Name       : %s" % instance_name
    print "Boot Image : %s" % image_name
    print "VM Class   : %s" % classes[classslug]
    if not get_yes_no("Is this Information Correct?") :
        sys.stderr.write("Instance Creation Canceled. Feel free to try again.")
        return False
     
    print "\nCreating Instance (%s). This might take up to 3 minutes to complete, please be patient."%instance_name
    print "When finished, you will recieve a description of your new instance."
    r = requests.post(COMPUTE_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if ret_json : #return early without printing if the caller wants such
        return response


    inst = response.get('instance', None)

    print "-"*80
    print "New Instance Created"
    print "Inst Name   : %s" % (inst['name'])
    print "Inst ID     : %s" % inst['id']
    print "Inst IP     : %s" % inst['ip']
    print "Inst Status : %s" % inst['status']
    print "Inst Class  : %s RAM" % inst['class']
    print "Inst Disk   : %sGB SSD" % inst['disk']
    print "Inst Creator: %s" % inst['creator']
    print "Created At  : %s" % str(inst['created_at'])
    print "-"*80
    print ""
    return response

# @info - walk the user through the steps of destroying an instance
def destroy_instance(argv=None, ret_json=False) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information, try logging in first.\n")
        return {} 

    if argv and len(argv) > 0 :
        inst_id = argv[0]
    else :
        instances = get_instances(ret_json=True)['instances']
        inst_list = [" %s" % inst['name'] + (30-len(inst['name']))*' ' + " | Owner : %s" % inst['creator']  for inst in instances]
        choice = get_input_choices("Choose an Existing Instance To Destroy", inst_list)
        inst_id = instances[choice]['id']

    if data['username'] != instances[choice]['creator'] :
        print "Remember, only the root user can delete instances that they do not own."


    if get_yes_no("Would you like to create a snapshot for this instance?") :
        res = create_snapshot(argv=[inst_id])

    if not get_yes_no("Confirm that you do want to delete instance %s (owned by %s)" % (instances[choice]['name'],
                                                                                        instances[choice]['creator'])) :
        sys.stderr.write("Instance Deletion Canceled. Exiting.\n")
        return {} 

    token = data['token']
    
    payload = {'token' : token}
    headers = {'content-type': 'application/json'}
    r = requests.delete(COMPUTE_URL+str(inst_id), data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if ret_json : #return early without printing if the caller wants such
        return response
    
    inst = response.get('instance', None)
    print ""
    print "-"*80
    print "Instance Deletion Successful" 
    print "Inst Name : %s" % (inst['name'])
    print "Inst ID   : %s" % inst['id']
    print "-"*80
    print ""
    return response

# @info - grab info on all instances
def get_instances(argv=None, ret_json=False) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information, try logging in first.\n")
        return False

    token = data['token']

    payload = {'token' : token}
    headers = {'content-type': 'application/json'}

    if argv and len(argv) > 0 :
       payload['username'] = argv[0]
    
    r = requests.get(COMPUTE_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if ret_json : #return early without printing if the caller wants such
        return response
    
    print "-"*80
    
    for inst in response.get('instances', []) :
        print "Inst Name   : %s" % (inst['name'])
        print "Inst ID     : %s" % inst['id']
        print "Inst IP     : %s" % inst['ip']
        print "Inst Status : %s" % inst['status']
        print "Inst Class  : %s RAM" % inst['class']
        print "Inst Disk   : %sGB SSD" % inst['disk']
        print "Inst Creator: %s" % inst['creator']
        print "Created At  : %s" % str(inst['created_at'])
        print ""

    print "Number of Instances : %s" % str(len(response.get('instances', [])))
    print "-"*80

    return response

# @info - grab info on an existing instance
def get_instance(argv=None, ret_json=False) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information, try logging in first.\n")
        return False

    if argv and len(argv) > 0 :
        inst_id = argv[0]
    else :
        instances = get_instances(ret_json=True)
        instances = instances['instances'] if instances else []
        inst_list = ["%s" % (inst['name'])  + (30-len(inst['name']))*' ' + " | Owner : %s" % inst['creator'] for inst in instances]
        choice = get_input_choices("Choose an existing instance", inst_list)
        inst_id = instances[choice]['id']

    token = data['token']
    
    payload = {'token' : token}
    headers = {'content-type': 'application/json'}
    r = requests.get(COMPUTE_URL+str(inst_id), data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if ret_json : #return early without printing if the caller wants such
        return response
    
    inst = response.get('instance', None)

    print ""
    print "-"*80
    print "Inst Name   : %s" % (inst['name'])
    print "Inst ID     : %s" % inst['id']
    print "Inst IP     : %s" % inst['ip']
    print "Inst Status : %s" % inst['status']
    print "Inst Class  : %s RAM" % inst['class']
    print "Inst Disk   : %sGB SSD" % inst['disk']
    print "Inst Creator: %s" % inst['creator']
    print "Created At  : %s" % str(inst['created_at'])
    print "-"*80
    print ""

    return response



#### SNAPSHOTS ######

# @info - walk the user through the process of creating a snapshot from an exisiting instance
def create_snapshot(argv=None, ret_json=False) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information, try logging in first.")
        return False

    token = data['token']

    payload = {'token' : token}
    headers = {'content-type': 'application/json'}
    inst_id = None
    snapshot_name = ""
    description = ""
    shutdown = False

    if argv and len(argv) > 0 :
       snapshot_name = argv[0]
    while not snapshot_name or len(snapshot_name) < 6 or len(snapshot_name) >= 40 or any(i in snapshot_name for i in '_=+\|/,') :
        snapshot_name = get_input("Please Enter a Name for this new Snapshot")
    payload['snapshot_name'] = snapshot_name

    if argv and len(argv) > 1 :
        inst_id = argv[1]
    else :
        instances = get_instances(ret_json=True)['instances']
        inst_list = ["Name : %s" % (inst['name']) + ", Owner : (%s)" % inst['creator']  for inst in instances]
        choice = get_input_choices("Choose an Existing Instance To Snapshot", inst_list)
        inst_id = instances[choice]['id']
    payload['inst_id'] =  str(inst_id)

    while not description :
        description = get_input("Please Enter a Short (1 sentence) description for this Snapshot")
    payload['description'] = description

    if get_yes_no("If this instance is running, do you want to shut it down for the snapshot?") :
        shutdown =True
    payload['shutdown'] = shutdown


    print "New Snapshot Details "
    print "Snapshot Name  : (%s)" % snapshot_name
    print "Instance Name  : (%s)" % instances[choice]['name']
    print "Instance ID    : (%s)" % instances[choice]['id']
    print "Description    : %s"  % description
    print "Shutdown Inst? : %s" % ("Yes" if shutdown else "False")
    if not get_yes_no("Is this Information Correct?") :
        sys.stderr.write("Snapshot Creation Canceled. Feel free to try again.")
        return False
     
    print "Creating Snapshot (%s). This might take up to 3 minutes to complete, please be patient."%snapshot_name
    print "When finished, you will recieve a description of your new instance."
    r = requests.post(SNAPSHOTS_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if ret_json : #return early without printing if the caller wants such
        return response


    snap = response.get('snapshot', None)

    print ""
    print "-"*80
    print "Snapshot Creation Successful. "
    print "Snapshot Name : (%s)" % snap['name']
    print "Snapshot ID   : (%s)" % snap['id']
    print "Instance Name : (%s)" % snap['inst_name']
    print "Created At    : %s" % str(snap['created_at'])
    print "Description   : %s" % snap['description']
    print "-"*80
    print ""
    return response


def get_snapshot(argv=None, ret_json=False) : 
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information, try logging in first.")
        return False

    if argv and len(argv) > 0 :
        snap_id = argv[0]
    else :
        snapshots = get_snapshots(ret_json=True)['snapshots']
        snap_list = ["%s" % (snap['name']) for snap in snapshots]
        if not snap_list :
            print "It doesn't look like any snapshots exist currently."
            return False
        choice = get_input_choices("Choose an Existing Snapshots", snap_list)
        snap_id = snapshots[choice]['id']

    token = data['token']
    
    payload = {'token' : token}
    headers = {'content-type': 'application/json'}
    r = requests.get(SNAPSHOTS_URL+str(snap_id), data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if ret_json : #return early without printing if the caller wants such
        return response
    
    snap = response.get('snapshot', None)

    print ""
    print "-"*80
    print "Snapshot Name : (%s)" % snap['name']
    print "Snapshot ID   : (%s)" % snap['id']
    print "Instance Name : (%s)" % snap['inst_name']
    print "Created At    : %s" % str(snap['created_at'])
    print "Description   : %s" % snap['description']
    print "-"*80
    print ""
    return response

def get_snapshots(argv=None, ret_json=False) :
    data = load_auth_info()
    if not data :
        sys.stderr.write("You must have a valid token to view user information, try logging in first.")
        return False

    token = data['token']

    payload = {'token' : token}
    headers = {'content-type': 'application/json'}

    r = requests.get(SNAPSHOTS_URL, data=json.dumps(payload), headers=headers)

    if not check_return(r) :
        return False

    response = json.loads(r.text)

    if ret_json : #return early without printing if the caller wants such
        return response

    print ""
    print "-"*80
    print "Number of Snapshots : %s" % str(len(response.get('snapshots', [])))
    
    for snap in response.get('snapshots', []) :
        print "Snapshot Name : %s" % (snap['name'])
        print "Snap ID       : %s " % snap['id']
        print "Snap Instance : %s" % snap['inst_name']
        print "Created At    : %s" % str(snap['created_at'])
        print "Description   : %s" % snap['description']
        print ""

    print "-"*80
    print ""
    return response
    

ACTION_MAP = {   'create' : { "instance"  : create_instance,
                              "snapshot"  : create_snapshot,
                              "user"      : create_user},
                 'update' : { "user"      : update_user},
                 'destroy': { "instance"  : destroy_instance,
                              # "snapshot"  : destroy_snapshot,
                              "user"      : destroy_user},
                 'get'    : { "instance"  : get_instance,
                              "instances" : get_instances,
                              "snapshot"  : get_snapshot,
                              "snapshots" : get_snapshots,
                              "user"      : get_user,
                              "users"     : get_users} }   
                

# @info - main function, has the sys.argv args parsed and performs a switch based on those arguments.
if __name__ == "__main__" :
    args = parse_args(sys.argv)

    if args.root :
        CLIENT_CONFIG_FILE = CONFIG_DIR + 'root.config'

    if args.action == "setup" :
        res = setup_client()
        sys.exit(0 if res else 1)

    if args.action == "login" :
        res = login_client()
        sys.exit(0 if res else 1)

    if not args.action or args.action not in ACTIONS :
        sys.stderr.write("Must include a valid Action (%s) \n"%ACTIONS)
        sys.exit(1)
    
    if not args.noun or args.noun not in NOUNS :
        sys.stderr.write("Must include a valid noun (instance[s], user[s], snapshot[s]) for action (%s)\n "%args.action)
        sys.exit(1)

    action_func = ACTION_MAP.get(args.action).get(args.noun, None)
    if not action_func :
        sys.stderr.write(("It looks like your input of [%s] is invalid or unimplemented." +\
                         " If you think this is wrong tell John. \n") % (args.action+" " +args.noun)) 
        sys.exit(1)
    res = action_func(argv=args.specifics)
    
    sys.exit(0 if res else 1)
    
    

