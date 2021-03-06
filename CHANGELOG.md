# Changelog

## 0.4.8 (2018-06-01)

### New

* Adds the `before_start_command` configuration option. [Corey Oordt]

* Added pytest-html for html reports. [Corey Oordt]

### Updates

* Reorganized documentation around new homepage. [Corey Oordt]

* Adding links to home page and fixed latex and other rendering. [Corey Oordt]

* Added new Boston.gov branding fonts to the theme. [Corey Oordt]


## 0.4.7 (2018-05-31)

### New

* Added ability to wait for the Docker MySQL service to start before continuing. [Corey Oordt]

### Updates

* More documentation editing. [Corey Oordt]

* Added a homepage to the docs. [Corey Oordt]

* Rearranging documentation for better accessibility. [Corey Oordt]


## 0.4.6 (2018-05-30)

### Fix

* Updated that test again. [Corey Oordt]


## 0.4.5 (2018-05-30)

### Fix

* Tixed a test that was non-determinative. [Corey Oordt]


## 0.4.4 (2018-05-30)

### New

* Changes the string $VIRTUAL_HOST in environment variables to the actual virtual host name when writing the environment. [Corey Oordt]

* Added docker mysql tests. [Corey Oordt]


## 0.4.3 (2018-05-29)

### Fix

* Changed the name of the container in the systemd template. [Corey Oordt]


## 0.4.2 (2018-05-29)

### Updates

* Changed the naming convention of the code container to allow for easier container manipulation. [Corey Oordt]

### Fix

* Changed the import from providers to service_providers when deleting an experiment. [Corey Oordt]

* Changed the import of ConfigParser for python 2.7. [Corey Oordt]


## 0.4.1 (2018-05-29)

[Fix] Actually merged the 0.4 branch this time.

## 0.4 (2018-05-29)

### New

* Provided new tests and mock SSH server. [Corey Oordt]

* Added a local script state provider. [Corey Oordt]

* Added secret providers to providers module. [Corey Oordt]

* Added a version command to print the version. [Corey Oordt]

* Added S3 state provider. [Corey Oordt]

* Added basic secret management using AWS KMS. [Corey Oordt]

### Updates

* Updated testing options. [Corey Oordt]

* Provided a more robust checking for starting services. [Corey Oordt]

* Provide better output when deleting and updating experiments. [Corey Oordt]

* Created a standard way to set up the environment. [Corey Oordt]

* Minor cleanup to config. [Corey Oordt]

* Does a better job at checking if the MySQL configuration has changed and explains what has changed. [Corey Oordt]

* Alphabetized the configuration to make it easier to look for settings. [Corey Oordt]

* Added http:// in front of the URL of the experiment and the successful completion of a create. [Corey Oordt]

* Refactored several common remote filesystem commands into a single module for convenience. [Corey Oordt]

### Fix

* Better hide and some output and write the correct mode on the docker-build file. [Corey Oordt]

* Checks if backing_service_configs is in env before using. [Corey Oordt]

* The pruning of volumes and containers now uses the correct docker command. [Corey Oordt]

### Other

* Added a splash page to use for a default server. [Corey Oordt]

* Added auto section bookmarking and removed unused manual bookmarks. [Corey Oordt]

* Update the docstring for the check services config. [Corey Oordt]


## 0.3.5 (2018-05-25)

### Fix

* Update now sets the docker_image correctly. [Corey Oordt]


## 0.3.4 (2018-05-25)

### Fix

* Update now sets appropriate service_name and network_name. [Corey Oordt]


## 0.3.3 (2018-05-25)

### Fix

* Update now calls setup_backing_services. [Corey Oordt]


## 0.3.2 (2018-05-23)

### Fix

* Included the templates for the docker provider. [Corey Oordt]


## 0.3.1 (2018-05-23)

### Fix

* Fixed the packaging so that the provider submodule is included. [Corey Oordt]


## 0.3.0 (2018-05-21)

### New

* Updated example testserver cloud formation file to include rexray. [Corey Oordt]

* Added individual Docker bridge networks for each experiment. [Corey Oordt]

* Added defaults for services, app_build_image, and app_build_command. [Corey Oordt]

* Created a base provider class to make it easy to create different backing services using different providers. Docker mysql is the first. [Corey Oordt]

### Updates

