<script setup>
import { ref, watch, onMounted } from 'vue'
import { useComptabiliteStore } from '../stores/comptabilite'
import api, { formaterMontant, avecConfirmationPassee } from '../services/api'

const store = useComptabiliteStore()
const entrees = ref([])
const totaux = ref(null)
const chargement = ref(true)
const formulaire = ref(null)

async function charger() {
  chargement.value = true
  const { data } = await api.get(`/api/periodes/${store.annee}/${store.mois}/kilometrage`)
  entrees.value = data.entrees
  totaux.value = data.totaux
  chargement.value = false
}

function nouvelleEntree() {
  formulaire.value = {
    date: `${store.annee}-${String(store.mois).padStart(2, '0')}-01`,
    odometre_debut: 0,
    odometre_fin: 0,
    km_professionnels: 0,
  }
}

async function sauvegarder() {
  const payload = { ...formulaire.value }
  await avecConfirmationPassee(store.annee, store.mois, async (confirmer) => {
    await api.post(`/api/periodes/${store.annee}/${store.mois}/kilometrage`, {
      ...payload,
      confirmer_modification_passee: confirmer,
    })
  })
  formulaire.value = null
  await charger()
}

async function supprimer(id) {
  if (!confirm('Supprimer cette entrée ?')) return
  await avecConfirmationPassee(store.annee, store.mois, async (confirmer) => {
    await api.delete(`/api/periodes/${store.annee}/${store.mois}/kilometrage/${id}`, {
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
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-semibold">Registre de kilométrage</h3>
      <button class="btn-primary" @click="nouvelleEntree">Ajouter une journée</button>
    </div>

    <div v-if="totaux" class="grid grid-cols-3 gap-4">
      <div class="card text-center">
        <p class="text-sm text-slate-500">Km totaux du mois</p>
        <p class="text-2xl font-bold">{{ totaux.km_totaux_mois }} km</p>
      </div>
      <div class="card text-center">
        <p class="text-sm text-slate-500">Km professionnels</p>
        <p class="text-2xl font-bold">{{ totaux.km_pro_mois }} km</p>
      </div>
      <div class="card text-center">
        <p class="text-sm text-slate-500">Taux d'utilisation pro.</p>
        <p class="text-2xl font-bold">{{ (Number(totaux.taux_pro) * 100).toFixed(1) }} %</p>
      </div>
    </div>

    <div v-if="formulaire" class="card space-y-4">
      <h4 class="font-medium">Nouvelle journée</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label class="text-sm text-slate-600">Date</label>
          <input v-model="formulaire.date" type="date" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Odomètre début</label>
          <input v-model.number="formulaire.odometre_debut" type="number" min="0" step="0.1" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Odomètre fin</label>
          <input v-model.number="formulaire.odometre_fin" type="number" min="0" step="0.1" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Km professionnels</label>
          <input v-model.number="formulaire.km_professionnels" type="number" min="0" step="0.1" class="input" />
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
            <th>Odomètre début</th>
            <th>Odomètre fin</th>
            <th>Km totaux</th>
            <th>Km pro</th>
            <th>Taux pro</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="chargement"><td colspan="7" class="text-center text-slate-500">Chargement...</td></tr>
          <tr v-else-if="!entrees.length"><td colspan="7" class="text-center text-slate-500">Aucune entrée saisie</td></tr>
          <tr v-for="entree in entrees" :key="entree.id">
            <td>{{ entree.date }}</td>
            <td>{{ entree.odometre_debut }}</td>
            <td>{{ entree.odometre_fin }}</td>
            <td>{{ entree.km_totaux }}</td>
            <td>{{ entree.km_professionnels }}</td>
            <td>{{ (Number(entree.taux_pro) * 100).toFixed(1) }} %</td>
            <td><button class="btn-danger" @click="supprimer(entree.id)">Suppr.</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
