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
  <div class="min-h-screen relative overflow-hidden flex items-center justify-center p-4 sm:p-6">
    <div class="absolu-fond" aria-hidden="true">
      <div class="route">
        <div class="ligne-centrale" />
        <div class="voiture-animee">
          <svg viewBox="0 0 160 70" class="w-36 sm:w-44 drop-shadow-lg">
            <ellipse cx="80" cy="58" rx="54" ry="5" fill="#0f172a" opacity="0.18" />
            <path
              d="M28 42 h18 l10-16 h48 l12 16 h16 a6 6 0 0 1 6 6 v8 H22 v-8 a6 6 0 0 1 6-6z"
              fill="#4F46E5"
            />
            <path d="M58 26 h36 l8 14 H50 z" fill="#C7D2FE" />
            <rect x="24" y="38" width="14" height="5" rx="1.5" fill="#EEF2FF" opacity="0.9" />
            <rect x="122" y="38" width="12" height="5" rx="1.5" fill="#F59E0B" />
            <circle cx="48" cy="56" r="9" fill="#1E1B4B" />
            <circle cx="48" cy="56" r="4" fill="#94A3B8" />
            <circle cx="116" cy="56" r="9" fill="#1E1B4B" />
            <circle cx="116" cy="56" r="4" fill="#94A3B8" />
            <text x="78" y="44" text-anchor="middle" fill="white" font-size="9" font-weight="700">TAXI</text>
          </svg>
        </div>
      </div>
    </div>

    <form
      class="relative z-10 w-full max-w-md bg-white/95 backdrop-blur-sm rounded-2xl shadow-carte border border-trait p-6 sm:p-8 space-y-5"
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

<style scoped>
.absolu-fond {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(79, 70, 229, 0.12), transparent 40%),
    radial-gradient(circle at 80% 10%, rgba(16, 185, 129, 0.10), transparent 35%),
    linear-gradient(180deg, #F7F8FC 0%, #EEF1F8 55%, #E4E9F4 100%);
}

.route {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 12%;
  height: 72px;
  background: linear-gradient(180deg, #334155 0%, #1e293b 100%);
  overflow: hidden;
}

.ligne-centrale {
  position: absolute;
  top: 50%;
  left: 0;
  width: 200%;
  height: 4px;
  margin-top: -2px;
  background: repeating-linear-gradient(
    90deg,
    #f8fafc 0 28px,
    transparent 28px 52px
  );
  animation: route-defile 1.2s linear infinite;
}

.voiture-animee {
  position: absolute;
  bottom: 10px;
  animation: voiture-roule 7s ease-in-out infinite;
}

@keyframes route-defile {
  from { transform: translateX(0); }
  to { transform: translateX(-52px); }
}

@keyframes voiture-roule {
  0% { left: -20%; transform: translateY(0); }
  40% { transform: translateY(-2px); }
  50% { left: 78%; transform: translateY(0); }
  60% { transform: translateY(-2px); }
  100% { left: 110%; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .ligne-centrale,
  .voiture-animee {
    animation: none;
  }
  .voiture-animee {
    left: 40%;
  }
}
</style>
