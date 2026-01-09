<template>
  <div class="knowledge-base-file-manager">
    <a-card title="文件管理" :bordered="false">
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
            支持PDF、图片、ZIP等格式文件，ZIP文件上传后会自动展开显示其中的文件
          </p>
        </a-upload-dragger>
      </div>

      <!-- 已上传文件列表 -->
      <div v-if="uploadedFiles.length > 0" class="files-section">
        <h3>已上传文件</h3>
        <a-table 
          :dataSource="flattenedFiles" 
          :columns="fileColumns" 
          :pagination="{ pageSize: 10 }"
          :scroll="{ x: 'max-content' }"
          :expandedRowKeys="expandedRowKeys"
          @expand="handleExpand"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'actions'">
              <a-space>
                <a-button 
                  v-if="!record.isChild" 
                  type="link" 
                  @click="previewFile(record)" 
                  size="small"
                >
                  预览
                </a-button>
                <a-button 
                  v-if="!record.isChild" 
                  type="link" 
                  @click="downloadFile(record)" 
                  size="small"
                >
                  下载
                </a-button>
                <a-button 
                  v-if="canProcess(record) && !record.isChild" 
                  type="primary" 
                  size="small"
                  @click="processFile(record)"
                  :loading="record.processing"
                  :disabled="record.processed"
                >
                  {{ record.processed ? '已处理' : '内容识别' }}
                </a-button>
                <a-button 
                  v-if="record.processed && !record.isChild" 
                  type="default" 
                  size="small"
                  @click="showComparison(record)"
                >
                  对比查看
                </a-button>
              </a-space>
            </template>
            <template v-else-if="column.dataIndex === 'filename'">
              <div :style="{ paddingLeft: record.level * 20 + 'px' }">
                <folder-open-outlined v-if="record.isZip && record.expanded" />
                <folder-outlined v-else-if="record.isZip && !record.expanded" />
                <file-outlined v-else-if="record.isChild" />
                <ellipsis-tooltip :text="record.filename" :maxWidth="200" />
              </div>
            </template>
            <template v-else-if="column.dataIndex === 'fileSize'">
              {{ formatFileSize(record.fileSize) }}
            </template>
            <template v-else-if="column.dataIndex === 'uploadTime'">
              {{ formatTime(record.uploadTime) }}
            </template>
          </template>
          
          <!-- 展开行 -->
          <template #expandedRowRender="{ record }">
            <div v-if="record.isZip" style="padding: 16px 0;">
              <a-spin v-if="record.childrenLoading" tip="加载中..." />
              <div v-else>
                <a-alert 
                  :message="`ZIP包 '${record.original_name}' 包含 ${record.extractedFiles?.length || 0} 个文件`" 
                  type="info" 
                  style="margin-bottom: 16px;"
                />
                <a-table 
                  :dataSource="record.extractedFiles || []"
                  :columns="childFileColumns"
                  :pagination="false"
                  size="small"
                >
                  <template #bodyCell="{ column, record: childRecord }">
                    <template v-if="column.dataIndex === 'fileSize'">
                      {{ formatFileSize(childRecord.fileSize) }}
                    </template>
                    <template v-else-if="column.dataIndex === 'actions'">
                      <a-button type="link" size="small" @click="previewChildFile(childRecord)">
                        预览
                      </a-button>
                    </template>
                  </template>
                </a-table>
              </div>
            </div>
          </template>
        </a-table>
      </div>
    </a-card>

    <!-- ZIP内容浏览模态框 -->
    <a-modal
      v-model:visible="zipViewer.visible"
      title="ZIP文件内容"
      width="700px"
      @cancel="zipViewer.visible = false"
    >
      <div v-if="zipViewer.loading" class="loading-container">
        <a-spin tip="加载中..." />
      </div>
      <div v-else>
        <a-alert 
          :message="`原始文件: ${zipViewer.fileInfo?.original_name}`" 
          type="info" 
          style="margin-bottom: 16px;"
        />
        <a-table 
          :dataSource="zipViewer.files" 
          :columns="zipColumns" 
          :pagination="{ pageSize: 8 }"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'size'">
              {{ formatFileSize(record.size) }}
            </template>
            <template v-else-if="column.dataIndex === 'compressedSize'">
              {{ formatFileSize(record.compressed_size) }}
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>

    <!-- 内容对比模态框 -->
    <a-modal
      v-model:visible="comparisonViewer.visible"
      title="内容识别对比"
      width="90%"
      :footer="null"
      @cancel="comparisonViewer.visible = false"
    >
      <div v-if="comparisonViewer.loading" class="loading-container">
        <a-spin tip="加载中..." />
      </div>
      <div v-else class="comparison-container">
        <a-row :gutter="16" style="height: 70vh;">
          <a-col :span="12" class="comparison-panel">
            <div class="panel-header">
              <h3>原始文件</h3>
              <a-button type="link" @click="downloadOriginalFile">
                <download-outlined /> 下载原文件
              </a-button>
            </div>
            <div class="file-preview-container">
              <iframe 
                v-if="isPdfFile(comparisonViewer.originalFile)" 
                :src="comparisonViewer.originalFile.url" 
                class="file-preview-frame"
              ></iframe>
              <img 
                v-else-if="isImageFile(comparisonViewer.originalFile)" 
                :src="comparisonViewer.originalFile.url" 
                class="file-preview-image"
              />
              <div v-else class="file-preview-other">
                <a-result 
                  status="info" 
                  :title="getFileTypeName(comparisonViewer.originalFile)"
                  :sub-title="`文件名: ${comparisonViewer.originalFile.name}`"
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
          <a-col :span="12" class="comparison-panel">
            <div class="panel-header">
              <h3>识别后内容</h3>
              <a-button type="link" @click="downloadProcessedFile">
                <download-outlined /> 下载Markdown
              </a-button>
            </div>
            <div class="markdown-preview-container">
              <md-editor
                v-model="comparisonViewer.processedContent"
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
  DownloadOutlined,
  FolderOutlined,
  FolderOpenOutlined,
  FileOutlined
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
const expandedRowKeys = ref([])
const zipChildrenCache = ref({}) // 缓存ZIP子文件列表

