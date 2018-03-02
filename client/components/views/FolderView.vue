<template>
  <section class="section">
    <TaxonomyFolderView :id="id"/>
  </section>
</template>

<script>
  import { ModalProgrammatic } from 'buefy'
  import TaxonomyFolderView from './TaxonomyFolderView'

  export default {
    components: { TaxonomyFolderView },

    props: { id: String },
  }
</script>
