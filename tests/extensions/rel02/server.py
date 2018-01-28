foo_schema = {
        'attributes': {
            'foo': { 'type': 'string' },
            },
        'relationships': {
            "members": {
                "arity": "to-many",
                "type": "rel02/bar",
                }
            }
        }
bar_schema = {
        'attributes': {
            'bar': { 'type': 'string' },
            },
        'relationships': {
            }
        }
MANIFEST = {"types": {"foo": foo_schema, "bar": bar_schema}}
