<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const categories = ref([])
const nouvelleCategorie = ref('')
const message = ref('')

async function charger() {
  const { data } = await api.get('/api/categories')
  categories.value = data
}

async function ajouter() {
  if (!nouvelleCategorie.value.trim()) return
  try {
    await api.post('/api/categories', { nom: nouvelleCategorie.value.trim() })
    nouvelleCategorie.value = ''
    message.value = 'Catégorie ajoutée'
    await charger()
  } catch (e) {
    message.value = e.response?.data?.detail || 'Erreur'
  }
}

onMounted(charger)
</script>

<template>
  <div class="space-y-6 max-w-xl">
    <div class="card space-y-4">
      <ul class="space-y-2">
        <li v-for="cat in categories" :key="cat.id" class="flex justify-between items-center py-2 border-b border-slate-100">
          <span>{{ cat.nom }}</span>
          <span v-if="cat.est_systeme" class="text-xs text-slate-400">Système</span>
        </li>
      </ul>
    </div>

    <div class="card space-y-3">
      <h4 class="font-medium">Ajouter une catégorie</h4>
      <input v-model="nouvelleCategorie" type="text" class="input" placeholder="Nom de la catégorie" />
      <button class="btn-primary" @click="ajouter">Ajouter</button>
      <p v-if="message" class="text-sm text-slate-600">{{ message }}</p>
    </div>
  </div>
</template>
