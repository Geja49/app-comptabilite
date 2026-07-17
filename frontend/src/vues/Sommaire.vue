<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useComptabiliteStore } from '../stores/comptabilite'
import api, { formaterMontant, LIBELLES_METHODE, telechargerExport } from '../services/api'

const store = useComptabiliteStore()
const router = useRouter()
const sommaire = ref(null)
const chargement = ref(true)

const estRapide = computed(() => sommaire.value?.methode_tps_tvq === 'rapide')
const libelleMethode = computed(
  () => LIBELLES_METHODE[sommaire.value?.methode_tps_tvq] || LIBELLES_METHODE.reguliere,
)

async function charger() {
  chargement.value = true
  try {
    const { data } = await api.get(`/api/sommaire/${store.annee}`)
    sommaire.value = data
  } finally {
    chargement.value = false
  }
}

function allerAuMois(mois) {
  store.definirPeriode(store.annee, mois)
  router.push('/revenus')
}

async function exporterPdf() {
  await telechargerExport(`/api/export/pdf/${store.annee}`, `rapport_comptable_${store.annee}.pdf`)
}

async function exporterExcel(mois) {
  await telechargerExport(
    `/api/export/excel/${store.annee}/${mois}`,
    `comptabilite_${store.annee}_${String(mois).padStart(2, '0')}.xlsx`,
  )
}

watch(() => store.annee, charger, { immediate: true })
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-3">
      <div class="flex items-center gap-3">
        <span
          v-if="sommaire"
          class="badge"
          :class="estRapide ? 'bg-violet-100 text-violet-700' : 'bg-indigo-100 text-indigo-700'"
        >
          {{ libelleMethode }}
        </span>
      </div>
      <div class="flex items-center gap-3">
        <RouterLink to="/parametres-fiscaux" class="btn-secondary">Changer de méthode</RouterLink>
        <button class="btn-primary" @click="exporterPdf">Exporter PDF</button>
      </div>
    </div>

    <div v-if="sommaire" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card">
        <p class="text-sm text-slate-500">Revenu brut annuel</p>
        <p class="text-xl font-bold text-green-700">{{ formaterMontant(sommaire.total.revenu_brut) }}</p>
      </div>
      <div class="card">
        <p class="text-sm text-slate-500">TPS à remettre</p>
        <p class="text-xl font-bold text-blue-700">{{ formaterMontant(sommaire.total.tps_a_remettre) }}</p>
      </div>
      <div class="card">
        <p class="text-sm text-slate-500">TVQ à remettre</p>
        <p class="text-xl font-bold text-blue-700">{{ formaterMontant(sommaire.total.tvq_a_remettre) }}</p>
      </div>
      <div class="card">
        <p class="text-sm text-slate-500">Redevance à payer</p>
        <p class="text-xl font-bold text-amber-700">{{ formaterMontant(sommaire.total.redevance_totale) }}</p>
      </div>
    </div>

    <div v-if="estRapide && Number(sommaire?.rabais_rapide_applique) > 0" class="card border-purple-200 bg-purple-50">
      <p class="text-sm text-purple-800">
        Rabais méthode rapide appliqué sur l'année :
        <strong>{{ formaterMontant(sommaire.rabais_rapide_applique) }}</strong>
      </p>
    </div>

    <div class="card overflow-x-auto">
      <table class="table-base">
        <thead>
          <tr>
            <th>Mois</th>
            <th>Revenu brut</th>
            <th v-if="estRapide">Revenu TTC</th>
            <th>TPS perçue</th>
            <th>TVQ perçue</th>
            <th>Dépenses</th>
            <th v-if="!estRapide">TPS payée</th>
            <th v-if="!estRapide">TVQ payée</th>
            <th>TPS à remettre</th>
            <th>TVQ à remettre</th>
            <th v-if="estRapide">Rabais</th>
            <th>Redevance</th>
            <th>Dép. proratées</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="chargement"><td colspan="14" class="text-center text-slate-500">Chargement...</td></tr>
          <template v-else-if="sommaire">
            <tr
              v-for="ligne in sommaire.mois"
              :key="ligne.mois"
              class="hover:bg-slate-50 cursor-pointer"
              @click="allerAuMois(ligne.mois)"
            >
              <td class="font-medium">{{ ligne.mois_nom }}</td>
              <td>{{ formaterMontant(ligne.revenu_brut) }}</td>
              <td v-if="estRapide">{{ formaterMontant(ligne.revenu_total_ttc) }}</td>
              <td>{{ formaterMontant(ligne.tps_percue) }}</td>
              <td>{{ formaterMontant(ligne.tvq_percue) }}</td>
              <td>{{ formaterMontant(ligne.depenses_totales) }}</td>
              <td v-if="!estRapide">{{ formaterMontant(ligne.tps_payee) }}</td>
              <td v-if="!estRapide">{{ formaterMontant(ligne.tvq_payee) }}</td>
              <td>{{ formaterMontant(ligne.tps_a_remettre) }}</td>
              <td>{{ formaterMontant(ligne.tvq_a_remettre) }}</td>
              <td v-if="estRapide">{{ formaterMontant(ligne.rabais_rapide_applique) }}</td>
              <td>{{ formaterMontant(ligne.redevance_totale) }}</td>
              <td>{{ formaterMontant(ligne.depenses_admissibles_proratees) }}</td>
              <td @click.stop>
                <button class="text-blue-600 text-sm hover:underline" @click="exporterExcel(ligne.mois)">Excel</button>
              </td>
            </tr>
            <tr class="bg-slate-100 font-bold">
              <td>{{ sommaire.total.mois_nom }}</td>
              <td>{{ formaterMontant(sommaire.total.revenu_brut) }}</td>
              <td v-if="estRapide">{{ formaterMontant(sommaire.total.revenu_total_ttc) }}</td>
              <td>{{ formaterMontant(sommaire.total.tps_percue) }}</td>
              <td>{{ formaterMontant(sommaire.total.tvq_percue) }}</td>
              <td>{{ formaterMontant(sommaire.total.depenses_totales) }}</td>
              <td v-if="!estRapide">{{ formaterMontant(sommaire.total.tps_payee) }}</td>
              <td v-if="!estRapide">{{ formaterMontant(sommaire.total.tvq_payee) }}</td>
              <td>{{ formaterMontant(sommaire.total.tps_a_remettre) }}</td>
              <td>{{ formaterMontant(sommaire.total.tvq_a_remettre) }}</td>
              <td v-if="estRapide">{{ formaterMontant(sommaire.total.rabais_rapide_applique) }}</td>
              <td>{{ formaterMontant(sommaire.total.redevance_totale) }}</td>
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
