<template>
  <div class="knowledge-base-file-extractor">
    <a-card title="文件内容提取" :bordered="false">
      <!-- 文件上传区域 -->
      <div class="upload-section">
        <a-upload-dragger
          :multiple="true"
          :before-upload="beforeUpload"
          @change="handleFileUpload"
          :action="uploadUrl"
          :headers="authHeaders"
          :showUploadList="true"
        >
          <p class="ant-upload-drag-icon">
            <inbox-outlined />
          </p>
          <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p class="ant-upload-hint">
            支持PDF、图片、文档等格式文件，ZIP文件上传后会自动解压并处理其中的文件
          </p>
        </a-upload-dragger>
      </div>

      <!-- 文件列表和处理状态 -->
      <div v-if="uploadedFiles.length > 0" class="files-section">
        <h3>文件列表</h3>
        <a-table 
          :dataSource="uploadedFiles" 
          :columns="fileColumns" 
          :pagination="{ pageSize: 10 }"
          :scroll="{ x: 'max-content' }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'actions'">
              <a-space>
                <a-button 
                  type="link" 
                  @click="previewFile(record)" 
                  size="small"
                  :disabled="!record.processed"
                >
                  预览
                </a-button>
                <a-button 
                  type="link" 
                  @click="downloadFile(record)" 
                  size="small"
                >
                  下载
                </a-button>
                <a-button 
                  v-if="!record.processed || record.processing" 
                  type="primary" 
                  size="small"
                  @click="extractContent(record)"
                  :loading="record.processing"
                >
                  提取内容
                </a-button>
                <a-button 
                  v-else
                  type="default" 
                  size="small"
                  @click="showContent(record)"
                >
                  查看内容
                </a-button>
              </a-space>
            </template>
            <template v-else-if="column.dataIndex === 'filename'">
              <ellipsis-tooltip :text="record.filename" :maxWidth="200" />
            </template>
            <template v-else-if="column.dataIndex === 'fileSize'">
              {{ formatFileSize(record.fileSize) }}
            </template>
            <template v-else-if="column.dataIndex === 'status'">
              <a-tag v-if="record.processing" color="orange">处理中</a-tag>
              <a-tag v-else-if="record.processed && !record.processing_error" color="green">已处理</a-tag>
              <a-tag v-else-if="record.processing_error" color="red">处理失败</a-tag>
              <a-tag v-else color="blue">待处理</a-tag>
            </template>
            <template v-else-if="column.dataIndex === 'uploadTime'">
              {{ formatTime(record.uploadTime) }}
            </template>
          </template>
        </a-table>
      </div>
    </a-card>

    <!-- 内容预览模态框 -->
    <a-modal
      v-model:visible="contentViewer.visible"
      :title="`文件内容: ${contentViewer.file?.filename}`"
      width="80%"
      :footer="null"
      @cancel="contentViewer.visible = false"
    >
      <div v-if="contentViewer.loading" class="loading-container">
        <a-spin tip="加载中..." />
      </div>
      <div v-else class="content-preview-container">
        <a-row :gutter="16" style="height: 70vh;">
          <a-col :span="12" class="file-original-panel">
            <div class="panel-header">
              <h3>原始文件</h3>
              <a-button type="link" @click="downloadOriginalFile">
                <download-outlined /> 下载原文件
              </a-button>
            </div>
            <div class="file-preview-container">
              <iframe 
                v-if="isPdfFile(contentViewer.file)" 
                :src="contentViewer.file?.file_url" 
                class="file-preview-frame"
              ></iframe>
              <img 
                v-else-if="isImageFile(contentViewer.file)" 
                :src="contentViewer.file?.file_url" 
                class="file-preview-image"
              />
              <div v-else class="file-preview-other">
                <a-result 
                  status="info" 
                  :title="getFileTypeName(contentViewer.file)"
                  :sub-title="`文件名: ${contentViewer.file?.filename}`"
                >
                  <template #extra>
                    <a-button type="primary" @click="downloadOriginalFile">
                      <download-outlined /> 下载文件
                    </a-button>
                  </template>
                </a-result>
              </div>
            </div>
          </a-col>
          <a-col :span="12" class="file-content-panel">
            <div class="panel-header">
              <h3>提取内容</h3>
              <a-button type="link" @click="downloadProcessedContent">
                <download-outlined /> 下载Markdown
              </a-button>
            </div>
            <div class="content-display-container">
              <md-editor
                v-model="contentViewer.content"
                previewOnly
                theme="light"
                style="height: 100%;"
              />
            </div>
          </a-col>
        </a-row>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  InboxOutlined, 
  DownloadOutlined
} from '@ant-design/icons-vue'
import axios from 'axios'
import MdEditor from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

// Props
const props = defineProps({
  databaseId: {
    type: String,
    required: true
  }
})

// 状态管理
const uploadedFiles = ref([])
const contentViewer = ref({
  visible: false,
  loading: false,
  file: null,
  content: ''
})

// 计算属性
const uploadUrl = computed(() => {
  return `/api/knowledge-new-updated/databases/${props.databaseId}/files/upload-and-extract`
})

const authHeaders = computed(() => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

// 表格列定义
const fileColumns = [
  {
    title: '文件名',
    dataIndex: 'filename',
    key: 'filename',
    width: 250
  },
  {
    title: '大小',
    dataIndex: 'fileSize',
    key: 'fileSize',
    width: 100
  },
  {
    title: '类型',
    dataIndex: 'contentType',
    key: 'contentType',
    width: 150
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 120
  },
  {
    title: '上传时间',
    dataIndex: 'uploadTime',
    key: 'uploadTime',
    width: 180
  },
  {
    title: '操作',
    dataIndex: 'actions',
    key: 'actions',
    fixed: 'right',
    width: 200
  }
]

// 工具函数
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN')
  } catch (e) {
    return timeStr
  }
}