* Changed layout of the experiment. Improved console status messages. [Corey Oordt]

  Code is now checked out in a subdirectory named 'code' to isolate it from other files labtest might write for state reasons.

* Improved the output of the check-config command. Provides better indenting and bolds the field names. [Corey Oordt]

* Moved aws.py into a submodule to separate parts like ECR from RDS. [Corey Oordt]

* Updated the readme to make more sense. [Corey Oordt]

* Set the Fabric version to <2.0 since 2.0 was just released and there are significant changes required to update. [Corey Oordt]

* Moved the functions relating to OS services into one module for consistency. [Corey Oordt]


### Fix

* Update the makefile. [Corey Oordt]

* Ignoring the SASS and node stuff. [Corey Oordt]

* Removing old --links since we moved to user-defined bridge networks. [Corey Oordt]

* Removing the redundant _setup_service. [Corey Oordt]

* Including the instance.list command. [Corey Oordt]

* Moved the cd command up in the docker build command template so it would be in the actual git repository. [Corey Oordt]

### Documentation

* Fixing readable theme config again. [Corey Oordt]

* Fix the unused import for sphinx_readable_theme. [Corey Oordt]

* Added new zen theme. [Corey Oordt]

* General cleanup of API docs, makefile and readme. [Corey Oordt]

* Updated documentation. [Corey Oordt]

  - Removed some redundant PNGs
  - Updated some SVGs to show workflow better
  - Added captions to images where appropriate
  - Fixed admonitions
  - Standardized the formatting of configuration options
  - General clean up of markup to provide better formatting

* Added napoleon plugin so I can better format my doc strings. [Corey Oordt]

* Added a fulltoc plugin to sphinx. [Corey Oordt]

* Moved the autogenerated API docs to the API directory in the make command. [Corey Oordt]


## 0.2.6 (2018-05-08)

### Fix

* Change references from HISTORY.rst to CHANGELOG.md. [Corey Oordt]


## 0.2.5 (2018-05-08)

### Updates

* Renamed HISTORY.rst to CHANGELOG.md. [Corey Oordt]

### Fix

* Cast strings written by io.StringIO to unicode. [Corey Oordt]


## 0.2.4 (2018-05-07)

### Fix

* Fixing another python 3 thing for Click. [Corey Oordt]


## 0.2.3 (2018-05-07)

### Fix

* Fixing the python_requires keyword. [Corey Oordt]

* Fixing the repositories and stuff in configuration files. [Corey Oordt]

### Other

* Created release commands for patch, minor and major versions in the Makefile. [Corey Oordt]

* Remove future unicode literals import due to issues with Click. [Corey Oordt]


## 0.2.2 (2018-05-07)

### Updates

* Update MANIFEST.in to include requirements. [Corey Oordt]


## 0.2.1 (2018-05-07)

### New

* Added create and delete commands. [Corey Oordt]

* Added check for branch_name availability and get it when needed. [Corey Oordt]

* Added more required configuration options. [Corey Oordt]


### Updates

* Update the travis configuration. [Corey Oordt]

* Updated Fabric commands to run with configured verbose setting. [Corey Oordt]

* Updated documentation. [Corey Oordt]

* Updated instance to use new configuration. [Corey Oordt]

* Updated configuration. [Corey Oordt]

* Updated tests. [Corey Oordt]

* Updated the requirements. [Corey Oordt]

### Fix

* Fixed the manifest. [Corey Oordt]

* Fixed method of finding the default config files. [Corey Oordt]

* Fixed the repo in the travis configuration. [Corey Oordt]

### Other

* Removed references to Python 3. [Corey Oordt]

* Python 3 compatibility, for when we can do it. [Corey Oordt]

* Always write the contents of the environment file in case changes are made to it. [Corey Oordt]

* Renamed hosts config to host. [Corey Oordt]

* Add dotenv support and configuration. [Corey Oordt]

* Initial test instance creation tasks. [Corey Oordt]

* Add a dynamic configuration class to manage configuration. [Corey Oordt]

* Add oyaml to requirements. [Corey Oordt]

* Add templates for use with setting up services and building containers. [Corey Oordt]

* Added cloudformation template for the test server. [Corey Oordt]

* Ignore .env files. [Corey Oordt]

* Renamed labtest.py to instance.py. [Corey Oordt]


