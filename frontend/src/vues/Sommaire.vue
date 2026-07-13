<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useComptabiliteStore } from '../stores/comptabilite'
import api, { formaterMontant } from '../services/api'

const store = useComptabiliteStore()
const router = useRouter()
const sommaire = ref(null)
const chargement = ref(true)

async function charger() {
  chargement.value = true
  const { data } = await api.get(`/api/sommaire/${store.annee}`)
  sommaire.value = data
  chargement.value = false
}

function allerAuMois(mois) {
  store.definirPeriode(store.annee, mois)
  router.push('/revenus')
}

function exporterPdf() {
  window.open(`${api.defaults.baseURL}/api/export/pdf/${store.annee}`, '_blank')
}

function exporterExcel(mois) {
  window.open(`${api.defaults.baseURL}/api/export/excel/${store.annee}/${mois}`, '_blank')
}

watch(() => store.annee, charger, { immediate: true })
onMounted(charger)
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-semibold">Sommaire annuel de performance et taxes</h3>
      <button class="btn-secondary" @click="exporterPdf">Export PDF annuel</button>
    </div>

    <div class="card overflow-x-auto">
      <table class="table-base">
        <thead>
          <tr>
            <th>Mois</th>
            <th>Revenu brut</th>
            <th>TPS perçue</th>
            <th>TVQ perçue</th>
            <th>Dépenses</th>
            <th>TPS payée</th>
            <th>TVQ payée</th>
            <th>TPS à remettre</th>
            <th>TVQ à remettre</th>
            <th>Dép. proratées</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="chargement"><td colspan="11" class="text-center text-slate-500">Chargement...</td></tr>
          <template v-else-if="sommaire">
            <tr
              v-for="ligne in sommaire.mois"
              :key="ligne.mois"
              class="hover:bg-slate-50 cursor-pointer"
              @click="allerAuMois(ligne.mois)"
            >
              <td class="font-medium">{{ ligne.mois_nom }}</td>
              <td>{{ formaterMontant(ligne.revenu_brut) }}</td>
              <td>{{ formaterMontant(ligne.tps_percue) }}</td>
              <td>{{ formaterMontant(ligne.tvq_percue) }}</td>
              <td>{{ formaterMontant(ligne.depenses_totales) }}</td>
              <td>{{ formaterMontant(ligne.tps_payee) }}</td>
              <td>{{ formaterMontant(ligne.tvq_payee) }}</td>
              <td>{{ formaterMontant(ligne.tps_a_remettre) }}</td>
              <td>{{ formaterMontant(ligne.tvq_a_remettre) }}</td>
              <td>{{ formaterMontant(ligne.depenses_admissibles_proratees) }}</td>
              <td @click.stop>
                <button class="text-blue-600 text-sm hover:underline" @click="exporterExcel(ligne.mois)">Excel</button>
              </td>
            </tr>
            <tr class="bg-slate-100 font-bold">
              <td>{{ sommaire.total.mois_nom }}</td>
              <td>{{ formaterMontant(sommaire.total.revenu_brut) }}</td>
              <td>{{ formaterMontant(sommaire.total.tps_percue) }}</td>
              <td>{{ formaterMontant(sommaire.total.tvq_percue) }}</td>
              <td>{{ formaterMontant(sommaire.total.depenses_totales) }}</td>
              <td>{{ formaterMontant(sommaire.total.tps_payee) }}</td>
              <td>{{ formaterMontant(sommaire.total.tvq_payee) }}</td>
              <td>{{ formaterMontant(sommaire.total.tps_a_remettre) }}</td>
              <td>{{ formaterMontant(sommaire.total.tvq_a_remettre) }}</td>
              <td>{{ formaterMontant(sommaire.total.depenses_admissibles_proratees) }}</td>
              <td></td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    <p class="text-sm text-slate-500">Cliquez sur un mois pour accéder à la saisie mensuelle.</p>
  </div>
</template>
