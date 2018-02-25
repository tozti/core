foo_schema = {
        'attributes': {
            'foo': { 'type': 'string' },
            },
        'relationships': {
            "member": {
                "arity": "to-one",
                "type": "rel01/bar",
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
MANIFEST = {"name": "rel01", "types": {"foo": foo_schema, "bar": bar_schema}}
