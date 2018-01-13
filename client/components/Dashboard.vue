<template>
  <div class="uk-container uk-padding">
    <h1 class="uk-heading-primary">Dashboard</h1>
    <template v-for="widget in widgets">
      <component :is="widget"></component>
    </template>
    <div v-if="count == 0">
      <div class="uk-dark uk-background-muted uk-padding">
        <h3>No widget available just yet :(</h3>
        <p>Make sure you have installed some extensions providing new widgets.</p>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    computed: Vuex.mapState({
      count: state => state.dashboard.widgets.length,
      widgets: state => state.dashboard.widgets
    }),
  }
</script>
