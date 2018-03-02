<template>
  <t-new-resource-form
    title="Nouveau groupe"
    :resource="group"
    :callback="attemptNewGroup"
    :parent="$parent">
  </t-new-resource-form>
</template>

<script>
  export default {
    data() {
      return {
        group: {
          name: '',
          handle: '',
          children: { data: {} },
        },
      }
    },

    methods: {
      attemptNewGroup(handler) {
        let prom = tozti
          // create the group
          .store.create({ type: 'core/group', body: this.group }, false)

          // add the user as a member
          // and register the group in the handle store
          .then(({ id }) => Promise.all([
            tozti.store.rels.add(tozti.me.body.groups, { id }),
            tozti.api.post(tozti.api.handleURL(this.group.handle), { data: { id } })
          ]))

        handler(prom)
      }
    }
  }
</script>
