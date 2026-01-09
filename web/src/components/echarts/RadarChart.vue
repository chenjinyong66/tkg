<template>
  <div class="ability-radar-chart">
    <!-- 图表控制栏 -->
    <div class="chart-controls">
      <div class="controls-left">
        <a-tooltip title="重置视图">
          <a-button type="text" size="small" @click="resetView">
            <ReloadOutlined />
          </a-button>
        </a-tooltip>
        <a-tooltip title="导出图表">
          <a-button type="text" size="small" @click="exportChart">
            <ExportOutlined />
          </a-button>
        </a-tooltip>
      </div>
      <div class="controls-right">
        <a-tooltip title="显示/隐藏团队平均">
          <a-switch
              v-model:checked="showTeamAverage"
              size="small"
              checked-children="对比"
              un-checked-children="对比"
          />
        </a-tooltip>
        <a-tooltip title="显示/隐藏数据标签">
          <a-switch
              v-model:checked="showDataLabels"
              size="small"
              checked-children="数值"
              un-checked-children="数值"
          />
        </a-tooltip>
      </div>
    </div>

    <!-- 图表容器 -->
    <div ref="chartContainer" class="chart-container">
      <canvas ref="chartCanvas" class="chart-canvas" />
    </div>

    <!-- 能力详情面板 -->
    <div v-if="hoveredDimension" class="dimension-detail">
      <div class="detail-header">
        <h4>{{ hoveredDimension }}</h4>
        <a-button type="text" size="small" @click="hoveredDimension = null">
          <CloseOutlined />
        </a-button>
      </div>
      <div class="detail-content">
        <div class="score-item">
          <div class="score-label">个人得分</div>
          <div class="score-value">
            <span class="score-number">{{ getDimensionScore(hoveredDimension) }}</span>
            <span class="score-out-of">/10</span>
          </div>
          <a-progress
              :percent="getDimensionScore(hoveredDimension) * 10"
              :stroke-color="getScoreColor(getDimensionScore(hoveredDimension))"
              size="small"
              :show-info="false"
          />
        </div>
        <div v-if="showTeamAverage" class="score-item">
          <div class="score-label">团队平均</div>
          <div class="score-value">
            <span class="score-number">{{ getTeamAverageScore(hoveredDimension) }}</span>
            <span class="score-out-of">/10</span>
          </div>
          <a-progress
              :percent="getTeamAverageScore(hoveredDimension) * 10"
              stroke-color="rgba(24, 144, 255, 0.3)"
              size="small"
              :show-info="false"
          />
        </div>
        <div class="score-difference">
          <span class="difference-label">差异</span>
          <span
              class="difference-value"
              :class="{
              'positive': getScoreDifference(hoveredDimension) > 0,
              'negative': getScoreDifference(hoveredDimension) < 0,
              'neutral': getScoreDifference(hoveredDimension) === 0
            }"
          >
            {{ getScoreDifference(hoveredDimension) > 0 ? '+' : '' }}{{ getScoreDifference(hoveredDimension).toFixed(1) }}
          </span>
        </div>
        <div class="recommendation" v-if="getRecommendation(hoveredDimension)">
          <div class="recommendation-title">提升建议</div>
          <div class="recommendation-content">
            {{ getRecommendation(hoveredDimension) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 图表图例 -->
    <div class="chart-legend">
      <div class="legend-item">
        <div class="legend-color" style="background-color: #1890ff;"></div>
        <span class="legend-text">个人能力</span>
      </div>
      <div v-if="showTeamAverage" class="legend-item">
        <div class="legend-color" style="background-color: rgba(24, 144, 255, 0.3);"></div>
        <span class="legend-text">团队平均</span>
      </div>
      <div class="legend-stats">
        <span class="stat-item">
          <span class="stat-label">综合得分</span>
          <span class="stat-value">{{ overallScore }}/10</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">维度</span>
          <span class="stat-value">{{ dimensions?.length || 0 }}</span>
        </span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="chart-loading">
      <a-spin size="large" />
      <div class="loading-text">正在加载能力数据...</div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!dimensions || dimensions.length === 0" class="chart-empty">
      <div class="empty-content">
        <RadarChartOutlined style="font-size: 48px; color: #d9d9d9;" />
        <p>暂无能力数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  ReloadOutlined, ExportOutlined, CloseOutlined,
  RadarChartOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      overallScore: 0,
      topAbility: '',
      weakAbility: '',
      dimensions: []
    })
  },
  dimensions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['dimension-click'])

