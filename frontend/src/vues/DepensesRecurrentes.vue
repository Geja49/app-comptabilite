<script setup>
import { ref, onMounted } from 'vue'
import api, { formaterMontant } from '../services/api'

const recurrentes = ref([])
const categories = ref([])
const formulaire = ref(null)

async function charger() {
  const [rec, cat] = await Promise.all([
    api.get('/api/depenses-recurrentes'),
    api.get('/api/categories'),
  ])
  recurrentes.value = rec.data
  categories.value = cat.data
}

function nouvelle() {
  formulaire.value = {
    fournisseur: '',
    categorie_id: categories.value[0]?.id || 1,
    montant: 0,
    montant_ttc: false,
    jour_du_mois: 1,
    actif: true,
  }
}

async function sauvegarder() {
  await api.post('/api/depenses-recurrentes', formulaire.value)
  formulaire.value = null
  await charger()
}

async function basculerActif(rec) {
  await api.put(`/api/depenses-recurrentes/${rec.id}`, { ...rec, actif: !rec.actif })
  await charger()
}

async function supprimer(id) {
  if (!confirm('Supprimer cette dépense récurrente ?')) return
  await api.delete(`/api/depenses-recurrentes/${id}`)
  await charger()
}

onMounted(charger)
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-semibold">Dépenses récurrentes</h3>
      <button class="btn-primary" @click="nouvelle">Ajouter</button>
    </div>

    <div v-if="formulaire" class="card space-y-4">
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
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
          <input v-model.number="formulaire.montant" type="number" min="0" step="0.01" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Jour du mois</label>
          <input v-model.number="formulaire.jour_du_mois" type="number" min="1" max="28" class="input" />
        </div>
        <div class="flex items-end">
          <label class="flex items-center gap-2">
            <input v-model="formulaire.montant_ttc" type="checkbox" />
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
            <th>Fournisseur</th>
            <th>Catégorie</th>
            <th>Montant</th>
            <th>Jour</th>
            <th>Statut</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!recurrentes.length"><td colspan="6" class="text-center text-slate-500">Aucune dépense récurrente</td></tr>
          <tr v-for="rec in recurrentes" :key="rec.id">
            <td>{{ rec.fournisseur }}</td>
            <td>{{ rec.categorie_nom }}</td>
            <td>{{ formaterMontant(rec.montant) }} {{ rec.montant_ttc ? '(TTC)' : '(HT)' }}</td>
            <td>{{ rec.jour_du_mois }}</td>
            <td>
              <button
                class="text-sm px-2 py-1 rounded"
                :class="rec.actif ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'"
                @click="basculerActif(rec)"
              >
                {{ rec.actif ? 'Actif' : 'Inactif' }}
              </button>
            </td>
            <td><button class="btn-danger" @click="supprimer(rec.id)">Suppr.</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
