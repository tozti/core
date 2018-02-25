foo_schema = {
    'attributes': {
        'name': { 'type': 'string' },
        'email': { 'type': 'string', 'format': 'email' },
    },
    'relationships': {}
}
MANIFEST = {"name": "type-welldefined01", "types": {"foo": foo_schema}}
