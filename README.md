# Droit_v2

This repository contains implementation and utility code for Droit project, version 2. 

If you have any concerns or suggestions, please contact us at lyhao[AT]cs.columbia.edu. 

Major modification from the prior version: build a web app and implement federated identity management, abandon the access control mechanism in the previous version. We haven't find a concerete access control mechanism yet.

## Acknowledgement
We would like to thank Yifan for his valuable input and contribution on the implementation of this  prototype. 

## How to bootstrap the project

1. `git clone git@github.com:Halleloya/Droit_v2.git`.
2. Install dependencies `pip install -r requirements.txt`.
3. Configure the database, e.g., store your database in data/db, and `mongod --dbpath Droit/data/db`
4. Run the shell `python runall.py` or `./run.sh`. It create a simple tree-like structure illustrated in the following section. 

Sidenotes:

To run a local directory in the current structure `python run.py --level [level name]`. Try `python run.py --help` for more information. 

To run a single directory `python -m Droit.run`. It is easy and basically enough to test basic functions.

Please note that you are supposed to change the [ip] and [port] manually in the `config.py` file, if needed. 

## A sample walk-through 

Below we show a sample walk-through with a binary tree-like structure.

```
level1 (master)
level2a level2b
level3aa level3ab level3ba level3bb
level4aaa level4aab level4aba level4abb level4baa level4bab level4bba level4bbb  
level5aaaa level5aaab ...
level6aaaaa level6aaaab ...
```

## Settings

By default, all the directoires run on localhost. The tree-like structure starts from port 5001, with the name of level1 (also called master directory or root directory). The single directory module named SingleDirectory runs on port 4999.

MongoDB runs on its default port 27017. 

## Authentication

We utilize OpenID library to implement a federated identtiy assertion model among directories. In general, one directory can rely on its counterparts to authenticate a user after some configurations. From a user's perspective, one can sign in a directory with the identity from another directory. 

### Example 
To illustrate how to configure it, we give an example that level3aa provides a means of login with identity of level2b. In this example, level2b is the OIDC provider, while level3aa is the OIDC client.

> In level2b (http://localhost:5003/auth/oauth_list), register a new client. The only nonintuitive field is "Redirect URI", which is the address that the provider should redirect back to the client. In the example, it should be `http://localhost:5004/auth/oidc_auth_code/level2b`.

> In level3aa's backend configuration (Droit/auth/providers_config.py), change the providers_config with the client's id and secret specified in the known OIDC clients of level2b.

```
"level3aa": {
        "level2b": {
            "client_id": 'sQDK1uX1R62sZf3f9AB0eTJb',
            "client_secret": 'pkcqeqvYvzKE1zHjhRv30MFVcIDve6b4tZRmmjGf68M0ZmoK',
            "access_token_url": 'http://localhost:5003/auth/oidc_token',
            "access_token_params": None,
            "authorize_url": 'http://localhost:5003/auth/oidc_authorize',
            "authorize_params": None,
            "api_base_url": 'http://localhost:5003/api',
            "client_kwargs": {
                'scope': 'openid profile',
                'token_endpoint_auth_method': 'client_secret_basic'}
        }
    }
```

> Now you can login level3aa with your username and password in level2b.



## Attribute Based Access Control (ABAC)
The ABAC system can be used to specify in what conditions a thing can be accessed. Rules are specified in policies and requests are automatically generated when user request throught the web user interface. Details about policy formats can be found from py_abac documentations. By default, requests are denied if there are no policies associated. When there is a conflict, the policy with highest priority dominates. 


## Attribute Authorization System
The attribute authorization system can be used to retrieve attribute information from various resource providers. The authorization process is triggered by the "Authorize" button under "Attributes". The system identities and classifies the attributes required by the associated policies in the IoT directory. The user will be redirected to the user consent page, where they can choose the attribute what they allow the ABAC system to access. The authorization and data retrieval process can be done iteratively.

Currently, the system supports two types of attributes- user attributes (OIDC provider) and environmental attributes (example-oauth2-server). "example-oauth2-server" is a sample resource provider, which contains weather information including temperature and rainfall. The configuration for the oauth client is stored in "providers_config.py", which is client register under the username "test_user". Run the sample server by `python app.py` in the "example-oauth2-server" directory. The sample server runs on port 5100. Note: In current setting, you need to run `export AUTHLIB_INSECURE_TRANSPORT=1` in command line before starting the server.

