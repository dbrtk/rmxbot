""" Extra methods to be used on dictionaries.
"""
import collections
import logging


def update(origdict, updict):
    """
    Updating a nested dictionary.
    """
    for k, v in iter(updict.items()):
        if isinstance(v, collections.Mapping):
            nestdict = update(origdict.get(k, {}), v)
            origdict[k] = nestdict
        else:
            origdict[k] = updict[k]
    return origdict


def get_nested(dic, keys):
    """
    Given a nested dictionary and a list of keys, returns the value of the
    nested field as defined by the list of keys.
    If failure, will throw a KeyError.
    """
    for key in keys[:-1]:
        dic = dic.get(key, {})
    return dic[keys[-1]]


def set_nested(dic, keys, value):
    """
    Givens;
     1. a nested dictionary;
     2. a list of keys;
     3. a value.
    Sets the given value for the nested field. See example below:
     keys = ['groupName', 'subGroupName', 'fieldName']
     value = "the value"
    will result in :
    {
        'groupName': {
            'subGroupName': {
                'fieldName': 'the value'
            }
        }
    }
    """
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value
    return True


def remove_nested(dic, keys):
    """
    Givens;
     1. a nested dictionary;
     2. a list of keys.
    removes the nested field-value pair.
    """

    for key in keys[:-1]:
        dic = dic.get(key)
    del dic[keys[-1]]
    try:
        assert not keys[-1] in dic
    except AssertionError as e:
        logging.error(e)
        raise AssertionError(e)
    else:
        return dic
