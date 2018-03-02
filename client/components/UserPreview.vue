<template>
  <router-link :to="{ name: 'group', params: { id } }">
    <div v-if="resource" class="group-item">
      <div class="group-media"></div>
      <div class="group-content">
        <p class="title is-5">{{ resource.body.name }}</p>
        <p class="subtitle is-6">@{{ resource.body.handle }}</p>
      </div>
    </div>
    <div v-if="!resource" class="group-item">
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
    mixins: [ resourceMixin ]
  }
</script>