const isPdfFile = (file) => {
  return file?.filename?.toLowerCase().endsWith('.pdf') || file?.content_type === 'application/pdf'
}

const isImageFile = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
  return imageTypes.includes(file?.content_type) || 
         file?.filename?.match(/\.(jpg|jpeg|png|gif|bmp|webp)$/i)
}

const getFileTypeName = (file) => {
  const contentType = file?.content_type
  const fileName = file?.filename || ''
  
  if (contentType === 'application/pdf' || fileName.toLowerCase().endsWith('.pdf')) {
    return 'PDF文档'
  } else if (contentType?.startsWith('image/') || fileName.match(/\.(jpg|jpeg|png|gif|bmp|webp)$/i)) {
    return '图片文件'
  } else if (contentType === 'application/msword' || fileName.toLowerCase().endsWith('.doc')) {
    return 'Word文档'
  } else if (contentType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
             fileName.toLowerCase().endsWith('.docx')) {
    return 'Word文档'
  } else if (fileName.toLowerCase().endsWith('.txt')) {
    return '文本文件'
  } else if (fileName.toLowerCase().endsWith('.md')) {
    return 'Markdown文件'
  }
  return '文件'
}

// 上传前检查
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('文件大小不能超过10MB!')
    return false
  }
  return true
}

// 处理文件上传
const handleFileUpload = async (info) => {
  const file = info.file
  
  if (file.status === 'done') {
    try {
      // 重新加载文件列表
      await loadUploadedFiles()
      message.success(`${file.name} 上传并处理成功`)
    } catch (error) {
      message.error(`${file.name} 上传信息获取失败: ${error.message}`)
    }
  } else if (file.status === 'error') {
    message.error(`${file.name} 上传失败`)
  }
}

// 加载已上传文件
const loadUploadedFiles = async () => {
  try {
    const response = await axios.get(`/api/knowledge-new-updated/databases/${props.databaseId}/files`)
    uploadedFiles.value = response.data.files.map(file => ({
      ...file,
      key: file.content_hash,
      fileSize: file.file_size,
      contentType: file.content_type,
      uploadTime: file.upload_time,
      processed: file.processed,
      processing: file.processing || false,
      processingError: file.processing_error
    }))
  } catch (error) {
    message.error('获取文件列表失败: ' + error.message)
  }
}

// 预览文件
const previewFile = (record) => {
  window.open(record.file_url, '_blank')
}

// 下载文件
const downloadFile = (record) => {
  const link = document.createElement('a')
  link.href = record.file_url
  link.download = record.filename
  link.click()
}

// 提取文件内容
const extractContent = async (record) => {
  if (record.processing) return
  
  // 更新状态为处理中
  record.processing = true
  
  try {
    const response = await axios.post(
      `/api/knowledge-new-updated/databases/${props.databaseId}/files/${record.content_hash}/extract-content`,
      { force_reprocess: true }
    )
    
    message.success('内容提取完成')
    
    // 更新文件状态
    const index = uploadedFiles.value.findIndex(f => f.content_hash === record.content_hash)
    if (index !== -1) {
      uploadedFiles.value[index] = {
        ...uploadedFiles.value[index],
        ...response.data.file_info,
        processing: false,
        processed: true,
        processingError: null
      }
    }
  } catch (error) {
    message.error('内容提取失败: ' + error.message)
    
    // 更新处理状态
    const index = uploadedFiles.value.findIndex(f => f.content_hash === record.content_hash)
    if (index !== -1) {
      uploadedFiles.value[index].processing = false
      uploadedFiles.value[index].processingError = error.message
    }
  }
}

// 显示内容
const showContent = async (record) => {
  try {
    contentViewer.value.loading = true
    contentViewer.value.visible = true
    contentViewer.value.file = record
    
    // 获取处理后的内容
    const contentResponse = await axios.get(
      `/api/knowledge-new-updated/databases/${props.databaseId}/files/${record.content_hash}/processed-content`
    )
    
    contentViewer.value.content = contentResponse.data.content
  } catch (error) {
    message.error('获取处理后内容失败: ' + error.message)
    contentViewer.value.visible = false
  } finally {
    contentViewer.value.loading = false
  }
}

// 下载原文件
const downloadOriginalFile = () => {
  const link = document.createElement('a')
  link.href = contentViewer.value.file.file_url
  link.download = contentViewer.value.file.filename
  link.click()
}

// 下载处理后的内容
const downloadProcessedContent = () => {
  const content = contentViewer.value.content
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = contentViewer.value.file.filename.replace(/\.[^/.]+$/, "") + '_processed.md'
  link.click()
  URL.revokeObjectURL(url)
}

// 组件挂载时加载文件列表
onMounted(() => {
  loadUploadedFiles()
})

// EllipsisTooltip 组件
const EllipsisTooltip = {
  props: {
    text: String,
    maxWidth: {
      type: Number,
      default: 200
    }
  },
  template: `
    <a-tooltip :title="text">
      <div 
        :style="{ maxWidth: maxWidth + 'px' }" 
        class="ellipsis-text"
        :title="text"
      >
        {{ text }}
      </div>
    </a-tooltip>
  `
}
</script>

<style scoped>
.knowledge-base-file-extractor {
  padding: 20px;
}

.upload-section {
  margin-bottom: 30px;
}

.files-section h3 {
  margin-bottom: 16px;
}

.loading-container {
  text-align: center;
  padding: 40px 0;
}

.content-preview-container {
  height: 100%;
}

.file-original-panel, .file-content-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 10px;
}

.panel-header h3 {
  margin: 0;
}

.file-preview-container, .content-display-container {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-preview-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.file-preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.file-preview-other {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ellipsis-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>