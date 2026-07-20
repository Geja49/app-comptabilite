<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useComptabiliteStore } from './stores/comptabilite'
import {
  effacerSession,
  lireEmailSession,
  NOMS_MOIS,
  surErreurApi,
  surNonAutorise,
} from './services/api'
import SelecteurPeriode from './composants/SelecteurPeriode.vue'

const route = useRoute()
const router = useRouter()
const store = useComptabiliteStore()
const menuOuvert = ref(false)

const pagePublique = computed(() => route.meta.publique === true)

const modeAnnuel = computed(() => ['sommaire', 'parametres-fiscaux'].includes(route.name))
const titrePeriode = computed(() => `${NOMS_MOIS[store.mois - 1]} ${store.annee}`)

const saisieOuverte = computed(() =>
  ['revenus', 'depenses', 'kilometrage', 'tresorerie'].includes(route.name),
)
const configOuverte = computed(() =>
  ['categories', 'depenses-recurrentes', 'parametres-fiscaux'].includes(route.name),
)

const liensSaisie = [
  { to: '/revenus', label: 'Revenus', description: 'Courses et encaissements' },
  { to: '/depenses', label: 'Dépenses', description: 'Achats et charges' },
  { to: '/kilometrage', label: 'Kilométrage', description: 'Usage professionnel' },
  { to: '/tresorerie', label: 'Trésorerie', description: 'Caisse et banque' },
]

const liensConfig = [
  { to: '/categories', label: 'Catégories', description: 'Classement des dépenses' },
  { to: '/depenses-recurrentes', label: 'Récurrentes', description: 'Location et abonnements' },
  { to: '/parametres-fiscaux', label: 'Paramètres fiscaux', description: 'TPS, TVQ et méthodes' },
]

const titresPage = {
  accueil: { titre: 'Accueil', sousTitre: 'Tableau de bord et accès rapide' },
  revenus: { titre: 'Revenus', sousTitre: 'Saisie journalière des courses' },
  depenses: { titre: 'Dépenses', sousTitre: 'Charges et location véhicule' },
  kilometrage: { titre: 'Kilométrage', sousTitre: 'Suivi odomètre et taux pro' },
  tresorerie: { titre: 'Trésorerie', sousTitre: 'Caisse, banque et encaissements en temps réel' },
  sommaire: { titre: 'Sommaire annuel', sousTitre: 'Performance et taxes à remettre' },
  categories: { titre: 'Catégories', sousTitre: 'Organisation des dépenses' },
  'depenses-recurrentes': { titre: 'Dépenses récurrentes', sousTitre: 'Génération automatique mensuelle ou journalière' },
  'parametres-fiscaux': { titre: 'Paramètres fiscaux', sousTitre: 'Méthode régulière ou rapide' },
}

const page = computed(() => titresPage[route.name] || { titre: 'ComptaTaxi', sousTitre: '' })
const enTeteComplement = computed(() => {
  if (route.name === 'accueil') return null
  if (modeAnnuel.value) return `Année ${store.annee}`
  return titrePeriode.value
})

const emailSession = computed(() => lireEmailSession())
const erreur = ref('')
let minuterie = null
surErreurApi((message) => {
  erreur.value = message
  clearTimeout(minuterie)
  minuterie = setTimeout(() => (erreur.value = ''), 6000)
})
surNonAutorise(() => {
  if (route.name !== 'connexion') {
    router.push({ name: 'connexion' })
  }
})

watch(() => route.fullPath, () => {
  menuOuvert.value = false
})

function deconnecter() {
  effacerSession()
  menuOuvert.value = false
  router.push({ name: 'connexion' })
}
</script>

