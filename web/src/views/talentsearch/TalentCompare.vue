<template>
  <div class="talent-comparison-container layout-container">
    <!-- 顶部导航 -->
    <HeaderComponent title="人才对比分析">
      <template #actions>
        <div class="compare-actions">
          <a-button @click="router.back()" class="yn-grid-btn-secondary">
            <ArrowLeftOutlined />
            返回搜索
          </a-button>

          <a-button @click="addMoreTalent" style="margin-left: 12px;" class="yn-grid-btn-secondary">
            <PlusOutlined />
            添加对比人员
          </a-button>

          <a-dropdown>
            <template #overlay>
              <a-menu @click="handleCompareActions" class="yn-grid-dropdown-menu">
                <a-menu-item key="export" class="menu-item">
                  <ExportOutlined style="color: #0066b3;" />
                  <span style="color: #333;">导出对比结果</span>
                </a-menu-item>
                <a-menu-item key="save" class="menu-item">
                  <SaveOutlined style="color: #0066b3;" />
                  <span style="color: #333;">保存对比方案</span>
                </a-menu-item>
                <a-menu-divider style="border-color: #e6f0ff" />
                <a-menu-item key="clear" danger class="menu-item">
                  <DeleteOutlined />
                  清空对比列表
                </a-menu-item>
              </a-menu>
            </template>
            <a-button type="primary" class="yn-grid-btn-primary">
              <SettingOutlined />
              对比设置
            </a-button>
          </a-dropdown>
        </div>
      </template>
    </HeaderComponent>

    <!-- 对比人员区域 -->
    <div class="compare-participants yn-grid-card">
      <div class="participants-header">
        <h3 style="color: #0066b3;">对比人员 ({{ participants.length }}/5)</h3>
        <a-button
            type="link"
            @click="addMoreTalent"
            :disabled="participants.length >= 5"
            class="add-participant-link"
        >
          <PlusOutlined />
          添加人员
        </a-button>
      </div>

      <div class="participants-list">
        <div
            v-for="talent in participants"
            :key="talent.id"
            class="participant-card"
            :style="getParticipantCardStyle(talent)"
        >
          <div class="participant-avatar">
            {{ talent.name?.charAt(0) || '?' }}
          </div>
          <div class="participant-info">
            <div class="participant-name" style="color: #0066b3;">{{ talent.name }}</div>
            <div class="participant-position">{{ talent.position }}</div>
            <div class="participant-department">{{ talent.department }}</div>
          </div>
          <a-button
              type="text"
              size="small"
              @click="removeParticipant(talent.id)"
              class="remove-btn"
          >
            <CloseOutlined />
          </a-button>
        </div>

        <!-- 添加人员卡片 -->
        <div
            v-if="participants.length < 5"
            class="add-participant-card"
            @click="addMoreTalent"
        >
          <PlusOutlined style="font-size: 24px; color: #0066b3; opacity: 0.6;" />
          <div class="add-text" style="color: #0066b3;">添加人员</div>
        </div>
      </div>
    </div>

    <!-- 对比维度选择 -->
    <div class="compare-dimensions yn-grid-card">
      <div class="dimensions-header">
        <h3 style="color: #0066b3;">对比维度</h3>
        <a-switch
            v-model:checked="showAllDimensions"
            checked-children="显示全部"
            un-checked-children="常用维度"
            size="small"
            class="yn-grid-switch"
        />
      </div>

      <div class="dimensions-list">
        <a-checkbox-group
            v-model:value="selectedDimensions"
            :options="dimensionOptions"
            class="dimensions-checkbox-group"
        />
      </div>
    </div>

    <!-- 对比表格 -->
    <div class="compare-table-container yn-grid-card">
      <div class="table-wrapper" ref="tableWrapper">
        <table class="compare-table">
          <thead>
          <tr>
            <th class="dimension-col" style="background: #f8fafc; color: #0066b3;">对比维度</th>
            <th
                v-for="talent in participants"
                :key="talent.id"
                class="talent-col"
                :style="getTalentHeaderStyle(talent)"
            >
              <div class="talent-header">
                <div class="talent-avatar">
                  {{ talent.name?.charAt(0) || '?' }}
                </div>
                <div class="talent-info">
                  <div class="talent-name" style="color: #0066b3;">{{ talent.name }}</div>
                  <div class="talent-position">{{ talent.position }}</div>
                </div>
              </div>
            </th>
          </tr>
          </thead>
          <tbody>
          <!-- 基本信息 -->
          <tr class="dimension-group" v-if="showDimension('basic')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <TeamOutlined style="margin-right: 8px;" />
              基本信息
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">年龄</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ talent.age || '未设置' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">性别</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ talent.gender === 'male' ? '男' : '女' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">学历</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ getEducationLabel(talent.education) }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">司龄</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ talent.companyTenure || 0 }}年</span>
            </td>
          </tr>

          <!-- 工作信息 -->
          <tr class="dimension-group" v-if="showDimension('work')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <BriefcaseOutlined style="margin-right: 8px;" />
              工作信息
            </td>
          </tr>
          <tr v-if="showDimension('work')">
            <td class="dimension-name">职位级别</td>
            <td v-for="talent in participants" :key="talent.id">
              <a-tag :color="getLevelColor(talent.level)" size="small" class="yn-grid-tag">
                {{ getLevelLabel(talent.level) }}
              </a-tag>
            </td>
          </tr>
          <tr v-if="showDimension('work')">
            <td class="dimension-name">薪资范围</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ talent.salaryRange || '未设置' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('work')">
            <td class="dimension-name">工作地点</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ talent.location || '未设置' }}</span>
            </td>
          </tr>

          <!-- 绩效信息 -->
          <tr class="dimension-group" v-if="showDimension('performance')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <RiseOutlined style="margin-right: 8px;" />
              绩效信息
            </td>
          </tr>
          <tr v-if="showDimension('performance')">
            <td class="dimension-name">最近绩效</td>
            <td v-for="talent in participants" :key="talent.id">
              <a-progress
                  :percent="getPerformancePercent(talent.performance)"
                  :stroke-color="getPerformanceColor(talent.performance)"
                  size="small"
                  :show-info="false"
                  class="yn-grid-progress"
              />
              <span class="performance-value">{{ talent.performance || '未评估' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('performance')">
            <td class="dimension-name">平均绩效</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ talent.avgPerformance || '未评估' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('performance')">
            <td class="dimension-name">晋升次数</td>
            <td v-for="talent in participants" :key="talent.id">
              <span class="compare-value">{{ talent.promotionCount || 0 }}次</span>
            </td>
          </tr>

          <!-- 能力评估 -->
          <tr class="dimension-group" v-if="showDimension('capability')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <BulbOutlined style="margin-right: 8px;" />
              能力评估
            </td>
          </tr>
          <tr v-if="showDimension('capability')">
            <td class="dimension-name">专业技能</td>
            <td v-for="talent in participants" :key="talent.id">
              <div class="skills-cell">
                <a-tag
                    v-for="skill in (talent.skills || []).slice(0, 2)"
                    :key="skill"
                    size="small"
                    class="yn-grid-tag skill-tag"
                >
                  {{ skill }}
                </a-tag>
                <span v-if="talent.skills && talent.skills.length > 2" class="more-skills">
                    +{{ talent.skills.length - 2 }}
                  </span>
              </div>
            </td>
          </tr>
          <tr v-if="showDimension('capability')">
            <td class="dimension-name">领导能力</td>
            <td v-for="talent in participants" :key="talent.id">
              <a-rate :value="talent.leadership || 0" disabled class="yn-grid-rate" />
            </td>
          </tr>
          <tr v-if="showDimension('capability')">
            <td class="dimension-name">沟通能力</td>
            <td v-for="talent in participants" :key="talent.id">
              <a-rate :value="talent.communication || 0" disabled class="yn-grid-rate" />
            </td>
          </tr>

          <!-- 人才画像 -->
          <tr class="dimension-group" v-if="showDimension('profile')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <UserOutlined style="margin-right: 8px;" />
              人才画像
            </td>
          </tr>
          <tr v-if="showDimension('profile')">
            <td class="dimension-name">人才标签</td>
            <td v-for="talent in participants" :key="talent.id">
              <div class="tags-cell">
                <a-tag
                    v-for="tag in (talent.profileTags || []).slice(0, 3)"
                    :key="tag"
                    color="#0066b3"
                    size="small"
                    class="yn-grid-tag profile-tag"
                >
                  {{ tag }}
                </a-tag>
              </div>
            </td>
          </tr>
          <tr v-if="showDimension('profile')">
            <td class="dimension-name">发展潜力</td>
            <td v-for="talent in participants" :key="talent.id">
              <a-progress
                  :percent="talent.potential || 0"
                  size="small"
                  :stroke-color="getPotentialColor(talent.potential || 0)"
                  class="yn-grid-progress"
              />
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 对比分析结果 -->
    <div class="analysis-results yn-grid-card" v-if="participants.length >= 2">
      <div class="analysis-header">
        <h3 style="color: #0066b3;">对比分析结果</h3>
      </div>

      <div class="analysis-content">
        <!-- 雷达图 -->
        <div class="radar-chart-section">
          <h4 style="color: #0066b3;">能力雷达图对比</h4>
          <div id="radarChart" style="width: 100%; height: 400px;"></div>
        </div>

        <!-- 综合评分 -->
        <div class="score-summary">
          <h4 style="color: #0066b3;">综合评分对比</h4>
          <div class="score-bars">
            <div
                v-for="talent in participants"
                :key="talent.id"
                class="score-bar-item"
            >
              <div class="score-bar-label">
                <div class="talent-name" style="color: #0066b3;">{{ talent.name }}</div>
                <div class="score-value" style="color: #0066b3;">{{ calculateTotalScore(talent) }}/100</div>
              </div>
              <a-progress
                  :percent="calculateTotalScore(talent)"
                  :stroke-color="getScoreColor(calculateTotalScore(talent))"
                  class="yn-grid-progress"
              />
            </div>
          </div>
        </div>

        <!-- 推荐建议 -->
        <div class="recommendations">
          <h4 style="color: #0066b3;">推荐建议</h4>
          <div class="recommendation-list">
            <a-card
                v-for="(recommendation, index) in recommendations"
                :key="index"
                class="recommendation-card yn-grid-card"
                :style="{ borderLeft: `4px solid ${recommendation.color}` }"
            >
              <template #title>
                <div style="display: flex; align-items: center; gap: 8px">
                  <StarOutlined :style="{ color: recommendation.color }" />
                  <span style="color: #333;">{{ recommendation.title }}</span>
                </div>
              </template>
              <p style="color: #666;">{{ recommendation.content }}</p>
              <div class="recommended-talents">
                <span style="margin-right: 8px; color: #999;">推荐人员:</span>
                <a-tag
                    v-for="talentId in recommendation.talentIds"
                    :key="talentId"
                    color="#0066b3"
                    class="yn-grid-tag"
                >
                  {{ getTalentById(talentId)?.name }}
                </a-tag>
              </div>
            </a-card>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加人员模态框 -->
    <a-modal
        v-model:open="showAddModal"
        title="添加对比人员"
        width="800px"
        :footer="null"
        class="yn-grid-modal"
    >
      <talent-search-list
          :excluded-ids="participants.map(p => p.id)"
          @select="handleSelectTalent"
      />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { useComparisonStore } from '@/stores/comparison'
import * as echarts from 'echarts'
import {
  ArrowLeftOutlined,
  PlusOutlined,
  SettingOutlined,
  ExportOutlined,
  SaveOutlined,
  DeleteOutlined,
  CloseOutlined,
  StarOutlined,
  TeamOutlined,
  BriefcaseOutlined,
  RiseOutlined,
  BulbOutlined,
  UserOutlined
} from '@ant-design/icons-vue'
import HeaderComponent from '@/components/HeaderComponent.vue'
import TalentSearchList from '@/components/TalentSearchList.vue'

const router = useRouter()
const comparisonStore = useComparisonStore()

const participants = computed(() => comparisonStore.comparisonList)
const showAllDimensions = ref(false)
const showAddModal = ref(false)

const selectedDimensions = ref([
  'basic', 'work', 'performance', 'capability', 'profile'
])

const dimensionOptions = [
  { label: '基本信息', value: 'basic' },
  { label: '工作信息', value: 'work' },
  { label: '绩效信息', value: 'performance' },
  { label: '能力评估', value: 'capability' },
  { label: '人才画像', value: 'profile' },
  { label: '项目经验', value: 'project', disabled: true },
  { label: '培训经历', value: 'training', disabled: true },
  { label: '考勤数据', value: 'attendance', disabled: true }
]

const recommendations = ref([
  {
    title: '最适合晋升人选',
    content: '综合绩效表现优异，具备较强的领导潜力和专业技能',
    talentIds: [],
    color: '#0066b3'
  },
  {
    title: '最佳项目负责人',
    content: '项目管理能力突出，沟通协调能力强，适合负责跨部门项目',
    talentIds: [],
    color: '#0088cc'
  },
  {
    title: '重点培养对象',
    content: '发展潜力大，学习能力强，建议纳入重点培养计划',
    talentIds: [],
    color: '#66a3ff'
  }
])

const getParticipantCardStyle = (talent) => {
  const colors = [
    'linear-gradient(135deg, #e6f0ff, #f0f5ff)',
    'linear-gradient(135deg, #e6f7ff, #f0f5ff)',
    'linear-gradient(135deg, #f0f5ff, #e6f0ff)',
    'linear-gradient(135deg, #f0f5ff, #e6f7ff)',
    'linear-gradient(135deg, #e6f0ff, #e6f7ff)'
  ]

  const index = participants.value.findIndex(p => p.id === talent.id) % colors.length
  return {
    background: colors[index],
    border: '1px solid #b3d1ff'
  }
}

const getTalentHeaderStyle = (talent) => {
  const colors = [
    'linear-gradient(135deg, #e6f0ff, #f0f5ff)',
    'linear-gradient(135deg, #e6f7ff, #f0f5ff)',
    'linear-gradient(135deg, #f0f5ff, #e6f0ff)',
    'linear-gradient(135deg, #f0f5ff, #e6f7ff)',
    'linear-gradient(135deg, #e6f0ff, #e6f7ff)'
  ]

  const index = participants.value.findIndex(p => p.id === talent.id) % colors.length
  return {
    background: colors[index]
  }
}

const showDimension = (dimension) => {
  return selectedDimensions.value.includes(dimension) &&
      (showAllDimensions.value || !dimensionOptions.find(d => d.value === dimension)?.disabled)
}

const getEducationLabel = (value) => {
  const education = {
    college: '大专',
    bachelor: '本科',
    master: '硕士',
    doctor: '博士'
  }
  return education[value] || '未设置'
}

const getLevelLabel = (level) => {
  const labels = {
    junior: '初级',
    intermediate: '中级',
    senior: '高级',
    expert: '专家'
  }
  return labels[level] || '未设置'
}

const getLevelColor = (level) => {
  const colors = {
    junior: '#66a3ff',
    intermediate: '#0088cc',
    senior: '#0066b3',
    expert: '#004d99'
  }
  return colors[level] || '#e6f0ff'
}

const getPerformancePercent = (performance) => {
  const values = {
    'A': 95,
    'B': 80,
    'C': 65,
    'D': 50
  }
  return values[performance] || 0
}

const getPerformanceColor = (performance) => {
  const colors = {
    'A': '#0066b3',
    'B': '#0088cc',
    'C': '#66a3ff',
    'D': '#99c2ff'
  }
  return colors[performance] || '#e6f0ff'
}

const getPotentialColor = (percent) => {
  if (percent >= 80) return '#0066b3'
  if (percent >= 60) return '#0088cc'
  if (percent >= 40) return '#66a3ff'
  return '#99c2ff'
}

const getScoreColor = (score) => {
  if (score >= 85) return '#0066b3'
  if (score >= 70) return '#0088cc'
  if (score >= 60) return '#66a3ff'
  return '#99c2ff'
}

const calculateTotalScore = (talent) => {
  let score = 0
  let factors = 0

  // 绩效评分
  if (talent.performance) {
    score += getPerformancePercent(talent.performance)
    factors++
  }

  // 能力评分
  if (talent.leadership) {
    score += talent.leadership * 20
    factors++
  }

  if (talent.communication) {
    score += talent.communication * 20
    factors++
  }

  // 潜力评分
  if (talent.potential) {
    score += talent.potential
    factors++
  }

  return factors > 0 ? Math.round(score / factors) : 0
}

const getTalentById = (id) => {
  return participants.value.find(t => t.id === id)
}

const removeParticipant = (talentId) => {
  comparisonStore.removeFromComparison(talentId)
  message.success('已移除对比人员')
}

const addMoreTalent = () => {
  if (participants.value.length >= 5) {
    message.warning('对比列表最多支持5位人才')
    return
  }
  showAddModal.value = true
}

const handleSelectTalent = (talent) => {
  if (participants.value.length >= 5) {
    message.warning('对比列表最多支持5位人才')
    return
  }

  if (participants.value.find(p => p.id === talent.id)) {
    message.warning('该人才已在对比列表中')
    return
  }

  comparisonStore.addToComparison(talent)
  message.success('已添加到对比列表')
  showAddModal.value = false
}

const handleCompareActions = ({ key }) => {
  switch (key) {
    case 'export':
      exportComparison()
      break
    case 'save':
      saveComparison()
      break
    case 'clear':
      clearComparison()
      break
  }
}

const exportComparison = () => {
  message.info('导出功能开发中')
}

const saveComparison = () => {
  message.info('保存对比方案功能开发中')
}

const clearComparison = () => {
  Modal.confirm({
    title: '清空对比列表',
    content: '确定要清空所有对比人员吗？',
    okText: '清空',
    okType: 'danger',
    cancelText: '取消',
    onOk() {
      comparisonStore.clearComparison()
      message.success('对比列表已清空')
      router.back()
    }
  })
}

// 初始化雷达图
let radarChart = null
const initRadarChart = () => {
  if (participants.value.length < 2) return

  const chartDom = document.getElementById('radarChart')
  if (!chartDom) return

  radarChart = echarts.init(chartDom)

  const indicator = [
    { name: '专业技能', max: 5 },
    { name: '领导能力', max: 5 },
    { name: '沟通能力', max: 5 },
    { name: '学习能力', max: 5 },
    { name: '创新能力', max: 5 },
    { name: '团队协作', max: 5 }
  ]

  const seriesData = participants.value.map(talent => ({
    name: talent.name,
    value: [
      talent.technicalSkill || Math.random() * 5,
      talent.leadership || Math.random() * 5,
      talent.communication || Math.random() * 5,
      talent.learningAbility || Math.random() * 5,
      talent.innovation || Math.random() * 5,
      talent.teamwork || Math.random() * 5
    ],
    itemStyle: {
      color: getRadarColor(participants.value.indexOf(talent))
    }
  }))

  const option = {
    title: {
      text: '能力维度对比',
      left: 'center',
      textStyle: {
        color: '#0066b3',
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      data: participants.value.map(t => t.name),
      bottom: 10,
      textStyle: {
        color: '#333'
      }
    },
    radar: {
      indicator: indicator,
      center: ['50%', '50%'],
      radius: '65%',
      shape: 'polygon',
      splitNumber: 4,
      axisLine: {
        lineStyle: {
          color: '#e6f0ff'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e6f0ff'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(0,102,179,0.05)', 'rgba(0,102,179,0.02)']
        }
      },
      name: {
        textStyle: {
          color: '#333'
        }
      }
    },
    series: [{
      type: 'radar',
      data: seriesData,
      emphasis: {
        lineStyle: {
          width: 4
        },
        areaStyle: {
          opacity: 0.5
        }
      },
      areaStyle: {
        opacity: 0.3
      },
      lineStyle: {
        width: 2
      }
    }]
  }

  radarChart.setOption(option)

  // 自动生成推荐建议
  generateRecommendations()
}

const getRadarColor = (index) => {
  const colors = [
    '#0066b3', '#0088cc', '#66a3ff', '#99c2ff', '#004d99'
  ]
  return colors[index] || colors[0]
}

const generateRecommendations = () => {
  if (participants.value.length < 2) return

  // 计算综合评分
  const scoredTalents = participants.value.map(talent => ({
    ...talent,
    totalScore: calculateTotalScore(talent)
  })).sort((a, b) => b.totalScore - a.totalScore)

  // 更新推荐建议
  recommendations.value[0].talentIds = [scoredTalents[0].id]
  recommendations.value[1].talentIds = scoredTalents
      .filter(t => t.leadership >= 4)
      .slice(0, 2)
      .map(t => t.id)
  recommendations.value[2].talentIds = scoredTalents
      .filter(t => t.potential >= 70 && t.age < 35)
      .slice(0, 2)
      .map(t => t.id)
}

// 监听参与者变化
watch(participants, () => {
  if (participants.value.length >= 2) {
    setTimeout(initRadarChart, 100)
  }
}, { deep: true })

onMounted(() => {
  if (participants.value.length >= 2) {
    initRadarChart()
  }
})

onUnmounted(() => {
  if (radarChart) {
    radarChart.dispose()
  }
})
</script>

<style lang="less" scoped>
.talent-comparison-container {
  padding: 0;
  background: #f8fafc;
}

.compare-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.yn-grid-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e6f0ff;
  box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 102, 179, 0.1);
  }
}