// 响应式数据
const chartContainer = ref(null)
const chartCanvas = ref(null)
const hoveredDimension = ref(null)
const showTeamAverage = ref(true)
const showDataLabels = ref(true)

// 图表状态
const state = reactive({
  width: 0,
  height: 0,
  ctx: null,
  centerX: 0,
  centerY: 0,
  radius: 0,
  animationProgress: 0,
  hoveredIndex: -1,
  isAnimating: false
})

// 颜色配置
const scoreColors = [
  '#ff4d4f', // 0-2分: 红色
  '#ff7a45', // 2-4分: 橙红
  '#ffa940', // 4-6分: 橙色
  '#ffc53d', // 6-7分: 橙黄
  '#ffec3d', // 7-8分: 黄色
  '#bae637', // 8-9分: 黄绿
  '#73d13d', // 9-10分: 绿色
  '#52c41a'  // 10分: 深绿
]

// 能力提升建议
const recommendations = {
  '专业技能': '建议参与相关技术培训或实际项目积累经验，可以参考行业最佳实践进行专项提升。',
  '项目经验': '建议承担更多关键项目角色，积累不同规模和复杂度的项目经验。',
  '团队协作': '建议加强跨部门沟通，积极参与团队建设活动，提升协作效率。',
  '沟通能力': '建议参加沟通技巧培训，练习公众演讲，提高表达清晰度。',
  '学习能力': '建议制定学习计划，关注行业动态，培养持续学习的习惯。',
  '创新能力': '建议参与创新项目，培养批判性思维，鼓励尝试新方法。'
}

// 计算综合得分
const overallScore = computed(() => {
  if (!props.data.dimensions || props.data.dimensions.length === 0) return 0

  const total = props.data.dimensions.reduce((sum, d) => sum + (d.value || 0), 0)
  return (total / props.data.dimensions.length).toFixed(1)
})

// 初始化图表
const initChart = () => {
  if (!chartCanvas.value || !chartContainer.value) return

  const container = chartContainer.value
  state.width = container.clientWidth
  state.height = container.clientHeight

  chartCanvas.value.width = state.width
  chartCanvas.value.height = state.height

  state.ctx = chartCanvas.value.getContext('2d')

  // 计算中心点和半径
  state.centerX = state.width / 2
  state.centerY = state.height / 2
  state.radius = Math.min(state.width, state.height) * 0.35

  // 开始动画
  startAnimation()

  // 添加事件监听
  chartCanvas.value.addEventListener('mousemove', handleMouseMove)
  chartCanvas.value.addEventListener('click', handleClick)
  chartCanvas.value.addEventListener('mouseleave', handleMouseLeave)
}

// 开始动画
const startAnimation = () => {
  state.animationProgress = 0
  state.isAnimating = true

  const animate = () => {
    state.animationProgress += 0.02
    if (state.animationProgress >= 1) {
      state.animationProgress = 1
      state.isAnimating = false
    }

    render()

    if (state.isAnimating) {
      requestAnimationFrame(animate)
    }
  }

  animate()
}

// 渲染图表
const render = () => {
  if (!state.ctx || !props.dimensions || props.dimensions.length === 0) return

  // 清除画布
  state.ctx.clearRect(0, 0, state.width, state.height)

  // 绘制背景网格
  drawBackground()

  // 绘制雷达图
  drawRadarChart()

  // 绘制数据点
  drawDataPoints()

  // 绘制维度标签
  drawDimensionLabels()

  // 绘制数据标签
  if (showDataLabels.value) {
    drawDataLabels()
  }

  // 绘制悬停效果
  if (state.hoveredIndex >= 0) {
    drawHoverEffect(state.hoveredIndex)
  }
}

