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
  <section id="hero-connexion" class="hero-connexion">
    <div class="cs-container">
      <div class="cs-flex-group">
        <span class="cs-topper">ComptaTaxi · Québec</span>
        <h1 class="cs-title">Votre comptabilité taxi, claire et à jour</h1>
        <p class="cs-text">
          Connectez-vous à votre espace privé : revenus, dépenses, taxes et trésorerie restent
          séparés pour chaque chauffeur.
        </p>

        <form class="cs-formulaire" @submit.prevent="soumettre">
          <p class="cs-form-titre">
            {{ modeInscription ? 'Créer un compte' : 'Espace sécurisé' }}
          </p>

          <div class="cs-champ">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              autocomplete="username"
              placeholder="vous@exemple.com"
            />
          </div>

          <div class="cs-champ">
            <label for="mdp">Mot de passe</label>
            <input
              id="mdp"
              v-model="motDePasse"
              type="password"
              required
              minlength="8"
              autocomplete="current-password"
              placeholder="Au moins 8 caractères"
            />
          </div>

          <p v-if="erreur" class="cs-erreur">{{ erreur }}</p>

          <div class="cs-button-group">
            <button type="submit" class="cs-button-solid cs-button" :disabled="chargement">
              {{ chargement ? 'Patientez…' : modeInscription ? 'Créer mon compte' : 'Se connecter' }}
            </button>
            <button
              v-if="inscriptionOuverte && !modeInscription"
              type="button"
              class="cs-button-transparent cs-button"
              @click="modeInscription = true"
            >
              Créer un compte
            </button>
            <button
              v-else-if="modeInscription"
              type="button"
              class="cs-button-transparent cs-button"
              @click="modeInscription = false"
            >
              Déjà un compte ?
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="cs-picture" aria-hidden="true">
      <div class="cs-fond" />
      <div class="route">
        <div class="ligne-centrale" />
        <div class="voiture-animee">
          <img
            :src="taxiGif"
            alt=""
            class="taxi-img"
            draggable="false"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-connexion {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  overflow: hidden;
  padding: 0 1rem;
  display: flex;
  align-items: center;
}

.hero-connexion .cs-picture {
  position: absolute;
  inset: 0;
  z-index: -2;
  display: block;
}

.hero-connexion .cs-picture::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: #000;
  opacity: 0.55;
  pointer-events: none;
}

.hero-connexion .cs-fond {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 80% at 18% 28%, rgba(29, 78, 216, 0.5), transparent 55%),
    radial-gradient(ellipse 50% 60% at 88% 72%, rgba(15, 23, 42, 0.4), transparent 50%),
    linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 42%, #0f172a 100%);
}

.hero-connexion .cs-container {
  position: relative;
  width: 100%;
  max-width: 80rem;
  margin: 0 auto;
  padding: clamp(4rem, 12vw, 7rem) 0 clamp(7rem, 16vw, 10rem);
}

.hero-connexion .cs-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, rgba(250, 251, 252, 0.5), rgba(250, 251, 252, 0));
}

.hero-connexion .cs-flex-group {
  width: min(88vw, 28rem);
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  box-sizing: border-box;
}

.hero-connexion .cs-topper {
  display: block;
  width: 100%;
  margin-bottom: 1rem;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.1rem;
  font-size: clamp(0.8125rem, 1.6vw, 1rem);
  font-weight: 700;
  line-height: 1.2;
  color: #93c5fd;
}

.hero-connexion .cs-title {
  width: 100%;
  margin: 0 auto 1.25rem;
  text-align: center;
  font-size: clamp(2rem, 5.5vw, 3.25rem);
  font-weight: 900;
  line-height: 1.15;
  color: #fff;
}

.hero-connexion .cs-text {
  width: 100%;
  margin: 0 auto 2rem;
  text-align: center;
  font-size: clamp(1rem, 1.8vw, 1.15rem);
  line-height: 1.5;
  color: rgba(248, 250, 252, 0.9);
}

.hero-connexion .cs-formulaire {
  width: 100%;
  padding: 1.5rem;
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(10px);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.25);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: entree-carte 0.55s ease-out both;
}

.hero-connexion .cs-form-titre {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
}

.hero-connexion .cs-champ {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.hero-connexion .cs-champ label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #0f172a;
}

.hero-connexion .cs-champ input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.7rem 0.85rem;
  font-size: 0.95rem;
  color: #0f172a;
  background: #fff;
}

.hero-connexion .cs-champ input:focus {
  outline: none;
  border-color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.2);
}

.hero-connexion .cs-erreur {
  margin: 0;
  font-size: 0.875rem;
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 0.6rem 0.75rem;
}

.hero-connexion .cs-button-group {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.75rem;
  margin-top: 0.25rem;
}

.hero-connexion .cs-button {
  min-width: 0;
  width: 100%;
  font-size: 1rem;
  font-weight: 700;
  text-decoration: none;
  box-sizing: border-box;
  cursor: pointer;
  transition: color 0.3s;
}

.hero-connexion .cs-button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.hero-connexion .cs-button-solid {
  position: relative;
  z-index: 1;
  overflow: hidden;
  border: none;
  padding: 0 1.5rem;
  line-height: 3rem;
  text-align: center;
  color: #fff;
  background-color: #1d4ed8;
}

.hero-connexion .cs-button-solid::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  z-index: -1;
  width: 0;
  height: 100%;
  background: #0f172a;
  transition: width 0.3s;
}

.hero-connexion .cs-button-solid:hover:not(:disabled)::before {
  width: 100%;
}

.hero-connexion .cs-button-transparent {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 3rem;
  padding: 0 1.25rem;
  color: #1d4ed8;
  background: transparent;
  border: 1px solid #cbd5e1;
}

.hero-connexion .cs-button-transparent::before {
  content: '';
  position: absolute;
  inset: -1px;
  z-index: -1;
  background: #e2e8f0;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s;
}

.hero-connexion .cs-button-transparent:hover::before {
  transform: scaleX(1);
}

.route {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  height: 72px;
  background: linear-gradient(180deg, #334155 0%, #0f172a 100%);
  overflow: hidden;
}

.ligne-centrale {
  position: absolute;
  top: 50%;
  left: 0;
  width: 200%;
  height: 4px;
  margin-top: -2px;
  background: repeating-linear-gradient(90deg, #f8fafc 0 28px, transparent 28px 52px);
  animation: route-defile 1.1s linear infinite;
}

.voiture-animee {
  position: absolute;
  bottom: 2px;
  animation: voiture-roule 8s ease-in-out infinite;
}

.taxi-img {
  height: 3.25rem;
  width: auto;
  display: block;
  pointer-events: none;
  user-select: none;
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.35));
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

@media (min-width: 48rem) {
  .hero-connexion {
    padding: 0 clamp(2rem, 5vw, 2.5rem);
  }

  .hero-connexion .cs-container::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 1px;
    height: 100%;
    background: linear-gradient(to bottom, rgba(250, 251, 252, 0), rgba(250, 251, 252, 0.5));
  }

  .taxi-img {
    height: 4.5rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ligne-centrale,
  .voiture-animee,
  .cs-formulaire {
    animation: none;
  }
  .voiture-animee {
    left: 38%;
  }
}
</style>
