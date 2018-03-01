import Vue from 'vue'
import Buefy from 'buefy'
import ToztiLayout from './components/Tozti.vue'
import promiseFinally from 'promise.prototype.finally'

promiseFinally.shim()

import { resourceMixin } from './mixins'
import { addRoutes, getRoutes } from './routes'
import { addTaxonomyItem, TaxonomyItemComponent } from './components/views/TaxonomyFolderView'
import store from './store'
import api from './api'

import AppView from './components/App'
import HandleInput from './components/generic/HandleInput'
import NewResourceForm from './components/generic/NewResourceForm'

Vue.use(Buefy)
Vue.component('t-handle-field', HandleInput)
Vue.component('t-new-resource-form', NewResourceForm)


// Create a 'polymorphic' component.
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

// TODO(flupe): move this to a more appropriate place
//              i mean, come on Lapin0t

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


const tozti = window.tozti = {
  resourceMixin,

  addTaxonomyItem,
  TaxonomyItemComponent,

  addRoutes,
  store,
  api,

  me:  null,
  app: null,

  globalMenuItems:
    [ { name: 'Mes groupes', route: '/g/', props: { icon: 'nc-multiple-11' } }
    , { name: 'Paramètres', route: '/settings', props: { icon: 'nc-settings-gear-63' } }
    ],

  workspaceMenuItems: [],

  resourceTypes: [],


  /**
   * Define a global sidebar menu item.
   * @param {string} name - The name of the menu item.
   * @param {string | Location} route - The route it points to.
   */
  addMenuItem(name, route, props = {}) {
    tozti.globalMenuItems.push({ name, route, props})
  },


  /**
   * @param {string} name  - The name of the workspace menu item.
   * @param {string} route - The name of the route it is associated with.
   *                         This route should expect an id as a parameter.
   */
  addWorkspaceMenuItem(name, route, props = {}) {
    tozti.workspaceMenuItems.push({ name, route, props })
  },


  /**
   * @param {string} type         - The type of resource to register (e.g. `discussion/thread`).
   * @param {string} name         - The lowercase name of the resource (e.g. `discussion`).
   * @param {string} name         - The gender of `name`. Must be either 'm' or 'f'.
   * @param {string} creationForm - The component responsible for creating this resource type.
   */
  addResourceType(type, name, gender, creationForm) {
    tozti.resourceTypes.push({ type, name, gender, creationForm })
  },


  /**
   * Start the tozti web app.
   */
  launch() {
    this.app = new Vue({
      el: '#app',

      router: new VueRouter({
        mode: "history",
        routes: getRoutes()
      }),

      render: h => h(AppView)
    })
  }

}

export default tozti
