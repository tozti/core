<template>
  <section class="section content">
    <h1>Paramètres</h1>
    <div class="tabs">
      <ul>
        <li class="is-active"><a>Profil</span></a></li>
        <li><a>Confidentialité</a></li>
      </ul>
    </div>
    <form @submit.prevent="updateProfile">
      <b-field label-for="name" label="Nom">
        <b-input
          v-model="user.name"
          ref="name"
          required>
        </b-input>
      </b-field>
      <input
        class="button is-primary"
        type="submit"
        value="Mettre à jour">
    </form>
  </section>
</template>

<script>
  export default {
    data() {
      return {
        user: { name: tozti.me.attributes.name }
      }
    },

    methods: {
      updateProfile() {
        tozti.store
          .update({ id: tozti.me.id, attributes: this.user })
          .then(() => {
            this.$toast.open({
              message: 'Votre profil a été mis à jour !',
              type: 'is-success'
            })
          })
          .catch(() => {
            this.$toast.open({
              message: 'Une erreur est survenue lors de la mise à jour.',
              type: 'is-danger'
            })
          })
      }
    }
  }
</script>
