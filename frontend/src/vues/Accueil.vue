<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { formaterMontant, LIBELLES_METHODE, NOMS_MOIS, telechargerExport } from '../services/api'

const tableau = ref(null)
const chargement = ref(true)

const libelleMethode = computed(
  () => LIBELLES_METHODE[tableau.value?.sommaire?.methode_tps_tvq] || LIBELLES_METHODE.reguliere,
)
const estRapide = computed(() => tableau.value?.sommaire?.methode_tps_tvq === 'rapide')
const libellePeriode = computed(() => {
  if (!tableau.value) return ''
  const { mois, annee } = tableau.value.periode
  return `${NOMS_MOIS[mois - 1]} ${annee}`
})

const indicateurs = computed(() => {
  if (!tableau.value) return []
  const s = tableau.value.sommaire
  return [
    { label: 'Revenu brut', valeur: s.revenu_brut, teinte: 'text-emerald-700', fond: 'from-emerald-50 to-white' },
    { label: 'Dépenses totales', valeur: s.depenses_totales, teinte: 'text-rose-600', fond: 'from-rose-50 to-white' },
    { label: 'TPS à remettre', valeur: s.tps_a_remettre, teinte: 'text-indigo-700', fond: 'from-indigo-50 to-white' },
    { label: 'TVQ à remettre', valeur: s.tvq_a_remettre, teinte: 'text-indigo-700', fond: 'from-indigo-50 to-white' },
    { label: 'Redevance', valeur: s.redevance_totale, teinte: 'text-amber-700', fond: 'from-amber-50 to-white' },
  ]
})

async function charger() {
  chargement.value = true
  try {
    const { data } = await api.get('/api/tableau-de-bord')
    tableau.value = data
  } finally {
    chargement.value = false
  }
}

async function exporterExcel() {
  if (!tableau.value) return
  const { annee, mois } = tableau.value.periode
  await telechargerExport(
    `/api/export/excel/${annee}/${mois}`,
    `comptabilite_${annee}_${String(mois).padStart(2, '0')}.xlsx`,
  )
}

async function exporterPdf() {
  if (!tableau.value) return
  const annee = tableau.value.periode.annee
  await telechargerExport(`/api/export/pdf/${annee}`, `rapport_comptable_${annee}.pdf`)
}

onMounted(charger)
</script>

<template>
  <div v-if="chargement" class="text-muet">Chargement...</div>
  <div v-else class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <span class="badge bg-indigo-50 text-indigo-700">{{ libellePeriode }}</span>
        <RouterLink
          to="/parametres-fiscaux"
          class="badge hover:opacity-90 transition"
          :class="estRapide ? 'bg-violet-100 text-violet-700' : 'bg-indigo-100 text-indigo-700'"
        >
          {{ libelleMethode }}
        </RouterLink>
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="btn-secondary" @click="exporterExcel">Exporter Excel</button>
        <button class="btn-primary" @click="exporterPdf">Exporter PDF</button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
      <div
        v-for="item in indicateurs"
        :key="item.label"
        class="card bg-gradient-to-b p-5"
        :class="item.fond"
      >
        <p class="text-xs font-semibold uppercase tracking-wide text-muet">{{ item.label }}</p>
        <p class="text-2xl font-extrabold mt-2" :class="item.teinte">{{ formaterMontant(item.valeur) }}</p>
      </div>
    </div>

    <div v-if="tableau.alertes.length" class="card border-amber-200 bg-amber-50/80">
      <h3 class="font-bold text-amber-900 mb-2">Alertes</h3>
      <ul class="space-y-1.5">
        <li v-for="(alerte, i) in tableau.alertes" :key="i" class="text-amber-800 text-sm flex gap-2">
          <span class="text-amber-500">•</span>
          <span>{{ alerte.message }}</span>
        </li>
      </ul>
    </div>

    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-bold text-encre">Accès rapide</h3>
          <p class="text-sm text-muet">Continuer la saisie du mois</p>
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <RouterLink to="/revenus" class="lien-rapide">
          <span class="nav-icone"><span class="text-sm font-bold">R</span></span>
          <span>
            <span class="block text-sm font-bold">Revenus</span>
            <span class="block text-xs text-muet">Journées de courses</span>
          </span>
        </RouterLink>
        <RouterLink to="/depenses" class="lien-rapide">
          <span class="nav-icone"><span class="text-sm font-bold">D</span></span>
          <span>
            <span class="block text-sm font-bold">Dépenses</span>
            <span class="block text-xs text-muet">Location et charges</span>
          </span>
        </RouterLink>
        <RouterLink to="/kilometrage" class="lien-rapide">
          <span class="nav-icone"><span class="text-sm font-bold">K</span></span>
          <span>
            <span class="block text-sm font-bold">Kilométrage</span>
            <span class="block text-xs text-muet">Taux professionnel</span>
          </span>
        </RouterLink>
        <RouterLink to="/tresorerie" class="lien-rapide">
          <span class="nav-icone"><span class="text-sm font-bold">T</span></span>
          <span>
            <span class="block text-sm font-bold">Trésorerie</span>
            <span class="block text-xs text-muet">Caisse et banque</span>
          </span>
        </RouterLink>
        <RouterLink to="/sommaire" class="lien-rapide">
          <span class="nav-icone"><span class="text-sm font-bold">S</span></span>
          <span>
            <span class="block text-sm font-bold">Sommaire</span>
            <span class="block text-xs text-muet">Bilan de l’année</span>
          </span>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lien-rapide {
  @apply flex items-center gap-3 p-3 rounded-xl border border-trait bg-barre hover:bg-white hover:shadow-douce transition;
}
</style>
