<template>
  <div id="questions-graph">
    <VueApexCharts type="line" height="250px" :options="chartOptions" :series="series" />
  </div>
</template>

<script setup lang="ts">
import VueApexCharts from 'vue3-apexcharts'
import { useDashboardStore } from '@/stores/dashboard'
import type { IQuestionData } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const store = useDashboardStore()
const { generatePeriod } = store
const { dashboardData } = storeToRefs(store)
const { t } = useI18n()
const period = generatePeriod()

const total = computed(() => {
  if (!dashboardData.value) return []
  return dashboardData.value.total_questions_per_day
})
const like = computed(() => {
  if (!dashboardData.value) return []
  return dashboardData.value.like_questions_per_day
})
const dislike = computed(() => {
  if (!dashboardData.value) return []
  return dashboardData.value.dislike_questions_per_day
})

const series = computed(() => {
  return [
    {
      name: t('dashboard_questions_count'),
      data: period.map((p) => {
        const date = total.value.find((x: IQuestionData) => x.date === p.key)
        return date?.count || 0
      })
    },
    {
      name: t('dashboard_questions_liked'),
      data: period.map((p) => {
        const date = like.value.find((x: IQuestionData) => x.date === p.key)
        return date?.count || 0
      })
    },
    {
      name: t('dashboard_questions_disliked'),
      data: period.map((p) => {
        const date = dislike.value.find((x: IQuestionData) => x.date === p.key)
        return date?.count || 0
      })
    }
  ]
})

const chartOptions = {
  chart: {
    height: 350,
    type: 'line',
    dropShadow: {
      enabled: true,
      color: '#000',
      top: 18,
      left: 7,
      blur: 10,
      opacity: 0.2
    },
    toolbar: {
      show: false
    }
  },
  colors: ['#77B6EA', '#4cd42f', '#d42f55'],
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  title: {
    text: t('dashboard_questions_activity'),
    align: 'left'
  },
  grid: {
    borderColor: '#e7e7e7',
    row: {
      colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
      opacity: 0.5
    }
  },
  markers: {
    size: 1
  },
  xaxis: {
    categories: period.map((p) => p.label),
    title: {
      text: t('date')
    }
  },
  yaxis: {
    title: {
      text: t('questions_count')
    }
    /* min: 5,
    max: 40*/
  },
  legend: {
    position: 'top',
    horizontalAlign: 'right',
    floating: true,
    offsetY: -25,
    offsetX: -5
  }
}
</script>

<style scoped lang="scss"></style>
