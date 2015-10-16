DevOps API Documentation
===============

This document defines the API for the Praxyk devops server, which controls the compute resource distribution for our development group. 

**Host** - `devops.praxyk.com`

**API Overview**

This is a list of all possible API calls, the details of the parameters for each call is given in the next section.

 * `/users/` - User creation, deletion, management.
   * `GET /users/{user}`
   * `POST /users/`
   * `PUT /users/{user}`
 * `/compute/` - VM creation, deletion, management.
   * `GET /compute/`
   * `GET /compute/{instance_id}`
   * `POST /compute/`
   * `DELETE /compute{instance_id}`
 * `/snapshots/` - VM-snapshot creation, deletion, management.
   * `GET /compute/`
   * `GET /compute/{instance_id}`
   * `POST /compute/`
   * `DELETE /compute{instance_id}`
 * `/tokens/`
   * `POST /tokens/`
 * `/sshkeys/` - User SSH-key management.
   * `GET /sshkeys/` 
   * `POST /sshkeys/` 
   * `DELETE /sshkeys/{key_name}` 


___
___


### Users Route
The users route (`/users/`) is used for all things related to individual users. This includes creating a user (POST), partially/fully updating a user (PUT), and getting limited info about a user (GET).

___

#### Add a New User
Add a new user to the system. Username must be unique. Only users with root priviledges can add users to the system.

`POST /users/`

**Parameters**

 Name       | Type       | Description                         | Optional
----------- | ---------- | ----------------------------------- | ------------------
   name     | _string_   | The username of the new user        | No
   email    | _string_   | The email associated with the user  | No
   password | _string_   | Password for the new user           | No
   auth     | _int_      | The auth level for the new user.    | No
   token    | _string_   | 512-bit auth token for root user.   | No
 
**RESPONSE**
```json
{
  "code" : 200,
  "username" : "$new_username",
  "email": "$new_email"
 }
 ```
___
#### Update an Existing User
To update an existing user, perform the action below. This action must be authenticated by a token either from the given user or from the root user.

`PUT /users/{user}`

**Parameters**

 Name       | Type       | Description                         | Optional
----------- | ---------- | ----------------------------------- | ------------------
   token    | _string_   | Users temporary access token.       | No
   email    | _string_   | The email associated with the user  | Yes
   password | _string_   | Updated password for the user       | Yes
 
**RESPONSE**
```json
{
 "code" : 200,
 "username" : "$username",
 "email": "$user_email"
 }
 ```
___

#### Get a User's Info
This returns the users info given a name and a auth token for that user or root.

`GET /users/{user}`

**Parameters**

 Name       | Type       | Description                      | Optional
----------- | ---------- | -------------------------------- | ------------------
   token    | _string_   | Users temporary access token.    | No

**RESPONSE**
```json
{
  "code" : 200,
  "user" : {
     "username" : "$username",
     "email": "$user_email",
     "instances" : ["$inst_id", "$inst_id_2", "$inst_id_n"]
   }
 }
 ```


#### Get All User's Info
This gets information on all existing users, can only be run by users with root privileges. 

`GET /users/`

**Parameters**

 Name       | Type       | Description                      | Optional
----------- | ---------- | -------------------------------- | ------------------
   token    | _string_   | Users temporary access token.    | No

**RESPONSE**
```json
{
  "code" : 200,
  "users" : [
    {
      "username" : "$username_1",
      "email": "$user_email_1",
      "instances" : ["$inst_id", "$inst_id_2", "$inst_id_n"]
     },
     {"..." : "..."},
     {"..." : "..."}
   ]
 }
 ```
 
 ___
 ___
 
 

### Tokens
Tokens are used to perform requests, but they are temporary and thus the user must be revalidated every once in a while.

___

#### Validate a User, get an Access Token
This is used to get a temp access token that authorizes and validates the given user.

`POST /tokens/`

**Parameters**

 Name       | Type       | Description                              | Optional
----------- | ---------- | ---------------------------------------- | ------------------
 username   | _string_   | the name of the user being validated.    | No
 password   | _string_   | The user's password.                     | No

 
