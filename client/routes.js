import LoginView from './components/Login.vue'
import ToztiLayout from './components/Tozti.vue'
import DashboardView from './components/views/Dashboard.vue'
import SummaryView from './components/views/Summary.vue'
import TaxonomyView from './components/views/Taxonomy.vue'

const routes =
  [ { path: '/login'
    , component: LoginView
    }
  , { path: '/'
    , component: ToztiLayout
    , children:
        [ { path: '/',      component: DashboardView }
        , { path: 'w/:id',  component: SummaryView }
        , { path: 'w/:taxonomy+', component: TaxonomyView, props: true }
        ]
    }
  ]

export default routes
