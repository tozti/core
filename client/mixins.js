function fetch() {
  this.loading = true
  tozti.store.get(this.id)
    .then(resource => {
      this.resource = resource
      this.loading = false
    })
}

export let resourceMixin = {
  props: { id: String },

  watch: {
    id() {
      fetch.call(this)
    }
  },

  mounted() {
    fetch.call(this)
  },

  data() {
    return {
      loading: true,
      resource: null,
    }
  }
}
