<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useComptabiliteStore } from '../stores/comptabilite'
import api, {
  formaterMontant,
  formaterPourcentage,
  LIBELLES_METHODE,
  NOMS_MOIS,
  telechargerExport,
} from '../services/api'
import DiagrammeBarres from '../composants/DiagrammeBarres.vue'
import DiagrammeLignes from '../composants/DiagrammeLignes.vue'

const store = useComptabiliteStore()
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
  const p = tableau.value.productivite
  return [
    { label: 'Revenu brut', valeur: s.revenu_brut, teinte: 'text-emerald-700', fond: 'from-emerald-50 to-white' },
    { label: 'Dépenses totales', valeur: s.depenses_totales, teinte: 'text-rose-600', fond: 'from-rose-50 to-white' },
    {
      label: 'Bénéfice',
      valeur: p?.benefice ?? Number(s.revenu_brut) - Number(s.depenses_totales),
      teinte: 'text-indigo-700',
      fond: 'from-indigo-50 to-white',
    },
    { label: 'TPS à remettre', valeur: s.tps_a_remettre, teinte: 'text-violet-700', fond: 'from-violet-50 to-white' },
    { label: 'TVQ à remettre', valeur: s.tvq_a_remettre, teinte: 'text-violet-700', fond: 'from-violet-50 to-white' },
  ]
})

const etiquettesMois = computed(() => (tableau.value?.serie_mensuelle || []).map((p) => p.mois_nom))

const seriesVentesDepenses = computed(() => {
  const points = tableau.value?.serie_mensuelle || []
  return [
    { nom: 'Ventes', couleur: '#059669', valeurs: points.map((p) => Number(p.ventes) || 0) },
    { nom: 'Dépenses', couleur: '#E11D48', valeurs: points.map((p) => Number(p.depenses) || 0) },
  ]
})

const seriesBenefice = computed(() => {
  const points = tableau.value?.serie_mensuelle || []
  return [
    { nom: 'Bénéfice', couleur: '#1D4ED8', valeurs: points.map((p) => Number(p.benefice) || 0) },
  ]
})

const seriesCourbes = computed(() => [
  ...seriesVentesDepenses.value,
  ...seriesBenefice.value,
])

const ratiosProductivite = computed(() => {
  const p = tableau.value?.productivite
  if (!p) return []
  return [
    { label: 'Jours travaillés', valeur: `${p.jours_travailles} j` },
    { label: 'Heures (12 h/j)', valeur: `${Number(p.heures_totales).toFixed(0)} h` },
    { label: 'Revenu / heure', valeur: formaterMontant(p.revenu_par_heure) },
    { label: 'Revenu / jour', valeur: formaterMontant(p.revenu_par_jour) },
    { label: 'Bénéfice / heure', valeur: formaterMontant(p.benefice_par_heure) },
    { label: 'Courses / heure', valeur: Number(p.courses_par_heure).toFixed(2) },
    { label: 'Ratio dépenses', valeur: formaterPourcentage(p.ratio_depenses) },
    { label: 'Marge bénéfice', valeur: formaterPourcentage(p.marge_benefice) },
  ]
})

const rappelsFiscaux = computed(() => tableau.value?.rappels_fiscaux || [])

function formaterDateLimite(iso) {
  if (!iso) return ''
  const [annee, mois, jour] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat('fr-CA', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(annee, mois - 1, jour))
}

function libelleJours(rappel) {
  const j = rappel.jours_restants
  if (j < 0) return `En retard de ${Math.abs(j)} j`
  if (j === 0) return "Aujourd'hui"
  return `Dans ${j} j`
}

function classeUrgence(urgence) {
  if (urgence === 'echue' || urgence === 'haute') return 'border-rose-200 bg-rose-50/80'
  if (urgence === 'moyenne') return 'border-amber-200 bg-amber-50/70'
  return 'border-trait bg-barre/60'
}

function badgeUrgence(urgence) {
  if (urgence === 'echue') return 'bg-rose-100 text-rose-800'
  if (urgence === 'haute') return 'bg-orange-100 text-orange-800'
  if (urgence === 'moyenne') return 'bg-amber-100 text-amber-900'
  return 'bg-indigo-50 text-indigo-700'
}