// 绘制背景网格
const drawBackground = () => {
  const { ctx, centerX, centerY, radius } = state
  const dimensions = props.dimensions
  const dimensionCount = dimensions.length

  if (dimensionCount < 3) return

  // 计算角度
  const angleStep = (2 * Math.PI) / dimensionCount

  // 绘制背景多边形
  ctx.save()
  ctx.strokeStyle = '#e8e8e8'
  ctx.fillStyle = 'rgba(250, 250, 250, 0.6)'
  ctx.lineWidth = 1

  // 绘制5层同心多边形
  for (let level = 1; level <= 5; level++) {
    const levelRadius = (radius * level) / 5

    ctx.beginPath()
    for (let i = 0; i < dimensionCount; i++) {
      const angle = i * angleStep - Math.PI / 2
      const x = centerX + levelRadius * Math.cos(angle)
      const y = centerY + levelRadius * Math.sin(angle)

      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    }
    ctx.closePath()
    ctx.stroke()

    // 最外层填充浅色背景
    if (level === 5) {
      ctx.fill()
    }
  }

  // 绘制从中心到每个顶点的连线
  ctx.beginPath()
  for (let i = 0; i < dimensionCount; i++) {
    const angle = i * angleStep - Math.PI / 2
    const x = centerX + radius * Math.cos(angle)
    const y = centerY + radius * Math.sin(angle)

    ctx.moveTo(centerX, centerY)
    ctx.lineTo(x, y)
  }
  ctx.stroke()
  ctx.restore()
}

// 绘制雷达图
const drawRadarChart = () => {
  const { ctx, centerX, centerY, radius, animationProgress } = state
  const dimensions = props.dimensions
  const dimensionCount = dimensions.length

  if (dimensionCount < 3 || !props.data.dimensions) return

  const angleStep = (2 * Math.PI) / dimensionCount

  // 绘制个人能力多边形
  ctx.save()
  ctx.beginPath()

  for (let i = 0; i < dimensionCount; i++) {
    const dimensionData = props.data.dimensions.find(d => d.name === dimensions[i])
    if (!dimensionData) continue

    const score = dimensionData.value || 0
    const animatedScore = score * animationProgress

    const angle = i * angleStep - Math.PI / 2
    const pointRadius = (radius * animatedScore) / 10
    const x = centerX + pointRadius * Math.cos(angle)
    const y = centerY + pointRadius * Math.sin(angle)

    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  }

  ctx.closePath()
  ctx.fillStyle = 'rgba(24, 144, 255, 0.3)'
  ctx.strokeStyle = '#1890ff'
  ctx.lineWidth = 2
  ctx.fill()
  ctx.stroke()
  ctx.restore()

  // 绘制团队平均多边形
  if (showTeamAverage.value) {
    ctx.save()
    ctx.beginPath()

    for (let i = 0; i < dimensionCount; i++) {
      const dimensionData = props.data.dimensions.find(d => d.name === dimensions[i])
      if (!dimensionData || !dimensionData.avg) continue

      const avgScore = dimensionData.avg
      const animatedAvgScore = avgScore * animationProgress

      const angle = i * angleStep - Math.PI / 2
      const pointRadius = (radius * animatedAvgScore) / 10
      const x = centerX + pointRadius * Math.cos(angle)
      const y = centerY + pointRadius * Math.sin(angle)

      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    }

    ctx.closePath()
    ctx.fillStyle = 'rgba(24, 144, 255, 0.1)'
    ctx.strokeStyle = 'rgba(24, 144, 255, 0.5)'
    ctx.lineWidth = 1
    ctx.setLineDash([5, 5])
    ctx.fill()
    ctx.stroke()
    ctx.restore()
  }
}

