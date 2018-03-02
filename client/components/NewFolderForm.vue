<template>
  <t-new-resource-form
    title="Nouveau dossier"
    :resource="folder"
    :callback="attemptNewFolder"
    :parent="$parent"
    :root="root">
  </t-new-resource-form>
</template>

<script>
  export default {
    props: {
      root: {
        type: Object,
        default: null,
        validate(root) {
          return root && [
            'core/group',
            'core/folder',
          ].indexOf(root.type) > -1
        }
      }
    },

    data() {
      return {
        folder: {
          name: '',
          handle: '',
          children: { data: {} },
        },
      }
    },

    methods: {
      attemptNewFolder(handler) {
        let prom = tozti
          // create the folder
          .store.create({
            type: 'core/folder',
            body: this.folder
          }, false)

          // pin the folder to the root
          .then(({ id, type }) => {
            let linkage = { id, type }
            if (this.root)
              return tozti.store
                .rels.add(this.root.body.children, {
                  [this.folder.handle]: linkage
                })

            else {
              return tozti.api
                .post(tozti.api.handleURL(this.folder.handle), {
                  data: linkage
                })
            }
          })

        handler(prom)
      }
    }
  }
</script>
