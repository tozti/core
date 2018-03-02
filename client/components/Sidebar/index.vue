<template>
  <aside class="main-sidebar">

    <nav>
      <router-link v-for="{ name, route, props } in globalMenuItems"
        :to="route"
        :key="name"
        active-class="active"
        exact>
        <i v-if="props.icon" :class="'nc-icon ' + props.icon"></i>{{ name }}
      </router-link>
    </nav>

    <workspace-menu
        v-for="workspace in workspaces"
        :key="workspace.id"
        :id="workspace.id">
    </workspace-menu>

    <nav v-if="pinned.length">
      <h3>épinglé</h3>
      <pinned-item v-for="pin in pinned"
        :id="pin.id"
        :key="pin.id">
      </pinned-item>
    </nav>

  </aside>
</template>

<script>
  import PinnedItem from './PinnedItem'
  import WorkspaceMenu from './WorkspaceMenu'

  export default {
    components: { PinnedItem, WorkspaceMenu },

    data: _ => ({
      globalMenuItems: tozti.globalMenuItems,
      pinned: tozti.me.body.pinned.data,
      workspaces: tozti.me.body.groups.data
    })
  }
</script>
