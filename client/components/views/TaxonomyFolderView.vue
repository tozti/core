<template>
  <div v-if="resource" class="taxonomy">
    <p>
      <a class="button" @click="displayCreationModal('core/folder')">Nouveau dossier</a>
      <b-dropdown style="margin-left: 10px;">
        <a class="button" slot="trigger">
          <b-icon pack="mdi" icon="file-plus"></b-icon>
        </a>

        <b-dropdown-item 
          v-for="{ type, name, gender } in resourceTypes"
          @click="displayCreationModal(type)"
          :key="type">
          <template v-if="gender == 'm'">Nouveau</template>
          <template v-else>Nouvelle</template>
          {{ name }}
        </b-dropdown-item>
      </b-dropdown>
    </p>
    <div
      v-if="isEmpty"
      class="content has-text-grey has-text-centered has-vertical-space">
      <p>
      <i class="nc-icon nc-grid-45 x3"></i>
      </p>
      <p>Ce dossier est vide.</p>
    </div>
    <div v-else>
      <component
        v-for="(item, handle) in children"
        :is="getItemComponent(item)"
        :id="item.id"
        :handle="handle"
        :key="item.id"
        :root="resource" />
    </div>
  </div>
</template>

<script>
  import { ModalProgrammatic } from 'buefy'
  import { resourceMixin } from '../../mixins'
  import DefaultItem from './TaxonomyResourceItem'

  export { DefaultItem as TaxonomyItemComponent }

  export function addTaxonomyItem(type, component) {
    taxonomyItems.add(type, component)
  }

  export default {
    mixins: [ resourceMixin ],

    computed: {
      isEmpty() {
        return Object
          .getOwnPropertyNames(this.children)
          .filter(key => this.children.propertyIsEnumerable(key))
          .length == 0
      },

      children() {
        return this.resource.body.children.data
      },

      resourceTypes() {
        return tozti.resourceTypes
      }
    },

    methods: {
      getItemComponent({ type }) {
        if (tozti.taxonomyItems.has(type)) {
          return tozti.taxonomyItems.get(type)
        }

        return DefaultItem
      },

      getCreationFormComponent({ type }) {
        if (tozti.creationForms.has(type)) {
          return tozti.creationForms.get(type)
        }

        return null
      },

      displayCreationModal(type) {
        ModalProgrammatic.open({
          parent: this,
          component: this.getCreationFormComponent({ type }),
          scroll: 'keep',
          props: {
            root: this.resource
          }
        })
      }
    }

  }
</script>
