"""
This is a place to put miscellaneous utilities, not specific to this project
"""
import json  # Note dont "from json import dumps" as clashes with overdefined dumps below
from datetime import datetime
import requests
import logging
from magneturi import bencode
import base64
import hashlib
import urllib.parse
from .Errors import TransportURLNotFound


def mergeoptions(a, b):
    """
    Deep merge options dictionaries
     - note this might not (yet) handle Arrays correctly but handles nested dictionaries

    :param a,b: Dictionaries
    :returns: Deep copied merge of the dictionaries
    """
    c = a.copy()
    for key in b:
        val = b[key]
        if isinstance(val, dict) and a.get(key, None):
            c[key] = mergeoptions(a[key], b[key])
        else:
            c[key] = b[key]
    return c

def dumps(obj):    #TODO-BACKPORT FROM GATEWAY TO DWEB - moved from Transport to miscutils
    """
    Convert arbitrary data into a JSON string that can be deterministically hashed or compared.
    Must be valid for loading with json.loads (unless change all calls to that).
    Exception: UnicodeDecodeError if data is binary

    :param obj:    Any
    :return: JSON string that can be deterministically hashed or compared
    """
    # ensure_ascii = False was set otherwise if try and read binary content, and embed as "data" in StructuredBlock then complains
    # if it cant convert it to UTF8. (This was an example for the Wrenchicon), but loads couldnt handle return anyway.
    # sort_keys = True so that dict always returned same way so can be hashed
    # separators = (,:) gets the most compact representation
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), default=json_default)

def loads(s):
    if isinstance(s, bytes): #TODO can remove once python upgraded to 3.6.2
        s = s.decode('utf-8')
    return json.loads(s)    # Will fail if s empty, or not json

def json_default(obj): #TODO-BACKPORT FROM GATEWAY TO DWEB - moved from Transport to miscutils
    """
    Default JSON serialiser especially for handling datetime, can add handling for other special cases here

    :param obj: Anything json dumps can't serialize
    :return: string for extended types
    """
    if isinstance(obj, datetime):    # Using isinstance rather than hasattr because __getattr__ always returns true
    #if hasattr(obj,"isoformat"):  # Especially for datetime
        return obj.isoformat()
    try:
        return obj.dumps()          # See if the object has its own dumps
    except Exception as e:
        raise TypeError("Type {0} not serializable".format(obj.__class__.__name__)) from e


def httpget(url, wantmime=False):
    # Returns the content - i.e. bytes
    #TODO-STREAMS future work to return a stream

    r = None  # So that if exception in get, r is still defined and can be tested for None
    try:
        logging.debug("GET {}".format(url))
        r = requests.get(url)
        r.raise_for_status()
        if not r.encoding or ("application/pdf" in r.headers.get('content-type')):
            data = r.content  # Should work for PDF or other binary types
        else:
            data = r.text
        if wantmime:
            return data, r.headers.get('content-type')
        else:
            return data
        #TODO-STREAM support streams in future

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
        if r is not None and (r.status_code == 404):
            raise TransportURLNotFound(url=url)
        else:
            logging.error("HTTP request failed", exc_info=True)
            raise e
    except requests.exceptions.MissingSchema as e:
            logging.error("HTTP request failed", exc_info=True)
            raise e  # For now just raise it


# Copied from https://github.com/thomasleveil/magneturi/blob/master/magneturi/__init__.py
# Which is pip3 install magneturi - but adding the HTTP url
def from_torrent_data(torrenturl, torrent_contents):
    """
    return a magnet URI given Bittorrent torrent file content
    """
    metadata = bencode.bdecode(torrent_contents)
    hash_contents = bencode.bencode(metadata['info'])
    digest = hashlib.sha1(hash_contents).digest()
    b32hash = base64.b32encode(digest)

    if 'announce-list' in metadata:
        tracker_list = ''.join(['&tr='+urllib.parse.quote_plus(t[0]) \
                                for t in metadata['announce-list']])
    elif 'announce' in metadata:
        tracker_list = '&tr='+urllib.parse.quote_plus(metadata['announce'])
    else:
        tracker_list = ''

    tracker_community_list = ''.join(['&tr='+urllib.parse.quote_plus(t) for t in [
        'wss://tracker.btorrent.xyz','wss://tracker.openwebtorrent.com' , 'wss://tracker.fastcast.nz' ]]);
    if 'url-list' in metadata:
        url_list = ''.join(['&ws='+urllib.parse.quote_plus(t) \
                                for t in metadata['url-list']])

    torrenturlparm = '&xs='+urllib.parse.quote_plus(torrenturl)

    result = ''.join([b32hash.decode('ASCII'), tracker_list, url_list,torrenturlparm,tracker_community_list])
    return 'magnet:?xt=urn:btih:%s' % result
