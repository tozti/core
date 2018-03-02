<template>
  <router-link
    v-if="!loading"
    :to="'/t/' + groupHandle + '/' + handle + '/'"
    active-class="active">
    <i class="nc-icon nc-folder-15"></i>
    {{ resource.body.name }}
  </router-link>
</template>

<script>
  import { resourceMixin } from '../../mixins'
  
  export default {
    mixins: [ resourceMixin ],
    props: ['groupHandle', 'handle']
  }
</script>