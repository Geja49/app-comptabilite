<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { formaterMontant } from '../services/api'

const resume = ref(null)
const operations = ref([])
const chargement = ref(true)
const formulaireOuvert = ref(false)

const LIBELLES_TYPE = {
  encaissement: 'Encaissement',
  depot: 'Dépôt bancaire',
  retrait: 'Retrait',
  paiement: 'Paiement',
  transfert: 'Transfert',
  ajustement: 'Ajustement',
}

const aujourdHui = new Date().toISOString().slice(0, 10)

const formulaire = ref({
  date_operation: aujourdHui,
  type_operation: 'encaissement',
  compte_id: null,
  compte_contrepartie_id: null,
  montant: 0,
  est_entree: true,
  libelle: '',
  reference: '',
})

const comptes = computed(() => resume.value?.comptes || [])
const caisses = computed(() => comptes.value.filter((c) => c.type_compte === 'caisse'))
const banques = computed(() => comptes.value.filter((c) => c.type_compte === 'banque'))

const besoinContrepartie = computed(() =>
  ['depot', 'retrait', 'transfert'].includes(formulaire.value.type_operation),
)

const besoinSens = computed(() => formulaire.value.type_operation === 'ajustement')

async function charger() {
  chargement.value = true
  try {
    const [r, ops] = await Promise.all([
      api.get('/api/tresorerie/resume'),
      api.get('/api/tresorerie/operations', { params: { limite: 100 } }),
    ])
    resume.value = r.data
    operations.value = ops.data
    if (!formulaire.value.compte_id && r.data.comptes.length) {
      formulaire.value.compte_id = r.data.comptes[0].id
    }
  } finally {
    chargement.value = false
  }
}

function preparerType() {
  const type = formulaire.value.type_operation
  if (type === 'encaissement') {
    formulaire.value.compte_id = caisses.value[0]?.id || banques.value[0]?.id
    formulaire.value.compte_contrepartie_id = null
    formulaire.value.libelle = formulaire.value.libelle || 'Encaissement courses'
  } else if (type === 'depot') {
    formulaire.value.compte_id = caisses.value[0]?.id
    formulaire.value.compte_contrepartie_id = banques.value[0]?.id
    formulaire.value.libelle = formulaire.value.libelle || 'Dépôt à la banque'
  } else if (type === 'retrait') {
    formulaire.value.compte_id = banques.value[0]?.id
    formulaire.value.compte_contrepartie_id = caisses.value[0]?.id
    formulaire.value.libelle = formulaire.value.libelle || 'Retrait d’espèces'
  } else if (type === 'paiement') {
    formulaire.value.libelle = formulaire.value.libelle || 'Paiement'
  }
}

async function enregistrer() {
  const payload = {
    ...formulaire.value,
    montant: Number(formulaire.value.montant),
    reference: formulaire.value.reference || null,
    compte_contrepartie_id: besoinContrepartie.value
      ? formulaire.value.compte_contrepartie_id
      : null,
    est_entree: besoinSens.value ? formulaire.value.est_entree : null,
  }
  await api.post('/api/tresorerie/operations', payload)
  formulaireOuvert.value = false
  formulaire.value = {
    date_operation: aujourdHui,
    type_operation: 'encaissement',
    compte_id: caisses.value[0]?.id || null,
    compte_contrepartie_id: null,
    montant: 0,
    est_entree: true,
    libelle: '',
    reference: '',
  }
  await charger()
}

async function supprimer(id) {
  if (!confirm('Supprimer cette opération de trésorerie ?')) return
  await api.delete(`/api/tresorerie/operations/${id}`)
  await charger()
}

onMounted(charger)
</script>

