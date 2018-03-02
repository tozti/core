<template>
  <t-taxonomy-item :loading="loading" :title="title" :date="date" :subtitle="subtitle" :resource="resource" :root="root"/>
</template>

<script>
  import { resourceMixin } from '../../mixins'

  export default {
    mixins: [ resourceMixin ],

    props: {
      handle: {
        type: String,
      },

      root: {
        type: Object,
        default: null
      }
    },

    data() {
      return {
        title: '',
        subtitle: '',
      }
    },

    watch: {
      loading() {
        this.title = this.id
        this.date = this.resource.meta['last-modified']
        this.subtitle = this.resource.meta['last-modified']
      }
    }
  }
</script>
