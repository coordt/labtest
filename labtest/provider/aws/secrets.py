from fabric.api import env, run
from labtest.provider.base_secret import BaseSecret


class KMSSecret(BaseSecret):
    default_config = None

    def encrypt(self, plaintext):
        cmd = [
            'aws kms encrypt',
            '--key-id {}'.format(self.key_id),
            '--plaintext "{}"'.format(plaintext),
            '--query CiphertextBlob',
            '--output text',
        ]
        return run(' '.join(cmd), quiet=env.quiet)

    def decrypt(self, ciphertext):
        cmd = [
            'aws kms decrypt',
            '--ciphertext-blob fileb://<(echo "{}" | base64 -d)'.format(ciphertext),
            '--output text',
            '--query Plaintext',
            '| base64 -d',
        ]
        return run(' '.join(cmd), quiet=env.quiet)
