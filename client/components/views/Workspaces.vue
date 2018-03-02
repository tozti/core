<template>
  <section class="section">
    <div class="content has-text-grey has-text-centered has-vertical-space">
      <p>
      <i class="nc-icon nc-grid-45 x3"></i>
      </p>
      <p>Vous ne faites partie d'aucun espace de travail.</p>
      <p>
        <a class="button" @click="displayCreationModal">Créer un espace de travail</a>
      </p>
    </div>
  </section>
</template>

<script>
  import { ModalProgrammatic } from 'buefy'
  import NewFolderForm from '../NewFolderForm.vue'

  export default {
    methods: {
      displayCreationModal() {
        ModalProgrammatic.open({
          parent: this,
          component: NewFolderForm,
          scroll: 'keep'
        })
      }
    }
  }
</script>
