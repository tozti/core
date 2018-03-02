import ToztiLayout from './components/Tozti'

import LoginView from './components/Login'
import SignUpView from './components/SignUp'

import Workspaces from './components/views/Workspaces'
import Groups from './components/views/Groups'
import GroupView from './components/views/Group'
import SettingsView from './components/views/Settings'
import TaxonomyView from './components/views/TaxonomyView'


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
  [ { path: 'g', component: Groups }

  , { name: 'taxonomy', path: 't/:taxonomy+', component: TaxonomyView }

  , { path: 'settings', component: SettingsView }


  , { path: 'w/', component: Workspaces }
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