**RESPONSE**
```json
{
  "code" : 200,
  "username" : "$username",
  "token" : "$token_str",
 }
 ```

____
____

### Compute

This domain allows authenticated users (with an active access-token) to create and manage VM resources.

___

#### List Available Instances
Get a list of all available instances. Instances are returned as a list of dictionaries.

`GET /compute/`

**Parameters**

 Name       | Type       | Description                      | Optional
----------- | ---------- | -------------------------------- | ------------------
   token    | _string_   | Users temporary access token.    | No
   username | _string_   | Creator of instances returned.   | Yes (Defaults to "ALL")

    
**RESPONSE**
```json
{
  "code" : 200,
  "instances" : [
    { 
        "name" : "$inst_name_1",
        "id"   : "$inst_id_1",
        "ip"   : "$inst_ip_1",
        "creator" : "$creator_name_1",
        "status" : "$inst_status_1",
        "class"  : "$inst_class_1",
        "disk"   : "$inst_disk_1",
        "image"  : "$inst_image_id_1",
        "created_at"  : "$created_timestamp_1"
      },
      {"..." : "..."},
      {"..." : "..."},
    ]
 }
 ```

___

#### Get Specific Instance
Get a list of all available instances. Instances are returned as a list of dictionaries.

`GET /compute/{instance_id}`

**Parameters**

 Name       | Type       | Description                      | Optional
----------- | ---------- | -------------------------------- | ------------------
   token    | _string_   | Users temporary access token.    | No

    
**RESPONSE**
```json
{
  "code" : 200,
  "instance" : { 
        "name" : "$inst_name",
        "id"   : "$inst_id",
        "ip"   : "$inst_ip",
        "creator" : "$creator_name",
        "status" : "$inst_status",
        "class"  : "$inst_class",
        "disk"   : "$inst_disk",
        "image"  : "$inst_image_id",
        "created_at"  : "$created_timestamp"
      }
 }
 ```

___

#### Create New Instance
Create a new Virtual-Machine instance. As of right now the only provider is Digital Ocean, that might change in the near future.

`POST /compute/`

**Parameters**

 Name         | Type       | Description                           | Optional
------------- | ---------- | ------------------------------------  | ------------------
   token      | _string_   | Users temporary access token.         | No
instance_name | _string_   | Chosen name of the instance (unique)  | No
    image     | _string_   | ID of a boot-image (custom or public) | Yes (defaults to Ubuntu 14.04 x86)
    class     | _string_   | Chosen name of the instance (unique)  | YES (defaults to 1GB/30GB DO Inst)      
    Provider  | _string_   | Provider ID Tag (not used currently)  | Yes (defaults to "DO")


    
**RESPONSE**
```json
{
  "code" : 200,
  "instance" : { 
        "name" : "$inst_name",
        "id"   : "$inst_id",
        "ip"   : "$inst_ip",
        "creator" : "$creator_name",
        "status" : "$inst_status",
        "class"  : "$inst_class",
        "disk"   : "$inst_disk",
        "image"  : "$inst_image_id",
        "created_at"  : "$created_timestamp"
      }
 }
 ```

___

#### Delete VM Instance
Deletes a VM instance. Root user can delete any instance, other users can only delete their own.

`DELETE /compute/{instance_id}`

**Parameters**

 Name         | Type       | Description                                            | Optional
------------- | ---------- | -----------------------------------------------------  | ------------------
   token      | _string_   | Users temporary access token.                          | No
take_snapshot | _bool_     | Will cause the instance to be imaged before deletion.  | Yes (default = False)

    
**RESPONSE**
```json
{
  "code" : 200,
  "instance" : { 
        "name" : "$inst_name",
        "id"   : "$inst_id"
      }
 }
 ```

____
____

### Snapshots

Snapshots are just disk-images of virtual-machines at a given point in time. They can they be used to spin up other machines which are exact copies of the imaged-machine very quickly. Note that machines must be shutdown to perform a snapshot, the shutdown process can be performed via this API. See below for details.

___

