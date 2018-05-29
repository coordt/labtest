================
Managing secrets
================

Managing secret information is difficult to do well.

The most secure ways of pasing secrets to Docker containers require specific tooling within your Docker image, and possibly additional software.

Since environment variables are the primary method of passing configuration information, we wanted to create a method that could utilize that method as it would require the least amount of change.

Secret providers
================

Secrets are managed via plugins called secret providers. Which secret provider you want to use is configured in your :ref:`state<admin/defaults_and_state/index:Default values and state>` under the ``/secrets`` key.






The default method is to encrypt secrets so they in the experiment configuration so they can be saved in the code repository.
decrypt the information on the laboratory server into the ``test.env`` file that passes the environment variables to the contianer.

The workflow looks like this:

1. Developer encodes the secret using a command:

    .. code-block:: console

        $ labtest encrypt SECRET_API_KEY=asdfghjklqwerotoyiuuzxvcbn
        Did you want to encrypt "asdfghjklqwerotoyiuuzxvcbn" for key "SECRET_API_KEY"? (No will encrypt the entire string) [y/N]: y
        [test] Executing task 'encrypt_task'

        Add this to the appropriate environment configuration section:

        SECRET_API_KEY=ENC[AQICAHiKPdb9Tw2bL4fBWqJfhZgTUythiqX7JQrHhc0oicus1QF/tvGsrs3pGB9leNIFKEv0AAAAeDB2BgkqhkiG9w0BBwagaTBnAgEAMGIGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQM9fKloF5nDS4aTGvbAgEQgDUVUen/whYrsIHpZo+bLu25aa95eqzK9aMkz/2/WQZ+XS0NEqurzj+0drzwdNeAj4mvJKg0lg==]

2. Developer adds the result to the environment

    .. code-block:: yaml

        labtest:
            environment:
                - SECRET_API_KEY=ENC[AQICAHiKPdb9Tw2bL4fBWqJfhZgTUythiqX7JQrHhc0oicus1QF/tvGsrs3pGB9leNIFKEv0AAAAeDB2BgkqhkiG9w0BBwagaTBnAgEAMGIGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQM9fKloF5nDS4aTGvbAgEQgDUVUen/whYrsIHpZo+bLu25aa95eqzK9aMkz/2/WQZ+XS0NEqurzj+0drzwdNeAj4mvJKg0lg==]

3. The value is decoded and written to the server when an experiment is created.




Setting the secret provider
===========================

LabTest looks for the secret provider configuration in key ``/secrets`` in the state provider.

.. code-block:: json
    :caption: A sample secret provider configuration in ``/secrets``

    {
        "provider": "aws",
        "service": "kms",
        "options": {
            "key_id": "aaaaaaaa-7553-4444-87c1-903903505d9a"
        }
    }

