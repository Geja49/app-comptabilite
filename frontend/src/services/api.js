import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

export default api

export const NOMS_MOIS = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
]

export function formaterMontant(valeur) {
  return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(Number(valeur || 0))
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
