from fabric.api import env, run
from labtest.provider.base_secret import BaseSecret


class KMSSecret(BaseSecret):
    default_config = None

    def encrypt(self, plaintext):
        cmd = [
            'aws kms encrypt',
            f'--key-id {self.key_id}',
            f'--plaintext "{plaintext}"',
            '--query CiphertextBlob',
            '--output text',
        ]
        return run(' '.join(cmd), quiet=env.quiet)

    def decrypt(self, ciphertext):
        cmd = [
            'aws kms decrypt',
            f'--ciphertext-blob fileb://<(echo "{ciphertext}" | base64 -d)',
            '--output text',
            '--query Plaintext',
            '| base64 -d',
        ]
        return run(' '.join(cmd), quiet=env.quiet)
