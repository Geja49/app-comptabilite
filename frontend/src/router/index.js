import { createRouter, createWebHistory } from 'vue-router'
import Accueil from '../vues/Accueil.vue'
import Revenus from '../vues/Revenus.vue'
import Depenses from '../vues/Depenses.vue'
import Kilometrage from '../vues/Kilometrage.vue'
import Sommaire from '../vues/Sommaire.vue'
import Categories from '../vues/Categories.vue'
import DepensesRecurrentes from '../vues/DepensesRecurrentes.vue'
import ParametresFiscaux from '../vues/ParametresFiscaux.vue'
import Connexion from '../vues/Connexion.vue'
import { estConnecte } from '../services/api'

const routes = [
  { path: '/connexion', name: 'connexion', component: Connexion, meta: { publique: true } },
  { path: '/', name: 'accueil', component: Accueil },
  { path: '/revenus', name: 'revenus', component: Revenus },
  { path: '/depenses', name: 'depenses', component: Depenses },
  { path: '/kilometrage', name: 'kilometrage', component: Kilometrage },
  { path: '/sommaire', name: 'sommaire', component: Sommaire },
  { path: '/categories', name: 'categories', component: Categories },
  { path: '/depenses-recurrentes', name: 'depenses-recurrentes', component: DepensesRecurrentes },
  { path: '/parametres-fiscaux', name: 'parametres-fiscaux', component: ParametresFiscaux },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((vers) => {
  if (vers.meta.publique) {
    if (estConnecte() && vers.name === 'connexion') return { name: 'accueil' }
    return true
  }
  if (!estConnecte()) return { name: 'connexion', query: { suivant: vers.fullPath } }
  return true
})

export default router
