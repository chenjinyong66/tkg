<template>
  <div class="line-chart-container" :style="{ height: height + 'px' }" ref="chartContainer">
    <div v-if="loading" class="chart-loading">
      <a-spin size="large" />
    </div>
    <div v-else-if="error" class="chart-error">
      <Empty :description="errorMessage" />
    </div>
    <div v-else-if="data.length === 0" class="chart-empty">
      <Empty description="暂无数据" />
    </div>
    <div v-else ref="chartRef" class="chart-canvas"></div>

    <!-- 图例 -->
    <div v-if="showLegend && series.length > 0" class="chart-legend">
      <div
          v-for="(seriesItem, index) in series"
          :key="index"
          class="legend-item"
          @click="toggleSeries(index)"
          :style="{ color: seriesItem.active ? seriesItem.color : '#ccc' }"
      >
        <span class="legend-marker" :style="{ backgroundColor: seriesItem.color }"></span>
        <span class="legend-label">{{ seriesItem.name }}</span>
      </div>
    </div>

    <!-- 工具提示 -->
    <div
        v-if="tooltip.visible"
        class="chart-tooltip"
        :style="{
        left: tooltip.x + 'px',
        top: tooltip.y + 'px'
      }"
    >
      <div class="tooltip-title">{{ tooltip.title }}</div>
      <div
          v-for="(item, index) in tooltip.items"
          :key="index"
          class="tooltip-item"
      >
        <span class="tooltip-marker" :style="{ backgroundColor: item.color }"></span>
        <span class="tooltip-label">{{ item.label }}:</span>
        <span class="tooltip-value">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Empty } from 'ant-design-vue'
import * as echarts from 'echarts'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/grid'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/dataZoom'