async function charger() {
  chargement.value = true
  try {
    const { data } = await api.get('/api/tableau-de-bord', {
      params: { annee: store.annee, mois: store.mois },
    })
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

watch(() => [store.annee, store.mois], charger)
onMounted(charger)
</script>

<template>
  <div v-if="chargement" class="text-muet">Chargement...</div>
  <div v-else class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-2 sm:gap-3">
        <span class="badge bg-indigo-50 text-indigo-700">{{ libellePeriode }}</span>
        <RouterLink
          to="/parametres-fiscaux"
          class="badge hover:opacity-90 transition"
          :class="estRapide ? 'bg-violet-100 text-violet-700' : 'bg-indigo-100 text-indigo-700'"
        >
          {{ libelleMethode }}
        </RouterLink>
      </div>
      <div class="flex flex-wrap gap-2 w-full sm:w-auto">
        <button class="btn-secondary flex-1 sm:flex-none" @click="exporterExcel">Exporter Excel</button>
        <button class="btn-primary flex-1 sm:flex-none" @click="exporterPdf">Exporter PDF</button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-3 sm:gap-4">
      <div
        v-for="item in indicateurs"
        :key="item.label"
        class="card bg-gradient-to-b p-4 sm:p-5"
        :class="item.fond"
      >
        <p class="text-xs font-semibold uppercase tracking-wide text-muet">{{ item.label }}</p>
        <p class="text-xl sm:text-2xl font-extrabold mt-2" :class="item.teinte">{{ formaterMontant(item.valeur) }}</p>
      </div>
    </div>

    <section class="space-y-4">
      <div>
        <h2 class="text-lg font-extrabold text-encre">Graphiques comptables</h2>
        <p class="text-sm text-muet">Mises à jour automatiques selon vos saisies de l’année.</p>
      </div>
      <div class="grid grid-cols-1 gap-4">
        <DiagrammeLignes
          titre="Courbes ventes, dépenses et bénéfice"
          sous-titre="Vision continue sur 12 mois"
          :etiquettes="etiquettesMois"
          :series="seriesCourbes"
        />
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <DiagrammeBarres
          titre="Ventes et dépenses"
          sous-titre="Comparaison mensuelle"
          :etiquettes="etiquettesMois"
          :series="seriesVentesDepenses"
        />
        <DiagrammeBarres
          titre="Bénéfice"
          sous-titre="Ventes − dépenses par mois"
          :etiquettes="etiquettesMois"
          :series="seriesBenefice"
        />
      </div>
    </section>

    <div v-if="tableau.alertes.length" class="card border-amber-200 bg-amber-50/80">
      <h3 class="font-bold text-amber-900 mb-2">Alertes</h3>
      <ul class="space-y-1.5">
        <li v-for="(alerte, i) in tableau.alertes" :key="i" class="text-amber-800 text-sm flex gap-2">
          <span class="text-amber-500">•</span>
          <span>{{ alerte.message }}</span>
        </li>
      </ul>
    </div>

    <div v-if="rappelsFiscaux.length" class="card">
      <div class="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 class="font-bold text-encre">Rappels fiscaux</h3>
          <p class="text-sm text-muet">
            Déclarations et paiements à surveiller (Revenu Québec / ARC). Ajustez votre fréquence dans
            <RouterLink to="/parametres-fiscaux" class="text-indigo-700 font-semibold">Paramètres fiscaux</RouterLink>.
          </p>
        </div>
      </div>
      <ul class="space-y-3">
        <li
          v-for="(rappel, i) in rappelsFiscaux"
          :key="`${rappel.impot}-${rappel.type}-${rappel.date_limite}-${i}`"
          class="rounded-xl border px-4 py-3"
          :class="classeUrgence(rappel.urgence)"
        >
          <div class="flex flex-wrap items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="font-bold text-encre">{{ rappel.titre }}</p>
              <p class="text-sm text-muet mt-1">{{ rappel.description }}</p>
              <p class="text-xs text-muet mt-2">
                {{ rappel.organisme }} · {{ rappel.periode }} ·
                {{ rappel.type === 'declaration' ? 'Déclaration' : 'Paiement' }}
              </p>
            </div>
            <div class="text-right shrink-0">
              <span class="badge" :class="badgeUrgence(rappel.urgence)">{{ libelleJours(rappel) }}</span>
              <p class="text-sm font-semibold text-encre mt-2">{{ formaterDateLimite(rappel.date_limite) }}</p>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <div class="card">
      <div class="mb-4">
        <h3 class="font-bold text-encre">Productivité ({{ tableau.productivite?.heures_par_jour || 12 }} h / jour)</h3>
        <p class="text-sm text-muet">
          Ratios calculés sur les jours avec revenu saisi pour {{ libellePeriode }}.
        </p>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div
          v-for="ratio in ratiosProductivite"
          :key="ratio.label"
          class="rounded-xl border border-trait bg-barre px-4 py-3"
        >
          <p class="text-xs font-semibold uppercase tracking-wide text-muet">{{ ratio.label }}</p>
          <p class="text-lg font-extrabold text-encre mt-1">{{ ratio.valeur }}</p>
        </div>
      </div>
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
