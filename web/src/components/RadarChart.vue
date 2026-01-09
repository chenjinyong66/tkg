<template>
  <div ref="chartRef" class="radar-chart"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = {
  data: {
    type: Array,
    default: () => []
  },
  height: {
    type: Number,
    default: 300
  }
}

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    
    const indicator = props.data.map(item => ({
      name: item.name,
      max: 10
    }))
    
    const option = {
      tooltip: {},
      radar: {
        indicator: indicator,
        radius: '60%',
        center: ['50%', '50%']
      },
      series: [{
        name: '能力评估',
        type: 'radar',
        data: [
          {
            value: props.data.map(item => item.value),
            name: '能力评估',
            areaStyle: {
              opacity: 0.4,
              color: '#1890ff'
            },
            lineStyle: {
              width: 2,
              color: '#1890ff'
            },
            itemStyle: {
              color: '#1890ff'
            }
          }
        ]
      }]
    }
    
    chartInstance.setOption(option)
  }
}

const updateChart = () => {
  if (chartInstance) {
    const indicator = props.data.map(item => ({
      name: item.name,
      max: 10
    }))
    
    const option = {
      radar: {
        indicator: indicator
      },
      series: [{
        data: [
          {
            value: props.data.map(item => item.value)
          }
        ]
      }]
    }
    
    chartInstance.setOption(option, true)
  }
}

onMounted(() => {
  initChart()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  window.removeEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})

// 监听数据变化
watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>

<style scoped>
.radar-chart {
  width: 100%;
  height: v-bind('props.height + "px"');
}
</style>