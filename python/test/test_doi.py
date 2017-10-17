from python.ServerGateway import DwebGatewayHTTPRequestHandler
import base58
from python.Multihash import Multihash
import logging

DOIURL = "metadata/doi/10.1001/jama.2009.1064"
CONTENTMULTIHASH = "5dqpnTaoMSJPpsHna58ZJHcrcJeAjW"
PDF_SHA1HEX="02efe2abec13a309916c6860de5ad8a8a096fe5d"
CONTENTHASHURL = "content/contenthash/" + CONTENTMULTIHASH
SHA1HEXMETADATAURL = "metadata/sha1hex/"+PDF_SHA1HEX
SHA1HEXCONTENTURL = "content/sha1hex/"+PDF_SHA1HEX
CONTENTSIZE = 262438
logging.basicConfig(level=logging.DEBUG)    # Log to stderr


def _processurl(url, verbose):
    # Simulates HTTP Server process - wont work for all methods
    args=url.split('/')
    method = args.pop(0)
    assert method in ("content","metadata","contenthash"), "Unsupported method for _processurl"
    namespace = args.pop(0)
    kwargs = {}
    if verbose: kwargs["verbose"]=True
    obj = DwebGatewayHTTPRequestHandler.namespaceclasses[namespace].new(namespace, *args, **kwargs)
    assert obj
    res = getattr(obj, method)(verbose=verbose)
    if verbose: logging.info(res)
    return res

def test_doi_resolve():
    verbose=False   # True to debug
    res = _processurl(DOIURL, verbose)
    assert res["Content-type"] == "application/json"
    #assert res["data"]["files"][0]["sha1_hex"] == PDF_SHA1HEX, "Would check sha1_hex, but not returning now do multihash58"
    assert res["data"]["files"][0]["multihash58"] == CONTENTMULTIHASH


def test_contenthash_resolve():
    verbose=False   # True to debug
    res = _processurl(CONTENTHASHURL, verbose)  # Simulate what the server would do with the URL
    assert res["Content-type"] == "application/pdf", "Check retrieved content of expected type"
    assert len(res["data"]) == CONTENTSIZE, "Check retrieved content of expected length"
    multihash = Multihash(data=res["data"], code=Multihash.SHA1)
    assert multihash.multihash58 == CONTENTMULTIHASH, "Check retrieved content has same multihash58_sha1 as we expect"
    assert multihash.sha1_hex == PDF_SHA1HEX, "Check retrieved content has same hex sha1 as we expect"

def test_sha1hexcontent_resolve():
    verbose = False  # True to debug
    res = _processurl(SHA1HEXCONTENTURL, verbose)  # Simulate what the server would do with the URL
    assert res["Content-type"] == "application/pdf", "Check retrieved content of expected type"
    assert len(res["data"]) == CONTENTSIZE, "Check retrieved content of expected length"
    multihash = Multihash(data=res["data"], code=Multihash.SHA1)
    assert multihash.multihash58 == CONTENTMULTIHASH, "Check retrieved content has same multihash58_sha1 as we expect"
    assert multihash.sha1_hex == PDF_SHA1HEX, "Check retrieved content has same hex sha1 as we expect"

def test_sha1hexmetadata_resolve():
    verbose = True  # True to debug
    res = _processurl(SHA1HEXMETADATAURL, verbose)  # Simulate what the server would do with the URL
    assert res["Content-type"] == "application/json", "Check retrieved content of expected type"
    assert res["data"]["size_bytes"] == CONTENTSIZE
    assert res["data"]["multihash58"] == CONTENTMULTIHASH, "Expecting multihash58 of sha1"
