<template>
  <b-field label-for="handle" 
           label="Identifiant"
           :type="type">
    <b-input v-model="handle" 
             :loading="checking"
             @input="tickHandle"
             required>
    </b-input>
  </b-field>
</template>

<script>
  export default {
    props: ['value', 'root'],

    data() {
      return {
        handle: this.value,
        available: false,
        synced:    false,
        checking:  false,
      }
    },

    computed: {
      type() {
        if (this.handle == '' || !this.synced)
          return ''
        return this.available ? 'is-success' : 'is-danger'
      }
    },

    methods: {
      checkHandle() {
        if (this.handle == '') return

        this.checking = true
        let test
        if (this.root) {
          test = this.root.body.children.data.hasOwnProperty(this.handle) ? Promise.reject() : Promise.resolve()
        }
        else
          test = tozti.api.checkHandle(this.handle)

        test
          .then(() => { this.available = true })
          .catch(() => { this.available = false })
          .finally(() => {
            this.checking = false
            this.synced = true
            this.$emit('update:available', this.available)
          })
      },

      tickHandle: (function() {
        let timestamp, timeout
        let delay = 400

        function later() {
          let last = Date.now() - timestamp

          if (last < delay && last >= 0) {
            timeout = window.setTimeout(later.bind(this), delay - last)
          }
          else {
            timeout = null
            this.checkHandle()
          }
        }

        return function() {
          this.$emit('input', this.handle)
          this.synced = false
          timestamp = Date.now()
          if(!timeout) {
            this.$emit('update:available', false)
            timeout = window.setTimeout(later.bind(this), delay)
          }
        }
      })(),
    }
  }
</script>