<template>
  <div v-if="chargement" class="text-muet">Chargement...</div>
  <div v-else class="space-y-6">
    <p class="text-sm text-muet max-w-3xl">
      Suivi de trésorerie en temps réel (approche NCECF simplifiée) : registres
      <strong>caisse</strong> et <strong>banque</strong>, encaissements, dépôts et paiements.
    </p>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card bg-gradient-to-b from-emerald-50 to-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-muet">Caisse (espèces)</p>
        <p class="text-2xl font-extrabold text-emerald-700 mt-2">{{ formaterMontant(resume.total_caisse) }}</p>
      </div>
      <div class="card bg-gradient-to-b from-indigo-50 to-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-muet">Banque</p>
        <p class="text-2xl font-extrabold text-indigo-700 mt-2">{{ formaterMontant(resume.total_banque) }}</p>
      </div>
      <div class="card bg-gradient-to-b from-slate-50 to-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-muet">Trésorerie totale</p>
        <p class="text-2xl font-extrabold text-encre mt-2">{{ formaterMontant(resume.total_tresorerie) }}</p>
      </div>
    </div>

    <div class="card">
      <h3 class="font-bold text-encre mb-3">Comptes</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="compte in comptes"
          :key="compte.id"
          class="flex items-center justify-between rounded-xl border border-trait px-4 py-3"
        >
          <div>
            <p class="font-semibold text-encre">{{ compte.nom }}</p>
            <p class="text-xs text-muet capitalize">{{ compte.type_compte }}</p>
          </div>
          <p class="font-extrabold" :class="compte.solde_actuel >= 0 ? 'text-emerald-700' : 'text-rose-600'">
            {{ formaterMontant(compte.solde_actuel) }}
          </p>
        </div>
      </div>
    </div>

    <div class="flex justify-between items-center gap-3">
      <h3 class="font-bold text-encre">Journal des opérations</h3>
      <button class="btn-primary" @click="formulaireOuvert = true; preparerType()">Nouvelle opération</button>
    </div>

    <div v-if="formulaireOuvert" class="card space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="text-sm text-slate-600">Date</label>
          <input v-model="formulaire.date_operation" type="date" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Type</label>
          <select v-model="formulaire.type_operation" class="input" @change="preparerType">
            <option value="encaissement">Encaissement (argent reçu)</option>
            <option value="depot">Dépôt caisse → banque</option>
            <option value="retrait">Retrait banque → caisse</option>
            <option value="paiement">Paiement (sortie)</option>
            <option value="transfert">Transfert entre comptes</option>
            <option value="ajustement">Ajustement / conciliation</option>
          </select>
        </div>
        <div>
          <label class="text-sm text-slate-600">Montant</label>
          <input v-model.number="formulaire.montant" type="number" min="0.01" step="0.01" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">
            {{ besoinContrepartie ? 'Compte source' : 'Compte' }}
          </label>
          <select v-model="formulaire.compte_id" class="input">
            <option v-for="c in comptes" :key="c.id" :value="c.id">{{ c.nom }}</option>
          </select>
        </div>
        <div v-if="besoinContrepartie">
          <label class="text-sm text-slate-600">Compte destination</label>
          <select v-model="formulaire.compte_contrepartie_id" class="input">
            <option v-for="c in comptes" :key="c.id" :value="c.id">{{ c.nom }}</option>
          </select>
        </div>
        <div v-if="besoinSens">
          <label class="text-sm text-slate-600">Sens</label>
          <select v-model="formulaire.est_entree" class="input">
            <option :value="true">Entrée (+)</option>
            <option :value="false">Sortie (−)</option>
          </select>
        </div>
        <div>
          <label class="text-sm text-slate-600">Libellé</label>
          <input v-model="formulaire.libelle" type="text" class="input" placeholder="Ex. Encaissement journée" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Référence (chèque / bordereau)</label>
          <input v-model="formulaire.reference" type="text" class="input" />
        </div>
      </div>
      <div class="flex gap-2">
        <button class="btn-primary" @click="enregistrer">Enregistrer</button>
        <button class="btn-secondary" @click="formulaireOuvert = false">Annuler</button>
      </div>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-muet border-b border-trait">
            <th class="py-2 pr-3">Date</th>
            <th class="py-2 pr-3">Type</th>
            <th class="py-2 pr-3">Compte</th>
            <th class="py-2 pr-3">Libellé</th>
            <th class="py-2 pr-3 text-right">Montant</th>
            <th class="py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!operations.length">
            <td colspan="6" class="py-6 text-center text-muet">Aucune opération enregistrée.</td>
          </tr>
          <tr
            v-for="op in operations"
            :key="op.id"
            class="border-b border-trait/60"
          >
            <td class="py-2.5 pr-3">{{ op.date_operation }}</td>
            <td class="py-2.5 pr-3">{{ LIBELLES_TYPE[op.type_operation] || op.type_operation }}</td>
            <td class="py-2.5 pr-3">
              {{ op.compte_nom }}
              <span v-if="op.compte_contrepartie_nom" class="text-muet"> ↔ {{ op.compte_contrepartie_nom }}</span>
            </td>
            <td class="py-2.5 pr-3">
              {{ op.libelle }}
              <span v-if="op.reference" class="text-xs text-muet"> · {{ op.reference }}</span>
            </td>
            <td
              class="py-2.5 pr-3 text-right font-semibold"
              :class="op.est_entree ? 'text-emerald-700' : 'text-rose-600'"
            >
              {{ op.est_entree ? '+' : '−' }}{{ formaterMontant(op.montant) }}
            </td>
            <td class="py-2.5 text-right">
              <button class="text-rose-600 text-xs font-semibold" @click="supprimer(op.id)">Supprimer</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
