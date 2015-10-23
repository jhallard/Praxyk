#### Development Operations

Development operations covers the acquisition and management of all tools needed for development purposes. This mostly includes tools to regulate shared resource usage amount a group (like VMs and databases) and other tools to provide testing and integration services.

#### Client
The client code is available at `praxyk/devops/client/`. It consists of a single script that wraps around the DevOps API and allows users to easily access VM resources from the command line. For information on installing the client, see the README in the `/client` directory.

#### Server
The server code is available at `praxyk/devops/server/`.
The code tree for the server defines a Flask environment where requests to the DevOps API are authenticated and handled.
