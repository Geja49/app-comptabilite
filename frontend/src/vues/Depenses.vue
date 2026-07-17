<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useComptabiliteStore } from '../stores/comptabilite'
import api, { formaterMontant, avecConfirmationPassee } from '../services/api'

const store = useComptabiliteStore()
const depenses = ref([])
const categories = ref([])
const chargement = ref(true)
const formulaire = ref(null)

const totaux = computed(() => {
  if (!depenses.value.length) return null
  return {
    montant_ht: depenses.value.reduce((s, d) => s + Number(d.montant_ht), 0),
    tps: depenses.value.reduce((s, d) => s + Number(d.tps), 0),
    tvq: depenses.value.reduce((s, d) => s + Number(d.tvq), 0),
    montant_total: depenses.value.reduce((s, d) => s + Number(d.montant_total), 0),
  }
})

async function charger() {
  chargement.value = true
  const [dep, cat] = await Promise.all([
    api.get(`/api/periodes/${store.annee}/${store.mois}/depenses`),
    api.get('/api/categories'),
  ])
  depenses.value = dep.data
  categories.value = cat.data
  chargement.value = false
}

function nouvelleDepense() {
  formulaire.value = {
    date: `${store.annee}-${String(store.mois).padStart(2, '0')}-01`,
    fournisseur: '',
    categorie_id: categories.value[0]?.id || 1,
    montant_saisi: 0,
    saisie_ttc: false,
  }
}

async function sauvegarder() {
  const payload = { ...formulaire.value }
  await avecConfirmationPassee(store.annee, store.mois, async (confirmer) => {
    await api.post(`/api/periodes/${store.annee}/${store.mois}/depenses`, {
      ...payload,
      confirmer_modification_passee: confirmer,
    })
  })
  formulaire.value = null
  await charger()
}

async function genererRecurrentes() {
  await api.post(`/api/periodes/${store.annee}/${store.mois}/generer-recurrentes`)
  await charger()
}

async function supprimer(id) {
  if (!confirm('Supprimer cette dépense ?')) return
  await avecConfirmationPassee(store.annee, store.mois, async (confirmer) => {
    await api.delete(`/api/periodes/${store.annee}/${store.mois}/depenses/${id}`, {
      params: { confirmer_modification_passee: confirmer },
    })
  })
  await charger()
}

watch([() => store.annee, () => store.mois], charger, { immediate: true })
onMounted(charger)
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center flex-wrap gap-3">
      <p class="text-sm text-muet">Registre du mois</p>
      <div class="flex gap-2">
        <button class="btn-secondary" @click="genererRecurrentes">Générer récurrentes</button>
        <button class="btn-primary" @click="nouvelleDepense">Ajouter une dépense</button>
      </div>
    </div>

    <div v-if="formulaire" class="card space-y-4">
      <h4 class="font-medium">Nouvelle dépense</h4>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div>
          <label class="text-sm text-slate-600">Date</label>
          <input v-model="formulaire.date" type="date" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Fournisseur</label>
          <input v-model="formulaire.fournisseur" type="text" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Catégorie</label>
          <select v-model="formulaire.categorie_id" class="input">
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.nom }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm text-slate-600">Montant</label>
          <input v-model.number="formulaire.montant_saisi" type="number" min="0" step="0.01" class="input" />
        </div>
        <div class="flex items-end gap-4">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="formulaire.saisie_ttc" type="checkbox" />
            <span class="text-sm">Montant TTC</span>
          </label>
        </div>
      </div>
      <div class="flex gap-2">
        <button class="btn-primary" @click="sauvegarder">Enregistrer</button>
        <button class="btn-secondary" @click="formulaire = null">Annuler</button>
      </div>
    </div>

    <div class="card overflow-x-auto">
      <table class="table-base">
        <thead>
          <tr>
            <th>Date</th>
            <th>Fournisseur</th>
            <th>Catégorie</th>
            <th>Montant HT</th>
            <th>TPS</th>
            <th>TVQ</th>
            <th>Total</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="chargement"><td colspan="8" class="text-center text-slate-500">Chargement...</td></tr>
          <tr v-else-if="!depenses.length"><td colspan="8" class="text-center text-slate-500">Aucune dépense saisie</td></tr>
          <tr v-for="depense in depenses" :key="depense.id">
            <td>{{ depense.date }}</td>
            <td>
              {{ depense.fournisseur }}
              <span v-if="depense.est_recurrente" class="ml-1 text-xs bg-blue-100 text-blue-700 px-1 rounded">récurrente</span>
            </td>
            <td>{{ depense.categorie_nom }}</td>
            <td>{{ formaterMontant(depense.montant_ht) }}</td>
            <td>{{ formaterMontant(depense.tps) }}</td>
            <td>{{ formaterMontant(depense.tvq) }}</td>
            <td class="font-medium">{{ formaterMontant(depense.montant_total) }}</td>
            <td><button class="btn-danger" @click="supprimer(depense.id)">Suppr.</button></td>
          </tr>
          <tr v-if="totaux" class="bg-slate-50 font-semibold">
            <td colspan="3">Total</td>
            <td>{{ formaterMontant(totaux.montant_ht) }}</td>
            <td>{{ formaterMontant(totaux.tps) }}</td>
            <td>{{ formaterMontant(totaux.tvq) }}</td>
            <td>{{ formaterMontant(totaux.montant_total) }}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
