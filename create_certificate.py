#!/usr/bin/env python3
from acme import client
from acme import messages
from acme import crypto_util
from acme import challenges
from acme import standalone
from contextlib import contextmanager
import OpenSSL
import base64
import josepy as jose
from acme.client import ClientNetwork, ClientV2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import os
from ftplib import FTP

DIRECTORY_URL = 'https://acme-staging-v02.api.letsencrypt.org/directory'
#DIRECTORY_URL = 'https://acme-v02.api.letsencrypt.org/directory'
USER_AGENT = 'python-acme-example'
ACC_KEY_BITS = 2048
CERT_PKEY_BITS = 2048
PORT = 80

def token_decode(token):
    """ decode base64 encoded strings from CA responses"""
    return base64.urlsafe_b64encode(token).decode('utf8').replace("=", "")

def challenge_upload(ftp_server, ftp_user, ftp_pass, ftp_dir, challenges):
    """ upload file to ftp server, used for challenge files"""
    f = FTP(ftp_server)
    if f.login(ftp_user, ftp_pass):
        f.cwd(ftp_dir)
        for c in challenges:
            f.storlines('STOR ' + str(os.path.basename(c)), open(c, 'rb'))
        f.quit()
    else:
        return False

    return True

def create_certificate(domains, email, ftp_server, ftp_user, ftp_pass, local_path):
    """ register account, request certificate, prove challenge, save certificate"""
    acc_key = jose.JWKRSA(
        key=rsa.generate_private_key(public_exponent=65537,
                                     key_size=ACC_KEY_BITS,
                                     backend=default_backend()))

    net = client.ClientNetwork(acc_key, user_agent=USER_AGENT)
    directory = messages.Directory.from_json(net.get(DIRECTORY_URL).json())
    client_acme = client.ClientV2(directory, net=net)

    regr = client_acme.new_account(
        messages.NewRegistration.from_data(
           email=email, terms_of_service_agreed=True))

    pkey_pem, csr_pem = new_csr_comp([d.url for d in domains])

    # write domain key to local path
    print("- Saving domain key file")
    k = open(os.path.join(local_path, 'domain-key.txt'),'w')
    k.write(pkey_pem.decode('utf-8'))
    k.close()

    # write domain csr to local path
    print("- Saving domain csr file")
    k2 = open(os.path.join(local_path, 'domain-csr.txt'),'w')
    k2.write(csr_pem.decode('utf-8'))
    k2.close()

    print("- Placing new order")
    orderr = client_acme.new_order(csr_pem)

    print("- Selecting HTTP-01 challenge")
    challb = select_http01_chall(orderr)

    for i, c in enumerate(challb):
        # get challenge token & thumbprint
        token_file_name = token_decode(c.chall.token)   
        token_file_content = token_file_name + str('.') + token_decode(acc_key.thumbprint())

        # save challenge file(s)
        print(" ")
        print("- Responding to challenge (" + str(i+1) + '/' + str(len(challb)) + ')')
        print("-- Creating local challenge file")
        f = open(os.path.join(local_path, token_file_name), 'w')
        f.write(token_file_content)
        f.close()

        # upload file
        # to do: check unsuccessful
        print("-- Uploading challenge file to server")
        challenge_upload(ftp_server, ftp_user, ftp_pass, domains[i].challenge_path, [os.path.join(local_path, token_file_name)])

        # delete local challenge file
        print("-- Deleting local challenge file")
        os.remove(os.path.join(local_path, token_file_name))

        print("-- Validating challenge")
        perform_http01(client_acme, c, orderr)

    # confirm validations done
    print("- Informing CA that all challenges complete")
    try:
        fullchain_pem = confirm_challenges_complete(client_acme, orderr)

        # write certificate file
        print("- Creating local cert file in " + str(local_path))
        c = open(os.path.join(local_path, 'domain.crt'),'w')
        c.write(fullchain_pem)
        c.close()

        print('- Certificate created')
        return True
        
    except:
        print('- Certificate creation failed')
        return False

def confirm_challenges_complete(client_acme, orderr):
    """Let CA know that all challenges are completed."""
    finalized_orderr = client_acme.poll_and_finalize(orderr)
    return finalized_orderr.fullchain_pem

# thank you -- below is from
# https://github.com/certbot/certbot/blob/master/acme/examples/http01_example.py
def new_csr_comp(domain_name, pkey_pem=None):
    """Create certificate signing request."""
    if pkey_pem is None:
        # Create private key.
        pkey = OpenSSL.crypto.PKey()
        pkey.generate_key(OpenSSL.crypto.TYPE_RSA, CERT_PKEY_BITS)
        pkey_pem = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM,
                                                  pkey)
    csr_pem = crypto_util.make_csr(pkey_pem, domain_name)
    return pkey_pem, csr_pem

@contextmanager
def challenge_server(http_01_resources):
    """Manage standalone server set up and shutdown."""

    # Setting up a fake server that binds at PORT and any address.
    address = ('', PORT)
    try:
        servers = standalone.HTTP01DualNetworkedServers(address,
                                                        http_01_resources)
        # Start client standalone web server.
        servers.serve_forever()
        yield servers
    finally:
        # Shutdown client web server and unbind from PORT
        servers.shutdown_and_server_close()

def select_http01_chall(orderr):
    """Extract authorization resource from within order resource."""
    # Authorization Resource: authz.
    # This object holds the offered challenges by the server and their status.
    authz_list = orderr.authorizations
    challenge_list = []
    for authz in authz_list:
        # Choosing challenge.
        # authz.body.challenges is a set of ChallengeBody objects.
        for i in authz.body.challenges:
            # Find the supported challenge.
            if isinstance(i.chall, challenges.HTTP01):
                challenge_list.append(i)

    if len(challenge_list) > 0:
        return challenge_list
    else:
        raise Exception('HTTP-01 challenge was not offered by the CA server.')

def perform_http01(client_acme, challb, orderr):
    """Set up standalone webserver and perform HTTP-01 challenge."""

    response, validation = challb.response_and_validation(client_acme.net.key)

    resource = standalone.HTTP01RequestHandler.HTTP01Resource(
        chall=challb.chall, response=response, validation=validation)

    with challenge_server({resource}):
        # Let the CA server know that we are ready for the challenge.
        client_acme.answer_challenge(challb, response)

        # Wait for challenge status and then issue a certificate.
        # It is possible to set a deadline time.
        # finalized_orderr = client_acme.poll_and_finalize(orderr)

    # commented out, multi-domain use need separate answer & finalization
    # return finalized_orderr.fullchain_pem
    return True
