"""
Functions declared in this file are helper functions that can be shared by all other modules
"""
import flask
from urllib.parse import urljoin
from datetime import datetime
from flask.helpers import url_for
from py_abac.pdp import EvaluationAlgorithm
from .models import DirectoryNameToURL, TargetToChildName
from flask_login import current_user
from .auth import User
from pymongo import MongoClient
from py_abac.storage.mongo import MongoStorage
from py_abac import PDP, Policy, AccessRequest
from py_abac.provider.base import AttributeProvider
import re

def is_json_request(request: flask.Request, properties: list = []) -> bool:
    """Check whether the request's body could be parsed to JSON format, and all necessary properties specified by `properties` are in the JSON object

    Args:
        request (flask.Request): the flask request object wrapping the real HTTP request data
        properties (list[str]): list of property names to check. By default its an empty list

    Returns:
        boolean: whether the request is a JSON-content request and contains all the properties
    """
    try:
        body = request.get_json()
    except TypeError:
        return False
    if body is None:
        return False
    for prop in properties:
        if prop not in body:
            return False
    return True

def clean_thing_description(thing_description: dict) -> dict:
    """Change the property name "@type" to "thing_type" and "id" to "thing_id" in the thing_description

    Args:
        thing_description (dict): dict representing a thing description

    Returns:
        dict: the same dict with "@type" and "id" keys are mapped to "thing_type" and "thing_id"
    """
    if "@type" in thing_description:
        thing_description["thing_type"] = thing_description.pop("@type")
    if "id" in thing_description:
        thing_description["thing_id"] = thing_description.pop("id")
    return thing_description


def get_target_url(location: str, api: str = "") -> str:
    """Check the next possible location to request in order to get the 'location' directory

    It will check database if the 'location' is an adjacent directory to the current one.
    If it is, then return the concatenated URI using this adjacent directory's URI.

    Then it will check whether this 'location' is one of descendants directories.
    If it is, then return.

    Finally if current directory is not master, then it will return the URI using master directory's location

    Args:
        location (str): the target location to be searched
        api(str): url path after the host name, such as /register, /search. It is highly encouraged to form this parameter using 'url_for'

    Returns:
        str: if the location is possible, return the concatenated URI along with the 'api', otherwise return None

    """
    target_url = None
    # 1. check whether the location is known to current directory (parent or direct children)
    known_directory = DirectoryNameToURL.objects(
        directory_name=location).first()
    if known_directory is not None:
        target_url = urljoin(known_directory.url, api)

    # 2. check if the location is its descendants
    elif TargetToChildName.objects(target_name=location).first() is not None:
        descendant_directory = TargetToChildName.objects(
            target_name=location).first()
        target_url = urljoin(DirectoryNameToURL.objects(
            directory_name=descendant_directory.child_name).first().url, api)

    # 3. if current is not master directory, return the url of master directory
    elif DirectoryNameToURL.objects(relationship="parent").first() is not None:
        master_url = DirectoryNameToURL.objects(
            directory_name="master").first().url
        target_url = urljoin(master_url, api)

    return target_url

def add_policy_to_storage(policy: dict, location: str) -> bool :
    #json = request.get_json()
    policy = Policy.from_json(policy)
    client = MongoClient()
    storage = MongoStorage(client, db_name = location)
    try:
        storage.add(policy)
    except:
        return False
    return True

def delete_policy_from_storage(uid : str)  -> bool :
    pass
    """
    client = MongoClient()
    storage = MongoStorage(client)
    storage.delete(uid = uid)
    """
    

# check if the request is allowed by policy in the current level
def is_request_allowed(request: flask.Request) -> bool:
    other_attributes = []

    class UserIdAttributeProvider(AttributeProvider):
        def get_attribute_value(self, ace, attribute_path,ctx):
            if (not current_user):
                return None
            if(ace == "subject" and attribute_path == "$.id"):
                return current_user.get_user_id()
            return None
            
    class EmailAttributeProvider(AttributeProvider):
        def get_attribute_value(self, ace, attribute_path,ctx):
            user_id = ctx.get_attribute_value("subject","$.id")
            if not user_id:
                return None
            if(ace == "subject" and attribute_path == "$.email"):
                user = User.query.filter_by(id = user_id).first()
                user_email = user.get_email()
                return user_email
            return None
    
    class TimestampAttributeProvider(AttributeProvider):
        def get_attribute_value(self, ace, attribute_path,ctx):
            print(f"accessed 1, timestamp")
            if(attribute_path == "$.timestamp"):
                print(f"accessed, current timestamp:{datetime.now().timestamp()}")
                return datetime.now().timestamp()
            return None

    class OtherAttributeProvider(AttributeProvider):
        def get_attribute_value(self, ace: str, attribute_path: str, ctx):
            # Assume attribute_path is in the form "$.<attribute_name>"
            attr_name = re.search("[a-zA-Z]+", attribute_path).group().lower()
            print("attribute_path: ", attribute_path)
            print("attr_name: ", attr_name)
            # attr_value = flask.session.get(attr_name, None)
            attr_value = auth_attributes.get(attr_name, None)
            if attr_value:
                print("attr_value: ", attr_value)
                return attr_value
            if attr_name not in other_attributes:
                other_attributes.append(attr_name)
            return None

    # Name: ryan, Email:yunboryan@gmail.com

    request_json = request.get_json()
    thing_id = request_json['thing_id']
    policy_location = request_json['location']

    client = MongoClient()
    storage = MongoStorage(client, db_name=policy_location)
    print("storage.get_for_target(resource_id=str(thing_id)): ")
    for p in storage.get_for_target("", str(thing_id), ""):
        print(p)
        # TODO: PRINT OUT AND SEE
        p.rules.subject.keys()
        p.rules.context.keys()
    print(" END storage.get_for_target(resource_id=str(thing_id))")
    pdp = PDP(storage,EvaluationAlgorithm.HIGHEST_PRIORITY,[EmailAttributeProvider(),UserIdAttributeProvider(),TimestampAttributeProvider(),OtherAttributeProvider()])

    AccessRequest_json = {
        "subject": {
            "id": '', 
            "attributes": {}
        },
        "resource": {
            "id": str(thing_id), 
            "attributes": {}
        },
        "action": {
            "id": "", 
            "attributes": {"method": "get"}
        },
        "context": {
            "timestamp":{}
        }
    }
    # for attribute in other_attributes_returned:
    #     # ...AccessRequest['subject']['address'] = "new york"
    access_request = AccessRequest.from_json(AccessRequest_json)
    other_attributes = remove_attr_accessed(other_attributes)
    if pdp.is_allowed(access_request):
        flask.session['authorized'] = 0
        print("pdp.is_allowed(access_request): return 1")
        return 1
    elif other_attributes:
        print("other_attributes: ", other_attributes)
        return 2
    else:
        print("pdp.is_allowed(access_request): return 0")
        flask.session['authorized'] = 0
        return 0


def remove_attr_accessed(other_attributes):
    for att in other_attributes:
        if auth_attributes.get(att, None) is not None:
            other_attributes.remove(att)
    return other_attributes


auth_attributes = {"address": None, "weather": None}
policy_request = {"policy_request": None}


def is_policy_request(policy: dict, keys: list = []) -> bool:
    if policy is None:
        return False
    for key in keys:
        if key not in policy:
            return False
    return True


