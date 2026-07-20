import axios from 'axios'

const JETON_STOCKAGE = 'comptataxi_jeton'
const EMAIL_STOCKAGE = 'comptataxi_email'

export function lireJeton() {
  return localStorage.getItem(JETON_STOCKAGE) || ''
}

export function lireEmailSession() {
  return localStorage.getItem(EMAIL_STOCKAGE) || ''
}

export function enregistrerSession(jeton, email) {
  localStorage.setItem(JETON_STOCKAGE, jeton)
  localStorage.setItem(EMAIL_STOCKAGE, email || '')
}

export function effacerSession() {
  localStorage.removeItem(JETON_STOCKAGE)
  localStorage.removeItem(EMAIL_STOCKAGE)
}

export function estConnecte() {
  return Boolean(lireJeton())
}

const api = axios.create({
  // Vide = même origine (déploiement Render)
  baseURL: import.meta.env.VITE_API_URL || '',
})

api.interceptors.request.use((config) => {
  const jeton = lireJeton()
  if (jeton) {
    config.headers.Authorization = `Bearer ${jeton}`
  }
  return config
})

const abonnesErreur = []
const abonnesNonAutorise = []

export function surErreurApi(rappel) {
  abonnesErreur.push(rappel)
}

export function surNonAutorise(rappel) {
  abonnesNonAutorise.push(rappel)
}

api.interceptors.response.use(
  (reponse) => reponse,
  (erreur) => {
    if (erreur.response?.status === 401) {
      effacerSession()
      abonnesNonAutorise.forEach((rappel) => rappel())
    }
    if (erreur.response?.status !== 409 && erreur.response?.status !== 401) {
      const message =
        erreur.response?.data?.detail ||
        (erreur.request ? 'Le serveur est injoignable' : 'Une erreur est survenue')
      abonnesErreur.forEach((rappel) => rappel(String(message)))
    }
    return Promise.reject(erreur)
  },
)

export async function telechargerExport(chemin, nomFichier) {
  const { data } = await api.get(chemin, { responseType: 'blob' })
  const url = URL.createObjectURL(data)
  const lien = document.createElement('a')
  lien.href = url
  lien.download = nomFichier
  document.body.appendChild(lien)
  lien.click()
  lien.remove()
  URL.revokeObjectURL(url)
}

export async function connecter(email, motDePasse) {
  const { data } = await api.post('/api/auth/connexion', {
    email,
    mot_de_passe: motDePasse,
  })
  enregistrerSession(data.jeton, data.email)
  return data
}

export async function inscrire(email, motDePasse) {
  const { data } = await api.post('/api/auth/inscription', {
    email,
    mot_de_passe: motDePasse,
  })
  enregistrerSession(data.jeton, data.email)
  return data
}

export async function obtenirStatutAuth() {
  const { data } = await api.get('/api/auth/statut')
  return data
}

export default api

export const NOMS_MOIS = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
]

export const LIBELLES_METHODE = {
  reguliere: 'Méthode régulière',
  rapide: 'Méthode rapide',
}

export function formaterMontant(valeur) {
  return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(Number(valeur || 0))
}

export function formaterPourcentage(valeur) {
  return new Intl.NumberFormat('fr-CA', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 3,
  }).format(Number(valeur || 0))
}

export function obtenirParametresFiscaux(annee) {
  return api.get(`/api/parametres-fiscaux/${annee}`)
}

export function definirMethodeFiscale(annee, methode, frequenceDeclaration = null) {
  const corps = { methode_tps_tvq: methode }
  if (frequenceDeclaration) {
    corps.frequence_declaration = frequenceDeclaration
  }
  return api.put(`/api/parametres-fiscaux/${annee}`, corps)
}

export function estPeriodePassee(annee, mois) {
  const maintenant = new Date()
  const anneeActuelle = maintenant.getFullYear()
  const moisActuel = maintenant.getMonth() + 1
  return annee < anneeActuelle || (annee === anneeActuelle && mois < moisActuel)
}

export async function avecConfirmationPassee(annee, mois, action) {
  try {
    return await action(false)
  } catch (erreur) {
    if (erreur.response?.status === 409) {
      const confirmer = window.confirm(
        'Vous modifiez des données d\'un mois passé. Voulez-vous continuer ?'
      )
      if (confirmer) {
        return await action(true)
      }
    }
    throw erreur
  }
}
