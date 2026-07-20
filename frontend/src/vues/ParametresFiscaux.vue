<script setup>
import { ref, computed, watch } from 'vue'
import { useComptabiliteStore } from '../stores/comptabilite'
import {
  obtenirParametresFiscaux,
  definirMethodeFiscale,
  formaterMontant,
  formaterPourcentage,
} from '../services/api'

const store = useComptabiliteStore()
const parametres = ref(null)
const chargement = ref(true)
const enregistrement = ref(false)
const message = ref('')

const methodeChoisie = ref('reguliere')
const frequenceChoisie = ref('annuelle')

const frequences = [
  {
    valeur: 'annuelle',
    titre: 'Annuelle',
    texte: 'Cas fréquent pour chauffeurs (paiement 30 avril, déclaration 15 juin).',
  },
  {
    valeur: 'trimestrielle',
    titre: 'Trimestrielle',
    texte: 'Déclaration et paiement environ un mois après chaque trimestre.',
  },
  {
    valeur: 'mensuelle',
    titre: 'Mensuelle',
    texte: 'Déclaration et paiement environ un mois après chaque mois.',
  },
]

const modifie = computed(
  () =>
    parametres.value &&
    (methodeChoisie.value !== parametres.value.methode_tps_tvq ||
      frequenceChoisie.value !== (parametres.value.frequence_declaration || 'annuelle')),
)

async function charger() {
  chargement.value = true
  message.value = ''
  const { data } = await obtenirParametresFiscaux(store.annee)
  parametres.value = data
  methodeChoisie.value = data.methode_tps_tvq
  frequenceChoisie.value = data.frequence_declaration || 'annuelle'
  chargement.value = false
}

async function enregistrer() {
  if (!modifie.value) return
  enregistrement.value = true
  try {
    const { data } = await definirMethodeFiscale(
      store.annee,
      methodeChoisie.value,
      frequenceChoisie.value,
    )
    parametres.value = data
    methodeChoisie.value = data.methode_tps_tvq
    frequenceChoisie.value = data.frequence_declaration || 'annuelle'
    message.value = 'Paramètres enregistrés'
  } finally {
    enregistrement.value = false
  }
}

watch(() => store.annee, charger, { immediate: true })
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div v-if="chargement" class="text-muet">Chargement...</div>

    <template v-else-if="parametres">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label
          class="card cursor-pointer border-2 transition"
          :class="methodeChoisie === 'reguliere' ? 'border-indigo-600 shadow-douce' : 'border-trait'"
        >
          <div class="flex items-start gap-3">
            <input v-model="methodeChoisie" type="radio" value="reguliere" class="mt-1" />
            <div>
              <p class="font-semibold">Méthode régulière</p>
              <p class="text-sm text-slate-500 mt-1">
                Vous remettez la TPS/TVQ perçue moins celle payée sur vos dépenses.
              </p>
              <ul class="text-sm text-slate-600 mt-3 space-y-1">
                <li>TPS : {{ formaterPourcentage(parametres.tps_taux_reguliere) }} du revenu</li>
                <li>TVQ : {{ formaterPourcentage(parametres.tvq_taux_reguliere) }} du revenu</li>
              </ul>
            </div>
          </div>
        </label>

        <label
          class="card cursor-pointer border-2 transition"
          :class="methodeChoisie === 'rapide' ? 'border-indigo-600 shadow-douce' : 'border-trait'"
        >
          <div class="flex items-start gap-3">
            <input v-model="methodeChoisie" type="radio" value="rapide" class="mt-1" />
            <div>
              <p class="font-semibold">Méthode rapide</p>
              <p class="text-sm text-slate-500 mt-1">
                Vous remettez un pourcentage fixe de votre revenu total (taxes incluses).
              </p>
              <ul class="text-sm text-slate-600 mt-3 space-y-1">
                <li>TPS : {{ formaterPourcentage(parametres.tps_taux_rapide) }} du revenu TTC</li>
                <li>TVQ : {{ formaterPourcentage(parametres.tvq_taux_rapide) }} du revenu TTC</li>
                <li>
                  Rabais de {{ formaterPourcentage(parametres.rabais_rapide_taux) }} sur les premiers
                  {{ formaterMontant(parametres.rabais_rapide_plafond) }}
                </li>
              </ul>
            </div>
          </div>
        </label>
      </div>

      <div class="card space-y-3">
        <div>
          <h3 class="font-bold text-encre">Fréquence de déclaration TPS / TVQ</h3>
          <p class="text-sm text-muet mt-1">
            Selon la confirmation reçue de Revenu Québec. Utilisée pour les rappels du tableau de bord.
          </p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <label
            v-for="freq in frequences"
            :key="freq.valeur"
            class="rounded-xl border-2 p-3 cursor-pointer transition"
            :class="frequenceChoisie === freq.valeur ? 'border-indigo-600 bg-indigo-50/50' : 'border-trait'"
          >
            <div class="flex items-start gap-2">
              <input v-model="frequenceChoisie" type="radio" :value="freq.valeur" class="mt-1" />
              <div>
                <p class="font-semibold text-sm">{{ freq.titre }}</p>
                <p class="text-xs text-muet mt-1 leading-relaxed">{{ freq.texte }}</p>
              </div>
            </div>
          </label>
        </div>
      </div>

      <div class="card bg-slate-50">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <p class="text-sm text-slate-600">
            Redevance de transport :
            <strong>{{ formaterMontant(parametres.redevance_par_course) }}</strong> par course
            (appliquée aux deux méthodes).
          </p>
          <div class="flex items-center gap-3">
            <span v-if="message" class="text-sm text-green-700">{{ message }}</span>
            <button class="btn-primary" :disabled="!modifie || enregistrement" @click="enregistrer">
              {{ enregistrement ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>

      <p class="text-sm text-slate-500">
        Le changement de méthode recalcule automatiquement le sommaire annuel {{ store.annee }}.
        Les dates de rappels sont indicatives (Revenu Québec / ARC).
      </p>
    </template>
  </div>
</template>
