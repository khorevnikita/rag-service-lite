<template>
  <div id="conversation-graph">
    <VueApexCharts type="line" height="250px" :options="chartOptions" :series="series" />
  </div>
</template>

<script setup lang="ts">
import VueApexCharts from 'vue3-apexcharts'
import { computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import type { IConversationData } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'

const store = useDashboardStore()
const { generatePeriod } = store
const { dashboardData } = storeToRefs(store)
const { t } = useI18n()
const period = generatePeriod()

const data = computed(() => {
  if (!dashboardData.value) return []
  return dashboardData.value.conversations_on_day
})

const series = computed(() => {
  const s: number[] = []
  for (let idx in period) {
    const p = period[idx]
    const date = data.value.find((x: IConversationData) => x.date === p.key)
    if (date) {
      s.push(date.count)
    } else {
      s.push(s[Number(idx) - 1] || 0)
    }
  }

  return [
    {
      name: t('dashboard_dialogs'),
      data: s
    }
  ]
})

const chartOptions = computed(() => {
  return {
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
    colors: ['#77B6EA'],
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth'
    },
    title: {
      text: t('dashboard_dialogs_growth'),
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
        text: t('dialogs_count')
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
})
</script>

<style scoped lang="scss"></style>