const zipViewer = ref({
  visible: false,
  loading: false,
  files: [],
  fileInfo: null
})

const comparisonViewer = ref({
  visible: false,
  loading: false,
  originalFile: {},
  processedContent: '',
  processedFileInfo: {}
})

// 计算属性 - 扁平化的文件列表用于表格展示
const flattenedFiles = computed(() => {
  const result = []
  
  uploadedFiles.value.forEach(file => {
    // 只添加顶级文件（非ZIP子文件）
    if (!file.is_child_of) {
      result.push({
        ...file,
        key: file.content_hash,
        level: 0,
        isChild: false,
        isZip: file.is_zip || file.filename.toLowerCase().endsWith('.zip')
      })
    }
  })
  
  return result
})

// 计算属性
const uploadUrl = computed(() => {
  return `/api/knowledge-new/databases/${props.databaseId}/files/upload-with-preview`
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
    title: '上传时间',
    dataIndex: 'uploadTime',
    key: 'uploadTime',
    width: 180
  },
  {
    title: '状态',
    dataIndex: 'processed',
    key: 'processed',
    width: 100,
    customRender: ({ record }) => {
      if (record.processed) {
        return <a-tag color="green">已处理</a-tag>
      } else if (canProcess(record)) {
        return <a-tag color="orange">待处理</a-tag>
      } else {
        return <a-tag color="blue">原文件</a-tag>
      }
    }
  },
  {
    title: '操作',
    dataIndex: 'actions',
    key: 'actions',
    fixed: 'right',
    width: 200
  }
]

