import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useComptabiliteStore = defineStore('comptabilite', () => {
  const annee = ref(new Date().getFullYear())
  const mois = ref(new Date().getMonth() + 1)

  function definirPeriode(nouvelleAnnee, nouveauMois) {
    annee.value = nouvelleAnnee
    mois.value = nouveauMois
  }

  return { annee, mois, definirPeriode }
})
