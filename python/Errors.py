# encoding: utf-8

class MyBaseException(Exception):
    """
    Base class for Exceptions

    Create subclasses with parameters in their msg e.g. {message} or {name}
    and call as in: raise NewException(name="Foo");

    msgargs Arguments that slot into msg
    __str__ Returns msg expanded with msgparms
    """
    errno=0
    httperror = 500         # See BaseHTTPRequestHandler for list of errors
    msg="Generic Model Exception"   #: Parameterised string for message
    def __init__(self, **kwargs):
        self.msgargs=kwargs # Store arbitrary dict of message args (can be used ot output msg from template

    def __str__(self):
        try:
            return self.msg.format(**self.msgargs)
        except:
            return self.msg + " UNFORMATABLE ARGS:" + repr(self.msgargs)

class ToBeImplementedException(MyBaseException):
    """
    Raised when some code has not been implemented yet
    """
    httperror = 501
    msg = "{name} needs implementing"

# Note TransportError is in Transport.py

class IPFSException(MyBaseException):
    httperror = 500
    msg = "IPFS Error: {message}"

class CodingException(MyBaseException):
    httperror = 501
    msg = "Coding Error: {message}"

class SignatureException(MyBaseException):
    httperror = 501
    msg = "Signature Verification Error: {message}"

class EncryptionException(MyBaseException):
    httperror = 500  # Failure in the encryption code other than lack of authentication
    msg = "Encryption error: {message}"

class ForbiddenException(MyBaseException):
    httperror = 403     # Forbidden (WWW Authentication won't help (note there is no real HTTP error for authentication (other than HTTP authentication) failed )
    msg = "Not allowed: {what}"

class AuthenticationException(MyBaseException):
    """
    Raised when some code has not been implemented yet
    """
    httperror = 403     # Forbidden - this should be 401 except that requires extra headers (see RFC2616)
    msg = "Authentication Exception: {message}"

class IntentionallyUnimplementedException(MyBaseException):
    """
    Raised when some code has not been implemented yet
    """
    httperror = 501
    msg = "Intentionally not implemented: {message}"

class DecryptionFailException(MyBaseException):
    """
    Raised if decrypytion failed - this could be cos its the wrong (e.g. old) key
    """
    httperror = 500
    msg = "Decryption fail"

class SecurityWarning(MyBaseException):
    msg = "Security warning: {message}"


class AssertionFail(MyBaseException): #TODO-BACKPORT - console.assert on JS should throw this
    """
    Raised when something that should be True isn't - usually a coding failure or some change not propogated fully
    """
    httperror = 500
    msg = "{message}"

class TransportURLNotFound(MyBaseException):
    httperror = 404
    msg = "{url} not found"

class NoContentException(MyBaseException):
    httperror = 404
    msg = "No content found"

class MultihashError(MyBaseException):
    httperror = 500
    msg = "Multihash error {message}"

class SearchException(MyBaseException):
    httperror = 404
    msg = "{search} not found"

class TransportFileNotFound(MyBaseException):
    httperror = 404
    msg = "file {file} not found"

"""

# Following are currently obsolete - not being used in Python or JS

class PrivateKeyException(MyBaseException):
    #Raised when some code has not been implemented yet
    httperror = 500
    msg = "Operation requires Private Key, but only Public available."

"""
