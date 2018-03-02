<template>
  <div class="login">
    <section class="content">
      <p class="content-header">
        <img src="~assets/img/logo.svg" width="50">
      </p>
      <div class="box">
        <form v-on:submit.prevent="signin">
          <t-handle-field v-model="user.handle"
                          :available.sync="available">
          </t-handle-field>

          <b-field label-for="mail" label="Adresse mail :">
            <b-input id="mail" type="mail" v-model="user.email"></b-input>
          </b-field>

          <b-field label-for="name" label="Nom d'utilisateur·ice :">
            <b-input id="name" v-model="user.name"></b-input>
          </b-field>

          <b-field label-for="passwd" label="Mot de passe :">
            <b-input id="passwd" v-model="user.passwd" type="password" password-reveal></b-input>
          </b-field>

          <div class="field is-grouped is-grouped-left">
            <p class="control">
              <button type="submit" class="button" :disabled="!available">
                S'enregistrer
              </button>
            </p>
          </div>
        </form>
      </div>
    </section>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        user: {
          handle: '',
          name: '',
          passwd: '',
          email: '',
        },
        available: false
      }
    },

    mounted() {
      // this.$refs.handle.focus()
    },

    methods: {
      signin() {
        tozti.api
          .post(tozti.api.endpoints.signup, this.user)
          .then(res => {
            this.$router.push('/login')
            this.$toast.open({
              message: 'Votre inscription a réussi !',
              type: 'is-success',
              position: 'is-top'
            })
          })
          .catch(err => {
            this.$toast.open({
              message: 'Une erreur est survenue lors de l\'inscription',
              type: 'is-danger',
              position: 'is-top'
            })
          })
      },
    },
  }
</script>
