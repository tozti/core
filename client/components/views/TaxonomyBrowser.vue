<template>
  <div v-if="loaded">
    <component :is="getRootComponent(root.type)" :id="root.id"/>
  </div>
</template>

<script>

  function splitPath(path) {
    if (path.substr(-1) == '/')
      path = path.subtr(0, path.length - 1)

    return path.split('/')
  }


  export default {
    props: {
      path: {
        type: String,
        required: true,
        // validator(value) {
        //   // TODO(flupe): make sure this does what we want
        //   //              I wrote this and I am no regex master
        //   return /^([a-zA-Z0-9_\-.]+\/?)+$/.test(value)
        // }
      }
    },

    data() {
      return {
        stack: null,
        root: null,
        loaded: false,
      }
    },

    beforeMount() {
      let segments = splitPath(this.path)
      let [global, ...nested] = segments
      let stack = []

      nested
        .reduce(
          (acc, segment) => {
            return acc.then(linkage => {
              if (['core/folder', 'core/group'].indexOf(linkage.type) == -1) {
                return tozti.store.get(linkage)
              }
              return tozti.store.get(linkage.id)
                .then(res => {
                  if (res.body.children.data.hasOwnProperty(segment)) {
                    return res.body.children.data[segment]
                  }
                  else {
                    return Promise.reject()
                  }
                })
            })
          },
          tozti.store.handle.get(global)
        ).then(root => {
          this.root = root
          this.stack = stack
          this.loaded = true
        })
    },

    watch: {
      path() {
        let segments = splitPath(this.path)
        let [global, ...nested] = segments
        let stack = []

        this.loaded = false

        nested
          .reduce(
            (acc, segment) => {
              return acc.then(linkage => {
                if (['core/folder', 'core/group'].indexOf(linkage.type) == -1) {
                  return tozti.store.get(linkage)
                }
                return tozti.store.get(linkage.id)
                  .then(res => {
                    if (res.body.children.data.hasOwnProperty(segment)) {
                      return res.body.children.data[segment]
                    }
                    else {
                      return Promise.reject()
                    }
                  })
              })
            },
            tozti.store.handle.get(global)
          ).then(root => {
            this.root = root
            this.stack = stack
            this.loaded = true
          })
        }
    },

    methods: {
      getRootComponent(type) {
        if (tozti.taxonomyViews.has(type)) {
          return tozti.taxonomyViews.get(type)
        }
      },

    }
  }
</script>
