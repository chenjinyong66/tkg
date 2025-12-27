<template>
  <div class="talent-analysis">
    <!-- 页面标题 -->
    <div class="analysis-header">
      <h2>能力分析</h2>
      <div class="header-actions">
        <a-select
            v-model:value="timeRange"
            placeholder="选择时间范围"
            style="width: 140px; margin-right: 8px;"
            @change="handleTimeRangeChange"
        >
          <a-select-option value="month">最近一个月</a-select-option>
          <a-select-option value="quarter">最近一个季度</a-select-option>
          <a-select-option value="halfYear">最近半年</a-select-option>
          <a-select-option value="year">最近一年</a-select-option>
          <a-select-option value="all">全部时间</a-select-option>
        </a-select>
        <a-select
            v-model:value="compareMode"
            placeholder="对比模式"
            style="width: 120px; margin-right: 8px;"
            @change="handleCompareChange"
        >
          <a-select-option value="none">不对比</a-select-option>
          <a-select-option value="self">自身对比</a-select-option>
          <a-select-option value="team">团队对比</a-select-option>
        </a-select>
        <a-button type="primary" @click="handleExportReport">
          <ExportOutlined />
          导出分析报告
        </a-button>
      </div>
    </div>

    <!-- 综合评分 -->
    <a-card class="overall-rating-card" :loading="loading">
      <div class="overall-content">
        <div class="rating-main">
          <div class="rating-score">
            <div class="score-value">{{ overallRating.score.toFixed(1) }}</div>
            <div class="score-label">综合评分</div>
          </div>
          <div class="rating-details">
            <div class="detail-item">
              <span class="detail-label">技术能力</span>
              <span class="detail-value">{{ overallRating.technical.toFixed(1) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">管理能力</span>
              <span class="detail-value">{{ overallRating.management.toFixed(1) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">沟通能力</span>
              <span class="detail-value">{{ overallRating.communication.toFixed(1) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">创新能力</span>
              <span class="detail-value">{{ overallRating.innovation.toFixed(1) }}</span>
            </div>
          </div>
        </div>
        <div class="rating-progress">
          <a-progress
              type="circle"
              :percent="overallRating.score * 10"
              :stroke-color="getRatingColor(overallRating.score)"
              :width="120"
          />
          <div class="progress-label">综合评价</div>
        </div>
      </div>
    </a-card>

    <!-- 能力雷达图 -->
    <div class="radar-section">
      <a-card class="radar-card">
        <template #title>
          <div class="card-title">
            <span>能力雷达图</span>
            <a-radio-group v-model:value="radarType" size="small">
              <a-radio-button value="comprehensive">综合能力</a-radio-button>
              <a-radio-button value="technical">技术能力</a-radio-button>
              <a-radio-button value="soft">软技能</a-radio-button>
            </a-radio-group>
          </div>
        </template>
        <div class="radar-container">
          <RadarChart
              v-if="radarData.length > 0"
              :data="radarData"
              :dimensions="radarDimensions"
              :height="350"
              :compare-data="compareData"
              :compare-dimensions="compareDimensions"
          />
          <div v-else class="no-data">
            <Empty description="暂无能力评估数据" />
            <a-button type="primary" @click="handleQuickAssess" style="margin-top: 16px;">
              快速评估
            </a-button>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 能力趋势图 -->
    <div class="trend-section">
      <a-card class="trend-card" title="能力发展趋势">
        <div class="trend-controls">
          <a-select
              v-model:value="trendDimension"
              placeholder="选择维度"
              style="width: 150px;"
              @change="handleTrendDimensionChange"
          >
            <a-select-option v-for="dim in trendDimensions" :key="dim.value" :value="dim.value">
              {{ dim.label }}
            </a-select-option>
          </a-select>
          <div class="trend-legend" v-if="trendData.length > 0">
            <div class="legend-item">
              <span class="legend-color" style="background: #1890ff;"></span>
              <span class="legend-text">{{ talentInfo?.name || '当前人才' }}</span>
            </div>
            <div class="legend-item" v-if="compareMode === 'team'">
              <span class="legend-color" style="background: #52c41a;"></span>
              <span class="legend-text">团队平均</span>
            </div>
          </div>
        </div>
        <div class="trend-container">
          <LineChart
              v-if="trendData.length > 0"
              :data="trendData"
              :x-field="'time'"
              :y-field="'score'"
              :series-field="'type'"
              :height="300"
              :smooth="true"
              :show-area="true"
          />
          <div v-else class="no-data">
            <Empty description="暂无趋势数据" />
          </div>
        </div>
      </a-card>
    </div>

    <!-- 详细能力分析 -->
    <div class="detailed-analysis">
      <a-card title="详细能力分析">
        <template #extra>
          <a-button @click="handleAddAssessment">
            <PlusOutlined />
            新增评估
          </a-button>
        </template>
        <a-table
            :data-source="detailedAnalysis"
            :columns="analysisColumns"
            :pagination="false"
            size="middle"
            :loading="loading"
            row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'dimension'">
              <div class="dimension-cell">
                <div class="dimension-name">{{ record.dimension }}</div>
                <div class="dimension-desc">{{ record.description }}</div>
              </div>
            </template>

            <template v-if="column.key === 'score'">
              <div class="score-cell">
                <a-progress
                    :percent="record.score * 10"
                    :stroke-color="getScoreColor(record.score)"
                    :show-info="false"
                    size="small"
                    style="flex: 1;"
                />
                <span class="score-value">{{ record.score.toFixed(1) }}</span>
              </div>
            </template>

            <template v-if="column.key === 'level'">
              <a-tag :color="getLevelColor(record.level)" size="small">
                {{ getLevelLabel(record.level) }}
              </a-tag>
            </template>

            <template v-if="column.key === 'trend'">
              <div class="trend-cell">
                <span v-if="record.trend === 'up'" class="trend-up">
                  <RiseOutlined style="color: #52c41a;" />
                  <span class="trend-text">上升</span>
                </span>
                <span v-else-if="record.trend === 'down'" class="trend-down">
                  <FallOutlined style="color: #ff4d4f;" />
                  <span class="trend-text">下降</span>
                </span>
                <span v-else class="trend-stable">
                  <MinusOutlined style="color: #faad14;" />
                  <span class="trend-text">稳定</span>
                </span>
                <span class="trend-value" v-if="record.trendValue">
                  {{ Math.abs(record.trendValue).toFixed(1) }}
                </span>
              </div>
            </template>

            <template v-if="column.key === 'actions'">
              <div class="analysis-actions">
                <a-tooltip title="查看详情">
                  <a-button type="link" size="small" @click="viewAssessmentDetail(record)">
                    <EyeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="编辑">
                  <a-button type="link" size="small" @click="editAssessment(record)">
                    <EditOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="删除">
                  <a-popconfirm
                      title="确定要删除这个评估吗？"
                      @confirm="deleteAssessment(record.id)"
                  >
                    <a-button type="link" size="small" danger>
                      <DeleteOutlined />
                    </a-button>
                  </a-popconfirm>
                </a-tooltip>
              </div>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 改进建议 -->
    <div class="suggestions-section">
      <a-card class="suggestions-card" title="改进建议">
        <div class="suggestions-content">
          <a-list :data-source="suggestions" :loading="loading">
            <template #renderItem="{ item, index }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <div class="suggestion-title">
                      <span class="suggestion-index">{{ index + 1 }}</span>
                      <span class="suggestion-text">{{ item.content }}</span>
                    </div>
                  </template>
                  <template #description>
                    <div class="suggestion-details">
                      <span class="dimension-tag">
                        关联维度：{{ item.dimension }}
                      </span>
                      <span class="priority-tag">
                        <a-tag :color="getPriorityColor(item.priority)" size="small">
                          {{ getPriorityLabel(item.priority) }}
                        </a-tag>
                      </span>
                      <span class="suggestion-time">
                        {{ formatRelativeTime(item.createTime) }}
                      </span>
                    </div>
                  </template>
                </a-list-item-meta>
                <div class="suggestion-actions">
                  <a-button type="link" size="small" @click="markSuggestionDone(item)">
                    <CheckCircleOutlined />
                    标记完成
                  </a-button>
                </div>
              </a-list-item>
            </template>
          </a-list>
          <div v-if="suggestions.length === 0 && !loading" class="no-suggestions">
            <Empty description="暂无改进建议" />
          </div>
        </div>
      </a-card>
    </div>

    <!-- 快速评估模态框 -->
    <a-modal
        v-model:open="showQuickAssessModal"
        title="快速能力评估"
        @ok="handleQuickAssessSubmit"
        @cancel="showQuickAssessModal = false"
        width="800px"
        :confirm-loading="assessing"
    >
      <div class="quick-assess-modal">
        <p style="margin-bottom: 20px; color: #666;">
          请为人才 <strong>{{ talentInfo?.name }}</strong> 的各个能力维度进行评分（1-10分）：
        </p>

        <div class="assess-items">
          <div
              v-for="dimension in assessmentDimensions"
              :key="dimension.key"
              class="assess-item"
          >
            <div class="assess-dimension">
              <span class="dimension-name">{{ dimension.label }}</span>
              <span class="dimension-desc">{{ dimension.description }}</span>
            </div>
            <div class="assess-rating">
              <a-rate
                  v-model:value="assessmentValues[dimension.key]"
                  :count="10"
                  allow-half
                  @change="(value) => handleRatingChange(dimension.key, value)"
                  character="★"
                  style="font-size: 18px;"
              />
              <span class="rating-value">
                {{ assessmentValues[dimension.key] || 0 }}/10
              </span>
            </div>
          </div>
        </div>

        <div class="assess-remarks">
          <a-textarea
              v-model:value="assessmentRemarks"
              placeholder="请输入评估备注"
              :rows="3"
              style="margin-top: 20px;"
          />
        </div>
      </div>
    </a-modal>

    <!-- 新增评估模态框 -->
    <a-modal
        v-model:open="showAssessmentModal"
        :title="editMode ? '编辑评估' : '新增评估'"
        @ok="handleAssessmentSubmit"
        @cancel="handleAssessmentCancel"
        width="600px"
        :confirm-loading="submitting"
    >
      <a-form :model="assessmentForm" layout="vertical">
        <a-form-item label="评估维度" required>
          <a-select
              v-model:value="assessmentForm.dimension"
              placeholder="请选择评估维度"
          >
            <a-select-option v-for="dim in assessmentDimensions" :key="dim.key" :value="dim.key">
              {{ dim.label }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="评分" required>
          <a-slider
              v-model:value="assessmentForm.score"
              :min="0"
              :max="10"
              :step="0.1"
              :marks="{0: '0', 5: '5', 10: '10'}"
          />
          <div class="slider-value">
            {{ assessmentForm.score.toFixed(1) }}/10
          </div>
        </a-form-item>

        <a-form-item label="评估说明">
          <a-textarea
              v-model:value="assessmentForm.remarks"
              placeholder="请输入评估说明"
              :rows="3"
          />
        </a-form-item>

        <a-form-item label="评估人">
          <a-input
              v-model:value="assessmentForm.evaluator"
              placeholder="请输入评估人"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { h } from 'vue'
import {
  ExportOutlined, RiseOutlined, FallOutlined,
  MinusOutlined, CheckCircleOutlined, PlusOutlined,
  EyeOutlined, EditOutlined, DeleteOutlined
} from '@ant-design/icons-vue'
import { Empty } from 'ant-design-vue'
import RadarChart from '@/components/echarts/RadarChart.vue'
import LineChart from '@/components/echarts/LineChart.vue'
import { talentApi } from '@/apis/talent_api'
import dayjs from 'dayjs'

const route = useRoute()
const talentId = route.params.id

// 响应式数据
const loading = ref(false)
const timeRange = ref('quarter')
const compareMode = ref('none')
const radarType = ref('comprehensive')
const trendDimension = ref('technical')
const showQuickAssessModal = ref(false)
const showAssessmentModal = ref(false)
const editMode = ref(false)
const assessing = ref(false)
const submitting = ref(false)

// 数据
const talentInfo = ref({})
const overallRating = reactive({
  score: 0,
  technical: 0,
  management: 0,
  communication: 0,
  innovation: 0,
  execution: 0,
  teamwork: 0
})
const radarData = ref([])
const compareData = ref([])
const trendData = ref([])
const detailedAnalysis = ref([])
const suggestions = ref([])

// 评估表单
const assessmentForm = reactive({
  id: null,
  dimension: 'technical',
  score: 0,
  remarks: '',
  evaluator: ''
})

// 快速评估数据
const assessmentValues = reactive({})
const assessmentRemarks = ref('')
const assessmentDimensions = [
  { key: 'technical', label: '技术能力', description: '专业技术和解决问题的能力' },
  { key: 'management', label: '管理能力', description: '项目管理和团队领导能力' },
  { key: 'communication', label: '沟通能力', description: '表达和协作能力' },
  { key: 'innovation', label: '创新能力', description: '创新思维和解决问题的新方法' },
  { key: 'execution', label: '执行力', description: '任务执行和完成能力' },
  { key: 'teamwork', label: '团队协作', description: '团队合作和协作精神' }
]

// 趋势维度选项
const trendDimensions = [
  { value: 'technical', label: '技术能力' },
  { value: 'management', label: '管理能力' },
  { value: 'communication', label: '沟通能力' },
  { value: 'innovation', label: '创新能力' },
  { value: 'execution', label: '执行力' },
  { value: 'teamwork', label: '团队协作' }
]

// 表格列定义
const analysisColumns = [
  {
    title: '能力维度',
    key: 'dimension',
    width: 200
  },
  {
    title: '评分',
    key: 'score',
    width: 200
  },
  {
    title: '等级',
    key: 'level',
    width: 100
  },
  {
    title: '趋势',
    key: 'trend',
    width: 120
  },
  {
    title: '评估时间',
    key: 'evaluateTime',
    width: 150
  },
  {
    title: '操作',
    key: 'actions',
    width: 120
  }
]

// 计算属性
const radarDimensions = computed(() => {
  switch (radarType.value) {
    case 'technical':
      return [
        { key: 'specialty', label: '专业技术' },
        { key: 'depth', label: '技术深度' },
        { key: 'width', label: '技术广度' },
        { key: 'problem_solving', label: '问题解决' },
        { key: 'technical_innovation', label: '技术创新' },
        { key: 'learning', label: '学习能力' }
      ]
    case 'soft':
      return [
        { key: 'communication', label: '沟通能力' },
        { key: 'teamwork', label: '团队协作' },
        { key: 'leadership', label: '领导力' },
        { key: 'adaptability', label: '适应能力' },
        { key: 'pressure', label: '抗压能力' },
        { key: 'responsibility', label: '责任心' }
      ]
    default:
      return [
        { key: 'technical', label: '技术能力' },
        { key: 'management', label: '管理能力' },
        { key: 'communication', label: '沟通能力' },
        { key: 'innovation', label: '创新能力' },
        { key: 'execution', label: '执行力' },
        { key: 'teamwork', label: '团队协作' }
      ]
  }
})

const compareDimensions = computed(() => {
  if (compareMode.value === 'team') {
    return [{ key: 'team_avg', label: '团队平均' }]
  }
  return []
})

// 工具函数
const formatRelativeTime = (dateTime) => {
  if (!dateTime) return ''
  return dayjs(dateTime).fromNow()
}

const getRatingColor = (score) => {
  if (score >= 8) return '#52c41a'
  if (score >= 6) return '#faad14'
  return '#ff4d4f'
}

const getScoreColor = (score) => {
  return getRatingColor(score)
}

const getLevelColor = (level) => {
  const colors = {
    excellent: 'success',
    good: 'processing',
    average: 'warning',
    poor: 'error'
  }
  return colors[level] || 'default'
}

const getLevelLabel = (level) => {
  const labels = {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    poor: '待提升'
  }
  return labels[level] || level
}

const getPriorityColor = (priority) => {
  const colors = {
    high: 'error',
    medium: 'warning',
    low: 'processing'
  }
  return colors[priority] || 'default'
}

const getPriorityLabel = (priority) => {
  const labels = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return labels[priority] || priority
}

// 业务函数
const loadTalentInfo = async () => {
  try {
    const response = await talentApi.getTalentDetail(talentId)
    talentInfo.value = response.talent || {}
  } catch (error) {
    console.error('加载人才信息失败:', error)
  }
}

const loadAnalysisData = async () => {
  loading.value = true
  try {
    // 加载综合评分
    const ratingResponse = await talentApi.getTalentOverallRating(talentId)
    Object.assign(overallRating, ratingResponse.rating || {})

    // 加载雷达图数据
    const radarResponse = await talentApi.getTalentRadar(talentId, {
      type: radarType.value,
      timeRange: timeRange.value
    })
    radarData.value = radarResponse.data || []

    // 加载对比数据
    if (compareMode.value === 'team') {
      const compareResponse = await talentApi.getTeamComparison(talentId, timeRange.value)
      compareData.value = compareResponse.data || []
    } else {
      compareData.value = []
    }

    // 加载趋势数据
    await loadTrendData()

    // 加载详细分析数据
    const analysisResponse = await talentApi.getTalentAnalysis(talentId, timeRange.value)
    detailedAnalysis.value = analysisResponse.analysis || []

    // 加载改进建议
    const suggestionsResponse = await talentApi.getTalentSuggestions(talentId)
    suggestions.value = suggestionsResponse.suggestions || []
  } catch (error) {
    console.error('加载分析数据失败:', error)
    message.error('加载分析数据失败')
  } finally {
    loading.value = false
  }
}

const loadTrendData = async () => {
  try {
    const response = await talentApi.getTalentTrend(talentId, {
      dimension: trendDimension.value,
      timeRange: timeRange.value,
      compareMode: compareMode.value
    })
    trendData.value = response.data || []
  } catch (error) {
    console.error('加载趋势数据失败:', error)
    trendData.value = []
  }
}

const handleTimeRangeChange = () => {
  loadAnalysisData()
}

const handleCompareChange = () => {
  loadAnalysisData()
}

const handleTrendDimensionChange = () => {
  loadTrendData()
}

const handleExportReport = async () => {
  try {
    const response = await talentApi.exportTalentAnalysisReport(talentId, {
      timeRange: timeRange.value,
      includeCharts: true,
      includeSuggestions: true
    })

    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${talentInfo.value?.name || '人才'}_能力分析报告.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    message.success('报告导出成功')
  } catch (error) {
    console.error('导出报告失败:', error)
    message.error('导出报告失败')
  }
}

const handleQuickAssess = () => {
  // 初始化评分值
  assessmentDimensions.forEach(dim => {
    assessmentValues[dim.key] = 0
  })
  assessmentRemarks.value = ''
  showQuickAssessModal.value = true
}

const handleRatingChange = (dimension, value) => {
  assessmentValues[dimension] = value
}

const handleQuickAssessSubmit = async () => {
  // 检查是否至少有一个维度有评分
  const hasRating = Object.values(assessmentValues).some(value => value > 0)
  if (!hasRating) {
    message.warning('请至少为一个维度评分')
    return
  }

  assessing.value = true
  try {
    // 整理评分数据
    const scores = []
    let total = 0
    let count = 0

    assessmentDimensions.forEach(dim => {
      const score = assessmentValues[dim.key] || 0
      if (score > 0) {
        total += score
        count++
        scores.push({
          dimension: dim.key,
          score: score,
          label: dim.label
        })
      }
    })

    // 提交评估
    await talentApi.submitTalentAssessment(talentId, {
      scores: scores,
      averageScore: total / count,
      remarks: assessmentRemarks.value,
      timeRange: timeRange.value,
      type: 'quick'
    })

    message.success('评估提交成功')
    showQuickAssessModal.value = false

    // 重新加载数据
    loadAnalysisData()
  } catch (error) {
    console.error('提交评估失败:', error)
    message.error('提交评估失败')
  } finally {
    assessing.value = false
  }
}

const handleAddAssessment = () => {
  editMode.value = false
  Object.assign(assessmentForm, {
    id: null,
    dimension: 'technical',
    score: 0,
    remarks: '',
    evaluator: ''
  })
  showAssessmentModal.value = true
}

const editAssessment = (record) => {
  editMode.value = true
  Object.assign(assessmentForm, {
    id: record.id,
    dimension: record.dimensionKey || record.dimension,
    score: record.score,
    remarks: record.remarks || '',
    evaluator: record.evaluator || ''
  })
  showAssessmentModal.value = true
}

const viewAssessmentDetail = (record) => {
  // 查看评估详情
  message.info('查看评估详情功能开发中')
}

const deleteAssessment = async (assessmentId) => {
  try {
    await talentApi.deleteAssessment(assessmentId)
    message.success('评估删除成功')
    loadAnalysisData()
  } catch (error) {
    console.error('删除评估失败:', error)
    message.error('删除评估失败')
  }
}

const handleAssessmentSubmit = async () => {
  if (!assessmentForm.dimension || assessmentForm.score === 0) {
    message.warning('请填写完整的评估信息')
    return
  }

  submitting.value = true
  try {
    if (editMode.value) {
      await talentApi.updateAssessment(assessmentForm.id, assessmentForm)
      message.success('评估更新成功')
    } else {
      await talentApi.addAssessment(talentId, assessmentForm)
      message.success('评估添加成功')
    }

    showAssessmentModal.value = false
    loadAnalysisData()
  } catch (error) {
    console.error('保存评估失败:', error)
    message.error('保存评估失败')
  } finally {
    submitting.value = false
  }
}

const handleAssessmentCancel = () => {
  showAssessmentModal.value = false
}

const markSuggestionDone = async (suggestion) => {
  try {
    await talentApi.markSuggestionDone(suggestion.id)
    message.success('建议已标记为完成')

    // 从列表中移除
    const index = suggestions.value.findIndex(s => s.id === suggestion.id)
    if (index !== -1) {
      suggestions.value.splice(index, 1)
    }
  } catch (error) {
    console.error('标记建议失败:', error)
    message.error('标记建议失败')
  }
}

onMounted(() => {
  loadTalentInfo()
  loadAnalysisData()
})

// 监听雷达图类型变化
watch(() => radarType.value, () => {
  loadAnalysisData()
})
</script>

<style lang="less" scoped>
.talent-analysis {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;

  h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #1f1f1f;
  }

  .header-actions {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }
}

.overall-rating-card {
  .overall-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 24px;

    .rating-main {
      flex: 1;
      min-width: 300px;

      .rating-score {
        margin-bottom: 24px;

        .score-value {
          font-size: 48px;
          font-weight: 700;
          color: #1890ff;
          line-height: 1;
          margin-bottom: 8px;
        }

        .score-label {
          font-size: 16px;
          color: #666;
        }
      }

      .rating-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;

        .detail-item {
          padding: 12px;
          background: #fafafa;
          border-radius: 6px;
          border: 1px solid #f0f0f0;

          .detail-label {
            display: block;
            font-size: 14px;
            color: #666;
            margin-bottom: 4px;
          }

          .detail-value {
            font-size: 18px;
            font-weight: 600;
            color: #333;
          }
        }
      }
    }

    .rating-progress {
      text-align: center;

      .progress-label {
        margin-top: 12px;
        font-size: 14px;
        color: #666;
      }
    }
  }
}

.radar-section,
.trend-section,
.detailed-analysis,
.suggestions-section {
  .radar-card,
  .trend-card {
    .card-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .trend-controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .trend-legend {
        display: flex;
        gap: 16px;

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;

          .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 2px;
          }
        }
      }
    }

    .radar-container,
    .trend-container {
      height: 350px;
      display: flex;
      align-items: center;
      justify-content: center;

      .no-data {
        text-align: center;
        width: 100%;
      }
    }
  }
}

.detailed-analysis {
  :deep(.ant-table) {
    .dimension-cell {
      .dimension-name {
        font-weight: 500;
        color: #333;
        margin-bottom: 4px;
      }

      .dimension-desc {
        font-size: 12px;
        color: #999;
      }
    }

    .score-cell {
      display: flex;
      align-items: center;
      gap: 12px;

      .score-value {
        min-width: 40px;
        text-align: right;
        font-weight: 500;
      }
    }

    .trend-cell {
      display: flex;
      align-items: center;
      gap: 6px;

      .trend-text {
        margin: 0 4px;
      }

      .trend-value {
        font-size: 12px;
        color: #999;
      }
    }

    .analysis-actions {
      display: flex;
      gap: 4px;

      .ant-btn {
        padding: 0;
        width: 24px;
        height: 24px;
      }
    }
  }
}

.suggestions-section {
  .suggestions-card {
    .suggestions-content {
      .suggestion-title {
        display: flex;
        align-items: flex-start;
        gap: 8px;

        .suggestion-index {
          background: #1890ff;
          color: white;
          width: 20px;
          height: 20px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          flex-shrink: 0;
        }

        .suggestion-text {
          flex: 1;
        }
      }

      .suggestion-details {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 4px;
        flex-wrap: wrap;

        .dimension-tag {
          font-size: 12px;
          color: #666;
        }

        .suggestion-time {
          font-size: 12px;
          color: #999;
        }
      }

      .suggestion-actions {
        :deep(.ant-btn) {
          padding: 0;
        }
      }

      .no-suggestions {
        text-align: center;
        padding: 20px 0;
      }
    }
  }
}

.quick-assess-modal {
  .assess-items {
    .assess-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .assess-dimension {
        flex: 1;
        margin-right: 24px;

        .dimension-name {
          display: block;
          font-weight: 500;
          color: #333;
          margin-bottom: 4px;
        }

        .dimension-desc {
          font-size: 12px;
          color: #666;
          line-height: 1.4;
        }
      }

      .assess-rating {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 200px;

        .rating-value {
          min-width: 40px;
          text-align: right;
          font-weight: 500;
        }
      }
    }
  }
}

.assess-remarks {
  margin-top: 20px;
}

.slider-value {
  text-align: center;
  margin-top: 8px;
  font-weight: 500;
  color: #1890ff;
}

@media (max-width: 768px) {
  .analysis-header {
    flex-direction: column;
    align-items: stretch;

    .header-actions {
      flex-direction: column;
      align-items: stretch;

      .ant-select, .ant-btn {
        width: 100% !important;
        margin-right: 0 !important;
        margin-bottom: 8px;
      }
    }
  }

  .overall-rating-card .overall-content {
    flex-direction: column;
    text-align: center;

    .rating-details {
      grid-template-columns: 1fr;
    }
  }

  .radar-card .card-title,
  .trend-card .trend-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .quick-assess-modal .assess-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;

    .assess-rating {
      justify-content: space-between;
    }
  }

  .suggestions-content .suggestion-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>