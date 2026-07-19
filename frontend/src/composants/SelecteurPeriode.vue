<script setup>
import { useComptabiliteStore } from '../stores/comptabilite'
import { NOMS_MOIS } from '../services/api'

defineProps({
  modeAnnuel: { type: Boolean, default: false },
})

const store = useComptabiliteStore()
const annees = Array.from({ length: 10 }, (_, i) => new Date().getFullYear() - 5 + i)
</script>

<template>
  <div class="flex items-center gap-1 sm:gap-2 bg-surface border border-trait rounded-bouton p-1 shadow-douce w-full sm:w-auto">
    <select v-model="store.annee" class="input border-0 shadow-none bg-transparent flex-1 sm:w-auto py-2 focus:ring-0 text-sm">
      <option v-for="a in annees" :key="a" :value="a">{{ a }}</option>
    </select>
    <select
      v-if="!modeAnnuel"
      v-model="store.mois"
      class="input border-0 shadow-none bg-transparent flex-1 sm:w-auto py-2 border-l border-trait rounded-none focus:ring-0 text-sm"
    >
      <option v-for="(nom, index) in NOMS_MOIS" :key="nom" :value="index + 1">{{ nom }}</option>
    </select>
  </div>
</template>
