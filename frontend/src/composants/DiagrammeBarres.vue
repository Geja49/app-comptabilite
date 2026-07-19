<script setup>
import { computed } from 'vue'
import { formaterMontant } from '../services/api'

const props = defineProps({
  titre: { type: String, required: true },
  sousTitre: { type: String, default: '' },
  etiquettes: { type: Array, default: () => [] },
  series: {
    type: Array,
    default: () => [],
    // [{ nom, couleur, valeurs: number[] }]
  },
})

const largeur = 640
const hauteur = 220
const margeGauche = 44
const margeDroite = 12
const margeHaut = 16
const margeBas = 36

const maxValeur = computed(() => {
  const valeurs = props.series.flatMap((s) => s.valeurs.map((v) => Math.abs(Number(v) || 0)))
  const max = Math.max(...valeurs, 0)
  return max === 0 ? 1 : max * 1.1
})

const largeurUtile = largeur - margeGauche - margeDroite
const hauteurUtile = hauteur - margeHaut - margeBas
const groupes = computed(() => props.etiquettes.length || 1)
const largeurGroupe = computed(() => largeurUtile / groupes.value)
const largeurBarre = computed(() => {
  const n = Math.max(props.series.length, 1)
  return Math.max(6, (largeurGroupe.value * 0.7) / n)
})

function xBarre(indexGroupe, indexSerie) {
  const n = Math.max(props.series.length, 1)
  const debut = margeGauche + indexGroupe * largeurGroupe.value + largeurGroupe.value * 0.15
  return debut + indexSerie * largeurBarre.value
}

function hauteurBarre(valeur) {
  return (Math.abs(Number(valeur) || 0) / maxValeur.value) * hauteurUtile
}

function yBarre(valeur) {
  const h = hauteurBarre(valeur)
  const base = margeHaut + hauteurUtile
  return Number(valeur) < 0 ? base : base - h
}

const graduations = computed(() => {
  const max = maxValeur.value
  return [0, 0.5, 1].map((p) => ({
    y: margeHaut + hauteurUtile * (1 - p),
    label: Math.round(max * p),
  }))
})
</script>

<template>
  <div class="card">
    <div class="mb-3">
      <h3 class="font-bold text-encre">{{ titre }}</h3>
      <p v-if="sousTitre" class="text-sm text-muet">{{ sousTitre }}</p>
    </div>
    <div class="overflow-x-auto">
      <svg :viewBox="`0 0 ${largeur} ${hauteur}`" class="w-full min-w-[320px] h-auto">
        <line
          v-for="g in graduations"
          :key="g.y"
          :x1="margeGauche"
          :x2="largeur - margeDroite"
          :y1="g.y"
          :y2="g.y"
          stroke="#E5E7EB"
          stroke-width="1"
        />
        <text
          v-for="g in graduations"
          :key="'l' + g.y"
          :x="margeGauche - 6"
          :y="g.y + 4"
          text-anchor="end"
          class="fill-slate-400"
          font-size="10"
        >
          {{ g.label }}
        </text>

        <template v-for="(serie, si) in series" :key="serie.nom">
          <rect
            v-for="(valeur, gi) in serie.valeurs"
            :key="serie.nom + '-' + gi"
            :x="xBarre(gi, si)"
            :y="yBarre(valeur)"
            :width="largeurBarre"
            :height="hauteurBarre(valeur)"
            :fill="serie.couleur"
            rx="3"
          >
            <title>{{ etiquettes[gi] }} · {{ serie.nom }} : {{ formaterMontant(valeur) }}</title>
          </rect>
        </template>

        <text
          v-for="(etiq, i) in etiquettes"
          :key="'e' + i"
          :x="margeGauche + i * largeurGroupe + largeurGroupe / 2"
          :y="hauteur - 12"
          text-anchor="middle"
          class="fill-slate-500"
          font-size="10"
        >
          {{ etiq }}
        </text>
      </svg>
    </div>
    <div class="flex flex-wrap gap-4 mt-2">
      <div v-for="serie in series" :key="'leg' + serie.nom" class="flex items-center gap-2 text-xs text-muet">
        <span class="inline-block w-3 h-3 rounded-sm" :style="{ background: serie.couleur }" />
        {{ serie.nom }}
      </div>
    </div>
  </div>
</template>