.compare-participants {
  padding: 20px;
  margin: 20px;

  .participants-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 18px;
    }

    .add-participant-link {
      color: #0066b3;

      &:hover {
        color: #0088cc;
      }

      &:disabled {
        color: #999;
        cursor: not-allowed;
      }
    }
  }

  .participants-list {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;

    .participant-card {
      display: flex;
      align-items: center;
      padding: 12px;
      border-radius: 8px;
      width: 220px;
      position: relative;
      transition: all 0.3s;

      .participant-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0066b3, #0088cc);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 16px;
        font-weight: 600;
        margin-right: 12px;
      }

      .participant-info {
        flex: 1;

        .participant-name {
          font-weight: 600;
          font-size: 14px;
          margin-bottom: 2px;
        }

        .participant-position,
        .participant-department {
          font-size: 12px;
          color: #666;
          line-height: 1.2;
        }
      }

      .remove-btn {
        position: absolute;
        top: 4px;
        right: 4px;
        opacity: 0.5;
        color: #999;

        &:hover {
          opacity: 1;
          color: #ff4d4f;
        }
      }

      &:hover {
        box-shadow: 0 2px 8px rgba(0, 102, 179, 0.15);
        transform: translateY(-2px);
      }
    }

    .add-participant-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      background: #f8fafc;
      border: 2px dashed #e6f0ff;
      border-radius: 8px;
      width: 220px;
      cursor: pointer;
      transition: all 0.3s;

      .add-text {
        margin-top: 8px;
        font-size: 14px;
      }

      &:hover {
        border-color: #0066b3;
        background: #e6f0ff;

        .add-text {
          color: #0066b3;
        }
      }
    }
  }
}

