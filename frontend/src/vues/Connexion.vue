<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { connecter, inscrire, obtenirStatutAuth } from '../services/api'

const router = useRouter()
const email = ref('')
const motDePasse = ref('')
const modeInscription = ref(false)
const inscriptionOuverte = ref(false)
const chargement = ref(false)
const erreur = ref('')

onMounted(async () => {
  try {
    const statut = await obtenirStatutAuth()
    inscriptionOuverte.value = statut.inscription_ouverte
    modeInscription.value = statut.inscription_ouverte
  } catch {
    inscriptionOuverte.value = false
  }
})

async function soumettre() {
  erreur.value = ''
  if (!email.value || motDePasse.value.length < 8) {
    erreur.value = 'Mot de passe d’au moins 8 caractères requis.'
    return
  }
  chargement.value = true
  try {
    if (modeInscription.value) {
      await inscrire(email.value, motDePasse.value)
    } else {
      await connecter(email.value, motDePasse.value)
    }
    router.replace('/')
  } catch (e) {
    erreur.value =
      e.response?.data?.detail ||
      (modeInscription.value ? 'Inscription impossible.' : 'Identifiants incorrects.')
  } finally {
    chargement.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-fond flex items-center justify-center p-4">
    <form
      class="w-full max-w-md bg-white rounded-2xl shadow-carte border border-trait p-8 space-y-5"
      @submit.prevent="soumettre"
    >
      <div class="flex items-center gap-3">
        <div class="w-11 h-11 rounded-xl bg-indigo-600 text-white flex items-center justify-center">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 17h8M6 9h12l-1 8H7L6 9zm3-4h6l1 4H8l1-4z" />
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-extrabold text-encre">ComptaTaxi</h1>
          <p class="text-sm text-muet">
            {{ modeInscription ? 'Créer le compte administrateur' : 'Connexion' }}
          </p>
        </div>
      </div>

      <p v-if="modeInscription" class="text-sm text-muet">
        Premier démarrage : créez votre compte. L’inscription sera ensuite fermée.
      </p>

      <div class="space-y-1.5">
        <label class="text-sm font-semibold text-encre" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          autocomplete="username"
          class="w-full border border-trait rounded-xl px-3 py-2.5 text-sm"
          placeholder="vous@exemple.com"
        />
      </div>

      <div class="space-y-1.5">
        <label class="text-sm font-semibold text-encre" for="mdp">Mot de passe</label>
        <input
          id="mdp"
          v-model="motDePasse"
          type="password"
          required
          minlength="8"
          autocomplete="current-password"
          class="w-full border border-trait rounded-xl px-3 py-2.5 text-sm"
          placeholder="Au moins 8 caractères"
        />
      </div>

      <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>

      <button
        type="submit"
        class="w-full bg-indigo-600 text-white font-bold rounded-xl py-2.5 hover:bg-indigo-700 disabled:opacity-60"
        :disabled="chargement"
      >
        {{ chargement ? 'Patientez…' : modeInscription ? 'Créer mon compte' : 'Se connecter' }}
      </button>

      <button
        v-if="inscriptionOuverte && !modeInscription"
        type="button"
        class="w-full text-sm text-indigo-700 font-semibold"
        @click="modeInscription = true"
      >
        Créer le premier compte
      </button>
      <button
        v-if="modeInscription && !inscriptionOuverte"
        type="button"
        class="w-full text-sm text-muet font-semibold"
        @click="modeInscription = false"
      >
        Déjà un compte ? Se connecter
      </button>
    </form>
  </div>
</template>
