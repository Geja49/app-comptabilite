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
      <div class="grille" />
      <div class="route">
        <div class="ligne-centrale" />
        <div class="voiture-animee">
          <svg viewBox="0 0 220 90" class="w-48 sm:w-56 drop-shadow-xl" aria-hidden="true">
            <defs>
              <linearGradient id="carrosserie" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#2563EB" />
                <stop offset="55%" stop-color="#1D4ED8" />
                <stop offset="100%" stop-color="#1E3A8A" />
              </linearGradient>
              <linearGradient id="vitre" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#E0F2FE" />
                <stop offset="100%" stop-color="#93C5FD" />
              </linearGradient>
              <linearGradient id="jante" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#CBD5E1" />
                <stop offset="100%" stop-color="#64748B" />
              </linearGradient>
              <filter id="ombre-voiture" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#0f172a" flood-opacity="0.28" />
              </filter>
            </defs>

            <!-- Ombre au sol -->
            <ellipse cx="112" cy="78" rx="78" ry="6" fill="#0f172a" opacity="0.22" />

            <!-- Carrosserie moderne -->
            <g filter="url(#ombre-voiture)">
              <path
                d="M36 58
                   C38 48, 46 42, 58 40
                   L78 28 C84 24, 96 22, 112 22
                   L148 22 C162 22, 172 28, 178 36
                   L196 48 C204 52, 208 56, 208 60
                   L208 66 C208 70, 204 72, 198 72
                   L40 72 C34 72, 30 70, 30 66
                   L30 62 C30 60, 32 58, 36 58 Z"
                fill="url(#carrosserie)"
              />
              <!-- Ligne de caractère -->
              <path d="M48 58 H196" stroke="#60A5FA" stroke-width="1.2" opacity="0.35" />
              <!-- Bas de caisse -->
              <path d="M34 66 H200" stroke="#0F172A" stroke-width="2" opacity="0.25" stroke-linecap="round" />
            </g>

            <!-- Toit / vitre panoramique -->
            <path
              d="M82 28 L110 24 L146 24 L168 36 L150 48 L86 48 Z"
              fill="url(#vitre)"
              opacity="0.95"
            />
            <path d="M118 24 V48" stroke="#1E40AF" stroke-width="1" opacity="0.2" />

            <!-- Phares LED -->
            <rect x="198" y="50" width="10" height="6" rx="2" fill="#FDE68A" />
            <rect x="199" y="51" width="7" height="2" rx="1" fill="#FFFBEB" opacity="0.9" />
            <!-- Feux arrière -->
            <rect x="30" y="50" width="9" height="6" rx="2" fill="#F87171" />

            <!-- Pare-chocs -->
            <rect x="200" y="62" width="10" height="5" rx="1.5" fill="#E2E8F0" opacity="0.85" />
            <rect x="28" y="62" width="10" height="5" rx="1.5" fill="#E2E8F0" opacity="0.75" />

            <!-- Gyrophare taxi -->
            <rect x="108" y="14" width="18" height="8" rx="2" fill="#FBBF24" />
            <rect x="110" y="16" width="14" height="4" rx="1" fill="#FEF3C7" />
            <text x="117" y="20" text-anchor="middle" fill="#92400E" font-size="5" font-weight="800">TAXI</text>

            <!-- Portière / poignée -->
            <rect x="128" y="52" width="10" height="2.5" rx="1" fill="#BFDBFE" opacity="0.7" />

            <!-- Roues (jantes modernes) -->
            <g class="roue">
              <circle cx="64" cy="70" r="12" fill="#0F172A" />
              <circle cx="64" cy="70" r="7.5" fill="url(#jante)" />
              <circle cx="64" cy="70" r="3" fill="#1E293B" />
              <path d="M64 64.5 V75.5 M58.5 70 H69.5" stroke="#F8FAFC" stroke-width="1.2" opacity="0.55" />
            </g>
            <g class="roue">
              <circle cx="168" cy="70" r="12" fill="#0F172A" />
              <circle cx="168" cy="70" r="7.5" fill="url(#jante)" />
              <circle cx="168" cy="70" r="3" fill="#1E293B" />
              <path d="M168 64.5 V75.5 M162.5 70 H173.5" stroke="#F8FAFC" stroke-width="1.2" opacity="0.55" />
            </g>
          </svg>
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
  bottom: 6px;
  animation: voiture-roule 8s ease-in-out infinite;
}

.roue {
  transform-origin: center;
  animation: roue-tourne 0.55s linear infinite;
  transform-box: fill-box;
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
  45% { transform: translateY(-3px); }
  50% { left: 68%; transform: translateY(0); }
  55% { transform: translateY(-2px); }
  100% { left: 112%; transform: translateY(0); }
}

@keyframes roue-tourne {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  .roue,
  .animate-entree {
    animation: none;
  }
  .voiture-animee {
    left: 38%;
  }
}
</style>
