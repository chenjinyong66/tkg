<template>
  <div class="talent-activities">
    <!-- 页面标题 -->
    <div class="activities-header">
      <h2>操作记录</h2>
      <div class="header-actions">
        <a-range-picker
            v-model:value="dateRange"
            :ranges="ranges"
            :placeholder="['开始日期', '结束日期']"
            @change="handleDateChange"
            style="width: 250px; margin-right: 8px;"
        />
        <a-select
            v-model:value="activityType"
            placeholder="操作类型"
            style="width: 120px; margin-right: 8px;"
            allow-clear
            @change="handleFilter"
        >
          <a-select-option value="all">全部类型</a-select-option>
          <a-select-option value="upload">文件上传</a-select-option>
          <a-select-option value="parse">文件解析</a-select-option>
          <a-select-option value="edit">信息编辑</a-select-option>
          <a-select-option value="delete">删除操作</a-select-option>
          <a-select-option value="system">系统操作</a-select-option>
        </a-select>
        <a-select
            v-model:value="operator"
            placeholder="操作人"
            style="width: 120px; margin-right: 8px;"
            allow-clear
            show-search
            option-filter-prop="label"
            @change="handleFilter"
        >
          <a-select-option value="all">全部人员</a-select-option>
          <a-select-option
              v-for="op in operators"
              :key="op.id"
              :value="op.id"
              :label="op.name"
          >
            {{ op.name }}
          </a-select-option>
        </a-select>
        <a-button @click="handleExportLogs">
          <ExportOutlined />
          导出日志
        </a-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <a-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7ff;">
            <HistoryOutlined style="color: #1890ff; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ activityStats.total || 0 }}</div>
            <div class="stat-label">操作总数</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #f6ffed;">
            <UploadOutlined style="color: #52c41a; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ activityStats.upload || 0 }}</div>
            <div class="stat-label">文件上传</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6;">
            <CodeOutlined style="color: #fa8c16; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ activityStats.parse || 0 }}</div>
            <div class="stat-label">文件解析</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #f9f0ff;">
            <EditOutlined style="color: #722ed1; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ activityStats.edit || 0 }}</div>
            <div class="stat-label">信息编辑</div>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 操作时间线 -->
    <a-card class="timeline-card">
      <template #title>
        <div class="card-title">
          <span>操作时间线</span>
          <a-radio-group v-model:value="timelineView" size="small">
            <a-radio-button value="timeline">时间线</a-radio-button>
            <a-radio-button value="list">列表</a-radio-button>
          </a-radio-group>
        </div>
      </template>

      <!-- 时间线视图 -->
      <div v-if="timelineView === 'timeline' && filteredActivities.length > 0" class="timeline-container">
        <a-timeline mode="alternate">
          <a-timeline-item
              v-for="activity in filteredActivities"
              :key="activity.id"
              :color="getActivityColor(activity.type)"
              :dot="getActivityDot(activity.type)"
          >
            <div class="timeline-item">
              <div class="timeline-header">
                <div class="activity-type">
                  <a-tag :color="getActivityColor(activity.type)" size="small">
                    {{ getActivityTypeLabel(activity.type) }}
                  </a-tag>
                </div>
                <div class="activity-time">
                  {{ formatDateTime(activity.time) }}
                </div>
              </div>
              <div class="timeline-content">
                <div class="activity-title">
                  {{ activity.title }}
                </div>
                <div class="activity-description" v-if="activity.description">
                  {{ activity.description }}
                </div>
                <div class="activity-details" v-if="activity.details">
                  <div class="details-item" v-for="(value, key) in activity.details" :key="key">
                    <span class="detail-label">{{ getDetailLabel(key) }}：</span>
                    <span class="detail-value">{{ value }}</span>
                  </div>
                </div>
                <div class="activity-operator">
                  <UserOutlined />
                  <span>{{ activity.operator?.name || '系统' }}</span>
                  <span class="operator-role" v-if="activity.operator?.role">
                    ({{ activity.operator.role }})
                  </span>
                </div>
                <div class="activity-actions" v-if="activity.canRevert">
                  <a-button type="link" size="small" @click="handleRevert(activity)">
                    <RollbackOutlined />
                    撤销
                  </a-button>
                </div>
              </div>
            </div>
          </a-timeline-item>
        </a-timeline>
      </div>

      <!-- 列表视图 -->
      <div v-else-if="timelineView === 'list' && filteredActivities.length > 0" class="list-container">
        <a-list
            :data-source="filteredActivities"
            :loading="loading"
            item-layout="horizontal"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta>
                <template #title>
                  <div class="list-item-title">
                    <div class="activity-type">
                      <a-tag :color="getActivityColor(item.type)" size="small">
                        {{ getActivityTypeLabel(item.type) }}
                      </a-tag>
                    </div>
                    <div class="activity-title">
                      {{ item.title }}
                    </div>
                  </div>
                </template>
                <template #description>
                  <div class="list-item-description">
                    <div class="activity-description" v-if="item.description">
                      {{ item.description }}
                    </div>
                    <div class="activity-time">
                      <ClockCircleOutlined />
                      {{ formatDateTime(item.time) }}
                    </div>
                    <div class="activity-operator">
                      <UserOutlined />
                      {{ item.operator?.name || '系统' }}
                    </div>
                    <div class="activity-actions" v-if="item.canRevert">
                      <a-button type="link" size="small" @click="handleRevert(item)">
                        <RollbackOutlined />
                        撤销
                      </a-button>
                    </div>
                  </div>
                </template>
              </a-list-item-meta>
            </a-list-item>
          </template>
        </a-list>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-activities">
        <Empty description="暂无操作记录" />
      </div>
    </a-card>

    <!-- 分页 -->
    <div class="pagination-container" v-if="filteredActivities.length > 0">
      <a-pagination
          v-model:current="currentPage"
          v-model:pageSize="pageSize"
          :total="totalActivities"
          show-size-changer
          show-quick-jumper
          @change="handlePageChange"
          @showSizeChange="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  HistoryOutlined, UploadOutlined, CodeOutlined,
  EditOutlined, ExportOutlined, UserOutlined,
  ClockCircleOutlined, RollbackOutlined,
  FileAddOutlined, DeleteOutlined, SettingOutlined,
  CheckCircleOutlined, CloseCircleOutlined, WarningOutlined
} from '@ant-design/icons-vue'
import { Empty } from 'ant-design-vue'
import { talentApi } from '@/apis/talent_api'
import dayjs from 'dayjs'

