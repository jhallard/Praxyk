Praxyk Devops Server
=========================

This part of the source tree contains all code and libraries necessary to run the Praxyk devops server on a given machine. It includes many homemade utility classes to handle authorization, database access, and interaction with IaaS provider APIs.

##### Quick Start
To get the DevOps server up and running quickly, log onto the server that you want to act as the devops server and perform the following commands :
```sh
git clone -b devops https://github.com/jhallard/praxyk
cd praxyk/devops/server
./setup.sh # make the logging directories
./devops_request_handler.py --builddb --filldb  $CONFIGF_PATH $SCHEMAF_PATH # start the api request handler
```
 
 Note that for everything to work you will need to aquire the database `.schema` file that represents the devops database and a configuration json file that contains authorization information. If you are on the Praxyk team, ask me for these things. If you aren't, you're going to need to fill in your json files and pass them into the relevant scripts.
 
 If successful, the above call will make the database described by the given `.schema` file, sync its data with that of the various IaaS providers, add the root user to the system, then begin listening for API requests.
 
#### Request Handler
 This section will give more information on the request handler script, which acts as the the primary interface between the user and our server. The handler script is written in python and uses the Flask module to expose a REST API to the world. This program is meant to run continuously, taking API requests, parsing them and forwarding them to the appropriate functions contained in the various utility classes (see `/devops/server/libs/`).
 
 A complete description of running the `devops_request_handler.py` script is given below.
```sh
$ ./devops_request_handler.py -h
usage: devops_request_handler.py [-h] [--metaconfig METACONFIG]
                                 [--builddb BUILDDB] [--filldb FILLDB]
                                 config schemaf

This is the script that handles all incoming API requests for the Praxyk
development operations server (devops.praxyk.com). It uses the included
utilities (vmUtil, dbUtil, authUtil, devopsUtil) to expose a secure and simple
interface for users to access shared compute resources. The script must be
given the path to a configuration file containing sensitive information
(dbusers, dbpw, dbip, auth tokens for IaaS providers). It also must be given a
shema file representing the devops database that is being used. Most actions
that are performed by this script are triggered via incoming API calls, except
for the build/fill database commands. Those can only be triggered by giving
the input flag --builddb and --filldb respectively. Build DB will cause the
tables and indexes to be constructed, while fill DB will cause data in the DB
to be synced with data from IaaS providers. It will also add in the root user.
If you want to sync the DB with IaaS providers manually without building and
filling the DB from scratch, you can use the API to send a sync command. See
the DevOps API Docs.

positional arguments:
  config                Full path to the config file for this regression. It
                        should include the vm tokens, dbip, dbpw, and dbuser.
  schemaf               Full path to the .schema file for a database.

optional arguments:
  -h, --help            show this help message and exit
  --metaconfig METACONFIG
                        Full path to the json file containing info about the
                        meta-database for storing log files.
  --builddb BUILDDB     If present, the DB represented by the given schema
                        file will bebuilt from scratch but not filled, given
                        that it doesnt exist already.
  --filldb FILLDB       If present, the devops DB that was just built will be
                        synced withthe current info provided by IaaS
                        providers.
```

 
#### Unit Testing
 This part of the source tree includes a suite relatively extensive unit-test for all different levels of complexity. The modules and their respective unit tests are listed below.
  * `db_util.py` : `db_unit_test.py`
  * `vm_util.py` : `vm_unit_test.py`
  * `auth_util.py` : `auth_unit_test.py`
  * `devops_util.py` : `devops_unit_test.py`
  * `devops_request_handler.py` : `handler_unit_test.py`

Each `*.unit_test.py` file contains a single class that derives from the `UnitTest` class, defined in `/unittest/unit_test.py`. Each specific unit test class takes in one or more dictionaries of configuration arguments during construction, after which the `run()` function can be called to run the specific unit test suite. This is all encapsulated in `regression.py`, which takes in a few command-line arguments and creates all of the needed configuration dictionaries for the specific set of unit-tests being ran.

##### Running Regressions
 Regressions are run by calling `./regression.py` and passing in the appropriate arguments. All tests and components are logged in their own directories underneat `praxyk/devops/server/logs/`. They will all be created automatically when you run the `setup.sh` script.
A complete description of the regression python program is given below.
 ```sh
 usage: regression.py [-h] [--metaconfig METACONFIG] [--schemaf SCHEMAF]
                     [--flags FLAGS]
                     config testname

This is the set of unit tests for that devops server backend. From this
program you can test the main server program as well as the various utilities
that it relies on, like the dbUtil, vmUtil, devopsUtil, and authUtil classes.

positional arguments:
  config                Full path to the config file for this regression. It
                        should include the vm tokens, dbip, dbpw, and dbuser.
  testname              Which test do you want to run.The following are accepted :
                        {vmtest, authtest, devopstest, servertest, dbtest}

optional arguments:
  -h, --help            show this help message and exit
  --metaconfig METACONFIG
                        Full path to the json file containing info about the
                        meta-database for storing log files.
  --schemaf SCHEMAF     Full path to the .schema file for a database. This is
                        required if you are testing the datbase, auth, devops,
                        or server.
  --flags FLAGS         A string where each character represents a test flag.
                        Only used for vmtest so far.vmtest flags : [a b c d e
                        f] each one runs another series of tests.devopstest
                        flags : [a b c]
```

