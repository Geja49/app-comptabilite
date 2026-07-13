<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useComptabiliteStore } from './stores/comptabilite'
import { NOMS_MOIS } from './services/api'
import SelecteurPeriode from './composants/SelecteurPeriode.vue'

const route = useRoute()
const store = useComptabiliteStore()

const modeAnnuel = computed(() => route.name === 'sommaire')
const titrePeriode = computed(() => `${NOMS_MOIS[store.mois - 1]} ${store.annee}`)

const liensMensuels = [
  { to: '/revenus', label: 'Revenus' },
  { to: '/depenses', label: 'Dépenses' },
  { to: '/kilometrage', label: 'Kilométrage' },
]

const liensConfig = [
  { to: '/categories', label: 'Catégories' },
  { to: '/depenses-recurrentes', label: 'Dépenses récurrentes' },
]
</script>

<template>
  <div class="min-h-screen flex">
    <aside class="w-64 bg-slate-900 text-white flex flex-col">
      <div class="p-6 border-b border-slate-700">
        <h1 class="text-xl font-bold">Comptabilité Taxi</h1>
        <p class="text-slate-400 text-sm mt-1">Transport de personnes</p>
      </div>

      <nav class="flex-1 p-4 space-y-6">
        <div>
          <RouterLink to="/" class="nav-link" active-class="nav-active">Tableau de bord</RouterLink>
        </div>

        <div>
          <p class="text-xs uppercase text-slate-500 mb-2 px-3">Mensuel</p>
          <div class="space-y-1">
            <RouterLink v-for="lien in liensMensuels" :key="lien.to" :to="lien.to" class="nav-link" active-class="nav-active">
              {{ lien.label }}
            </RouterLink>
          </div>
        </div>

        <div>
          <p class="text-xs uppercase text-slate-500 mb-2 px-3">Annuel</p>
          <RouterLink to="/sommaire" class="nav-link" active-class="nav-active">Sommaire annuel</RouterLink>
        </div>

        <div>
          <p class="text-xs uppercase text-slate-500 mb-2 px-3">Configuration</p>
          <div class="space-y-1">
            <RouterLink v-for="lien in liensConfig" :key="lien.to" :to="lien.to" class="nav-link" active-class="nav-active">
              {{ lien.label }}
            </RouterLink>
          </div>
        </div>
      </nav>
    </aside>

    <main class="flex-1 flex flex-col">
      <header class="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between">
        <div>
          <h2 v-if="!modeAnnuel && route.name !== 'accueil'" class="text-lg font-semibold text-slate-800">
            Comptabilité de {{ titrePeriode }}
          </h2>
          <h2 v-else-if="route.name === 'sommaire'" class="text-lg font-semibold text-slate-800">
            Sommaire annuel {{ store.annee }}
          </h2>
        </div>
        <SelecteurPeriode :mode-annuel="modeAnnuel" />
      </header>

      <div class="flex-1 p-8 overflow-auto">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.nav-link {
  @apply block px-3 py-2 rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white transition;
}
.nav-active {
  @apply bg-blue-700 text-white;
}
</style>
