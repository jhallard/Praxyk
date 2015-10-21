### Praxyk API Documentation

#### Overview
The API is our contract with all users of Praxyk services that defines exactly how to get data in and results out of our servers. Even the [main website](http://www.praxyk.com) is just a fancy wrapper around this API. At a high level, the API needs to allow users to do a few things.
 * Manage their user account. This includes registering an account, updating their information, and being able to query for information on their account. It also involved authenticating requests and managing transaction history.
 * Interact with our internal models. This mostly involved giving the users an interface to upload information to our servers to be analyzed.
 * Receive the results of their prediction requests. 

#### Note About Pagination
Many routes that can return large batches of information to the user are paginated by default. This means that querying these routes will return a limited amount of data, along with a link to the next block of data. For example, calling a paginated-route with no page-related arguments will cause us to return page 0 with a default size of 100 values.

```sh
GET api.praxyk.com/results/12345/
``` 

returns

```python
{
 "code" : 200,
 "items" : ["$item1", "...", "$item100"],
 "next" : "api.praxyk.com/results/12345/?page=1"
}
```

Every paginated route can take any of the following optional arguments 
 * `pagination` - Boolean, if false we dump all resources to the user in a list. Defaults to true.
 * `page_size` - Page-size tells us how many items to put on each page. The default is 100.
 * `page=X` - This tells us to return a single page, given by X, of size `page_size`.
 * `pages=X` - This tells us to return X pages, starting from 0.
 * `start_page=X&pages=Y` - This tells us a starting page, and how many pages you want to grab from that start.

If conflicting arguments are given (example `pages=5&start_page=1&pages=8`) we will default to the last valid setting (so `start_page=1&pages=8` in this case). The exception to this is if the `pagination=false` flag is given, in which case all resources will be given to the user.


#### API Routes

**API Base** - `api.praxyk.com`

 * `/users/`
   * `GET /users/{user_id}`
   * `POST /users/`
   * `PUT /users/{user_id}`
   * `DELETE /users/{user_id}`
 * `/tokens/`
   * `POST /tokens/`
 * `/pod/`
   * `GET /pod/`
   * `/pod/ocr/`
     * `GET /pod/ocr/`
     * `POST /pod/ocr/`
   * `/pod/bayes_spam/`
     * `GET /pod/bayes_spam/`
     * `POST /pod/bayes_spam/`
 * `/tlp/`
 * `/transactions/`
   * `GET /transactions/`
   * `GET /transactions/{transaction_id}`
   * `DELETE /transactions/{transaction_id}`
 * `/results/`
   * `GET /results/{transaction_id}` 

___
___


### Users Route
The users route (`/users/`) is used for all things related to individual users. This includes creating a user (POST), partially/fully updating a user (PUT), and getting limited info about a user (GET).

___

#### Add a New User
Add a new user to the system. Only users with root priviledges can add users to the system.

`POST /users/`

**Parameters**

 Name       | Type       | Description                            | Optional
----------- | ---------- | -------------------------------------- | ------------------
   email    | _string_   | The email associated with the user     | No
   name     | _string_   | The full name of the user (one string).| No
   password | _string_   | Password for the new user              | No
 
**RESPONSE**
```json
{
  "code" : 200,
  "user" : {
    "email": "$new_email",
    "userid" : "$user_id",
    "name" : "$user_name",
    "uri" : "api.praxyk.com/users/$user_id",
    "transactions_url" : "api.praxyk.com/transactions/?user_id=$user_id",
    "created_at" : "$creation_time"
  } 
}
 ```
___
#### Update an Existing User
To update an existing user, perform the action below. This action must be authenticated by a token from the user being updated.

`PUT /users/{userid}`

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
  "user" : {
    "email": "$new_email",
    "userid" : "$user_id",
    "name" : "$user_name",
    "uri" : "api.praxyk.com/users/$user_id",
    "transactions_url" : "api.praxyk.com/transactions/?user_id=$user_id",
    "created_at" : "$creation_time"
  } 
 }
 ```
___

#### Get a User's Info
This returns information on a user, their transactions, and results. Note that the transactions are returned as a URL through which the caller can get paginated transaction information.

`GET /users/{userid}`

**Parameters**

 Name       | Type       | Description                      | Optional
----------- | ---------- | -------------------------------- | ------------------
   token    | _string_   | Users temporary access token.    | No

**RESPONSE**
```json
{
  "code" : 200,
  "user" : {
    "email": "$new_email",
    "userid" : "$user_id",
    "name" : "$user_name",
    "uri" : "api.praxyk.com/users/$user_id",
    "transactions_url" : "api.praxyk.com/transactions/?user_id=$user_id",
    "created_at" : "$creation_time"
  } 
 }
 ```

___

#### Delete A User
This call will remove the given user's account from our system, including all stored result-data. Transaction history will be kept until last bill is paid.

`DELETE /users/{userid}`

**Parameters**

 Name       | Type       | Description                         | Optional
----------- | ---------- | ----------------------------------- | ------------------
   token    | _string_   | Users temporary access token.       | No

**RESPONSE**
```json
{
  "code" : 200,
  "user" : {
    "email": "$new_email",
    "userid" : "$user_id",
    "name" : "$user_name",
    "uri" : "api.praxyk.com/users/$user_id",
    "transactions_url" : "api.praxyk.com/transactions/?user_id=$user_id",
    "created_at" : "$creation_time"
  }  
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
 email      | _string_   | the email of the user being validated.   | No
 password   | _string_   | The user's password.                     | No

 
**RESPONSE**
```json
{
  "code" : 200,
  "user" : {
    "email" : "$user_email",
    "userid" : "$user_id",
  },  
  "token" : "$token_str",
 }
 ```

___
___

### Transactions
`api.praxyk.com/transactions/` is the portal for all specific transaction information. Transactions are records that are generated for every service request that a user makes through our API. For instance, if a user makes a request to `api.praxyk.com/pod/bayes_spam/` with 100 email-bodies as data, a single transaction record is generated to group together those 100 inputs and their corresponding outputs.
The user is given the ID of this transaction as a return to making the call to the `/pod/` service, and they can use this ID to obtain information on the status of their request by using the routes described in this section.


___

#### Get All User Transactions
This route can be used to access a user's entire history of transactions. Users must be authorized with an auth token to perform this request, and they can only access their own transaction history. The `user_id` field is required and for regular users must match the user who owns the token that is given with the request, administrators can request the transaction history of any or all users.


`GET /transactions/`

**Parameters**

 Name       | Type       | Description                                   | Optional
----------- | ---------- | --------------------------------------------- | ------------------
   token    | _string_   | Users temporary access token.                 | No
   user_id  | _string_   | ID of the user whose data you're requesting.  | No
 pagination | _bool_     | If false, all results are dumped to the user. | Yes (defaults to false)
   page     | _int_      | The 'page' of transactions you want returned. | Yes (defaults to 0)
   pages    | _int_      | The number of pages to be returned (from `start_page` if provided or 0 if not) | Yes (defaults to 0)
page_size   | _int_      | The number of results on each page returned.  | Yes (defaults to 100)
start_page  | _int_      | Only valid when used with `pages`, tells us the start page to return.  | Yes (defaults to 100)

 
**RESPONSE**
```json
{
  "code" : 200,
  "userid" : "$user_id",
  "transactions" : [
    {
      "trans_id" : "$trans_id1",
      "user_id" : "$user_id1",
      "command_url" : "$command_url1",
      "data_url" : "$data_url1",
      "results_url" : "api.praxyk.com/results/$trans_id1",
      "status"   : "$status1",
      "created_at" : "$created_at1",
      "uploads_total" : "$num_files_uploaded1",
      "uploads_success" : "$num_uploads_success1",
      "uploads_failed" : "$num_uploads_failed1",
      "size_total_KB" : "$total_files_size_KB"
    },
    {"..." : "..."},
    {"..." : "..."}
  ] 
}
 ```

___

#### Get a Single Transaction
After making a request to a Praxyk service, the user is returned a transaction ID. They can use that ID to call a route under this category, which will return the specifics of that instance. The transaction object returned includes information on the number of files in the request and the total size of those files, which will count towards user data-ingress charges.


`GET /transactions/`

**Parameters**

 Name       | Type       | Description                                   | Optional
----------- | ---------- | --------------------------------------------- | ------------------
   token    | _string_   | Users temporary access token.                 | No

 
**RESPONSE**
```json
{
  "code" : 200,
  "transaction" :
    {
      "trans_id" : "$trans_id",
      "user_id" : "$user_id",
      "command_url" : "$command_url",
      "data_url" : "$data_url",
      "results_url" : "api.praxyk.com/results/$trans_id",
      "status"   : "$status",
      "created_at" : "$created_at",
      "uploads_total" : "$num_files_uploaded",
      "uploads_success" : "$num_uploads_success",
      "uploads_failed" : "$num_uploads_failed",
      "size_total_KB" : "$total_files_size_KB"
    }
}
 ```

___

#### Update a Transaction
There are times when a user might want to change an active transaction, to cancel one in progress for instance. To do such they can use the route described below.


`PUT /transactions/{trans_id}`

**Parameters**

 Name       | Type       | Description                                   | Optional
----------- | ---------- | --------------------------------------------- | ------------------
   token    | _string_   | Users temporary access token.                 | No
   cancel   | _bool_     | Flag, if true any in-progress processing will stop.   | Yes

 
**RESPONSE**
```json
{
  "code" : 200,
  "transaction" :
    {
      "trans_id" : "$trans_id",
      "command_url" : "$command_url",
      "data_url" : "$data_url",
      "results_url" : "api.praxyk.com/results/$trans_id",
      "status"   : "$status",
      "created_at" : "$created_at",
      "uploads_total" : "$num_files_uploaded",
      "uploads_success" : "$num_uploads_success",
      "uploads_failed" : "$num_uploads_failed",
      "size_total_KB" : "$total_files_size_MB"
    }
}
 ```


___
___

### POD
`api.praxyk.com/pod/` is the high-level route for all Prediction on Demand services. This route is used to pass data that needs analysis to specific POD models, the actual predictions made on the data that is passed in available through the `/results/{transaction_id}` route, where `transaction_id` is an ID that uniquely identifies your request through the Praxyk API. 

As of right now, no actual requests are made through `/pod/`, only through it's sub-routes which are shown below.


___
___

### POD-OCR
Optical character recognition (OCR) is one of the first services to be offered through the Praxyk API, and it allows user's to extract strings of text present in a given image file. 


___

#### Make a New POD-OCR Request

This route is used to instantiate a new request to the POD Ocular Character Recognition service. It takes an authorization token from the user and a list of image-files. The images can be any one of png, tif/tiff, jpg, bmp. You will receive in return a list of items describing the transaction, including a transaction ID that you can use to track the progress of and access the results of your request.
The names of the files you upload are important, they will be used to index the results that are returned to you.

`POST /pod/ocr/`

**Parameters**

 Name       | Type       | Description                                   | Optional
----------- | ---------- | --------------------------------------------- | ------------------
   token    | _string_   | Users temporary access token.                 | No
   files    | _list_     | List of valid image file to perform recognition on. | No


 
**RESPONSE**
```json
{
  "code" : 200,
  "transaction" :
    {
      "trans_id" : "$trans_id",
      "command_url" : "$command_url",
      "data_url" : "$data_url",
      "results_url" : "api.praxyk.com/results/$trans_id",
      "status"   : "$status",
      "created_at" : "$created_at",
      "uploads_total" : "$num_files_uploaded",
      "uploads_success" : "$num_uploads_success",
      "uploads_failed" : "$num_uploads_failed",
      "size_total_KB" : "$total_files_size_KB"
    }
}
 ```

___
##### Query Results
`api.praxyk.com/results/`

Users with a valid auth token can make `GET` requests to the results page, where a list of jobs will be displayed with the request and result (if the job is finished). If the user has enabled push notifications, in-progress jobs will be updated by the server. Otherwise, the user will need to refresh the page to refresh the data.

A `GET` request to `/results/` will receive the response:

```
{
  "code" : 200,
  "transaction_ids" : ["$transaction_id1", "$transaction_id2", ...],
}
```

##### Example Usage
Through the website:
Users can log in and use the UI to upload images or send text to be processed with all of the details handled for them.

In order to make a direct API call outside of the web UI, a valid auth token will need to be present in the `POST` body and the image/text data will need to be present in the HTTP request header. Any request without a valid auth token will be thrown out. Registered users can retrieve their auth token by making a `GET` call to api.praxyk.com/users/{username}

A successful API request will receive the response:
```
{
  "code" : 200,
  "transaction_id" : "$transaction_id",
}
```

Following this, the server will redirect to `/results/`

When the requested job is finished the server will push a notification to the user who made the request if the user has allowed notifications through their browser or in the `POST` request.
