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
                   tags=None, active_directories=None):

    account_body = NetAppAccount(location=location, tags=tags)

    return client.accounts.create_or_update(account_body,
                                            resource_group_name,
                                            anf_account_name).result()


def create_capacitypool_async(client, resource_group_name, anf_account_name,
                              capacitypool_name, service_level, size, location,
                              tags=None):
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
