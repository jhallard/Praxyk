Praxyk DevOps
===============

#### API Documentation

This document defines the API for the Praxyk devops server, which controls the compute resource distribution for our development group. The API is not meant to be used in a raw fashion, rather their are client programs which should be used to access the services provided by this API.

**Base API URL** - `devops.praxyk.com`

### High Level Routes

This is a list of all the highest level routes for the API.

 * `devops.praxyk.com/users/`
 * `devops.praxyk.com/compute/`

These determines if the caller is trying to access services related to user account information or whether the user has their auth info and wants to access compute resources like virtual machines and disk images.

### Users Route
The users route (`devops.praxyk.com/users/`) is used for all things related to individual users.

#### Get a User's Info
This returns the users name, email, and auth levels given a name or email (email has an @)

**GET** `devops.praxyk.com/users/$usrname_or_email`

**HEADERS**
 * Content-Type: application/json
 * tok: $user_token

#### Get a User's Token
This takes a user's secured login info and returns an access token'

**GET** `devops.praxyk.com/users/$username/validate/`

**HEADERS**
 * Content-Type: application/json
 * pwhash : $hashed_pw