const childFileColumns = [
  {
    title: '文件名',
    dataIndex: 'original_name',
    key: 'child_filename'
  },
  {
    title: '大小',
    dataIndex: 'fileSize',
    key: 'child_fileSize'
  },
  {
    title: '类型',
    dataIndex: 'contentType',
    key: 'child_contentType'
  },
  {
    title: '操作',
    dataIndex: 'actions',
    key: 'child_actions'
  }
]

const zipColumns = [
  {
    title: '文件名',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '原始大小',
    dataIndex: 'size',
    key: 'size'
  },
  {
    title: '压缩后大小',
    dataIndex: 'compressed_size',
    key: 'compressed_size'
  },
  {
    title: '压缩率',
    dataIndex: 'compression_rate',
    key: 'compression_rate',
    customRender: ({ text }) => {
      return text + '%'
    }
  },
  {
    title: '修改时间',
    dataIndex: 'modified',
    key: 'modified'
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

const getFileType = (filename) => {
  const ext = filename.toLowerCase().split('.').pop()
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  const docTypes = ['pdf', 'doc', 'docx']
  
  if (imageTypes.includes(ext)) return 'image'
  if (docTypes.includes(ext)) return 'document'
  if (ext === 'zip') return 'archive'
  return 'other'
}

const isPdfFile = (file) => {
  return file?.name?.toLowerCase().endsWith('.pdf') || file?.contentType === 'application/pdf'
}

const isImageFile = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
  return imageTypes.includes(file?.contentType) || 
         file?.name?.match(/\.(jpg|jpeg|png|gif|bmp|webp)$/i)
}

const getFileTypeName = (file) => {
  const contentType = file?.contentType
  const fileName = file?.name || ''
  
  if (contentType === 'application/pdf' || fileName.toLowerCase().endsWith('.pdf')) {
    return 'PDF文档'
  } else if (contentType?.startsWith('image/') || fileName.match(/\.(jpg|jpeg|png|gif|bmp|webp)$/i)) {
    return '图片文件'
  } else if (fileName.toLowerCase().endsWith('.zip')) {
    return 'ZIP压缩包'
  } else if (contentType === 'application/msword' || fileName.toLowerCase().endsWith('.doc')) {
    return 'Word文档'
  } else if (contentType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
             fileName.toLowerCase().endsWith('.docx')) {
    return 'Word文档'
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
      message.success(`${file.name} 上传成功`)
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
    const response = await axios.get(`/api/knowledge-new/databases/${props.databaseId}/files`)
    uploadedFiles.value = response.data.files
  } catch (error) {
    message.error('获取文件列表失败: ' + error.message)
  }
}

// 处理展开行
const handleExpand = async (expanded, record) => {
  if (expanded && record.isZip) {
    // 添加到展开键列表
    expandedRowKeys.value = [...expandedRowKeys.value, record.content_hash]
    
    // 如果还没有加载子文件，则加载
    if (!record.extractedFiles && !zipChildrenCache.value[record.content_hash]) {
      // 标记为加载中
      const index = uploadedFiles.value.findIndex(f => f.content_hash === record.content_hash)
      if (index !== -1) {
        uploadedFiles.value[index].childrenLoading = true
      }
      
      try {
        const response = await axios.get(
          `/api/knowledge-new/databases/${props.databaseId}/files/${record.content_hash}/children`
        )
        
        // 更新文件记录
        const fileIndex = uploadedFiles.value.findIndex(f => f.content_hash === record.content_hash)
        if (fileIndex !== -1) {
          uploadedFiles.value[fileIndex].extractedFiles = response.data.files
          uploadedFiles.value[fileIndex].childrenLoading = false
        }
        
        // 缓存结果
        zipChildrenCache.value[record.content_hash] = response.data.files
      } catch (error) {
        message.error('获取ZIP子文件失败: ' + error.message)
        
        // 更新加载状态
        const fileIndex = uploadedFiles.value.findIndex(f => f.content_hash === record.content_hash)
        if (fileIndex !== -1) {
          uploadedFiles.value[fileIndex].childrenLoading = false
        }
      }
    }
  } else {
    // 从展开键列表中移除
    expandedRowKeys.value = expandedRowKeys.value.filter(key => key !== record.content_hash)
  }
}

// 预览文件
const previewFile = async (record) => {
  if (record.filename.toLowerCase().endsWith('.zip')) {
    // 展开ZIP文件行来显示内容
    handleExpand(true, record)
  } else {
    // 在新窗口打开文件
    window.open(record.file_url, '_blank')
  }
}

// 显示ZIP内容
const showZipContent = async (record) => {
  try {
    zipViewer.value.loading = true
    zipViewer.value.visible = true
    
    const response = await axios.get(
      `/api/knowledge-new/databases/${props.databaseId}/files/${record.content_hash}/zip-content`
    )
    
    zipViewer.value.files = response.data.files
    zipViewer.value.fileInfo = response.data.original_file
  } catch (error) {
    message.error('获取ZIP内容失败: ' + error.message)
    zipViewer.value.visible = false
  } finally {
    zipViewer.value.loading = false
  }
}

// 预览ZIP子文件
const previewChildFile = (record) => {
  message.info(`预览子文件: ${record.original_name}`)
  // 这里可以实现子文件的预览逻辑
  // 例如，如果是图片可以直接显示，如果是文本可以展示内容等
}

// 下载文件
const downloadFile = (record) => {
  const link = document.createElement('a')
  link.href = record.file_url
  link.download = record.filename
  link.click()
}

// 判断文件是否可处理
const canProcess = (record) => {
  const processableExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.zip']
  const ext = (record.filename || '').toLowerCase().slice(record.filename.lastIndexOf('.'))
  return processableExtensions.includes(ext)
}

// 处理文件内容
const processFile = async (record) => {
  if (record.processing) return
  
  record.processing = true
  
  try {
    const response = await axios.post(
      `/api/knowledge-new/databases/${props.databaseId}/files/${record.content_hash}/process`,
      { ocr_engine: 'mineru_ocr' }
    )
    
    message.success('文件处理完成')
    
    // 更新文件状态
    const index = uploadedFiles.value.findIndex(f => f.content_hash === record.content_hash)
    if (index !== -1) {
      uploadedFiles.value[index].processed = true
      uploadedFiles.value[index].processed_time = new Date().toISOString()
    }
  } catch (error) {
    message.error('文件处理失败: ' + error.message)
  } finally {
    record.processing = false
  }
}

// 显示对比结果
const showComparison = async (record) => {
  try {
    comparisonViewer.value.loading = true
    comparisonViewer.value.visible = true
    
    // 获取处理后的内容
    const contentResponse = await axios.get(
      `/api/knowledge-new/databases/${props.databaseId}/files/${record.content_hash}/processed-content`
    )
    
    comparisonViewer.value.processedContent = contentResponse.data.content
    comparisonViewer.value.originalFile = {
      url: record.file_url,
      name: record.filename,
      contentType: record.contentType
    }
  } catch (error) {
    message.error('获取处理后内容失败: ' + error.message)
    comparisonViewer.value.visible = false
  } finally {
    comparisonViewer.value.loading = false
  }
}

// 下载原文件
const downloadOriginalFile = () => {
  const link = document.createElement('a')
  link.href = comparisonViewer.value.originalFile.url
  link.download = comparisonViewer.value.originalFile.name
  link.click()
}

// 下载处理后的文件
const downloadProcessedFile = () => {
  const content = comparisonViewer.value.processedContent
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = comparisonViewer.value.originalFile.name.replace(/\.[^/.]+$/, "") + '_processed.md'
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
.knowledge-base-file-manager {
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

.comparison-container {
  height: 100%;
}

.comparison-panel {
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

.file-preview-container {
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

.markdown-preview-container {
  flex: 1;
  overflow: hidden;
}

.ellipsis-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>