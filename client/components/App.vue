<template>
  <div>
    <b-loading :active="!ready"></b-loading>
    <router-view v-if="ready"></router-view>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        ready: false
      }
    },

    beforeMount() {
      tozti.store
        .fetchResource(tozti.api.endpoints.me)
        .then(user => {
          tozti.me = user
        })
        .catch(err => {
          this.$router.push('/login')
        })
        .finally(_ => {
          this.ready = true
        })
    },
  }
</script>
