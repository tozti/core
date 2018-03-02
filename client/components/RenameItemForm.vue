<template>
  <form v-on:submit.prevent="attemptRenameResource">
    <div class="modal-card" style="width: auto">
      <header>
        <p class="modal-card-head">Renommer la ressource {{ resource.body.name }}</p>
      </header>

      <section class="modal-card-body">
        <b-field label-for="name" label="Nom">
          <b-input
            v-model="name"
            ref="name"
            required>
          </b-input>
        </b-field>
      </section>

      <footer class="modal-card-foot">
        <input
          class="button is-primary"
          type="submit"
          value="Valider">
        <button class="button" type="button" @click="$parent.close()">Annuler</button>
        <i v-if="attempting" class="loading-spinner"></i>
      </footer>
    </div>
  </form>
</template>

<script>
  export default {
    props: {
      resource: Object
    },

    data() {
      return {
        name: this.resource.body.name,
        attempting: false,
      }
    },

    mounted() {
      this.$refs.name.focus()
    },

    methods: {
      attemptRenameResource() {
        this.attempting = true

        tozti.store
          .update({
            id: this.resource.id,
            body: { name: this.name }
          })

          .then(() => {
            this.attempting = false

            this.$parent.close()
            this.$toast.open({
              message: `La ressource a bien été renommée en ${this.name}.`,
              type: 'is-success',
              position: 'is-top'
            })
          })

          .catch(res => {
            this.$toast.open({
              message: 'Une erreur est survenue lors de la modification de la ressource',
              type: 'is-danger',
              position: 'is-top'
            })

            this.attempting = false
          })
      }
    }
  }
</script>
