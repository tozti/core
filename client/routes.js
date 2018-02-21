import LoginView from './components/Login.vue'
import SignUpView from './components/SignUp.vue'
import ToztiLayout from './components/Tozti.vue'
import DashboardView from './components/views/Dashboard.vue'
import SummaryView from './components/views/Summary.vue'
import TaxonomyView from './components/views/Taxonomy.vue'

import Workspaces from './components/views/Workspaces.vue'
import Groups from './components/views/Groups.vue'
import GroupView from './components/views/Group.vue'
import SettingsView from './components/views/Settings.vue'


const singleRoutes =
  [ { path: '/login'
    , component: LoginView
    , meta: { requiresNoAuth: true }
    }

  , { path: '/signup'
    , component: SignUpView
    , meta: { requiresNoAuth: true }
    }
  ]


const enclosedRoutes =
  [ { path: 'g/', component: Groups }

  , { name: 'group'
    , path: 'g/:id'
    , component: GroupView
    , props: route => ({ id: route.params.id }) 
    }

  , { path: 'settings', component: SettingsView }

  , { path: 'w/', component: Workspaces }
  , { path: 'w/:id',  name: 'workspace', component: SummaryView }
  , { path: 'w/:taxonomy+', component: TaxonomyView, props: true }
  ]


/**
 * @param {Route[]} routes - The routes to add.
 */
export function addRoutes(routes) {
  routes.forEach(route => {
    if (route.meta && route.meta.single) {
      singleRoutes.push(route)
    }
    else {
      enclosedRoutes.push(route)
    }
  })
}


export function getRoutes() {
  return singleRoutes.concat([
    { path: ''
    , component: ToztiLayout
    , meta: { requiresAuth: true }
    , redirect: 'g/'
    , readonly: true
    , children: enclosedRoutes
    }
  ])
}
