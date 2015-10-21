Praxyk API Clients
=================

This directory contains all of the various client bindings for the Praxyk API. These bindings simplify the process of interacting with the API and give developers a means of building applications around our services without having to make raw GET and POST requests.

The client bindings provided here include both a command-line utility and modules that can be imported into your existing code. Examples for both of these use cases are demonstrated in the examples section.

#### Requirements
The client scripts are free to download but in order to access the API you will need to provide a set of valid Praxyk account credentials, if you don't have a Praxyk account you can sign-up today at [our website](http://www.praxyk.com) or even through the bindings themselves!

 * **Operating Systems** - Linux, OSX
 * **Python** - Python 2.7

#### Install
To install, simply clone the API branch of the praxyk project and run the client setup process. This will put the client script on your path and make the necessary config directories. Feel free to remove the praxyk folder when you're done with the setup process.
```sh
git clone -b api https://github.com/jhallard/praxyk
cd praxyk/client
./setup.py
```

This will walk your through the steps of installing the various command-line utilities and modules that you choose during the setup process.

#### Client Bindings Status
Language       | Status      | Info      
-------------- | ----------- | ----------------------------------------------------
CL Utility     | In Progress | This is an interactive program that can be used to access the entire range of Praxyk services from a terminal.
Python         | In Progress | Python is the first language we plan to make bindings for, v.1 should be done soon.
C++            | Planned     | We would like to make some C++ bindings but it isn't very high on the priority list.


### Commmand-Line Utility
Included with this set of client bindings is an interactive command-line based script called `praxyk_client`. This script, written in Python, wraps around the requests library and provides a simple yet powerful way of programmatically interacting with the Praxyk API.

### Python Bindings
Python is the first language we plan to create client library for, and it is the one we will put the most effort into maintaining.
