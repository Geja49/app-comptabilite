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
    <section id="hero-accueil" class="hero-accueil" aria-labelledby="titre-hero-accueil">
      <div class="cs-container">
        <div class="cs-flex-group">
          <span class="cs-topper">ComptaTaxi · Québec</span>
          <h2 id="titre-hero-accueil" class="cs-title">Votre comptabilité taxi, claire et à jour</h2>
          <p class="cs-text">
            Suivez revenus, dépenses, taxes et trésorerie pour {{ libellePeriode }} — chaque compte
            reste privé, avec ses propres données.
          </p>
          <div class="cs-button-group">
            <RouterLink to="/revenus" class="cs-button-solid cs-button">Saisir les revenus</RouterLink>
            <RouterLink to="/sommaire" class="cs-button-transparent cs-button">Voir le sommaire</RouterLink>
          </div>
        </div>
      </div>
      <div class="cs-picture" aria-hidden="true">
        <div class="cs-fond" />
      </div>
    </section>

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

.hero-accueil {
  position: relative;
  z-index: 1;
  overflow: hidden;
  border-radius: 1.25rem;
  padding: 0 1rem;
}

.hero-accueil .cs-picture {
  position: absolute;
  inset: 0;
  z-index: -2;
  display: block;
}

.hero-accueil .cs-picture::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: #0f172a;
  opacity: 0.55;
  pointer-events: none;
}

.hero-accueil .cs-fond {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 80% at 20% 30%, rgba(29, 78, 216, 0.55), transparent 55%),
    radial-gradient(ellipse 50% 60% at 90% 70%, rgba(15, 23, 42, 0.35), transparent 50%),
    linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 42%, #0f172a 100%);
  background-size: cover;
}

.hero-accueil .cs-container {
  position: relative;
  width: 100%;
  max-width: 80rem;
  margin: 0 auto;
  padding: clamp(3.5rem, 10vw, 5.5rem) 0;
}

.hero-accueil .cs-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, rgba(248, 250, 252, 0.45), rgba(248, 250, 252, 0));
}

.hero-accueil .cs-flex-group {
  width: min(80vw, 35rem);
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: center;
  box-sizing: border-box;
}

.hero-accueil .cs-topper {
  display: block;
  width: 100%;
  margin-bottom: 1rem;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.1rem;
  font-size: clamp(0.8125rem, 1.6vw, 1rem);
  font-weight: 700;
  line-height: 1.2;
  color: #93c5fd;
}

.hero-accueil .cs-title {
  width: 100%;
  margin: 0 auto clamp(1.25rem, 3vw, 1.75rem);
  text-align: center;
  font-size: clamp(1.75rem, 4.5vw, 2.75rem);
  font-weight: 900;
  line-height: 1.2;
  color: #fff;
}

.hero-accueil .cs-text {
  width: 100%;
  margin: 0 auto clamp(1.75rem, 4vw, 2.5rem);
  text-align: center;
  font-size: clamp(1rem, 1.8vw, 1.125rem);
  line-height: 1.5;
  color: rgba(248, 250, 252, 0.92);
}

.hero-accueil .cs-button-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(0.75rem, 2vw, 1rem);
  width: 100%;
}

.hero-accueil .cs-button {
  min-width: 12rem;
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 700;
  box-sizing: border-box;
  transition: color 0.3s, background-color 0.3s, transform 0.3s;
}

.hero-accueil .cs-button-solid {
  display: inline-block;
  padding: 0 2rem;
  line-height: 3rem;
  text-align: center;
  color: #fff;
  background-color: #1d4ed8;
  border: none;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.hero-accueil .cs-button-solid::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  z-index: -1;
  width: 0;
  height: 100%;
  background: #0f172a;
  transition: width 0.3s;
}

.hero-accueil .cs-button-solid:hover::before {
  width: 100%;
}

.hero-accueil .cs-button-transparent {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 3rem;
  padding: 0 1.5rem;
  color: #fff;
  background: transparent;
  border: 1px solid rgba(248, 250, 252, 0.85);
  position: relative;
  z-index: 1;
}

.hero-accueil .cs-button-transparent::before {
  content: '';
  position: absolute;
  inset: -1px;
  z-index: -1;
  background: #0f172a;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s;
}

.hero-accueil .cs-button-transparent:hover::before {
  transform: scaleX(1);
}

@media (min-width: 48rem) {
  .hero-accueil {
    padding: 0 clamp(1.25rem, 3vw, 2rem);
  }

  .hero-accueil .cs-container::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 1px;
    height: 100%;
    background: linear-gradient(to bottom, rgba(248, 250, 252, 0), rgba(248, 250, 252, 0.45));
  }

  .hero-accueil .cs-button-group {
    flex-direction: row;
  }
}
</style>
