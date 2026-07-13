<script setup>
import { ref, onMounted } from 'vue'
import api, { formaterMontant } from '../services/api'

const tableau = ref(null)
const chargement = ref(true)

async function charger() {
  chargement.value = true
  const { data } = await api.get('/api/tableau-de-bord')
  tableau.value = data
  chargement.value = false
}

function exporterExcel() {
  if (!tableau.value) return
  const { annee, mois } = tableau.value.periode
  window.open(`${api.defaults.baseURL}/api/export/excel/${annee}/${mois}`, '_blank')
}

function exporterPdf() {
  if (!tableau.value) return
  window.open(`${api.defaults.baseURL}/api/export/pdf/${tableau.value.periode.annee}`, '_blank')
}

onMounted(charger)
</script>

<template>
  <div v-if="chargement" class="text-slate-500">Chargement...</div>
  <div v-else class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card">
        <p class="text-sm text-slate-500">Revenu brut</p>
        <p class="text-2xl font-bold text-green-700">{{ formaterMontant(tableau.sommaire.revenu_brut) }}</p>
      </div>
      <div class="card">
        <p class="text-sm text-slate-500">Dépenses totales</p>
        <p class="text-2xl font-bold text-red-600">{{ formaterMontant(tableau.sommaire.depenses_totales) }}</p>
      </div>
      <div class="card">
        <p class="text-sm text-slate-500">TPS à remettre</p>
        <p class="text-2xl font-bold text-blue-700">{{ formaterMontant(tableau.sommaire.tps_a_remettre) }}</p>
      </div>
      <div class="card">
        <p class="text-sm text-slate-500">TVQ à remettre</p>
        <p class="text-2xl font-bold text-blue-700">{{ formaterMontant(tableau.sommaire.tvq_a_remettre) }}</p>
      </div>
    </div>

    <div v-if="tableau.alertes.length" class="card border-amber-300 bg-amber-50">
      <h3 class="font-semibold text-amber-800 mb-2">Alertes</h3>
      <ul class="space-y-1">
        <li v-for="(alerte, i) in tableau.alertes" :key="i" class="text-amber-700 text-sm">• {{ alerte.message }}</li>
      </ul>
    </div>

    <div class="card">
      <h3 class="font-semibold mb-4">Accès rapide</h3>
      <div class="flex flex-wrap gap-3">
        <RouterLink to="/revenus" class="btn-primary">Revenus du mois</RouterLink>
        <RouterLink to="/depenses" class="btn-primary">Dépenses du mois</RouterLink>
        <RouterLink to="/kilometrage" class="btn-primary">Kilométrage</RouterLink>
        <RouterLink to="/sommaire" class="btn-secondary">Sommaire annuel</RouterLink>
        <button class="btn-secondary" @click="exporterExcel">Export Excel (mois)</button>
        <button class="btn-secondary" @click="exporterPdf">Export PDF (année)</button>
      </div>
    </div>
  </div>
</template>
