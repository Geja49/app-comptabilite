<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useComptabiliteStore } from '../stores/comptabilite'
import api, { formaterMontant, avecConfirmationPassee } from '../services/api'

const store = useComptabiliteStore()
const revenus = ref([])
const chargement = ref(true)
const formulaire = ref(null)

const totaux = computed(() => {
  if (!revenus.value.length) return null
  return {
    nombre_courses: revenus.value.reduce((s, r) => s + r.nombre_courses, 0),
    revenu_brut: revenus.value.reduce((s, r) => s + Number(r.revenu_brut), 0),
    redevance_gouv: revenus.value.reduce((s, r) => s + Number(r.redevance_gouv), 0),
    tps_percue: revenus.value.reduce((s, r) => s + Number(r.tps_percue), 0),
    tvq_percue: revenus.value.reduce((s, r) => s + Number(r.tvq_percue), 0),
    pourboires: revenus.value.reduce((s, r) => s + Number(r.pourboires), 0),
    total_net_encaisse: revenus.value.reduce((s, r) => s + Number(r.total_net_encaisse), 0),
  }
})

async function charger() {
  chargement.value = true
  const { data } = await api.get(`/api/periodes/${store.annee}/${store.mois}/revenus`)
  revenus.value = data
  chargement.value = false
}

function nouveauRevenu() {
  formulaire.value = {
    date: `${store.annee}-${String(store.mois).padStart(2, '0')}-01`,
    nombre_courses: 0,
    revenu_brut: 0,
    pourboires: 0,
  }
}

async function sauvegarder() {
  const payload = { ...formulaire.value }
  await avecConfirmationPassee(store.annee, store.mois, async (confirmer) => {
    await api.post(`/api/periodes/${store.annee}/${store.mois}/revenus`, {
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
    await api.delete(`/api/periodes/${store.annee}/${store.mois}/revenus/${id}`, {
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
      <p class="text-sm text-muet">Registre des journées</p>
      <button class="btn-primary" @click="nouveauRevenu">Ajouter une journée</button>
    </div>

    <div v-if="formulaire" class="card space-y-4">
      <h4 class="font-medium">Nouvelle journée</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label class="text-sm text-slate-600">Date</label>
          <input v-model="formulaire.date" type="date" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Nombre de courses</label>
          <input v-model.number="formulaire.nombre_courses" type="number" min="0" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Revenu brut ($)</label>
          <input v-model.number="formulaire.revenu_brut" type="number" min="0" step="0.01" class="input" />
        </div>
        <div>
          <label class="text-sm text-slate-600">Pourboires ($)</label>
          <input v-model.number="formulaire.pourboires" type="number" min="0" step="0.01" class="input" />
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
            <th>Courses</th>
            <th>Revenu brut</th>
            <th>Redevance gouv.</th>
            <th>TPS perçue</th>
            <th>TVQ perçue</th>
            <th>Pourboires</th>
            <th>Total net</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="chargement"><td colspan="9" class="text-center text-slate-500">Chargement...</td></tr>
          <tr v-else-if="!revenus.length"><td colspan="9" class="text-center text-slate-500">Aucun revenu saisi</td></tr>
          <tr v-for="revenu in revenus" :key="revenu.id">
            <td>{{ revenu.date }}</td>
            <td>{{ revenu.nombre_courses }}</td>
            <td>{{ formaterMontant(revenu.revenu_brut) }}</td>
            <td>{{ formaterMontant(revenu.redevance_gouv) }}</td>
            <td>{{ formaterMontant(revenu.tps_percue) }}</td>
            <td>{{ formaterMontant(revenu.tvq_percue) }}</td>
            <td>{{ formaterMontant(revenu.pourboires) }}</td>
            <td class="font-medium">{{ formaterMontant(revenu.total_net_encaisse) }}</td>
            <td><button class="btn-danger" @click="supprimer(revenu.id)">Suppr.</button></td>
          </tr>
          <tr v-if="totaux" class="bg-slate-50 font-semibold">
            <td>Total</td>
            <td>{{ totaux.nombre_courses }}</td>
            <td>{{ formaterMontant(totaux.revenu_brut) }}</td>
            <td>{{ formaterMontant(totaux.redevance_gouv) }}</td>
            <td>{{ formaterMontant(totaux.tps_percue) }}</td>
            <td>{{ formaterMontant(totaux.tvq_percue) }}</td>
            <td>{{ formaterMontant(totaux.pourboires) }}</td>
            <td>{{ formaterMontant(totaux.total_net_encaisse) }}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
