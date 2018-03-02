<template>
  <section class="section content">
    <div v-if="empty" class="content has-text-grey has-text-centered has-vertical-space">
      <p><i class="nc-icon nc-multiple-11 x3"></i></p>
      <p>Vous ne faites partie d'aucun groupe.</p>
      <p><a class="button" @click="displayForm">Créer un nouveau groupe</a></p>
    </div>

    <div v-if="!empty">
      <h1>Mes groupes</h1>
      <p><a class="button" @click="displayForm">Nouveau groupe</a></p>
      <div class="group-list">
        <transition-group name="zoomIn" tag="div">
          <group-preview v-for="group in groups" :key="group.id" :id="group.id"></group-preview>
        </transition-group>
      </div>
    </div>
  </section>
</template>

<script>
  import { ModalProgrammatic } from 'buefy'
  import GroupForm from '../NewGroupForm.vue'
  import GroupPreview from '../GroupPreview.vue'

  export default {
    components: { GroupPreview },

    computed: {
      empty() {
        return this.groups.length == 0
      }
    },

    data() {
      return {
        groups: tozti.me.body.groups.data
      }
    },

    methods: {
      displayForm() {
        ModalProgrammatic.open({
          parent: this,
          component: GroupForm,
          scroll: 'keep'
        })
      }
    }
  }
</script>
