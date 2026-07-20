<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { connecter, inscrire, obtenirStatutAuth } from '../services/api'
import taxiGif from '../static/photos/taxi.gif'

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
    inscriptionOuverte.value = statut.inscription_ouverte !== false
  } catch {
    inscriptionOuverte.value = true
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
      <div class="grille" />
      <div class="route">
        <div class="ligne-centrale" />
        <div class="voiture-animee">
          <img
            :src="taxiGif"
            alt=""
            class="h-14 sm:h-20 w-auto drop-shadow-xl select-none pointer-events-none"
            draggable="false"
          />
        </div>
      </div>
    </div>

    <form
      class="relative z-10 w-full max-w-md bg-white/90 backdrop-blur-md rounded-2xl shadow-carte border border-white/60 p-6 sm:p-8 space-y-5 animate-entree"
      @submit.prevent="soumettre"
    >
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-600 to-indigo-700 text-white flex items-center justify-center shadow-douce">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 17h8M6 9h12l-1 8H7L6 9zm3-4h6l1 4H8l1-4z" />
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-extrabold text-encre tracking-tight">ComptaTaxi</h1>
          <p class="text-sm text-muet">
            {{ modeInscription ? 'Créer le compte administrateur' : 'Espace sécurisé' }}
          </p>
        </div>
      </div>

      <p v-if="modeInscription" class="text-sm text-muet leading-relaxed">
        Créez votre compte : vos revenus, dépenses et rapports restent privés, séparés des autres chauffeurs.
      </p>

      <div class="space-y-1.5">
        <label class="text-sm font-semibold text-encre" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          autocomplete="username"
          class="input"
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
          class="input"
          placeholder="Au moins 8 caractères"
        />
      </div>

      <p v-if="erreur" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
        {{ erreur }}
      </p>

      <button
        type="submit"
        class="btn-primary w-full py-3"
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
        Créer un compte
      </button>
      <button
        v-if="modeInscription"
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
    radial-gradient(circle at 18% 18%, rgba(29, 78, 216, 0.14), transparent 42%),
    radial-gradient(circle at 85% 8%, rgba(15, 23, 42, 0.06), transparent 36%),
    linear-gradient(165deg, #F8FAFC 0%, #EEF2F7 48%, #E2E8F0 100%);
}

.grille {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(148, 163, 184, 0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.12) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(180deg, black 0%, transparent 70%);
}

.route {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 11%;
  height: 76px;
  background: linear-gradient(180deg, #334155 0%, #0f172a 100%);
  overflow: hidden;
  box-shadow: 0 -12px 40px rgba(15, 23, 42, 0.12);
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
  animation: route-defile 1.1s linear infinite;
}

.voiture-animee {
  position: absolute;
  bottom: 4px;
  animation: voiture-roule 8s ease-in-out infinite;
}

.animate-entree {
  animation: entree-carte 0.55s ease-out both;
}

@keyframes route-defile {
  from { transform: translateX(0); }
  to { transform: translateX(-52px); }
}

@keyframes voiture-roule {
  0% { left: -28%; transform: translateY(0); }
  45% { transform: translateY(-2px); }
  50% { left: 68%; transform: translateY(0); }
  55% { transform: translateY(-1px); }
  100% { left: 112%; transform: translateY(0); }
}

@keyframes entree-carte {
  from {
    opacity: 0;
    transform: translateY(14px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .ligne-centrale,
  .voiture-animee,
  .animate-entree {
    animation: none;
  }
  .voiture-animee {
    left: 38%;
  }
}
</style>
