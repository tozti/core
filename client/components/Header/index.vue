<template>
  <header class="main-header">
    <section class="branding">
      <router-link to="/">
        <img src="~assets/img/logo.svg" alt="tozti">
      </router-link>
    </section>

    <search-bar></search-bar>

    <section class="user">
      <notification-center></notification-center>
      <user-info></user-info>
    </section>
  </header>
</template>

<script>
  import NotificationCenter from './NotificationCenter'
  import SearchBar from './SearchBar'
  import UserInfo from './UserInfo'

  export default {
    components: {
      NotificationCenter,
      SearchBar,
      UserInfo,
    }
  }
</script>
