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
  <div class="flex items-center gap-3">
    <select v-model="store.annee" class="input w-auto">
      <option v-for="a in annees" :key="a" :value="a">{{ a }}</option>
    </select>
    <select v-if="!modeAnnuel" v-model="store.mois" class="input w-auto">
      <option v-for="(nom, index) in NOMS_MOIS" :key="nom" :value="index + 1">{{ nom }}</option>
    </select>
  </div>
</template>
