<template>
  <div v-if="resource">
    <b-collapse :open="true" animation="fadeInDown">
      <h3 slot="trigger">{{ resource.body.name }}</h3>
      <nav>
        <router-link
          :to="'/t/' + resource.body.handle + '/'"
          exact
          active-class="active">
          <i class="nc-icon nc-eye-19"></i>
          Résumé
        </router-link>

        <router-link
          v-for="{ name, route, props } in workspaceItems"
          :to="{ name: route, params: { id } }"
          :key="name"
          active-class="active">
          <i v-if="props.icon" :class="'nc-icon ' + props.icon"></i>
          {{ name }}
        </router-link>

        <folder-item
          v-for="(child, handle) in resource.body.children.data"
          :key="child.id"
          :id="child.id"
          :group-handle="resource.body.handle"
          :handle="handle">
        </folder-item>
      </nav>
    </b-collapse>
  </div>
</template>

<script>
  import { resourceMixin } from '../../mixins'
  import FolderItem from './FolderItem'

  export default {
    mixins: [ resourceMixin ],
    components: { FolderItem },

    data: _ => ({
      workspaceItems: tozti.workspaceMenuItems
    })
  }
</script>
