<template>
  <router-link :to="resource ? { name: 'taxonomy', params: { taxonomy: resource.body.handle } } : {}">
    <div v-if="resource" class="group-item">
      <div class="group-media"></div>
      <div class="group-content">
        <p class="title is-5">{{resource.body.name}}</p>
        <p class="subtitle is-6">@{{resource.body.handle}}</p>
      </div>
      <div class="group-actions">
        <b-icon v-if="pinned" size="is-small" pack="mdi" icon="pin"></b-icon>
      </div>
    </div>
    <div v-else class="group-item">
      <div class="group-media placeholder"></div>
      <div class="group-content">
        <p class="title is-5"><span class="placeholder"></span></p>
        <p class="subtitle is-6"><span class="placeholder"></span></p>
      </div>
    </div>
  </router-link>
</template>

<script>
  import { resourceMixin } from '../mixins'

  export default {
    mixins: [ resourceMixin ],

    computed: {
      pinned() {
        return tozti.me.body.pinned.data.some(group => group.id == this.id)
      }
    }
  }
</script>
