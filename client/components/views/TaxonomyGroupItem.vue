<template>
  <TaxonomyItem
    :loading="loading"
    :to="handle"
    :title="title"
    :date="date"
    :subtitle="subtitle"
    :resource="resource"
    :root="root" />
</template>
<script>
  import TaxonomyResourceItem from './TaxonomyResourceItem'

  export default {
    extends: TaxonomyResourceItem,

    props: {
      handle: String,
      root: {
        type: Object,
        default: null
      }
    },

    methods: {
      onLoaded() {
        this.title = this.resource.body.name
        this.date = this.resource.meta['last-modified']
        this.subtitle = this.resource.meta['last-modified']
      }
    }
  }
</script>
