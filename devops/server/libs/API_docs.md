Praxyk DevOps
===============

#### API Documentation

This document defines the API for the Praxyk devops server, which controls the compute resource distribution for our development group. The API is no

**Host** - `devops.praxyk.com`

#### High Level Routes

This is a list of all the highest level routes for the API.

 * `/users/` - User creation, deletion, management.
 * `/compute/` - VM creation, deletion, management.
 * `/snapshots/` - VM-snapshot creation, deletion, management.
 * `/sshkeys/` - User SSH-key management.

All interaction with the api must be accompanied by a valid token which uniquely identifies a user and allows them to acces these services. The exception to this is the `GET /users/{user}/token<F4>



#### Users Route
The users route (`/users/`) is used for all things related to individual users. This includes verifying a user (GET) to get a token, adding a new user (POST), and updating a user's info (PUT).

##### Add a New User
Add a new user to the system. Username must be unique. Only users with root priviledges can add users to the system.

`POST /users/`

**Parameters**

 * **token** | _str_    | 512-bit auth token for root user.
 * **name**  | _string_ | The username of the new user
 * **email** | _string_ | The email associated with the new user.
 * **passw** | _string_ | The password for the new user.
 * **auth**  | _int_    | The auth level for the new user.
 
**RESPONSE**

 * **Status** | 200 OK
 * **token**  | string | access token for the new user.

##### Update an Existing User
To update an existing user, perform the action below. Note that the auth-level and username cannot be changed via this method, only the contact email and password. This action must be authenticated by a token either from the given user or from the root user.

`PUT /users/{user}`

**Parameters**

 * **token** | _string_ | 512-bit auth token for the user or root.
 * **email** | _string_ | The email associated with the new user (optional).
 * **passw** | _string_ | The password for the new user (optional).
 
**RESPONSE**

 * **Status** | 200 OK
 * **token** | string | access token for the new user.

##### Get a User's Info
This returns the users name, email, and auth levels given a name or email (email has an @)

GET `/users/$username`

HEADERS
 * Content-Type: application/json
 * tok: $user_token

##### Get a User's Token
This takes a user's secured login info and returns an access token'

**GET** `devops.praxyk.com/users/$username/validate/`

**HEADERS**
 * Content-Type: application/json
 * pwhash : $hashed_pw