.compare-dimensions {
  padding: 20px;
  margin: 0 20px 20px;

  .dimensions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 18px;
    }
  }

  .dimensions-checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;

    :deep(.ant-checkbox-wrapper) {
      margin: 0;
      color: #333;

      &:hover {
        .ant-checkbox-inner {
          border-color: #0066b3;
        }
      }
    }

    :deep(.ant-checkbox-checked .ant-checkbox-inner) {
      background: #0066b3;
      border-color: #0066b3;
    }

    :deep(.ant-checkbox-disabled) {
      .ant-checkbox-inner {
        background: #f5f5f5;
        border-color: #d9d9d9;
      }

      & + span {
        color: #999;
      }
    }
  }
}

.yn-grid-switch {
  :deep(.ant-switch-checked) {
    background: #0066b3;
  }
}

.compare-table-container {
  padding: 20px;
  margin: 0 20px 20px;
  overflow-x: auto;

  .table-wrapper {
    min-width: 800px;
  }

  .compare-table {
    width: 100%;
    border-collapse: collapse;

    th, td {
      padding: 12px 16px;
      text-align: center;
      border-bottom: 1px solid #e6f0ff;
    }

    th {
      font-weight: 600;
      position: sticky;
      top: 0;
      z-index: 1;

      &.dimension-col {
        width: 200px;
        min-width: 200px;
        text-align: left;
      }

      &.talent-col {
        min-width: 180px;
      }

      .talent-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;

        .talent-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: linear-gradient(135deg, #0066b3, #0088cc);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 16px;
          font-weight: 600;
        }

        .talent-info {
          .talent-name {
            font-weight: 600;
            font-size: 14px;
          }

          .talent-position {
            font-size: 12px;
            color: #666;
          }
        }
      }
    }

    td {
      &.dimension-name {
        font-weight: 500;
        background: #f8fafc;
        text-align: left;
        color: #333;
      }
    }

    .dimension-group {
      .group-header {
        font-weight: 600;
        text-align: left;
        padding-left: 16px;
        font-size: 14px;
      }
    }

    .compare-value {
      font-weight: 500;
      color: #333;
    }

    .skills-cell {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: center;

      .more-skills {
        font-size: 12px;
        color: #999;
        align-self: center;
      }
    }

    .tags-cell {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: center;
    }

    .performance-value {
      margin-left: 8px;
      font-weight: 500;
      min-width: 30px;
      display: inline-block;
      color: #333;
    }
  }
}

