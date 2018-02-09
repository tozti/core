user_schema = {
    'attributes': {
        'name': { 'type': 'string' },
        'email': { 'type': 'string', 'format': 'email' },
        'login': { 'type': 'string' },
        'avatar': { 'type': 'string' }, # TODO(Lapin0t): upload id

        # TODO: config + notif
    },

    'relationships': {
        'groups': {
            'arity': 'to-many',
            'type': 'core/group',
        },

        # folders the user has made accessible from its sidebar
        'pinned': {
            'arity': 'to-many',
            'type': 'core/folder'
        }
    }
}


group_schema = {
    'attributes': {
        'name': { 'type': 'string' }
    },

    'relationships': {
        'members': {
            'reverse-of': {
                'type': 'core/user',
                'path': 'groups'
            }
        },

        'groups': {
            'arity': 'to-many',
            'type': 'core/group',
        },

        'pinned': {
            'arity': 'to-many',
            'type': 'core/folder'
        },
    }
}

acl_schema = {
    'type': 'object',
    'patternProperties': {
        '.*': {
            'type': 'object'
            'properties': {
                'type': { 'type': 'string' },
                'key': { 'type': 'string' },
            }
        }
    }
}

folder_schema = {
    'attributes': {
        'name': { 'type': 'string' }
    },

    'relationships': {
        'children': {
            'arity': 'to-many'
        },
        'parents': {
            'reverse-of': {
                'type': 'core/folder',
                'path': 'children'
            }
        },
    }
}

# core/thread
thread_schema = {
    'attributes': {
        'title': { 'type': 'string' },
    },
    'relationships': {
        'posts': {
            'arity': 'to-many',
            'type': 'discussion/post'
        }
    }
}

# core/post
post_schema = {
    'attributes': {
        'title': { 'type': 'string' },
    },

    'relationships': {
        'thread': {
            'reverse-of': {
                'type': 'discussion/thread',
                'path': 'posts'
            }
        },

        'parent': {
            'arity': 'to-one',
            'type': 'discussion/post'
        },

        'responses': {
            'reverse-of': {
                'type': 'discussion/post',
                'path': 'parent'
            }
        },

        'attachments': {
            'arity': 'to-many'
        }
    }
}


SCHEMAS = {
    'user': user_schema,
    'group': group_schema,
    'folder': folder_schema
}
