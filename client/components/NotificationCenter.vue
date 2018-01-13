<template>
  <a href="" class="uk-icon-link" uk-icon="icon: bell">
    <span class="uk-badge" v-if="count > 0">{{ count }}</span>
  </a>
</template>

<script>
  export default {
    computed: {
      count () {
        return this.$store.state.notifications
               .filter(notif => !notif.seen).length
      }
    }
  }
</script>
