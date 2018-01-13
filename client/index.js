import App       from './components/App.vue'
import Dashboard from './components/Dashboard.vue'
import Taxonomy  from './components/Taxonomy.vue'

import store from './store'

// Create a "polymorphic" component.
// A polymorphic component is a component with a single prop `resource` that
// transparently passes the rendering to another component based on the type
// of the passed resource. To register a new component handling a given type,
// add the instance as a property of the returned object.
//
// Example: make a 'thumbnail' component
//
//   let thumb_tbl = polymorphic_component('thumbnail', {
//       template: '<p>Thumbnail for {{resource.id}}</p>',
//       props: ['resource'],
//   });
//   thumb_tbl['image'] = {
//       template: '<p>Thumbnail for image {{resource.id}}'</p>,
//       props: ['resource'],
//   };
//   thumb_tbl['thread'] = {
//       template: '<p>Thumbnail for thread {{resource.id}}</p>',
//       props: ['resource'],
//   };
//
export function polymorphic_component(name, fallback) {
    let table = {fallback: fallback};
    Vue.component(name, {
        template: '<component :is="sub" :resource="resource"/>',
        props: ['resource'],
        computed: {
            sub() {
                return table[this.resource.type] || table['fallback'];
            }
        }
    });
    return table;
}

window.tozti = new Vue({
  el: '#app',
  store,

  router: new VueRouter({
    routes: [
      { path: '/', component: Dashboard },
      { path: '/:workspace/:taxonomy*', component: Taxonomy }
    ]
  }),

  render: h => h(App)
})
