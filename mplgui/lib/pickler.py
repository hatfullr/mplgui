import pickle as _pickle
import base64

def pickle(obj):
    return base64.b64encode(_pickle.dumps(obj))

def unpickle(obj):
    return _pickle.loads(base64.b64decode(obj))
