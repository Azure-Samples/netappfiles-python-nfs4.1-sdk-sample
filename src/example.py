# example.py Code Sample
#
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
import sample_utils
import resource_uri_utils
import azure.mgmt.netapp.models
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.netapp import AzureNetAppFilesManagementClient
from azure.mgmt.netapp.models import NetAppAccount, \
    CapacityPool, \
    Volume, \
    ExportPolicyRule, \
    VolumePropertiesExportPolicy
from msrestazure.azure_exceptions import CloudError
from sample_utils import console_output

SHOULD_CLEANUP = False
LOCATION = 'eastus'
RESOURCE_GROUP_NAME = 'anf01-rg'
VNET_NAME = 'vnet-01'
SUBNET_NAME = 'anf-sn'
VNET_RESOURCE_GROUP_NAME = 'anf01-rg'
ANF_ACCOUNT_NAME = Haikunator().haikunate(delimiter='')
CAPACITYPOOL_NAME = "Pool01"
CAPACITYPOOL_SERVICE_LEVEL = "Standard"
CAPACITYPOOL_SIZE = 4398046511104  # 4TiB
VOLUME_NAME = 'Vol-{}-{}'.format(ANF_ACCOUNT_NAME, CAPACITYPOOL_NAME)
VOLUME_USAGE_QUOTA = 107374182400  # 100GiB


def create_account(client, resource_group_name, anf_account_name, location,
                   tags=None):
    """Creates an Azure NetApp Files Account

    Function that creates an Azure NetApp Account, which requires building the
    account body object first.

    Args:
        client (AzureNetAppFilesManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            account will be created
        location (string): Azure short name of the region where resource will
            be deployed
        tags (object): Optional. Key-value pairs to tag the resource, default
            value is None. E.g. {'cc':'1234','dept':'IT'}

    Returns:
        NetAppAccount: Returns the newly created NetAppAccount resource
    """

    account_body = NetAppAccount(location=location, tags=tags)

    return client.accounts.create_or_update(account_body,
                                            resource_group_name,
                                            anf_account_name).result()


def create_capacitypool_async(client, resource_group_name, anf_account_name,
                              capacitypool_name, service_level, size, location,
                              tags=None):
    """Creates a capacity pool within an account

    Function that creates a Capacity Pool, capacity pools are needed to define
    maximum service level and capacity.

    Args:
        client (AzureNetAppFilesManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            capacity pool will be created, it needs to be the same as the
            Account
        anf_account_name (string): Name of the Azure NetApp Files Account where
            the capacity pool will be created
        capacitypool_name (string): Capacity pool name
        service_level (string): Desired service level for this new capacity
            pool, valid values are "Ultra","Premium","Standard"
        size (long): Capacity pool size, values range from 4398046511104
            (4TiB) to 549755813888000 (500TiB)
        location (string): Azure short name of the region where resource will
            be deployed, needs to be the same as the account
        tags (object): Optional. Key-value pairs to tag the resource, default
            value is None. E.g. {'cc':'1234','dept':'IT'}

    Returns:
        CapacityPool: Returns the newly created capacity pool resource
    """

    capacitypool_body = CapacityPool(
        location=location,
        service_level=service_level,
        size=size)

    return client.pools.create_or_update(capacitypool_body,
                                         resource_group_name,
                                         anf_account_name,
                                         capacitypool_name).result()


def create_volume(client, resource_group_name, anf_account_name,
                  capacitypool_name, volume_name, volume_usage_quota,
                  service_level, subnet_id, location, tags=None):
    """Creates a volume within a capacity pool

    Function that in this example creates a NFSv4.1 volume within a capacity
    pool, as a note service level needs to be the same as the capacity pool.
    This function also defines the volume body as the configuration settings
    of the new volume.

    Args:
        client (AzureNetAppFilesManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            volume will be created, it needs to be the same as the account
        anf_account_name (string): Name of the Azure NetApp Files Account where
            the capacity pool holding the volume exists
        capacitypool_name (string): Capacity pool name where volume will be
            created
        volume_name (string): Volume name
        volume_usage_quota (long): Volume size in bytes, minimum value is
            107374182400 (100GiB), maximum value is 109951162777600 (100TiB)
        service_level (string): Volume service level, needs to be the same as
            the capacity pool, valid values are "Ultra","Premium","Standard"
        subnet_id (string): Subnet resource id of the delegated to ANF Volumes
            subnet
        location (string): Azure short name of the region where resource will
            be deployed, needs to be the same as the account
        tags (object): Optional. Key-value pairs to tag the resource, default
            value is None. E.g. {'cc':'1234','dept':'IT'}

    Returns:
        Volume: Returns the newly created volume resource
    """                 

    rule_list = [ExportPolicyRule(
        allowed_clients="0.0.0.0/0",
        cifs=False,
        nfsv3=False,
        nfsv41=True,
        rule_index=1,
        unix_read_only=False,
        unix_read_write=True)]

    export_policies = VolumePropertiesExportPolicy(
        rules=rule_list)

    volume_body = Volume(
        usage_threshold=volume_usage_quota,
        creation_token=volume_name,
        location=location,
        service_level=service_level,
        subnet_id=subnet_id,
        protocol_types=["NFSv4.1"],
        export_policy=export_policies)

    return client.volumes.create_or_update(volume_body,
                                           resource_group_name,
                                           anf_account_name,
                                           capacitypool_name,
                                           volume_name).result()


