import ruamel.yaml


class DotDict(dict):
    """A dictionary that supports dot notation as well as dictionary access notation

    Examples:
        d = DotDict() or d = DotDict({'val1':'first'})
        set attributes: d.val2 = 'second' or d['val2'] = 'second'
        get attributes: d.val2 or d['val2']
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct=None):
        super(DotDict, self).__init__(self)
        if dct:
            for key, value in dct.items():
                if hasattr(value, 'keys'):
                    value = DotDict(value)
                self[key] = value

    # 20171122 dhl I don't know why but without this method DotDict is not going to work
    # TODO explore solutions later
    def __getattr__(self, key):
        if key in self:
            return self[key]

        raise AttributeError(key)

    def as_dict(self):
        data = dict()
        for k, v in self.items():
            if isinstance(v, DotDict):
                dict_val = v.as_dict()
            else:
                dict_val = v
            data[k] = dict_val
        return data

    def save_yaml(self, file_path):
        with open(file_path, "w") as f:
            ruamel.yaml.dump(self.as_dict(), f, ruamel.yaml.RoundTripDumper)

    @classmethod
    def load_yaml(cls, file_path):
        with open(file_path, "r") as f:
            yaml_obj = ruamel.yaml.load(f, ruamel.yaml.RoundTripLoader, preserve_quotes=True)

        data = DotDict()
        return _yaml_to_dot_dict(data, yaml_obj)


def _yaml_to_dot_dict(data, yaml_obj):

    for key, value in yaml_obj.items():
        if isinstance(value, ruamel.yaml.comments.CommentedMap):
            data[key] = DotDict()
            _yaml_to_dot_dict(data[key], value)
        else:
            data[key] = value
    return data


# if __name__ == '__main__':
#     dict_1 = DotDict({'root': {'child_1': {'grand_child_1': 'value_1', 'grand_child_2': 'value_3', 'grand_child_3': {'great_grand_child_1': 'value_4'}}, 'child_2': 'value_2'}})
#     dict_1.save_yaml("/tmp/dot_dict.txt")
#
#     dict_1_h = DotDict.load_yaml("/tmp/dot_dict.txt")
#     print(type(dict_1_h))
#     print("child_1: %s" % type(dict_1_h["root"]["child_1"]))
#     print("DotDict %s " % dict_1_h)
#     print("root.child_1.grand_child_3.great_grand_child_1: %s" % dict_1_h.root.child_1.grand_child_3.great_grand_child_1)

