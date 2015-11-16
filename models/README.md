Praxyk Models
===============

This directory contains definitions of all of the models in the shared-databases used by the various Praxyk servers. This includes both SQL models for our MySQL databases and the ROM models for our Redis NoSQL databases.

### MySQL Models
The bulk of the data used by Praxyk is stored in MySQL databases. This includes user data, authentication data, payment data, transaction history, and more. The models in the `//models/sql/` directory are listed and described below.

file             |  Model Clas   | Description
---------------- | ------------- | --------------------------------------
`user.py`        |    User       | The standard user model. Includes things like email (unique), password (hashed+salted), name (single string), and meta-data like signup date, if you're active, etc. 
`transaction.py` | Transaction   | This describes a single transaction with a Praxyk service, which in itself is a grouping of service requests.
`role.py`        |   Role        | Roles are data-types that can be attached to users to grant priviledge. 
`token.py`       |   Token       | Tokens allow user to access praxyk services, they are aquired by logging in with a username and password.


### NoSQL Models
file                    |  Model Clas      | Description
----------------------- | ---------------- | --------------------------------------
`result_base.py`        | Results          | An object that mirrors a MySQL Transaction object for use temporarily in the NoSQL code.
`result_base.py`        | ResultBase       | A base model that defines all meta-data common to results of different types. Is meant to be overridden by specific result classes.
`pod/pod_ocr_result.py` | POD\_OCR\_result | A child class of ResultBase that is specific to POD-OCR requests.
