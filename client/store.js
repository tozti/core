export default new Vuex.Store({
  state: {
    notifications: [],
    dashboard: {
      widgets: []
    },
  },

  mutations: {
    // temporary, of course notifications will be defined as entities later
    addNotification (state, title, content) {
      state.notifications.push({
        seen: false,
        title,
        content
      })
    },

    registerWidget (state, componentName) {
      state.dashboard.widgets.push(componentName)
    }
  },
  modules: {}
})
