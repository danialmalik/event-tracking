import json
from importlib import import_module


def fullname(o):
    # o.__module__ + "." + o.__class__.__qualname__ is an example in
    # this context of H.L. Mencken's "neat, plausible, and wrong."
    # Python makes no guarantees as to whether the __module__ special
    # attribute is defined, so we take a more circumspect approach.
    # Alas, the module name is explicitly excluded from __qualname__
    # in Python 3.
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + '.' + o.__class__.__name__


class BackendJSONEncoder(json.JSONEncoder):
    # class BackendJSONEncoder(object):
    """
    converts into json
    """

    def default(self, obj):
        return self.serialize_module(obj)

    def serialize_module(self, module):
        serialized = {}
        engine = fullname(module)
        options = self.serialize_options(module)
        serialized['ENGINE'] = engine
        serialized['OPTIONS'] = options
        return serialized

    def serialize_options(self, backend):
        options = {}
        for key, value in backend.__dict__.iteritems():
            # encode processors, backends and other options
            # key can be backends, processors or any other key
            options[key] = self.serialize_node(key, value)
        return options

    def serialize_node(self, name=None, node=None):
        serialized_node = node
        if isinstance(node, dict):
            serialized_node = node.copy()
            # if name in ('backends',) or self.contains_engine:
            if name in ('backends', 'async_backends'):
                for key, backend in node.iteritems():
                    serialized_node[key] = self.serialize_module(backend)
            else:
                for key, value in node.iteritems():
                    serialized_node[key] = self.serialize_node(key, value)
        elif isinstance(node, list):
            serialized_node = node[:]
            serialized_node = []
            for child in node:
                serialized_node.append(self.serialize_node(node=child))
        elif callable(node):
            serialized_node = self.serialize_module(node)
        return serialized_node


class BackendJSONDecoder(json.JSONDecoder):
    def default(self, object):
        backends = self.instantiate_objects(object)
        return backends

    def instantiate_objects(self, node):
        """
        Recursively traverse a structure to identify dictionaries that represent objects that need to be instantiated

        Traverse all values of all dictionaries and all elements of all lists to identify dictionaries that contain the
        special "ENGINE" key which indicates that a class of that type should be instantiated and passed all key-value
        pairs found in the sibling "OPTIONS" dictionary as keyword arguments.

        For example::

            tree = {
                'a': {
                    'b': {
                        'first_obj': {
                            'ENGINE': 'mypackage.mymodule.Clazz',
                            'OPTIONS': {
                                'size': 10,
                                'foo': 'bar'
                            }
                        }
                    },
                    'c': [
                        {
                            'ENGINE': 'mypackage.mymodule.Clazz2',
                            'OPTIONS': {
                                'more_objects': {
                                    'd': {'ENGINE': 'mypackage.foo.Bar'}
                                }
                            }
                        }
                    ]
                }
            }
            root = self.instantiate_objects(tree)

        That structure of dicts, lists, and strings will end up with (this example assumes that all keyword arguments to
        constructors were saved as attributes of the same name):

        assert type(root['a']['b']['first_obj']) == <type 'mypackage.mymodule.Clazz'>
        assert root['a']['b']['first_obj'].size == 10
        assert root['a']['b']['first_obj'].foo == 'bar'
        assert type(root['a']['c'][0]) == <type 'mypackage.mymodule.Clazz2'>
        assert type(root['a']['c'][0].more_objects['d']) == <type 'mypackage.foo.Bar'>
        """
        result = node
        if isinstance(node, dict):
            if 'ENGINE' in node:
                result = self.instantiate_from_dict(node)
            else:
                result = {}
                for key, value in node.iteritems():
                    result[key] = self.instantiate_objects(value)
        elif isinstance(node, list):
            result = []
            for child in node:
                result.append(self.instantiate_objects(child))

        return result

    def instantiate_from_dict(self, values):
        """
        Constructs an object given a dictionary containing an "ENGINE" key
        which contains the full module path to the class, and an "OPTIONS"
        key which contains a dictionary that will be passed in to the
        constructor as keyword args.
        """

        name = values['ENGINE']
        options = values.get('OPTIONS', {})

        # Parse the name
        parts = name.split('.')
        module_name = '.'.join(parts[:-1])
        class_name = parts[-1]

        # Get the class
        try:
            module = import_module(module_name)
            cls = getattr(module, class_name)
        except (ValueError, AttributeError, TypeError, ImportError):
            raise ValueError('Cannot find class %s' % name)

        options = self.instantiate_objects(options)

        return cls(**options)