const props = defineProps({
  // 图表数据
  data: {
    type: Array,
    default: () => []
  },
  // X轴字段名
  xField: {
    type: String,
    default: 'time'
  },
  // Y轴字段名
  yField: {
    type: String,
    default: 'value'
  },
  // 系列字段名（用于多条折线）
  seriesField: {
    type: String,
    default: 'category'
  },
  // 图表高度
  height: {
    type: [Number, String],
    default: 400
  },
  // 是否显示加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 错误信息
  error: {
    type: Boolean,
    default: false
  },
  errorMessage: {
    type: String,
    default: '数据加载失败'
  },
  // 是否平滑曲线
  smooth: {
    type: Boolean,
    default: false
  },
  // 是否显示面积
  showArea: {
    type: Boolean,
    default: false
  },
  // 是否显示数据点
  showSymbol: {
    type: Boolean,
    default: true
  },
  // 是否显示图例
  showLegend: {
    type: Boolean,
    default: true
  },
  // 是否显示工具栏
  showToolbox: {
    type: Boolean,
    default: false
  },
  // 是否显示数据缩放
  showDataZoom: {
    type: Boolean,
    default: false
  },
  // 图表标题
  title: {
    type: String,
    default: ''
  },
  // X轴标题
  xAxisName: {
    type: String,
    default: ''
  },
  // Y轴标题
  yAxisName: {
    type: String,
    default: ''
  },
  // 自定义颜色系列
  colors: {
    type: Array,
    default: () => ['#1890ff', '#52c41a', '#fa8c16', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#faad14']
  },
  // 网格配置
  grid: {
    type: Object,
    default: () => ({
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    })
  },
  // 自定义配置
  customOptions: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['point-click', 'legend-select'])

// 图表实例
const chartRef = ref(null)
const chartContainer = ref(null)
let chartInstance = null

// 响应式数据
const series = ref([])
const tooltip = reactive({
  visible: false,
  x: 0,
  y: 0,
  title: '',
  items: []
})

// 防抖函数实现
const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// 处理数据
const processData = () => {
  if (!props.data || props.data.length === 0) return

  const seriesMap = new Map()

  // 按系列分组数据
  props.data.forEach(item => {
    const seriesName = item[props.seriesField] || 'default'
    if (!seriesMap.has(seriesName)) {
      seriesMap.set(seriesName, [])
    }
    seriesMap.get(seriesName).push({
      name: item[props.xField],
      value: item[props.yField],
      rawData: item
    })
  })

  // 构建系列数据
  const seriesArray = Array.from(seriesMap.entries()).map(([name, data], index) => ({
    name,
    data,
    color: props.colors[index % props.colors.length],
    active: true
  }))

  series.value = seriesArray
}

// 获取X轴数据
const getXAxisData = () => {
  if (!props.data || props.data.length === 0) return []

  const xValues = new Set()
  props.data.forEach(item => {
    xValues.add(item[props.xField])
  })

  return Array.from(xValues).sort()
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  // 销毁现有实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新实例
  chartInstance = echarts.init(chartRef.value)

  // 设置配置
  const options = getChartOptions()
  chartInstance.setOption(options, true)

  // 绑定事件
  bindChartEvents()

  // 响应窗口变化
  window.addEventListener('resize', handleResize)
}

// 获取图表配置
const getChartOptions = () => {
  const xAxisData = getXAxisData()

  // 构建系列
  const echartsSeries = series.value
      .filter(s => s.active)
      .map((seriesItem, index) => ({
        name: seriesItem.name,
        type: 'line',
        data: seriesItem.data.map(d => d.value),
        smooth: props.smooth,
        showSymbol: props.showSymbol,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: seriesItem.color
        },
        lineStyle: {
          width: 2,
          color: seriesItem.color
        },
        areaStyle: props.showArea ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: seriesItem.color + '80' },
            { offset: 1, color: seriesItem.color + '10' }
          ])
        } : undefined,
        emphasis: {
          focus: 'series',
          itemStyle: {
            borderWidth: 2,
            borderColor: '#fff',
            shadowBlur: 10,
            shadowColor: seriesItem.color + '80'
          }
        }
      }))

  // 基础配置
  const baseOptions = {
    backgroundColor: 'transparent',
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicOut',

    title: props.title ? {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal',
        color: '#333'
      },
      padding: [10, 0, 20, 0]
    } : undefined,

    grid: props.grid,

    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#f0f0f0',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        },
        lineStyle: {
          color: '#999',
          type: 'dashed'
        }
      },
      formatter: (params) => {
        let html = `<div style="font-weight: bold; margin-bottom: 8px;">${params[0].axisValue}</div>`
        params.forEach(param => {
          const value = typeof param.value === 'number' ? param.value.toFixed(2) : param.value
          html += `
            <div style="display: flex; align-items: center; margin: 4px 0;">
              <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: ${param.color}; margin-right: 8px;"></span>
              <span style="flex: 1;">${param.seriesName}:</span>
              <span style="font-weight: bold;">${value}</span>
            </div>
          `
        })
        return html
      }
    },

    legend: props.showLegend ? {
      type: 'scroll',
      orient: 'horizontal',
      right: 'center',
      top: 0,
      icon: 'circle',
      itemWidth: 12,
      itemHeight: 12,
      textStyle: {
        color: '#666'
      },
      selected: series.value.reduce((obj, s) => {
        obj[s.name] = s.active
        return obj
      }, {})
    } : undefined,

    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLine: {
        lineStyle: {
          color: '#d9d9d9'
        }
      },
      axisTick: {
        alignWithLabel: true,
        lineStyle: {
          color: '#d9d9d9'
        }
      },
      axisLabel: {
        color: '#666',
        fontSize: 12,
        formatter: (value) => {
          // 处理日期格式
          if (value instanceof Date || /^\d{4}-\d{2}-\d{2}/.test(value)) {
            return echarts.format.formatTime('MM-dd', value)
          }
          // 处理长文本
          if (value.length > 10) {
            return value.substring(0, 10) + '...'
          }
          return value
        }
      },
      name: props.xAxisName,
      nameTextStyle: {
        color: '#666',
        fontSize: 12,
        padding: [10, 0, 0, 0]
      }
    },

    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666',
        fontSize: 12,
        formatter: (value) => {
          if (typeof value === 'number') {
            // 根据数值大小选择合适的单位
            if (Math.abs(value) >= 1000000) {
              return (value / 1000000).toFixed(1) + 'M'
            } else if (Math.abs(value) >= 1000) {
              return (value / 1000).toFixed(1) + 'K'
            } else {
              return value.toFixed(1)
            }
          }
          return value
        }
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0',
          type: 'dashed'
        }
      },
      name: props.yAxisName,
      nameTextStyle: {
        color: '#666',
        fontSize: 12,
        padding: [0, 0, 10, 0]
      }
    },

    series: echartsSeries,

    dataZoom: props.showDataZoom ? [
      {
        type: 'inside',
        xAxisIndex: 0,
        start: 0,
        end: 100,
        minValueSpan: 10,
        maxValueSpan: 100
      },
      {
        type: 'slider',
        xAxisIndex: 0,
        start: 0,
        end: 100,
        height: 20,
        bottom: 0,
        borderColor: '#fff',
        fillerColor: 'rgba(24, 144, 255, 0.2)',
        handleStyle: {
          color: '#1890ff'
        },
        textStyle: {
          color: '#666'
        }
      }
    ] : undefined,

    toolbox: props.showToolbox ? {
      feature: {
        saveAsImage: {
          title: '保存为图片',
          pixelRatio: 2
        },
        dataView: {
          title: '数据视图',
          readOnly: true,
          lang: ['数据视图', '关闭', '刷新']
        },
        restore: {
          title: '还原'
        }
      },
      right: 10,
      top: 0
    } : undefined
  }

  // 合并自定义配置
  return { ...baseOptions, ...props.customOptions }
}

