<template>
  <router-link v-if="this.resource"
               active-class="active"
               :to="{ name: 'group', params: { id: this.id } }">
    <i class="nc-icon" :class="icon"></i>{{ this.resource.attributes.name }}
  </router-link>
</template>

<script>
  import { resourceMixin } from '../../mixins'

  export default {
    mixins: [ resourceMixin ],

    computed: {
      icon() {
        return this.resource.type == 'core/group' ? 'nc-multiple-11' : 'nc-grid-45'
      }
    }
  }
</script>
