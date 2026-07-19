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
const hauteur = 240
const margeGauche = 44
const margeDroite = 12
const margeHaut = 20
const margeBas = 36

const maxValeur = computed(() => {
  const valeurs = props.series.flatMap((s) => s.valeurs.map((v) => Math.abs(Number(v) || 0)))
  const max = Math.max(...valeurs, 0)
  return max === 0 ? 1 : max * 1.15
})

const largeurUtile = largeur - margeGauche - margeDroite
const hauteurUtile = hauteur - margeHaut - margeBas
const groupes = computed(() => Math.max(props.etiquettes.length, 1))

function xPoint(index) {
  if (groupes.value === 1) return margeGauche + largeurUtile / 2
  return margeGauche + (index / (groupes.value - 1)) * largeurUtile
}

function yPoint(valeur) {
  const v = Number(valeur) || 0
  return margeHaut + hauteurUtile - (Math.abs(v) / maxValeur.value) * hauteurUtile
}

function cheminSerie(valeurs) {
  if (!valeurs.length) return ''
  return valeurs
    .map((valeur, i) => `${i === 0 ? 'M' : 'L'} ${xPoint(i)} ${yPoint(valeur)}`)
    .join(' ')
}

function aireSerie(valeurs) {
  if (!valeurs.length) return ''
  const ligne = cheminSerie(valeurs)
  const bas = margeHaut + hauteurUtile
  return `${ligne} L ${xPoint(valeurs.length - 1)} ${bas} L ${xPoint(0)} ${bas} Z`
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
  <div class="card overflow-hidden">
    <div class="mb-3">
      <h3 class="font-bold text-encre">{{ titre }}</h3>
      <p v-if="sousTitre" class="text-sm text-muet">{{ sousTitre }}</p>
    </div>
    <div class="overflow-x-auto -mx-2 px-2">
      <svg :viewBox="`0 0 ${largeur} ${hauteur}`" class="w-full min-w-[300px] h-auto">
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

        <template v-for="serie in series" :key="'aire-' + serie.nom">
          <path
            :d="aireSerie(serie.valeurs)"
            :fill="serie.couleur"
            opacity="0.12"
          />
          <path
            :d="cheminSerie(serie.valeurs)"
            fill="none"
            :stroke="serie.couleur"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <circle
            v-for="(valeur, i) in serie.valeurs"
            :key="serie.nom + i"
            :cx="xPoint(i)"
            :cy="yPoint(valeur)"
            r="3.5"
            :fill="serie.couleur"
          >
            <title>{{ etiquettes[i] }} · {{ serie.nom }} : {{ formaterMontant(valeur) }}</title>
          </circle>
        </template>

        <text
          v-for="(etiq, i) in etiquettes"
          :key="'e' + i"
          :x="xPoint(i)"
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
        <span class="inline-block w-3 h-3 rounded-full" :style="{ background: serie.couleur }" />
        {{ serie.nom }}
      </div>
    </div>
  </div>
</template>
