import { createRouter, createWebHistory } from 'vue-router'
import Accueil from '../vues/Accueil.vue'
import Revenus from '../vues/Revenus.vue'
import Depenses from '../vues/Depenses.vue'
import Kilometrage from '../vues/Kilometrage.vue'
import Sommaire from '../vues/Sommaire.vue'
import Categories from '../vues/Categories.vue'
import DepensesRecurrentes from '../vues/DepensesRecurrentes.vue'

const routes = [
  { path: '/', name: 'accueil', component: Accueil },
  { path: '/revenus', name: 'revenus', component: Revenus },
  { path: '/depenses', name: 'depenses', component: Depenses },
  { path: '/kilometrage', name: 'kilometrage', component: Kilometrage },
  { path: '/sommaire', name: 'sommaire', component: Sommaire },
  { path: '/categories', name: 'categories', component: Categories },
  { path: '/depenses-recurrentes', name: 'depenses-recurrentes', component: DepensesRecurrentes },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
