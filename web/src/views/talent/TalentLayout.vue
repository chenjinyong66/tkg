<template>
  <div class="talent-layout">
    <!-- 公共头部 -->
    <div class="layout-header">
      <div class="header-left">
        <a-button type="text" @click="goBack" class="back-button">
          <ArrowLeftOutlined />
          <span>返回列表</span>
        </a-button>
        <div class="header-info">
          <h2 class="talent-name">{{ talentInfo?.name || '人才详情' }}</h2>
          <div class="talent-meta">
            <a-tag :color="getStatusColor(talentInfo?.status)" size="small">
              {{ getStatusLabel(talentInfo?.status) }}
            </a-tag>
            <span class="employee-id">#{{ talentInfo?.employeeId || '未分配' }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <a-button-group>
          <a-tooltip title="上传文件">
            <a-button @click="handleUpload" type="primary">
              <UploadOutlined />
              上传文件
            </a-button>
          </a-tooltip>
          <a-dropdown :trigger="['click']">
            <template #overlay>
              <a-menu>
                <a-menu-item @click="handleEditTalent">
                  <EditOutlined />
                  编辑信息
                </a-menu-item>
                <a-menu-item @click="handleExportReport">
                  <ExportOutlined />
                  导出报告
                </a-menu-item>
                <a-menu-item @click="handleShare">
                  <ShareAltOutlined />
                  分享
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item @click="handleArchive" danger>
                  <FolderOutlined />
                  归档人才
                </a-menu-item>
              </a-menu>
            </template>
            <a-button type="primary">
              <DownOutlined />
            </a-button>
          </a-dropdown>
        </a-button-group>
      </div>
    </div>

    <!-- 导航菜单 -->
    <div class="layout-nav">
      <a-menu
          v-model:selectedKeys="activeKey"
          mode="horizontal"
          @select="handleMenuSelect"
      >
        <a-menu-item key="overview">
          <UserOutlined />
          概览
        </a-menu-item>
        <a-menu-item key="files">
          <FileTextOutlined />
          资料管理
        </a-menu-item>
        <a-menu-item key="analysis">
          <BarChartOutlined />
          能力分析
        </a-menu-item>
        <a-menu-item key="knowledge">
          <ClusterOutlined />
          关系图谱
        </a-menu-item>
        <a-menu-item key="activities">
          <HistoryOutlined />
          操作记录
        </a-menu-item>

      </a-menu>
    </div>

    <!-- 主要内容区 -->
    <div class="layout-content">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" :key="route.fullPath" :talent-info="talentInfo" />
        </keep-alive>
      </router-view>
    </div>

    <!-- 全局模态框 -->
    <FileUploadModal
        v-model:open="showUploadModal"
        :talent-id="talentId"
        @upload-success="handleUploadSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  ArrowLeftOutlined, UploadOutlined, DownOutlined,
  EditOutlined, ExportOutlined, ShareAltOutlined,
  FolderOutlined, UserOutlined, FileTextOutlined,
  BarChartOutlined, ClusterOutlined, HistoryOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'
import FileUploadModal from '@/components/FileUploadModal.vue'
import { talentApi } from '@/apis/talent_api'

const router = useRouter()
const route = useRoute()
const talentId = route.params.id

// 响应式数据
const talentInfo = ref(null)
const activeKey = ref(['overview'])
const showUploadModal = ref(false)

// 加载人才信息
const loadTalentInfo = async () => {
  try {
    const response = await talentApi.getTalentDetail(talentId)
    talentInfo.value = response.talent
  } catch (error) {
    console.error('加载人才信息失败:', error)
    message.error('加载人才信息失败')
  }
}

// 菜单选择
const handleMenuSelect = ({ key }) => {
  const routes = {
    overview: `/talent/${talentId}`,
    files: `/talent/${talentId}/files`,
    analysis: `/talent/${talentId}/analysis`,
    knowledge: `/talent/${talentId}/knowledge`,
    activities: `/talent/${talentId}/activities`,
    settings: `/talent/${talentId}/settings`
  }

  if (routes[key]) {
    router.push(routes[key])
  }
}

// 返回列表
const goBack = () => {
  router.push('/talent')
}

// 处理上传
const handleUpload = () => {
  showUploadModal.value = true
}

// 上传成功回调
const handleUploadSuccess = () => {
  showUploadModal.value = false
  message.success('文件上传成功')
  // 刷新当前页面
  if (route.name === 'TalentFiles') {
    window.location.reload()
  }
}

// 编辑人才
const handleEditTalent = () => {
  router.push(`/talent/${talentId}/edit`)
}

// 导出报告
const handleExportReport = async () => {
  try {
    const response = await talentApi.exportTalentReport(talentId)
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${talentInfo.value?.name || '人才'}_报告.pdf`
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

// 分享
const handleShare = () => {
  message.info('分享功能开发中')
}

// 归档人才
const handleArchive = () => {
  message.info('归档功能开发中')
}

// 工具函数
const getStatusColor = (status) => {
  const colors = {
    active: 'green',
    probation: 'orange',
    inactive: 'red',
    leave: 'blue'
  }
  return colors[status] || 'default'
}

const getStatusLabel = (status) => {
  const labels = {
    active: '在职',
    probation: '试用期',
    inactive: '离职',
    leave: '休假'
  }
  return labels[status] || '未知'
}

// 监听路由变化
watch(() => route.path, (newPath) => {
  // 根据当前路径设置激活的菜单项
  if (newPath.includes('/files')) {
    activeKey.value = ['files']
  } else if (newPath.includes('/analysis')) {
    activeKey.value = ['analysis']
  } else if (newPath.includes('/knowledge')) {
    activeKey.value = ['knowledge']
  } else if (newPath.includes('/activities')) {
    activeKey.value = ['activities']
  } else if (newPath.includes('/settings')) {
    activeKey.value = ['settings']
  } else {
    activeKey.value = ['overview']
  }
})

onMounted(() => {
  loadTalentInfo()
})
</script>

<style lang="less" scoped>
.talent-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .back-button {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .header-info {
      .talent-name {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #1f1f1f;
      }

      .talent-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 4px;

        .employee-id {
          font-size: 12px;
          color: #666;
        }
      }
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.layout-nav {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;

  :deep(.ant-menu) {
    border: none;
  }
}

.layout-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

@media (max-width: 768px) {
  .layout-header {
    padding: 0 16px;
    flex-direction: column;
    height: auto;
    padding: 16px;

    .header-left {
      width: 100%;
      justify-content: space-between;
    }

    .header-actions {
      width: 100%;
      justify-content: flex-end;
      margin-top: 12px;
    }
  }

  .layout-nav {
    padding: 0 16px;
  }

  .layout-content {
    padding: 16px;
  }
}
</style>