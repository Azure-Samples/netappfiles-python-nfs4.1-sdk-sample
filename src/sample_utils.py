# sample_utils.py Code Sample
#
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""sample_utils.py code sample

SDK related functions to be consumed by the example.py sample code.

"""

import os
import json
import time
from datetime import datetime
from azure.core.exceptions import HttpResponseError, \
    ResourceNotFoundError
from azure.identity import ClientSecretCredential
import resource_uri_utils

def print_header(header_string):
    """Prints a header output

    Args:
        header_string (string): String value to output
    """
    print(header_string)
    print('-' * len(header_string))


def get_credentials():
    """Gets the file system secured secret

    Gets the service principal credential file from a folder path defined the
    AZURE_AUTH_LOCATION environment variable to perform authentication.

    Returns:
        ServicePrincipalCredentials: Returns the Service Principal Credential object
        string: Returns the subscription id associated by default to the service principal
    """

    credential_file = os.environ.get('AZURE_AUTH_LOCATION')

    with open(credential_file) as credential_file_contents:
        credential_info = json.load(credential_file_contents)

    subscription_id = credential_info['subscriptionId']

    credentials = ClientSecretCredential(
        tenant_id=credential_info['tenantId'],
        client_id=credential_info['clientId'],
        client_secret=credential_info['clientSecret']
    )
    return credentials, subscription_id


def console_output(message):
    """Outputs a string to the console

    Outputs a string with date/time

    Args:
        message (string): String value to be displayed
    """
    print('{}: {}'.format(datetime.now(), message))


def get_bytes_in_tib(size):
    """Converts a value from bytes to TiB

    This function converts a value in bytes into TiB

    Args:
        size (long): Size in bytes

    Returns:
        int: Returns value in TiB
    """
    return size / 1024 / 1024 / 1024 / 1024


def get_tib_in_bytes(size):
    """Converts a value from TiB to bytes

    This function converts a value in bytes into TiB

    Args:
        size (int): Size in TiB

    Returns:
        long: Returns value in bytes
    """
    return size * 1024 * 1024 * 1024 * 1024


def wait_for_no_anf_resource(client, resource_id, interval_in_sec=10,
                             retries=60):
    """Waits for specific anf resource don't exist

    This function checks if a specific ANF resource that was recently delete
    stops existing. It breaks the wait if resource is not found anymore or
    if polling reached out maximum retries.

    Args:
        client (NetAppManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_id (string): Resource Id of the resource to be checked upon
        interval_in_sec (int): Interval used between checks
        retires (int): Number of times a poll will be performed
    """

    for _ in range(0, retries):
        time.sleep(interval_in_sec)
        try:
            if resource_uri_utils.is_anf_snapshot(resource_id):
                client.snapshots.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id),
                    resource_uri_utils.get_anf_capacity_pool(resource_id),
                    resource_uri_utils.get_anf_volume(resource_id),
                    resource_uri_utils.get_anf_snapshot(resource_id)
                )
            elif resource_uri_utils.is_anf_volume(resource_id):
                client.volumes.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id),
                    resource_uri_utils.get_anf_capacity_pool(resource_id),
                    resource_uri_utils.get_anf_volume(resource_id)
                )
            elif resource_uri_utils.is_anf_capacity_pool(resource_id):
                client.pools.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id),
                    resource_uri_utils.get_anf_capacity_pool(resource_id)
                )
            elif resource_uri_utils.is_anf_account(resource_id):
                client.accounts.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id)
                )
        except ResourceNotFoundError:
            break


def wait_for_anf_resource(client, resource_id, interval_in_sec=10, retries=60):
    """Waits for specific anf resource start existing

    This function checks if a specific ANF resource that was recently created
    is already being able to be polled. It breaks the wait if resource is found
    or if polling reached out maximum retries.

    Args:
        client (NetAppManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_id (string): Resource Id of the resource to be checked upon
        interval_in_sec (int): Interval used between checks
        retires (int): Number of times a poll will be performed
    """

    for _ in range(0, retries):
        time.sleep(interval_in_sec)
        try:
            if resource_uri_utils.is_anf_snapshot(resource_id):
                client.snapshots.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id),
                    resource_uri_utils.get_anf_capacity_pool(resource_id),
                    resource_uri_utils.get_anf_volume(resource_id),
                    resource_uri_utils.get_anf_snapshot(resource_id)
                )
            elif resource_uri_utils.is_anf_volume(resource_id):
                client.volumes.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id),
                    resource_uri_utils.get_anf_capacity_pool(resource_id),
                    resource_uri_utils.get_anf_volume(resource_id)
                )
            elif resource_uri_utils.is_anf_capacity_pool(resource_id):
                client.pools.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id),
                    resource_uri_utils.get_anf_capacity_pool(resource_id)
                )
            elif resource_uri_utils.is_anf_account(resource_id):
                client.accounts.get(
                    resource_uri_utils.get_resource_group(resource_id),
                    resource_uri_utils.get_anf_account(resource_id)
                )
            break
        except ResourceNotFoundError:
            pass


def resource_exists(resource_client, resource_id, api_version):
    """Generic function to check for existing Azure function

    This function checks if a specific Azure resource exists based on its
    resource Id.

    Args:
        client (ResourceManagementClient): Azure Resource Manager Client
        resource_id (string): Resource Id of the resource to be checked upon
        api_version (string): Resource provider specific API version
    """

    try:
        return resource_client.resources.check_existence_by_id(resource_id, api_version)
    except HttpResponseError as e:
        if e.status_code == 405: # HEAD not supported
            try:
                resource_client.resources.get_by_id(resource_id, api_version)
                return True
            except HttpResponseError as ie:
                if ie.status_code == 404:
                    return False
        raise # If not 405 or 404, not expected
