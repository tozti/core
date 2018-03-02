<template>
  <div class="taxonomy-item">
    <div class="taxonomy-item-media">
      <slot name="media">
        <b-icon pack="mdi" :icon="icon"></b-icon>
      </slot>
    </div>
    <div v-if="loading" class="taxonomy-item-info">
      <p class="title"><span class="placeholder"></span></p>
      <p class="subtitle"><span class="placeholder"></span></p>
    </div>
    <div v-else class="taxonomy-item-info">
      <router-link :to="to" append>
        <p class="title">{{ title }}</p>
        <p class="subtitle"><timeago :since="date"></timeago></span></p>
        <!-- <p class="subtitle">{{ subtitle }}</span></p> -->
      </router-link>
    </div>
    <div class="taxonomy-item-actions">
      <a @click="displayRenameModal" style="margin-left: 10px;">
        <b-icon pack="mdi" icon="pencil" type="is-dark"></b-icon>
      </a>
      <!-- <a @click="displayDeleteModal" style="margin-left: 10px;">
        <b-icon pack="mdi" icon="delete" type="is-dark"></b-icon>
      </a> -->
      <b-dropdown style="margin-left: 10px;">
        <b-icon pack="mdi" icon="dots-horizontal" slot="trigger"></b-icon>
        <b-dropdown-item>Something else</b-dropdown-item>
      </b-dropdown>
    </div>
  </div>
</template>

<script>
  import { ModalProgrammatic } from 'buefy'

  import RenameItemForm from '../RenameItemForm'

  export default {
    props: {
      icon: {
        type: String,
        default: 'help-circle',
      },

      title: {
        type: String,
        default: '',
      },

      subtitle: {
        type: String,
        default: '',
      },

      date: {
        type: String,
        default: '',
      },

      to: {
        type: String,
        default: '',
      },

      loading: {
        type: Boolean,
        default: false,
      },

      resource: {
        type: Object,
        default: null
      },

      root: {
        type: Object,
        default: null
      }
    },

    methods: {
      displayRenameModal() {
        ModalProgrammatic.open({
          parent: this,
          component: RenameItemForm,
          scroll: 'keep',
          props: {
            resource: this.resource,
            root: this.root
          }
        })
      },

      // displayDeleteModal() {

      // }
    }
  }
</script>
