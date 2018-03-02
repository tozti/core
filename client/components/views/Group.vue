<template>
  <section v-if="resource" class="section content">
    <h1>{{ resource.body.name }}</h1>

    <div class="tabs">
      <ul>
        <li class="is-active"><a>Espace</a></li>
        <li><a>Membres <span class="badge">{{ memberCount }}</span></a></li>
        <li><a>Paramètres</a></li>
      </ul>
    </div>

    <TaxonomyFolderView :id="id"/>
  </section>
</template>

<script>
  import { ModalProgrammatic } from 'buefy'
  import { resourceMixin } from '../../mixins'
  import TaxonomyFolderView from './TaxonomyFolderView'

  export default {
    mixins: [ resourceMixin ],
    components: { TaxonomyFolderView },

    data() {
      return {
        deleting: false,
      }
    },

    computed: {
      members() {
        return this.resource.body.members.data
      },

      memberCount() {
        return this.members.length
      }
    },

    methods: {
      createWorkspace() {
      },

      deleteGroup() {
        this.$dialog.confirm({
          message: 'Voulez-vous supprimer définitivement ce groupe ?',
          confirmText: 'Oui',
          cancelText: 'Annuler',
          type: 'is-danger',
          onConfirm: () => {
            this.deleting = true

            tozti.store
              .rels.delete(tozti.me.body.groups, { id: this.id })
              .then(() => tozti.store.rels.delete(tozti.me.body.pinned, { id: this.id }))
              .then(() => tozti.store.delete(this.id))
              .then(() => {
                this.$router.push('/g/')
                this.$toast.open({
                  message: 'Le groupe a été supprimé.',
                  type: 'is-success'
                })
              })
          }
        })
      }
    }
  }
</script>