// 绘制数据点
const drawDataPoints = () => {
  const { ctx, centerX, centerY, radius, animationProgress } = state
  const dimensions = props.dimensions
  const dimensionCount = dimensions.length

  if (dimensionCount < 3 || !props.data.dimensions) return

  const angleStep = (2 * Math.PI) / dimensionCount

  // 绘制个人能力数据点
  for (let i = 0; i < dimensionCount; i++) {
    const dimensionData = props.data.dimensions.find(d => d.name === dimensions[i])
    if (!dimensionData) continue

    const score = dimensionData.value || 0
    const animatedScore = score * animationProgress

    const angle = i * angleStep - Math.PI / 2
    const pointRadius = (radius * animatedScore) / 10
    const x = centerX + pointRadius * Math.cos(angle)
    const y = centerY + pointRadius * Math.sin(angle)

    // 绘制数据点
    ctx.save()
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fillStyle = '#1890ff'
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 2
    ctx.fill()
    ctx.stroke()
    ctx.restore()

    // 从数据点到多边形顶点的连线
    ctx.save()
    ctx.beginPath()
    const vertexX = centerX + radius * Math.cos(angle)
    const vertexY = centerY + radius * Math.sin(angle)
    ctx.moveTo(x, y)
    ctx.lineTo(vertexX, vertexY)
    ctx.strokeStyle = 'rgba(24, 144, 255, 0.2)'
    ctx.lineWidth = 1
    ctx.setLineDash([2, 2])
    ctx.stroke()
    ctx.restore()
  }
}

// 绘制维度标签
const drawDimensionLabels = () => {
  const { ctx, centerX, centerY, radius } = state
  const dimensions = props.dimensions
  const dimensionCount = dimensions.length

  if (dimensionCount < 3) return

  const angleStep = (2 * Math.PI) / dimensionCount
  const labelRadius = radius + 40

  ctx.save()
  ctx.font = '12px Arial'
  ctx.fillStyle = '#666'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  for (let i = 0; i < dimensionCount; i++) {
    const angle = i * angleStep - Math.PI / 2
    const x = centerX + labelRadius * Math.cos(angle)
    const y = centerY + labelRadius * Math.sin(angle)

    // 根据角度调整文本对齐方式
    if (Math.abs(Math.cos(angle)) < 0.3) {
      ctx.textAlign = 'center'
    } else if (angle > Math.PI / 2 && angle < 3 * Math.PI / 2) {
      ctx.textAlign = 'right'
    } else {
      ctx.textAlign = 'left'
    }

    ctx.fillText(dimensions[i], x, y)
  }
  ctx.restore()
}