const route = useRoute()
const talentId = route.params.id

// 响应式数据
const dateRange = ref([])
const activityType = ref('all')
const operator = ref('all')
const timelineView = ref('timeline')
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// 数据
const activities = ref([])
const operators = ref([])
const activityStats = reactive({
  total: 0,
  upload: 0,
  parse: 0,
  edit: 0
})

// 时间范围选项
const ranges = {
  '今天': [dayjs(), dayjs()],
  '本周': [dayjs().startOf('week'), dayjs().endOf('week')],
  '本月': [dayjs().startOf('month'), dayjs().endOf('month')],
  '最近30天': [dayjs().subtract(29, 'days'), dayjs()],
  '最近90天': [dayjs().subtract(89, 'days'), dayjs()]
}

// 计算属性
const totalActivities = computed(() => activities.value.length)

const filteredActivities = computed(() => {
  let filtered = activities.value

  // 时间范围过滤
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = dateRange.value[0]
    const endDate = dateRange.value[1]
    filtered = filtered.filter(activity => {
      const activityDate = dayjs(activity.time)
      return activityDate.isAfter(startDate) && activityDate.isBefore(endDate)
    })
  }

  // 操作类型过滤
  if (activityType.value && activityType.value !== 'all') {
    filtered = filtered.filter(activity => activity.type === activityType.value)
  }

  // 操作人过滤
  if (operator.value && operator.value !== 'all') {
    filtered = filtered.filter(activity => activity.operator?.id === operator.value)
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

// 工具函数
const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

const getActivityColor = (type) => {
  const colors = {
    upload: 'green',
    parse: 'blue',
    edit: 'orange',
    delete: 'red',
    system: 'purple',
    complete: 'success'
  }
  return colors[type] || 'default'
}

const getActivityDot = (type) => {
  const dots = {
    upload: UploadOutlined,
    parse: CodeOutlined,
    edit: EditOutlined,
    delete: DeleteOutlined,
    system: SettingOutlined,
    complete: CheckCircleOutlined
  }
  const Component = dots[type]
  return Component ? h(Component) : null
}

const getActivityTypeLabel = (type) => {
  const labels = {
    upload: '文件上传',
    parse: '文件解析',
    edit: '信息编辑',
    delete: '删除操作',
    system: '系统操作',
    complete: '操作完成'
  }
  return labels[type] || type
}

const getDetailLabel = (key) => {
  const labels = {
    filename: '文件名',
    fileSize: '文件大小',
    fileType: '文件类型',
    oldValue: '旧值',
    newValue: '新值',
    reason: '原因'
  }
  return labels[key] || key
}

// 业务函数
const loadActivities = async () => {
  loading.value = true
  try {
    const response = await talentApi.getTalentActivities(talentId)
    activities.value = response.activities || []
    operators.value = response.operators || []

    // 计算统计
    calculateStats()
  } catch (error) {
    console.error('加载操作记录失败:', error)
    message.error('加载操作记录失败')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const stats = {
    total: activities.value.length,
    upload: 0,
    parse: 0,
    edit: 0
  }

  activities.value.forEach(activity => {
    switch (activity.type) {
      case 'upload':
        stats.upload++
        break
      case 'parse':
        stats.parse++
        break
      case 'edit':
        stats.edit++
        break
    }
  })

  Object.assign(activityStats, stats)
}

const handleDateChange = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleExportLogs = async () => {
  try {
    const response = await talentApi.exportActivityLogs(talentId, {
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1],
      type: activityType.value !== 'all' ? activityType.value : null,
      operator: operator.value !== 'all' ? operator.value : null
    })

    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `操作记录_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    message.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    message.error('导出失败')
  }
}

const handleRevert = (activity) => {
  Modal.confirm({
    title: '确认撤销操作',
    content: '确定要撤销这个操作吗？这可能会影响相关数据。',
    okText: '撤销',
    cancelText: '取消',
    onOk: async () => {
      try {
        await talentApi.revertActivity(activity.id)
        message.success('操作已撤销')
        loadActivities()
      } catch (error) {
        console.error('撤销操作失败:', error)
        message.error('撤销操作失败')
      }
    }
  })
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const handleSizeChange = (current, size) => {
  currentPage.value = 1
  pageSize.value = size
}

onMounted(() => {
  loadActivities()
})
</script>

<style lang="less" scoped>
.talent-activities {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.activities-header {
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;

  .stat-card {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .stat-info {
        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: #1f1f1f;
          line-height: 1.2;
        }

        .stat-label {
          font-size: 14px;
          color: #666;
          margin-top: 4px;
        }
      }
    }

    &:hover {
      transform: translateY(-2px);
      transition: transform 0.3s;
    }
  }
}

.timeline-card {
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .timeline-container {
    padding: 24px 0;

    :deep(.ant-timeline) {
      .ant-timeline-item {
        padding-bottom: 40px;
      }

      .ant-timeline-item-tail {
        left: 50%;
      }

      .ant-timeline-item-head {
        left: 50%;
        margin-left: -4px;
      }

      .ant-timeline-item-content {
        left: calc(50% - 4px);
        width: calc(50% - 25px);
        margin: 0;
        text-align: left;
      }

      .ant-timeline-item:nth-child(even) .ant-timeline-item-content {
        left: 25px;
        text-align: right;
      }
    }

    .timeline-item {
      .timeline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .activity-time {
          font-size: 12px;
          color: #999;
        }
      }

      .timeline-content {
        padding: 16px;
        background: #fafafa;
        border-radius: 6px;
        border: 1px solid #f0f0f0;

        .activity-title {
          font-weight: 500;
          color: #333;
          margin-bottom: 8px;
          line-height: 1.4;
        }

        .activity-description {
          font-size: 14px;
          color: #666;
          margin-bottom: 12px;
          line-height: 1.5;
        }

        .activity-details {
          padding: 8px;
          background: #fff;
          border-radius: 4px;
          margin-bottom: 12px;
          border: 1px solid #f0f0f0;

          .details-item {
            display: flex;
            margin-bottom: 4px;
            font-size: 13px;

            &:last-child {
              margin-bottom: 0;
            }

            .detail-label {
              color: #666;
              min-width: 60px;
            }

            .detail-value {
              color: #333;
              flex: 1;
              word-break: break-word;
            }
          }
        }

        .activity-operator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          color: #666;
          margin-bottom: 8px;

          .operator-role {
            color: #999;
          }
        }

        .activity-actions {
          display: flex;
          justify-content: flex-end;
        }
      }
    }
  }

  .list-container {
    .list-item-title {
      display: flex;
      align-items: center;
      gap: 12px;

      .activity-title {
        flex: 1;
        font-weight: 500;
        color: #333;
      }
    }

    .list-item-description {
      display: grid;
      grid-template-columns: auto auto 1fr auto;
      gap: 16px;
      align-items: center;
      margin-top: 8px;

      .activity-description {
        grid-column: 1 / span 4;
        color: #666;
        font-size: 14px;
      }

      .activity-time, .activity-operator {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #999;
      }
    }
  }

  .empty-activities {
    text-align: center;
    padding: 40px 0;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

@media (max-width: 768px) {
  .activities-header {
    flex-direction: column;
    align-items: stretch;

    .header-actions {
      flex-direction: column;
      align-items: stretch;

      .ant-picker, .ant-select, .ant-btn {
        width: 100% !important;
        margin-right: 0 !important;
        margin-bottom: 8px;
      }
    }
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .timeline-container :deep(.ant-timeline) {
    .ant-timeline-item {
      flex-direction: column;
    }

    .ant-timeline-item-content {
      left: 25px !important;
      width: calc(100% - 50px) !important;
      text-align: left !important;
      margin-top: 8px;
    }
  }

  .list-container .list-item-description {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>