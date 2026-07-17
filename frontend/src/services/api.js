import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

const abonnesErreur = []

export function surErreurApi(rappel) {
  abonnesErreur.push(rappel)
}

api.interceptors.response.use(
  (reponse) => reponse,
  (erreur) => {
    // Le conflit 409 (modification d'un mois passé) est géré localement
    if (erreur.response?.status !== 409) {
      const message =
        erreur.response?.data?.detail ||
        (erreur.request ? 'Le serveur est injoignable' : 'Une erreur est survenue')
      abonnesErreur.forEach((rappel) => rappel(String(message)))
    }
    return Promise.reject(erreur)
  },
)

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

export function definirMethodeFiscale(annee, methode) {
  return api.put(`/api/parametres-fiscaux/${annee}`, { methode_tps_tvq: methode })
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
