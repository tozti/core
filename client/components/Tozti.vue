<template>
  <div>
    <tozti-header></tozti-header>
    <tozti-sidebar></tozti-sidebar>
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
  import ToztiHeader from './Header'
  import ToztiSidebar from './Sidebar'

  export default {
    components: { ToztiHeader, ToztiSidebar }
  }
</script>
