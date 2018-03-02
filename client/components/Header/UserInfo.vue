<template>
  <div href="#" class="logged">
    <div class="avatar">
      <img :src="'https://identicon-api.herokuapp.com/' + me.body.name + '/64?format=png'">
    </div>

    {{ me.body.name }} 

    <i class="material-icons">arrow_drop_down</i>
    <a v-on:click="logout" style="margin-left: 10px;"><b-icon icon="power"></b-icon></a>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        me: tozti.me
      }
    },
    methods: {
      logout() {
        document.cookie = 'auth-token=;expires=Thu, 01 Jan 1970 00:00:01 GMT;'
        tozti.me = null
        this.$toast.open({
          duration: 5000,
          message: 'Vous avez été déconnecté·e',
          type: 'is-success',
          position: 'is-top'
        })
        this.$router.push('/login')
      }
    }
  }
</script>