// 绑定图表事件
const bindChartEvents = () => {
  if (!chartInstance) return

  // 点击数据点
  chartInstance.on('click', (params) => {
    if (params.componentType === 'series') {
      emit('point-click', {
        seriesName: params.seriesName,
        dataIndex: params.dataIndex,
        value: params.value,
        rawData: series.value.find(s => s.name === params.seriesName)?.data[params.dataIndex]?.rawData
      })
    }
  })

  // 图例选择变化
  chartInstance.on('legendselectchanged', (params) => {
    const selectedSeries = series.value.find(s => s.name === params.name)
    if (selectedSeries) {
      selectedSeries.active = params.selected[params.name]
      emit('legend-select', {
        seriesName: params.name,
        selected: params.selected[params.name]
      })
    }
  })

  // 鼠标移动显示工具提示
  chartInstance.on('mousemove', (params) => {
    if (params.componentType === 'series' && params.dataIndex !== undefined) {
      const seriesItem = series.value.find(s => s.name === params.seriesName)
      if (seriesItem) {
        const dataPoint = seriesItem.data[params.dataIndex]
        const pointInPixel = chartInstance.convertToPixel({ seriesIndex: 0 }, [params.dataIndex, params.value])

        tooltip.visible = true
        tooltip.x = pointInPixel[0] + 20
        tooltip.y = pointInPixel[1] - 40
        tooltip.title = dataPoint.name
        tooltip.items = [
          {
            label: seriesItem.name,
            value: typeof dataPoint.value === 'number' ? dataPoint.value.toFixed(2) : dataPoint.value,
            color: seriesItem.color
          }
        ]
      }
    }
  })

  // 鼠标移出隐藏工具提示
  chartInstance.on('mouseout', () => {
    tooltip.visible = false
  })
}

// 切换系列显示
const toggleSeries = (index) => {
  if (index >= 0 && index < series.value.length) {
    series.value[index].active = !series.value[index].active

    if (chartInstance) {
      chartInstance.dispatchAction({
        type: 'legendToggleSelect',
        name: series.value[index].name
      })
    }
  }
}

// 处理窗口大小变化
const handleResize = debounce(() => {
  if (chartInstance) {
    chartInstance.resize()
  }
}, 200)

// 更新图表
const updateChart = () => {
  if (chartInstance) {
    const options = getChartOptions()
    chartInstance.setOption(options, true)
  }
}

// 清理
const cleanup = () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
}

// 监听数据变化
watch(() => props.data, () => {
  processData()
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

watch(() => props.loading, (newVal) => {
  if (!newVal) {
    nextTick(() => {
      initChart()
    })
  }
})

watch(() => props.height, () => {
  handleResize()
})

// 生命周期
onMounted(() => {
  processData()
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  cleanup()
})

// 暴露方法给父组件
defineExpose({
  getChartInstance: () => chartInstance,
  resize: handleResize,
  exportImage: (type = 'png', filename = 'chart') => {
    if (chartInstance) {
      const dataUrl = chartInstance.getDataURL({
        type: type,
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      const link = document.createElement('a')
      link.href = dataUrl
      link.download = filename + '.' + type
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  },
  getData: () => {
    return series.value.map(s => ({
      name: s.name,
      data: s.data,
      color: s.color,
      active: s.active
    }))
  }
})
</script>

<style lang="less" scoped>
.line-chart-container {
  position: relative;
  width: 100%;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;

  .chart-loading,
  .chart-error,
  .chart-empty {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    background: #fafafa;
  }

  .chart-canvas {
    width: 100%;
    height: 100%;
  }

  .chart-legend {
    position: absolute;
    top: 10px;
    right: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    background: rgba(255, 255, 255, 0.9);
    padding: 8px 12px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-width: 300px;
    z-index: 10;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      user-select: none;
      padding: 2px 4px;
      border-radius: 2px;
      transition: all 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }

      .legend-marker {
        width: 10px;
        height: 10px;
        border-radius: 50%;
      }

      .legend-label {
        font-size: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100px;
      }
    }
  }

  .chart-tooltip {
    position: absolute;
    z-index: 100;
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid #f0f0f0;
    border-radius: 6px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    min-width: 180px;
    transform: translate(-50%, -100%);
    pointer-events: none;

    &::after {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      width: 0;
      height: 0;
      border-left: 6px solid transparent;
      border-right: 6px solid transparent;
      border-top: 6px solid #fff;
    }

    .tooltip-title {
      font-weight: 500;
      color: #333;
      margin-bottom: 8px;
      padding-bottom: 4px;
      border-bottom: 1px solid #f0f0f0;
      font-size: 14px;
    }

    .tooltip-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
      font-size: 13px;

      &:last-child {
        margin-bottom: 0;
      }

      .tooltip-marker {
        width: 8px;
        height: 8px;
        border-radius: 50%;
      }

      .tooltip-label {
        color: #666;
        flex: 1;
      }

      .tooltip-value {
        font-weight: 500;
        color: #333;
        min-width: 60px;
        text-align: right;
      }
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .line-chart-container {
    .chart-legend {
      position: static;
      top: auto;
      right: auto;
      max-width: 100%;
      margin: 0;
      padding: 8px;
      border-radius: 0;
      border-top: 1px solid #f0f0f0;
      background: #fff;
      justify-content: center;
    }
  }
}
</style>