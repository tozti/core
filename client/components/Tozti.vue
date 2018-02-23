<template>
  <div>
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

    <navigation></navigation>

    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
  import NotificationCenter from './NotificationCenter.vue'
  import SearchBar from './SearchBar.vue'
  import Navigation from './Navigation.vue'
  import UserInfo from './UserInfo.vue'

  export default {
    components: {
      NotificationCenter,
      Navigation,
      SearchBar,
      UserInfo,
    }
  }
</script>
