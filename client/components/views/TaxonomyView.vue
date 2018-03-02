<template>
  <section>
    <TaxonomyBrowser :path="$route.params.taxonomy"/>
  </section>
</template>

<script>
  import TaxonomyBrowser from './TaxonomyBrowser'

  export default {
    components: { TaxonomyBrowser }
  }
</script>
