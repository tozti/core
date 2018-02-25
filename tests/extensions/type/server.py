foo_schema = {
    'attributes': {
        'name': { 'type': 'string' },
        'email': { 'type': 'string', 'format': 'email' },
    },
    'relationships': {}
}
MANIFEST = {"name": "type", "types": {"foo": foo_schema}}