.yn-grid-rate {
  :deep(.ant-rate-star) {
    color: #e6f0ff;

    &.ant-rate-star-full {
      color: #0066b3;
    }
  }
}

.analysis-results {
  padding: 20px;
  margin: 0 20px 20px;

  .analysis-header {
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
    }
  }

  .analysis-content {
    > div {
      margin-bottom: 30px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
    }

    .score-summary {
      .score-bars {
        .score-bar-item {
          margin-bottom: 16px;

          &:last-child {
            margin-bottom: 0;
          }

          .score-bar-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;

            .talent-name {
              font-weight: 500;
            }

            .score-value {
              font-weight: 600;
            }
          }
        }
      }
    }

    .recommendations {
      .recommendation-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;

        .recommendation-card {
          :deep(.ant-card-head-title) {
            font-size: 14px;
          }

          .recommended-talents {
            margin-top: 12px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .compare-participants,
  .compare-dimensions,
  .compare-table-container,
  .analysis-results {
    margin: 10px;
    padding: 16px;
  }

  .participants-list {
    justify-content: center;

    .participant-card,
    .add-participant-card {
      width: calc(50% - 8px);
    }
  }

  .dimensions-checkbox-group {
    grid-template-columns: 1fr !important;
  }

  .recommendation-list {
    grid-template-columns: 1fr !important;
  }
}
</style>