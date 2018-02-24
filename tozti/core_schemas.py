user_schema = {
    'body': {
        'name': { 'type': 'string' },
        'email': { 'type': 'string', 'format': 'email' },
        'handle': { 'type': 'string' },
        'hash': {'type': 'string'},
        'groups': {
            'type': 'relationship',
            'arity': 'to-many',
            'targets': 'core/group',
        },

        'pinned': {
            'type': 'relationship',
            'arity': 'to-many',
            'targets': 'core/folder'
        }
    }
}


group_schema = {
    'body': {
        'name': {
            'type': 'string'
        },
        'members': {
            'type': 'relationship',
            'arity': 'to-many',
            'targets': 'core/user'
        }
    }
}

folder_schema = {
    'body': {
        'name': { 'type': 'string' },
        'children': {
            'arity': 'to-many'
        },

        'parents': {
            'type': 'relationship',
            'arity': 'auto',
            'pred-type': 'core/folder',
            'pred-relationship': 'children'
        }
    }
}


SCHEMAS = {
    'user': user_schema,
    'group': group_schema,
    'folder': folder_schema
}