<template>
  <RouterView v-if="pagePublique" />

  <div v-else class="min-h-screen flex bg-fond">
    <!-- Overlay mobile -->
    <div
      v-if="menuOuvert"
      class="fixed inset-0 bg-encre/40 z-40 lg:hidden"
      @click="menuOuvert = false"
    />

    <aside
      class="fixed lg:static inset-y-0 left-0 z-50 w-[min(100%,288px)] bg-white/95 backdrop-blur-md border-r border-trait flex flex-col shrink-0 transition-transform duration-300 lg:translate-x-0 shadow-douce lg:shadow-none"
      :class="menuOuvert ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <div class="px-5 pt-6 pb-4 flex items-start justify-between gap-2">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-indigo-700 text-white flex items-center justify-center shadow-douce">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 17h8M6 9h12l-1 8H7L6 9zm3-4h6l1 4H8l1-4z" />
            </svg>
          </div>
          <div>
            <p class="font-extrabold text-encre leading-tight">ComptaTaxi</p>
            <p class="text-xs text-muet">Transport de personnes</p>
          </div>
        </div>
        <button
          type="button"
          class="lg:hidden text-muet text-2xl leading-none px-2"
          aria-label="Fermer le menu"
          @click="menuOuvert = false"
        >
          &times;
        </button>
      </div>

      <nav class="flex-1 px-3 pb-6 space-y-1 overflow-y-auto">
        <RouterLink
          to="/"
          class="menu-item"
          :class="{ 'menu-item-actif': route.name === 'accueil' }"
        >
          <span class="nav-icone">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 10.5V20h6v-5h4v5h6V10.5L12 4 4 10.5z" />
            </svg>
          </span>
          <span>
            <span class="block text-sm font-bold text-encre">Tableau de bord</span>
            <span class="block text-xs text-muet">Vue d’ensemble</span>
          </span>
        </RouterLink>

        <div class="pt-2">
          <div class="menu-item pointer-events-none" :class="{ 'opacity-100': saisieOuverte }">
            <span class="nav-icone">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 4h10v16H7zM9 8h6M9 12h6M9 16h4" />
              </svg>
            </span>
            <span>
              <span class="block text-sm font-bold text-encre">Saisie mensuelle</span>
              <span class="block text-xs text-muet">Revenus, dépenses et km</span>
            </span>
          </div>
          <div class="ml-6 mt-1 border-l-2 border-indigo-100 pl-3 space-y-0.5">
            <RouterLink
              v-for="lien in liensSaisie"
              :key="lien.to"
              :to="lien.to"
              class="sous-menu"
              :class="{ 'sous-menu-actif': route.path === lien.to }"
            >
              {{ lien.label }}
            </RouterLink>
          </div>
        </div>

        <RouterLink
          to="/sommaire"
          class="menu-item"
          :class="{ 'menu-item-actif': route.name === 'sommaire' }"
        >
          <span class="nav-icone">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 19V5M8 19V9M12 19v-6M16 19V7M20 19V11" />
            </svg>
          </span>
          <span>
            <span class="block text-sm font-bold text-encre">Sommaire annuel</span>
            <span class="block text-xs text-muet">Rapports et taxes</span>
          </span>
        </RouterLink>

        <div class="pt-2">
          <div class="menu-item pointer-events-none">
            <span class="nav-icone">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15.5a3.5 3.5 0 100-7 3.5 3.5 0 000 7z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.4 15a1.7 1.7 0 00.3 1.9l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.9-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1-1.5 1.7 1.7 0 00-1.9.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.9 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.5-1 1.7 1.7 0 00-.3-1.9l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.9.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.9-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.9V9c0 .7.4 1.3 1 1.5H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z" />
              </svg>
            </span>
            <span>
              <span class="block text-sm font-bold text-encre">Configuration</span>
              <span class="block text-xs text-muet">Paramètres de l’application</span>
            </span>
          </div>
          <div
            class="ml-6 mt-1 border-l-2 pl-3 space-y-0.5"
            :class="configOuverte ? 'border-indigo-200' : 'border-indigo-100'"
          >
            <RouterLink
              v-for="lien in liensConfig"
              :key="lien.to"
              :to="lien.to"
              class="sous-menu"
              :class="{ 'sous-menu-actif': route.path === lien.to }"
            >
              {{ lien.label }}
            </RouterLink>
          </div>
        </div>
      </nav>

      <div class="px-4 py-4 border-t border-trait space-y-2">
        <p v-if="emailSession" class="text-xs text-muet truncate px-1">{{ emailSession }}</p>
        <button
          type="button"
          class="w-full text-sm font-semibold text-indigo-700 hover:bg-white/80 rounded-xl py-2"
          @click="deconnecter"
        >
          Se déconnecter
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col min-w-0 w-full">
      <header class="px-4 sm:px-6 lg:px-8 pt-4 sm:pt-7 pb-4 flex flex-wrap items-start justify-between gap-3 sm:gap-4">
        <div class="flex items-start gap-3 min-w-0">
          <button
            type="button"
            class="lg:hidden mt-1 w-10 h-10 rounded-xl border border-trait bg-surface flex items-center justify-center shrink-0"
            aria-label="Ouvrir le menu"
            @click="menuOuvert = true"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
          <div class="min-w-0">
            <h1 class="titre-page truncate">{{ page.titre }}</h1>
            <p class="sous-titre-page">
              {{ page.sousTitre }}
              <span v-if="enTeteComplement" class="text-encre font-medium"> · {{ enTeteComplement }}</span>
            </p>
          </div>
        </div>
        <SelecteurPeriode :mode-annuel="modeAnnuel" />
      </header>

      <div class="flex-1 px-4 sm:px-6 lg:px-8 pb-10 overflow-auto">
        <RouterView />
      </div>
    </main>

    <Transition name="glisser">
      <div
        v-if="erreur"
        class="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:bottom-6 sm:max-w-sm bg-red-600 text-white px-4 py-3 rounded-bouton shadow-carte flex items-start gap-3 z-50"
      >
        <span class="text-sm flex-1">{{ erreur }}</span>
        <button class="text-white/80 hover:text-white" @click="erreur = ''">&times;</button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.menu-item {
  @apply flex items-start gap-3 px-3 py-2.5 rounded-xl transition;
}
.menu-item:hover {
  @apply bg-white/70;
}
.menu-item-actif {
  @apply bg-white shadow-douce;
}
.sous-menu {
  @apply block py-2 px-2 rounded-lg text-sm font-semibold text-muet hover:text-indigo-700 hover:bg-white/80 transition;
}
.sous-menu-actif {
  @apply text-indigo-700 bg-white shadow-douce;
}
.glisser-enter-active,
.glisser-leave-active {
  transition: all 0.3s ease;
}
.glisser-enter-from,
.glisser-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
</style>