#### List Available Snapshots
Get a list of all available snapshots. Snapshots are returned as a list of dictionaries.

`GET /snapshots/`

**Parameters**

 Name       | Type       | Description                      | Optional
----------- | ---------- | -------------------------------- | ------------------
   token    | _string_   | Users temporary access token.    | No

    
**RESPONSE**
```json
{
  "code" : 200,
  "snapshots" : [
    { 
        "name" : "$snap_name_1",
        "id"   : "$snap_id_1",
        "inst_name" : "$instance_name_1",
        "created_at" : "$creation_timestamp_1",
        "description" : "$snapshot_description_1",
      },
      {"..." : "..."},
      {"..." : "..."},
    ]
 }
 ```

___

#### Get Specific Snapshot
Get details about a specific snapshot by ID.

`GET /snapshots/{snapshot_id}`

**Parameters**

 Name       | Type       | Description                      | Optional
----------- | ---------- | -------------------------------- | ------------------
   token    | _string_   | Users temporary access token.    | No

    
**RESPONSE**
```json
{
  "code" : 200,
  "snapshot" : { 
        "name" : "$snap_name",
        "id"   : "$snap_id",
        "inst_name" : "$inst_name",
        "created_at" : "$creation_timestamp",
        "description" : "$snapshot_description",
      }
 }
 ```

___

#### Create New Snapshot
Create a new snapshot of an existing Virtual-Machine instance. As said above, machines must be shut-down before they can be imaged. You can supply the `shutdown` parameter in the below `POST` to cause us to shutdown the virtual machine before imaging it, afterwards re-enabling it.

`POST /snapshots/`

**Parameters**

 Name         | Type       | Description                               | Optional
------------- | ---------- | ----------------------------------------- | ------------------
   token      | _string_   | Users temporary access token.             | No
snapshot_name | _string_   | Chosen name for the Snapshot (unique).    | No
 instance_id  | _string_   | ID of an existing VM instance to image.   | No
description   | _string_   | Short description of the snapshot.        | Yes (default = "")
 shutdown     | _bool_     | Tell us to shutdown the running instance. | Yes (default = No)


    
**RESPONSE**
```json
{
  "code" : 200,
  "snapshot" : { 
        "name" : "$snap_name",
        "id"   : "$snap_id",
        "inst_name" : "$inst_name",
        "created_at" : "$creation_timestamp",
        "description" : "$snapshot_description",
      }
 }
 ```

___

#### Delete Snapshot
Deletes an existing snapshot. Right now only root user can delete snapshots.

`DELETE /snapshots/{snapshot_id}`

**Parameters**

 Name         | Type       | Description                                            | Optional
------------- | ---------- | -----------------------------------------------------  | ------------------
   token      | _string_   | Users temporary access token.                          | No

    
**RESPONSE**
```json
{
  "code" : 200,
  "instance" : { 
        "name" : "$snap_name",
        "id"   : "$snap_id"
      }
 }
 ```

____
____

### SSH Keys

SSHKeys can be set for each user in the DevOps database, then when that user creates a virtual machine instance, the ssh key for that user will be automatically added to the instance. This allows the user to log into their new instance immediately without having to configure passwords.


#### Create SSH Key for User
Create a new SSH key entry in the database and stored on Digital Ocean's servers. As said above, after this is done, anytime this user makes a VM instance they will be able to log in just by giving their ssh-key password..

`POST /sshkeys/`

**Parameters**

 Name         | Type       | Description                               | Optional
------------- | ---------- | ----------------------------------------- | ------------------
   token      | _string_   | Users temporary access token.             | No
  username    | _string_   | User that the key will apply to.          | Yes (defaults to caller)
 key_name     | _string_   | A short name for the key                  | No
pubkey_text   | _string_   | The raw public key text for the key.      | No
fingerprint   | _string_   | The fingerprint for the ssh key.          | Yes (not currently used)


    
**RESPONSE**
```json
{
  "code" : 200,
  "key"  : {
             "name" : "$keyname",
             "username" : "$username",
             "keyid"    : "$keyid"
           }
 }
 ```

___