def run_example():
    """Azure NetApp Files SDK management example."""

    print("Azure NetAppFiles Python SDK Sample - Sample project that performs CRUD management operations with Azure NetApp Files SDK with Python")
    print("-------------------------------------------------------------------------------------------------------------------------------------")

    # Creating the Azure NetApp Files Client with an Application
    # (service principal) token provider
    credentials, subscription_id = sample_utils.get_credentials()
    anf_client = AzureNetAppFilesManagementClient(
        credentials, subscription_id)

    # Creating an Azure NetApp Account
    console_output('Creating Azure NetApp Files account ...')
    account = None
    try:
        account = create_account(anf_client,
                                 RESOURCE_GROUP_NAME,
                                 ANF_ACCOUNT_NAME,
                                 LOCATION)
        console_output(
            '\tAccount successfully created, resource id: {}'
            .format(account.id))
    except CloudError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Creating a Capacity Pool
    console_output('Creating Capacity Pool ...')
    capacity_pool = None
    try:
        capacity_pool = create_capacitypool_async(anf_client,
                                                  RESOURCE_GROUP_NAME,
                                                  account.name,
                                                  CAPACITYPOOL_NAME,
                                                  CAPACITYPOOL_SERVICE_LEVEL,
                                                  CAPACITYPOOL_SIZE,
                                                  LOCATION)
        console_output('\tCapacity Pool successfully created, resource id: {}'
                       .format(capacity_pool.id))
    except CloudError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Creating a Volume
    #
    # Note: With exception of Accounts, all resources with Name property
    # returns a relative path up to the name and to use this property in
    # other methods, like Get for example, the argument needs to be
    # sanitized and just the actual name needs to be used (the hierarchy
    # needs to be cleaned up in the name).
    # Capacity Pool Name property example: "pmarques-anf01/pool01"
    # "pool01" is the actual name that needs to be used instead. Below
    # you will see a sample function that parses the name from its
    # resource id: resource_uri_utils.get_anf_capacitypool()
    console_output('Creating a Volume ...')
    subnet_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(
        subscription_id, VNET_RESOURCE_GROUP_NAME, VNET_NAME, SUBNET_NAME)
    volume = None
    try:
        pool_name = resource_uri_utils.get_anf_capacitypool(capacity_pool.id)

        volume = create_volume(anf_client,
                               RESOURCE_GROUP_NAME,
                               account.name,
                               pool_name,
                               VOLUME_NAME,
                               VOLUME_USAGE_QUOTA,
                               CAPACITYPOOL_SERVICE_LEVEL,
                               subnet_id,
                               LOCATION)
        console_output(
            '\tVolume successfully created, resource id: {}'.format(volume.id))
    except CloudError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Cleaning up volumes - for this to happen, please change the value of
    # SHOULD_CLEANUP variable to true.
    # Note: Volume deletion operations at the RP level are executed serially
    if SHOULD_CLEANUP:
        # Cleaning up. This process needs to start the cleanup from the
        # innermost resources down in the hierarchy chain in our case
        # Snapshots->Volumes->Capacity Pools->Accounts
        console_output('Cleaning up...')

        console_output("\tDeleting Volumes...")
        try:
            volume_ids = [volume.id]
            for volume_id in volume_ids:
                console_output("\t\tDeleting {}".format(volume_id))
                anf_client.volumes.delete(RESOURCE_GROUP_NAME,
                                          account.name,
                                          resource_uri_utils.get_anf_capacitypool(
                                              capacity_pool.id),
                                          resource_uri_utils.get_anf_volume(
                                              volume_id)
                                          ).wait()

                # ARM Workaround to wait the deletion complete/propagate
                sample_utils.wait_for_no_anf_resource(anf_client, volume_id)

                console_output('\t\tDeleted Volume: {}'.format(volume_id))
        except CloudError as ex:
            console_output(
                'An error ocurred. Error details: {}'.format(ex.message))
            raise

        # Cleaning up Capacity Pool
        console_output("\tDeleting Capacity Pool {} ...".format(
            resource_uri_utils.get_anf_capacitypool(capacity_pool.id)))
        try:
            anf_client.pools.delete(RESOURCE_GROUP_NAME,
                                    account.name,
                                    resource_uri_utils.get_anf_capacitypool(
                                        capacity_pool.id)
                                    ).wait()

            # ARM Workaround to wait the deletion complete/propagate
            sample_utils.wait_for_no_anf_resource(anf_client, capacity_pool.id)

            console_output(
                '\t\tDeleted Capacity Pool: {}'.format(capacity_pool.id))
        except CloudError as ex:
            console_output(
                'An error ocurred. Error details: {}'.format(ex.message))
            raise

        # Cleaning up Account
        console_output("\tDeleting Account {} ...".format(account.name))
        try:
            anf_client.accounts.delete(RESOURCE_GROUP_NAME, account.name)
            console_output('\t\tDeleted Account: {}'.format(account.id))
        except CloudError as ex:
            console_output(
                'An error ocurred. Error details: {}'.format(ex.message))
            raise


# This script expects that the following environment var are set:
#
# AZURE_AUTH_LOCATION: contains path for azureauth.json file
#
# File content (and how to generate) is documented at
# https://docs.microsoft.com/en-us/dotnet/azure/dotnet-sdk-azure-authenticate?view=azure-dotnet

if __name__ == "__main__":

    run_example()
