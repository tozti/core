<template>
  <div>
    <div uk-sticky class="uk-navbar-container">
        <div class="uk-container">
          <nav uk-navbar>
            <div class="uk-navbar-left">
              <a href="/" class="uk-navbar-item uk-logo">
                tozti
              </a>
            </div>
            <div class="uk-navbar-right" style="margin-right: 0;">
              <notification-center></notification-center>
            </div>
          </nav>
        </div>
    </div>
    <router-view></router-view>
  </div>
</template>

<script>
  import NotificationCenter from './NotificationCenter.vue'

  export default {
    components: {
      NotificationCenter
    }
  }
</script>
