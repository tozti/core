foo_schema = {
    'attributes': {
        'name': { 'type': 'string' },
        'email': { 'type': 'string', 'format': 'email' },
    }
}
MANIFEST = {"name": "type-baddefined01", "types": {"foo": foo_schema}}
