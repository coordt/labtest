================
Setting up users
================

Lab Test's SSH setup is based on a great article about `managing SSH access through IAM`_\ . The IAM documentation has more information about `using SSH keys and SSH with AWS CodeCommit`_.

1. Get the user's public key. It will look something like::

    ssh-rsa EXAMPLE-AfICCQD6m7oRw0uXOjANBgkqhkiG9w0BAQUFADCBiDELMAkGA1UEBhMCVVMxCzAJB
    gNVBAgTAldBMRAwDgYDVQQHEwdTZWF0dGxlMQ8wDQYDVQQKEwZBbWF6b24xFDASBgNVBAsTC0lBTSBDb2
    5zb2xlMRIwEAYDVQQDEwlUZXN0Q2lsYWMxHzAdBgkqhkiG9w0BCQEWEG5vb25lQGFtYXpvbi5jb20wHhc
    NMTEwNDI1MjA0NTIxWhcNMTIwNDI0MjA0NTIxWjCBiDELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAldBMRAw
    DgYDVQQHEwdTZWF0dGxlMQ8wDQYDVQQKEwZBbWF6b24xFDAS=EXAMPLE user-name@ip-192-0-2-137

2. Sign into the `IAM console`_.
3. In the IAM console, in the navigation pane, choose **Users**.

   .. image::  /images/ssh-users/select-user.png
       :alt: The IAM console

4. Click on the appropriate user. (If you need to create the user, `refer to the IAM documentation`_).
5. On the user details page, choose the **Security Credentials** tab.

   .. image::  /images/ssh-users/user-security-cred-tab.png
       :alt: The IAM User's security credentials tab

6. Scroll down to the **SSH keys for AWS CodeCommit** section.

   .. image:: /images/ssh-users/ssh-keys-for-code-commit-section.png
       :alt: The SSH keys for code commit section of the user page

7. Choose **Upload SSH public key**.
8. Paste the contents of the SSH public key into the field, and then choose **Upload SSH public key**.

   .. image::  /images/ssh-users/paste-public-key.png
       :alt: The upload SSH public key dialog

9. Done!

.. note::

    Some symbols in the IAM user name are changed for SSH. Specifically:

    - ``+`` to ``.plus.``
    - ``=`` to ``.equal.``
    - ``,`` to ``.comma.``
    - ``@`` to ``.at.``

    Also the length of the converted username must be 32 characters or less.


.. _managing ssh access through iam: https://cloudonaut.io/manage-aws-ec2-ssh-access-with-iam/
.. _refer to the iam documentation: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html
.. _using ssh keys and ssh with aws codecommit: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_ssh-keys.html
.. _iam console: https://console.aws.amazon.com/iam/
