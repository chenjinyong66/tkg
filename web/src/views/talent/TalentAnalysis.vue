<template>
  <div class="appointment-evaluation-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <h1>技术专家聘期考核</h1>
      <div class="header-info">
        <span class="expert-name">专家：{{ expertInfo.name }}</span>
        <span class="expert-id">工号：{{ expertInfo.employeeId }}</span>
        <span class="expert-dept">部门：{{ expertInfo.department }}</span>
        <span class="evaluation-type-tag">
          <a-tag color="blue" size="large">聘期考核</a-tag>
        </span>
      </div>
    </div>

    <!-- 聘期信息 -->
    <a-card class="appointment-info" title="聘期信息">
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">聘期开始时间：</span>
          <span class="info-value">{{ appointmentPeriod.startDate }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">聘期结束时间：</span>
          <span class="info-value">{{ appointmentPeriod.endDate }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">考核时间：</span>
          <span class="info-value">{{ evaluationTime }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">当前岗位：</span>
          <span class="info-value">{{ expertInfo.position }}</span>
        </div>
      </div>
    </a-card>

    <!-- 考核材料上传 -->
    <a-card class="upload-section" title="考核材料上传">
      <div class="upload-content">
        <div class="upload-instructions">
          <h3>上传说明</h3>
          <ul>
            <li>支持上传ZIP、RAR压缩包格式，最大支持500MB</li>
            <li>压缩包内应包含各项考核指标的证明材料</li>
            <li>文件结构建议按考核指标分类存放</li>
            <li>支持批量上传多个压缩包</li>
          </ul>
        </div>

        <div class="upload-area">
          <a-upload-dragger
              name="file"
              :multiple="true"
              :action="uploadUrl"
              :before-upload="beforeUpload"
              :file-list="uploadFiles"
              @change="handleUploadChange"
              accept=".zip,.rar,.7z"
          >
            <p class="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p class="ant-upload-text">点击或将考核材料压缩包拖拽到此处上传</p>
            <p class="ant-upload-hint">
              支持ZIP、RAR格式压缩包，单个文件不超过500MB
            </p>
          </a-upload-dragger>
        </div>

        <div class="upload-history" v-if="uploadHistory.length > 0">
          <h3>上传历史</h3>
          <a-list :data-source="uploadHistory" :loading="loading">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <div class="file-item">
                      <FileZipOutlined style="color: #1890ff; margin-right: 8px;" />
                      <span class="file-name">{{ item.fileName }}</span>
                      <a-tag size="small">{{ formatFileSize(item.fileSize) }}</a-tag>
                    </div>
                  </template>
                  <template #description>
                    <div class="file-info">
                      <span>上传时间：{{ formatTime(item.uploadTime) }}</span>
                      <span>解析状态：{{ getParseStatusText(item.parseStatus) }}</span>
                      <span class="action-buttons">
                        <a-button type="link" size="small" @click="reparseFile(item)">重新解析</a-button>
                        <a-button type="link" size="small" danger @click="deleteFile(item)">删除</a-button>
                      </span>
                    </div>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </div>
    </a-card>

    <!-- 考核指标完成情况 -->
    <a-card class="indicator-section" title="考核指标完成情况" :loading="parsing">
      <div class="indicator-header">
        <div class="indicator-filter">
          <a-select v-model:value="indicatorFilter" placeholder="筛选指标类型" style="width: 200px;">
            <a-select-option value="all">全部指标</a-select-option>
            <a-select-option value="project">科技项目</a-select-option>
            <a-select-option value="patent">专利成果</a-select-option>
            <a-select-option value="paper">学术论文</a-select-option>
            <a-select-option value="award">获奖情况</a-select-option>
            <a-select-option value="standard">技术标准</a-select-option>
            <a-select-option value="technicalSupport">技术支持</a-select-option>
            <a-select-option value="talentTraining">人才培育</a-select-option>
          </a-select>
        </div>

        <div class="completion-stats">
          <div class="stat-card">
            <div class="stat-title">完成率</div>
            <div class="stat-value" :style="{ color: getCompletionRateColor(completionRate) }">
              {{ completionRate }}%
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-title">总得分</div>
            <div class="stat-value" style="color: #1890ff;">
              {{ totalScore.toFixed(1) }}分
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-title">评价等级</div>
            <div class="stat-value">
              <a-tag :color="getCompletionLevelColor(completionLevel)" size="small">
                {{ getCompletionLevelText(completionLevel) }}
              </a-tag>
            </div>
          </div>
        </div>
      </div>

      <div class="indicator-grid">
        <div v-for="indicator in filteredIndicators" :key="indicator.id" class="indicator-card">
          <div class="indicator-header">
            <div class="indicator-title">
              <h4>{{ indicator.name }}</h4>
              <a-tag :color="getIndicatorTypeColor(indicator.type)" size="small">
                {{ getIndicatorTypeText(indicator.type) }}
              </a-tag>
            </div>
            <div class="indicator-score">
              <span class="current-score">{{ indicator.currentScore.toFixed(1) }}</span>
              <span class="target-score">/{{ indicator.targetScore }}分</span>
            </div>
          </div>

          <div class="indicator-progress">
            <a-progress
                :percent="getProgressPercent(indicator)"
                :stroke-color="getProgressColor(indicator)"
                :show-info="false"
                size="small"
            />
            <div class="progress-label">
              <span>完成度：{{ getProgressPercent(indicator) }}%</span>
              <span v-if="indicator.status === 'completed'" class="status-completed">
                <CheckCircleOutlined style="color: #52c41a; margin-right: 4px;" />
                已完成
              </span>
              <span v-else-if="indicator.status === 'partial'" class="status-partial">
                <ExclamationCircleOutlined style="color: #faad14; margin-right: 4px;" />
                部分完成
              </span>
              <span v-else class="status-not-started">
                <CloseCircleOutlined style="color: #ff4d4f; margin-right: 4px;" />
                未完成
              </span>
            </div>
          </div>

          <div class="indicator-details">
            <div class="detail-item">
              <span class="detail-label">考核要求：</span>
              <span class="detail-value">{{ indicator.requirement }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">证明材料：</span>
              <span class="detail-value">{{ indicator.evidenceCount }}个文件</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">材料说明：</span>
              <span class="detail-value">{{ indicator.evidenceDescription || '暂无说明' }}</span>
            </div>
          </div>

          <div class="indicator-actions">
            <a-button type="link" size="small" @click="viewEvidence(indicator)">
              <EyeOutlined /> 查看材料
            </a-button>
            <a-button type="link" size="small" @click="editIndicator(indicator)">
              <EditOutlined /> 编辑
            </a-button>
            <a-button type="link" size="small" @click="addEvidence(indicator)">
              <PlusOutlined /> 补充材料
            </a-button>
          </div>
        </div>
      </div>
    </a-card>

    <!-- 考核总结报告 -->
    <a-card class="report-section" title="聘期考核总结报告">
      <div class="report-content">
        <div class="report-summary">
          <h3>聘期工作总结</h3>
          <a-textarea
              v-model:value="evaluationSummary"
              placeholder="请输入聘期工作总结，包括主要工作内容、取得的成绩、存在的问题等"
              :rows="6"
              show-count
              :maxlength="2000"
          />
        </div>

        <div class="report-suggestions">
          <h3>改进建议</h3>
          <a-textarea
              v-model:value="improvementSuggestionsText"
              placeholder="请输入改进建议"
              :rows="4"
              show-count
              :maxlength="1000"
          />
        </div>

        <div class="expert-self-evaluation">
          <h3>专家自评</h3>
          <div class="self-evaluation-grid">
            <div class="evaluation-item">
              <span class="evaluation-label">工作态度：</span>
              <a-rate v-model:value="selfEvaluation.attitude" allow-half />
            </div>
            <div class="evaluation-item">
              <span class="evaluation-label">工作能力：</span>
              <a-rate v-model:value="selfEvaluation.ability" allow-half />
            </div>
            <div class="evaluation-item">
              <span class="evaluation-label">工作业绩：</span>
              <a-rate v-model:value="selfEvaluation.performance" allow-half />
            </div>
            <div class="evaluation-item">
              <span class="evaluation-label">团队合作：</span>
              <a-rate v-model:value="selfEvaluation.teamwork" allow-half />
            </div>
          </div>
        </div>

        <div class="report-actions">
          <a-button type="primary" @click="generateReport" :loading="generatingReport">
            <FilePdfOutlined /> 生成PDF报告
          </a-button>
          <a-button @click="exportExcel">
            <FileExcelOutlined /> 导出Excel
          </a-button>
          <a-button @click="printReport">
            <PrinterOutlined /> 打印报告
          </a-button>
          <a-button type="primary" danger @click="submitEvaluation" :loading="submitting">
            <SendOutlined /> 提交考核结果
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 查看材料模态框 -->
    <a-modal
        v-model:open="showEvidenceModal"
        :title="currentEvidence?.name || '查看材料'"
        width="90%"
        :footer="null"
        @cancel="closeEvidenceModal"
    >
      <div class="evidence-viewer">
        <div v-if="currentEvidence" class="evidence-content">
          <div v-if="currentEvidence.type === 'pdf'" class="pdf-viewer">
            <iframe
                :src="currentEvidence.url"
                width="100%"
                height="600px"
                frameborder="0"
            ></iframe>
          </div>
          <div v-else-if="['jpg', 'jpeg', 'png', 'gif'].includes(currentEvidence.type)" class="image-viewer">
            <img :src="currentEvidence.url" alt="证明材料" style="max-width: 100%;" />
          </div>
          <div v-else-if="['doc', 'docx', 'xls', 'xlsx'].includes(currentEvidence.type)" class="office-viewer">
            <p class="office-tip">文档预览需要下载后查看</p>
            <a-button type="primary" @click="downloadFile(currentEvidence)">
              <DownloadOutlined /> 下载文档
            </a-button>
          </div>
          <div v-else class="file-viewer">
            <FileUnknownOutlined style="font-size: 48px; color: #999; margin-bottom: 16px;" />
            <p>该文件格式不支持在线预览</p>
            <a-button type="primary" @click="downloadFile(currentEvidence)">
              <DownloadOutlined /> 下载文件
            </a-button>
          </div>
        </div>
        <div v-else class="no-evidence">
          <a-empty description="暂无材料可预览" />
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  InboxOutlined, FileZipOutlined, CheckCircleOutlined,
  ExclamationCircleOutlined, CloseCircleOutlined, EyeOutlined,
  EditOutlined, PlusOutlined, FilePdfOutlined, FileExcelOutlined,
  PrinterOutlined, SendOutlined, DownloadOutlined, FileUnknownOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'

// 状态
const loading = ref(false)
const parsing = ref(false)
const generatingReport = ref(false)
const submitting = ref(false)
const showEvidenceModal = ref(false)

// 专家信息
const expertInfo = reactive({
  name: '张三',
  employeeId: 'YNGD2023001',
  department: '电力科学研究院',
  position: '高级工程师'
})

// 聘期信息
const appointmentPeriod = reactive({
  startDate: '2023-01-01',
  endDate: '2025-12-31'
})
const evaluationTime = ref(dayjs().format('YYYY-MM-DD'))

// 上传相关
const uploadFiles = ref([])
const uploadHistory = ref([])
const uploadUrl = '/api/upload'

// 考核指标
const indicators = ref([])
const indicatorFilter = ref('all')

// 总结报告
const evaluationSummary = ref('')
const improvementSuggestionsText = ref('')
const selfEvaluation = reactive({
  attitude: 0,
  ability: 0,
  performance: 0,
  teamwork: 0
})

// 当前查看的证据
const currentEvidence = ref(null)

// 计算属性
const filteredIndicators = computed(() => {
  if (indicatorFilter.value === 'all') return indicators.value
  return indicators.value.filter(ind => ind.type === indicatorFilter.value)
})

const completionRate = computed(() => {
  if (indicators.value.length === 0) return 0
  const completed = indicators.value.filter(ind => ind.status === 'completed').length
  return Math.round((completed / indicators.value.length) * 100)
})

const totalScore = computed(() => {
  return indicators.value.reduce((sum, ind) => sum + ind.currentScore, 0)
})

const completionLevel = computed(() => {
  const rate = completionRate.value
  if (rate >= 90) return 'excellent'
  if (rate >= 70) return 'good'
  if (rate >= 60) return 'qualified'
  return 'unqualified'
})

// 工具函数
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const getParseStatusText = (status) => {
  const statusMap = {
    'pending': '等待解析',
    'parsing': '解析中',
    'success': '解析成功',
    'failed': '解析失败'
  }
  return statusMap[status] || status
}

const getIndicatorTypeText = (type) => {
  const typeMap = {
    'project': '科技项目',
    'patent': '专利成果',
    'paper': '学术论文',
    'award': '获奖情况',
    'standard': '技术标准',
    'technicalSupport': '技术支持',
    'talentTraining': '人才培育'
  }
  return typeMap[type] || type
}

const getIndicatorTypeColor = (type) => {
  const colorMap = {
    'project': 'blue',
    'patent': 'green',
    'paper': 'purple',
    'award': 'red',
    'standard': 'orange',
    'technicalSupport': 'cyan',
    'talentTraining': 'gold'
  }
  return colorMap[type] || 'default'
}

const getProgressPercent = (indicator) => {
  return Math.round((indicator.currentScore / indicator.targetScore) * 100)
}

const getProgressColor = (indicator) => {
  const percent = getProgressPercent(indicator)
  if (percent >= 100) return '#52c41a'
  if (percent >= 60) return '#faad14'
  return '#ff4d4f'
}

const getCompletionLevelText = (level) => {
  const levelMap = {
    'excellent': '优秀',
    'good': '良好',
    'qualified': '合格',
    'unqualified': '不合格'
  }
  return levelMap[level] || level
}

const getCompletionLevelColor = (level) => {
  const colorMap = {
    'excellent': 'success',
    'good': 'processing',
    'qualified': 'warning',
    'unqualified': 'error'
  }
  return colorMap[level] || 'default'
}

const getCompletionRateColor = (rate) => {
  if (rate >= 90) return '#52c41a'
  if (rate >= 70) return '#faad14'
  return '#ff4d4f'
}

// 业务函数
const beforeUpload = (file) => {
  const isArchive = file.type === 'application/zip' || file.type === 'application/x-rar-compressed' ||
      file.name.endsWith('.zip') || file.name.endsWith('.rar')
  if (!isArchive) {
    message.error('只能上传ZIP或RAR格式的压缩包!')
    return false
  }

  const isLt500M = file.size / 1024 / 1024 < 500
  if (!isLt500M) {
    message.error('压缩包大小不能超过500MB!')
    return false
  }

  return true
}

const handleUploadChange = (info) => {
  const { status } = info.file

  if (status === 'uploading') {
    parsing.value = true
  }

  if (status === 'done') {
    parsing.value = false
    message.success(`${info.file.name} 上传成功`)

    // 添加到上传历史
    uploadHistory.value.unshift({
      id: Date.now(),
      fileName: info.file.name,
      fileSize: info.file.size,
      uploadTime: new Date(),
      parseStatus: 'success'
    })

    // 解析考核指标
    parseIndicators()
  } else if (status === 'error') {
    parsing.value = false
    message.error(`${info.file.name} 上传失败`)
  }
}

const parseIndicators = () => {
  // 模拟解析考核指标
  indicators.value = [
    {
      id: 1,
      name: '完成国家科技重大专项',
      type: 'project',
      currentScore: 8.5,
      targetScore: 10,
      status: 'completed',
      requirement: '作为负责人或主要完成人参与国家科技重大专项项目',
      evidenceCount: 3,
      evidenceDescription: '项目立项文件、结题报告、验收证书'
    },
    {
      id: 2,
      name: '获得发明专利授权',
      type: 'patent',
      currentScore: 6,
      targetScore: 8,
      status: 'partial',
      requirement: '获得国内发明专利授权不少于3项',
      evidenceCount: 2,
      evidenceDescription: '专利授权证书、专利检索报告'
    },
    {
      id: 3,
      name: '发表SCI论文',
      type: 'paper',
      currentScore: 4,
      targetScore: 6,
      status: 'partial',
      requirement: '以第一作者或通讯作者发表SCI论文2篇',
      evidenceCount: 1,
      evidenceDescription: '论文PDF、检索证明'
    },
    {
      id: 4,
      name: '制定技术标准',
      type: 'standard',
      currentScore: 3,
      targetScore: 5,
      status: 'partial',
      requirement: '主持或主要参与制定行业及以上技术标准',
      evidenceCount: 1,
      evidenceDescription: '标准发布文件、编制说明'
    },
    {
      id: 5,
      name: '技术支持与创新',
      type: 'technicalSupport',
      currentScore: 7,
      targetScore: 8,
      status: 'completed',
      requirement: '解决重大技术难题，提供创新性解决方案',
      evidenceCount: 4,
      evidenceDescription: '技术方案、实施报告、效益分析'
    },
    {
      id: 6,
      name: '人才培育',
      type: 'talentTraining',
      currentScore: 9,
      targetScore: 10,
      status: 'completed',
      requirement: '培养青年技术人才，形成技术传承梯队',
      evidenceCount: 5,
      evidenceDescription: '培养计划、考核记录、成果报告'
    }
  ]
}

const viewEvidence = (item) => {
  currentEvidence.value = {
    name: item.name,
    type: 'pdf',
    url: '/sample.pdf'
  }
  showEvidenceModal.value = true
}

const editIndicator = (indicator) => {
  message.info(`编辑指标：${indicator.name}`)
}

const addEvidence = (indicator) => {
  message.info(`为 ${indicator.name} 添加补充材料`)
}

const reparseFile = (file) => {
  message.info('重新解析文件')
}

const deleteFile = (file) => {
  const index = uploadHistory.value.findIndex(f => f.id === file.id)
  if (index !== -1) {
    uploadHistory.value.splice(index, 1)
    message.success('文件删除成功')
  }
}

const closeEvidenceModal = () => {
  showEvidenceModal.value = false
  currentEvidence.value = null
}

const downloadFile = (file) => {
  message.info('开始下载文件')
}

const generateReport = async () => {
  generatingReport.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    message.success('PDF报告生成成功')
  } catch (error) {
    message.error('报告生成失败')
  } finally {
    generatingReport.value = false
  }
}

const exportExcel = () => {
  message.success('Excel导出成功')
}

const printReport = () => {
  window.print()
}

const submitEvaluation = async () => {
  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    message.success('考核结果提交成功')
  } catch (error) {
    message.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(() => {
  parseIndicators()
})
</script>

<style lang="less" scoped>
.appointment-evaluation-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  h1 {
    margin: 0 0 16px 0;
    color: #1f1f1f;
    font-size: 28px;
  }

  .header-info {
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;

    .expert-name {
      font-size: 18px;
      font-weight: 500;
      color: #333;
    }

    .expert-id,
    .expert-dept {
      color: #666;
    }
  }
}

.appointment-info {
  margin-bottom: 24px;

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;

    .info-item {
      .info-label {
        color: #666;
        font-size: 14px;
      }

      .info-value {
        color: #333;
        font-weight: 500;
        margin-left: 8px;
      }
    }
  }
}

.upload-section {
  margin-bottom: 24px;

  .upload-content {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .upload-instructions {
    background: #f6ffed;
    border: 1px solid #b7eb8f;
    border-radius: 4px;
    padding: 16px;

    h3 {
      margin: 0 0 12px 0;
      color: #389e0d;
    }

    ul {
      margin: 0;
      padding-left: 20px;

      li {
        margin-bottom: 8px;
        color: #666;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }

  .upload-area {
    :deep(.ant-upload-drag) {
      padding: 40px 24px;
    }
  }

  .upload-history {
    .file-item {
      display: flex;
      align-items: center;

      .file-name {
        margin-right: 8px;
        font-weight: 500;
      }
    }

    .file-info {
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 12px;
      color: #999;

      .action-buttons {
        margin-left: auto;
      }
    }
  }
}

.indicator-section {
  margin-bottom: 24px;

  .indicator-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;

    .completion-stats {
      display: flex;
      align-items: center;
      gap: 16px;

      .stat-card {
        background: white;
        border: 1px solid #f0f0f0;
        border-radius: 8px;
        padding: 16px;
        min-width: 120px;
        text-align: center;

        .stat-title {
          color: #666;
          font-size: 14px;
          margin-bottom: 8px;
        }

        .stat-value {
          font-size: 20px;
          font-weight: 600;
        }
      }
    }
  }

  .indicator-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 16px;
    margin-bottom: 24px;

    .indicator-card {
      background: white;
      border: 1px solid #f0f0f0;
      border-radius: 8px;
      padding: 16px;
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }

      .indicator-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;

        .indicator-title {
          h4 {
            margin: 0 0 8px 0;
            color: #333;
            font-size: 16px;
          }
        }

        .indicator-score {
          text-align: right;

          .current-score {
            font-size: 24px;
            font-weight: 700;
            color: #1890ff;
          }

          .target-score {
            font-size: 14px;
            color: #999;
          }
        }
      }

      .indicator-progress {
        margin-bottom: 16px;

        .progress-label {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 8px;
          font-size: 12px;
          color: #666;

          .status-completed {
            color: #52c41a;
          }

          .status-partial {
            color: #faad14;
          }

          .status-not-started {
            color: #ff4d4f;
          }
        }
      }

      .indicator-details {
        margin-bottom: 16px;

        .detail-item {
          display: flex;
          margin-bottom: 8px;
          font-size: 12px;

          &:last-child {
            margin-bottom: 0;
          }

          .detail-label {
            color: #999;
            min-width: 80px;
          }

          .detail-value {
            color: #666;
            flex: 1;
          }
        }
      }

      .indicator-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;

        :deep(.ant-btn) {
          padding: 0;
          height: auto;
        }
      }
    }
  }
}

.report-section {
  .report-content {
    > * {
      margin-bottom: 24px;
    }

    .report-summary,
    .report-suggestions {
      h3 {
        margin: 0 0 16px 0;
        color: #333;
      }
    }

    .expert-self-evaluation {
      h3 {
        margin: 0 0 16px 0;
        color: #333;
      }

      .self-evaluation-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;

        .evaluation-item {
          display: flex;
          align-items: center;
          gap: 8px;

          .evaluation-label {
            color: #666;
            min-width: 80px;
          }
        }
      }
    }

    .report-actions {
      display: flex;
      justify-content: center;
      gap: 16px;
      padding-top: 24px;
      border-top: 1px solid #e8e8e8;
    }
  }
}

.evidence-viewer {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;

  .office-tip {
    text-align: center;
    color: #666;
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px;

    h1 {
      font-size: 24px;
    }

    .header-info {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }

  .indicator-header {
    flex-direction: column;
    align-items: flex-start !important;
  }

  .indicator-grid {
    grid-template-columns: 1fr !important;
  }

  .completion-stats {
    width: 100%;
    justify-content: space-between;
    flex-wrap: wrap;

    .stat-card {
      min-width: calc(50% - 8px) !important;
    }
  }

  .report-actions {
    flex-direction: column;

    .ant-btn {
      width: 100%;
    }
  }
}
</style>