// 绘制数据标签
const drawDataLabels = () => {
  const { ctx, centerX, centerY, radius, animationProgress } = state
  const dimensions = props.dimensions
  const dimensionCount = dimensions.length

  if (dimensionCount < 3 || !props.data.dimensions) return

  const angleStep = (2 * Math.PI) / dimensionCount

  ctx.save()
  ctx.font = '11px Arial'
  ctx.fillStyle = '#333'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  for (let i = 0; i < dimensionCount; i++) {
    const dimensionData = props.data.dimensions.find(d => d.name === dimensions[i])
    if (!dimensionData) continue

    const score = dimensionData.value || 0
    const animatedScore = score * animationProgress

    const angle = i * angleStep - Math.PI / 2
    const pointRadius = (radius * animatedScore) / 10
    const labelRadius = pointRadius - 15
    const x = centerX + labelRadius * Math.cos(angle)
    const y = centerY + labelRadius * Math.sin(angle)

    // 绘制背景圆
    ctx.beginPath()
    ctx.arc(x, y, 10, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
    ctx.fill()
    ctx.strokeStyle = '#1890ff'
    ctx.lineWidth = 1
    ctx.stroke()

    // 绘制分数
    ctx.fillStyle = getScoreColor(score)
    ctx.fillText(score.toFixed(1), x, y)
  }
  ctx.restore()
}

// 绘制悬停效果
const drawHoverEffect = (dimensionIndex) => {
  const { ctx, centerX, centerY, radius } = state
  const dimensions = props.dimensions
  const dimensionCount = dimensions.length

  if (dimensionCount < 3) return

  const angleStep = (2 * Math.PI) / dimensionCount
  const angle = dimensionIndex * angleStep - Math.PI / 2

  // 绘制高亮区域
  ctx.save()
  ctx.beginPath()
  ctx.moveTo(centerX, centerY)
  ctx.lineTo(centerX + radius * Math.cos(angle), centerY + radius * Math.sin(angle))
  ctx.arc(centerX, centerY, radius, angle - angleStep/2, angle + angleStep/2)
  ctx.closePath()
  ctx.fillStyle = 'rgba(24, 144, 255, 0.1)'
  ctx.fill()
  ctx.restore()

  // 绘制高亮顶点
  const vertexX = centerX + radius * Math.cos(angle)
  const vertexY = centerY + radius * Math.sin(angle)

  ctx.save()
  ctx.beginPath()
  ctx.arc(vertexX, vertexY, 6, 0, Math.PI * 2)
  ctx.fillStyle = '#1890ff'
  ctx.strokeStyle = '#ffffff'
  ctx.lineWidth = 2
  ctx.fill()
  ctx.stroke()
  ctx.restore()

  // 绘制高亮文本
  const dimensionName = dimensions[dimensionIndex]
  ctx.save()
  ctx.font = '14px Arial'
  ctx.fillStyle = '#1890ff'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  const labelRadius = radius + 60
  const labelX = centerX + labelRadius * Math.cos(angle)
  const labelY = centerY + labelRadius * Math.sin(angle)

  // 绘制文本背景
  const textWidth = ctx.measureText(dimensionName).width
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
  ctx.fillRect(labelX - textWidth/2 - 8, labelY - 12, textWidth + 16, 24)

  // 绘制文本
  ctx.fillStyle = '#1890ff'
  ctx.fillText(dimensionName, labelX, labelY)
  ctx.restore()
}

// 鼠标移动事件处理
const handleMouseMove = (event) => {
  if (!chartCanvas.value) return

  const rect = chartCanvas.value.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top

  const dimensions = props.dimensions
  const dimensionCount = dimensions.length

  if (dimensionCount < 3) {
    state.hoveredIndex = -1
    hoveredDimension.value = null
    render()
    return
  }

  // 计算鼠标相对于中心点的极坐标
  const dx = mouseX - state.centerX
  const dy = mouseY - state.centerY
  const distance = Math.sqrt(dx * dx + dy * dy)

  // 只在雷达图区域内检测悬停
  if (distance > state.radius + 50 || distance < 20) {
    state.hoveredIndex = -1
    hoveredDimension.value = null
    render()
    return
  }

  // 计算角度
  let angle = Math.atan2(dy, dx)
  if (angle < -Math.PI / 2) angle += Math.PI * 2

  // 调整角度起点
  angle += Math.PI / 2
  if (angle < 0) angle += Math.PI * 2

  // 计算对应的维度索引
  const angleStep = (2 * Math.PI) / dimensionCount
  let dimensionIndex = Math.floor(angle / angleStep)
  if (dimensionIndex >= dimensionCount) dimensionIndex = 0

  if (state.hoveredIndex !== dimensionIndex) {
    state.hoveredIndex = dimensionIndex
    hoveredDimension.value = dimensions[dimensionIndex]

    // 更新鼠标样式
    chartCanvas.value.style.cursor = 'pointer'

    render()
  }
}

// 鼠标点击事件处理
const handleClick = (event) => {
  if (state.hoveredIndex >= 0) {
    const dimension = props.dimensions[state.hoveredIndex]
    emit('dimension-click', dimension)
  }
}

// 鼠标离开事件处理
const handleMouseLeave = () => {
  state.hoveredIndex = -1
  hoveredDimension.value = null
  if (chartCanvas.value) {
    chartCanvas.value.style.cursor = 'default'
  }
  render()
}

// 工具函数
const getScoreColor = (score) => {
  const index = Math.min(Math.floor(score), scoreColors.length - 1)
  return scoreColors[index] || scoreColors[0]
}

const getDimensionScore = (dimensionName) => {
  const dimensionData = props.data.dimensions?.find(d => d.name === dimensionName)
  return dimensionData?.value || 0
}

const getTeamAverageScore = (dimensionName) => {
  const dimensionData = props.data.dimensions?.find(d => d.name === dimensionName)
  return dimensionData?.avg || 0
}

const getScoreDifference = (dimensionName) => {
  const personalScore = getDimensionScore(dimensionName)
  const teamAverage = getTeamAverageScore(dimensionName)
  return personalScore - teamAverage
}

const getRecommendation = (dimensionName) => {
  return recommendations[dimensionName] || '建议通过实际工作和持续学习来提升此项能力。'
}

// 控制函数
const resetView = () => {
  startAnimation()
}

const exportChart = () => {
  if (!chartCanvas.value) return

  const link = document.createElement('a')
  link.download = `能力雷达图_${new Date().getTime()}.png`
  link.href = chartCanvas.value.toDataURL('image/png')
  link.click()
}

// 监听属性变化
watch(() => props.data, () => {
  if (state.isAnimating) return
  startAnimation()
}, { deep: true })

watch(() => props.dimensions, () => {
  if (state.isAnimating) return
  startAnimation()
})

watch(showTeamAverage, () => {
  render()
})

watch(showDataLabels, () => {
  render()
})

// 生命周期钩子
onMounted(() => {
  initChart()
  window.addEventListener('resize', initChart)
})

onUnmounted(() => {
  if (chartCanvas.value) {
    chartCanvas.value.removeEventListener('mousemove', handleMouseMove)
    chartCanvas.value.removeEventListener('click', handleClick)
    chartCanvas.value.removeEventListener('mouseleave', handleMouseLeave)
  }
  window.removeEventListener('resize', initChart)
})
</script>

<style lang="less" scoped>
.ability-radar-chart {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;

  .chart-controls {
    position: absolute;
    top: 8px;
    left: 8px;
    right: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 10;

    .controls-left,
    .controls-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .chart-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .chart-canvas {
    max-width: 100%;
    max-height: 100%;
    display: block;
  }

  .dimension-detail {
    position: absolute;
    bottom: 16px;
    left: 16px;
    right: 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 10;
    overflow: hidden;

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: #fafafa;
      border-bottom: 1px solid #f0f0f0;

      h4 {
        margin: 0;
        font-size: 16px;
        color: #333;
      }
    }

    .detail-content {
      padding: 16px;

      .score-item {
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }

        .score-label {
          font-size: 12px;
          color: #666;
          margin-bottom: 4px;
        }

        .score-value {
          display: flex;
          align-items: baseline;
          margin-bottom: 8px;

          .score-number {
            font-size: 24px;
            font-weight: 600;
            color: #1890ff;
          }

          .score-out-of {
            font-size: 14px;
            color: #999;
            margin-left: 4px;
          }
        }
      }

      .score-difference {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 16px 0;
        padding: 8px 12px;
        background: #fafafa;
        border-radius: 4px;

        .difference-label {
          font-size: 14px;
          color: #666;
        }

        .difference-value {
          font-size: 18px;
          font-weight: 600;

          &.positive {
            color: #52c41a;
          }

          &.negative {
            color: #ff4d4f;
          }

          &.neutral {
            color: #999;
          }
        }
      }

      .recommendation {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;

        .recommendation-title {
          font-size: 14px;
          font-weight: 500;
          color: #333;
          margin-bottom: 8px;
        }

        .recommendation-content {
          font-size: 13px;
          color: #666;
          line-height: 1.6;
        }
      }
    }
  }

  .chart-legend {
    position: absolute;
    top: 60px;
    right: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 10;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .legend-color {
        width: 12px;
        height: 12px;
        border-radius: 2px;
      }

      .legend-text {
        font-size: 12px;
        color: #666;
      }
    }

    .legend-stats {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid #f0f0f0;

      .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .stat-label {
          font-size: 12px;
          color: #666;
        }

        .stat-value {
          font-size: 14px;
          font-weight: 600;
          color: #1890ff;
        }
      }
    }
  }

  .chart-loading {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.8);
    z-index: 20;

    .loading-text {
      margin-top: 16px;
      font-size: 14px;
      color: #666;
    }
  }

  .chart-empty {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #fafafa;

    .empty-content {
      text-align: center;

      p {
        margin-top: 16px;
        color: #999;
      }
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .ability-radar-chart {
    .chart-controls {
      flex-direction: column;
      gap: 8px;

      .controls-left,
      .controls-right {
        width: 100%;
        justify-content: center;
      }
    }

    .dimension-detail {
      position: relative;
      margin-top: 16px;
    }

    .chart-legend {
      position: relative;
      top: auto;
      right: auto;
      margin: 16px auto 0;
      width: 90%;
    }
  }
}
</style>