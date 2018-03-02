<template>
  <t-taxonomy-item
    icon="folder"
    :loading="loading"
    :title="title"
    :to="handle"
    :date="date"
    :subtitle="date"
    :resource="resource"
    :root="root"
  />
</template>

<script>
  import { resourceMixin } from '../../mixins'

  export default {
    mixins: [ resourceMixin ],

    props: {
      handle: String,
      root: {
        type: Object,
        default: null
      }
    },

    data() {
      return {
        title: '',
        date: '',
      }
    },

    watch: {
      loading() {
        this.title = this.resource.body.name
        this.date = this.resource.meta['last-modified']
        this.url = this.resource.meta['last-modified']
      }
    }
  }
</script>
