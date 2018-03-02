<template>
  <form v-on:submit.prevent="attemptNewResource">
    <div class="modal-card" style="width: auto">
      <header>
        <p class="modal-card-head">{{ title }}</p>
      </header>
      <section class="modal-card-body">
        <b-field label-for="name" label="Nom">
          <b-input
            v-model="resource.name"
            ref="name"
            required>
          </b-input>
        </b-field>
        <t-handle-field v-model="resource.handle"
                        :root="root"
                        :available.sync="available">
        </t-handle-field>
      </section>
      <footer class="modal-card-foot">
        <input
          class="button is-primary"
          type="submit"
          :disabled="!available || attempting"
          value="Créer">
        <button class="button" type="button" @click="$parent.close()">Annuler</button>
        <i v-if="attempting" class="loading-spinner"></i>
      </footer>
    </div>
  </form>
</template>

<script>
  export default {
    props: {
      title: String,
      callback: Function,
      resource: Object,
      parent: Object,
      root: {
        type: Object,
        default: null
      }
    },

    data() {
      return {
        attempting: false,
        available: false,
      }
    },

    mounted() {
      this.$refs.name.focus()
    },

    methods: {
      attemptNewResource() {
        this.attempting = true

        this.callback(promise => {
          promise
            .then(() => {
              this.attempting = false

              this.parent.close()
              this.$toast.open({
                message: `${this.resource.name} vient d'être créé.`,
                type: 'is-success',
                position: 'is-top'
              })
            })

            .catch(res => {
              this.attempting = false
            
              this.$toast.open({
                message: `Une erreur est survenue lors de la création de ${this.resource.name}`,
                type: 'is-danger',
                position: 'is-top'
              })
            })
        })
      }
    }
  }
</script>
