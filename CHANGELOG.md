## Azure NetAppFiles NFSv 4.1 SDK Sample for Python Changelog

- [1.0.2 (2021-07-15)](#102-2021-07-15)
- [1.0.1 (2019-11-19)](#101-2019-11-19)
- [1.0.0 (2019-10-22)](#100-2019-10-22)

# 1.0.2 (2021-07-15)

*Features*
* Updated azure-mgmt-netapp version requirement to 3.0.0
* Updated azure-mgmt-resource version requirement to 18.0.0
* Applied code changes required by new SDK versions
* Added version requirement of 1.6.0 for azure-identity for new service principal credentials
* Cleaned code to improve pylint score

*Bug Fixes*
* N/A

*Breaking Changes*
* N/A

# 1.0.1 (2019-11-19)

*Features*
* Chagned console app header print statements for print_header function
* For cleaner code replaced multiple single line comments with multiline comments
* Removed active_directories from create_account function since SMB volumes are not being used in this sample
  
*Bug Fixes*
* Fixed function name get_anf_capacity_pool


# 1.0.0 (2019-10-22)

*Features*
* Initial commit

*Bug Fixes*
* N/A

*Breaking Changes*
* N/A
