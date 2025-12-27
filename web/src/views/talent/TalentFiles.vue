<template>
  <div class="talent-files">
    <!-- 文件管理头部 -->
    <div class="files-header">
      <div class="header-left">
        <h2>考核文件管理</h2>
        <div class="file-stats">
          <span class="stat-item">共 {{ totalFiles }} 个文件</span>
          <span class="stat-item">{{ parsedCount }} 个已解析</span>
          <span class="stat-item">{{ graphCount }} 个已抽取图谱</span>
        </div>
      </div>
      <div class="header-right">
        <a-button type="primary" @click="showUploadModal">
          <UploadOutlined />
          上传文件
        </a-button>
        <a-dropdown>
          <a-button>
            批量操作 <DownOutlined />
          </a-button>
          <template #overlay>
            <a-menu>
              <a-menu-item @click="handleBatchUpload">
                <UploadOutlined /> 批量上传
              </a-menu-item>
              <a-menu-item @click="handleBatchParse" :disabled="selectedFiles.length === 0">
                <CodeOutlined /> 批量解析
              </a-menu-item>
              <a-menu-item @click="handleBatchDelete" :disabled="selectedFiles.length === 0" danger>
                <DeleteOutlined /> 批量删除
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="files-toolbar">
      <div class="toolbar-left">
        <a-input-search
            v-model:value="searchKeyword"
            placeholder="搜索文件名..."
            style="width: 200px"
            @search="handleSearch"
            allow-clear
        />
        <a-select
            v-model:value="fileTypeFilter"
            placeholder="文件类型"
            style="width: 120px; margin-left: 8px;"
            allow-clear
            @change="handleFilter"
        >
          <a-select-option value="pdf">PDF</a-select-option>
          <a-select-option value="doc">Word</a-select-option>
          <a-select-option value="xls">Excel</a-select-option>
          <a-select-option value="txt">文本</a-select-option>
          <a-select-option value="md">Markdown</a-select-option>
        </a-select>
        <a-select
            v-model:value="statusFilter"
            placeholder="解析状态"
            style="width: 120px; margin-left: 8px;"
            allow-clear
            @change="handleFilter"
        >
          <a-select-option value="parsed">已解析</a-select-option>
          <a-select-option value="unparsed">未解析</a-select-option>
          <a-select-option value="error">解析失败</a-select-option>
        </a-select>
      </div>
      <div class="toolbar-right">
        <a-tooltip title="列表视图">
          <a-button
              :type="viewMode === 'list' ? 'primary' : 'text'"
              @click="viewMode = 'list'"
          >
            <UnorderedListOutlined />
          </a-button>
        </a-tooltip>
        <a-tooltip title="网格视图">
          <a-button
              :type="viewMode === 'grid' ? 'primary' : 'text'"
              @click="viewMode = 'grid'"
              style="margin-left: 4px;"
          >
            <AppstoreOutlined />
          </a-button>
        </a-tooltip>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="files-content">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid' && filteredFiles.length > 0" class="files-grid">
        <div
            v-for="file in filteredFiles"
            :key="file.id"
            class="file-card"
            :class="{
            'selected': selectedFiles.includes(file.id),
            'parsed': file.parsed,
            'error': file.parseError
          }"
            @click="toggleSelectFile(file.id)"
        >
          <div class="card-checkbox">
            <a-checkbox
                :checked="selectedFiles.includes(file.id)"
                @click.stop="toggleSelectFile(file.id)"
            />
          </div>
          <div class="card-content" @click="viewFileDetail(file)">
            <div class="file-header">
              <div class="file-type-icon" :class="getFileTypeClass(file.fileType)">
                {{ getFileTypeIcon(file.fileType) }}
              </div>
              <div class="file-actions">
                <a-dropdown :trigger="['click']" placement="bottomRight">
                  <a-button type="text" size="small" @click.stop>
                    <MoreOutlined />
                  </a-button>
                  <template #overlay>
                    <a-menu>
                      <a-menu-item @click.stop="downloadFile(file)">
                        <DownloadOutlined />
                        下载
                      </a-menu-item>
                      <a-menu-item @click.stop="parseFile(file)">
                        <CodeOutlined />
                        {{ file.parsed ? '重新解析' : '解析内容' }}
                      </a-menu-item>
                      <a-menu-item @click.stop="renameFile(file)">
                        <EditOutlined />
                        重命名
                      </a-menu-item>
                      <a-menu-divider />
                      <a-menu-item @click.stop="deleteFile(file)" danger>
                        <DeleteOutlined />
                        删除
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </div>
            </div>
            <div class="file-info">
              <div class="file-name" :title="file.filename">
                {{ truncateText(file.filename, 20) }}
              </div>
              <div class="file-meta">
                <div class="meta-item">
                  <FieldTimeOutlined />
                  {{ formatRelativeTime(file.uploadTime) }}
                </div>
                <div class="meta-item">
                  <DatabaseOutlined />
                  {{ formatFileSize(file.fileSize) }}
                </div>
              </div>
            </div>
            <div class="file-status">
              <a-tag :color="getFileStatusColor(file)" size="small">
                {{ getFileStatusLabel(file) }}
              </a-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else-if="viewMode === 'list' && filteredFiles.length > 0" class="files-table">
        <a-table
            :data-source="filteredFiles"
            :columns="tableColumns"
            :row-selection="rowSelection"
            :pagination="false"
            size="middle"
            row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'filename'">
              <div class="file-cell" @click="viewFileDetail(record)">
                <div class="file-type-icon-small" :class="getFileTypeClass(record.fileType)">
                  {{ getFileTypeIcon(record.fileType).charAt(0) }}
                </div>
                <div class="file-name-wrapper">
                  <div class="file-name">{{ record.filename }}</div>
                  <div class="file-description" v-if="record.description">
                    {{ record.description }}
                  </div>
                </div>
              </div>
            </template>
            <template v-if="column.key === 'status'">
              <a-tag :color="getFileStatusColor(record)" size="small">
                {{ getFileStatusLabel(record) }}
              </a-tag>
            </template>
            <template v-if="column.key === 'actions'">
              <div class="action-buttons">
                <a-tooltip title="查看">
                  <a-button type="link" size="small" @click="viewFileDetail(record)">
                    <EyeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="解析">
                  <a-button
                      type="link"
                      size="small"
                      @click="parseFile(record)"
                      :disabled="isTextFile(record.fileType)"
                  >
                    <CodeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="下载">
                  <a-button type="link" size="small" @click="downloadFile(record)">
                    <DownloadOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="删除">
                  <a-popconfirm
                      title="确定要删除这个文件吗？"
                      @confirm="deleteFile(record)"
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
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-files">
        <Empty description="暂无文件" />
        <div class="empty-actions">
          <a-button type="primary" @click="showUploadModal">
            <UploadOutlined />
            上传第一个文件
          </a-button>
          <a-button style="margin-left: 12px;" @click="handleImportSample">
            <FileAddOutlined />
            导入示例文件
          </a-button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="files-pagination" v-if="filteredFiles.length > 0">
      <a-pagination
          v-model:current="currentPage"
          v-model:pageSize="pageSize"
          :total="filteredFiles.length"
          show-size-changer
          show-quick-jumper
          @change="handlePageChange"
          @showSizeChange="handleSizeChange"
      />
    </div>

    <!-- 上传模态框 -->
    <FileUploadModal
        v-model:open="showUpload"
        :talent-id="talentId"
        @upload-success="handleUploadSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { h } from 'vue'
import {
  UploadOutlined, DownOutlined, CodeOutlined,
  DeleteOutlined, UnorderedListOutlined, AppstoreOutlined,
  MoreOutlined, DownloadOutlined, EditOutlined,
  EyeOutlined, FieldTimeOutlined, DatabaseOutlined,
  FileAddOutlined
} from '@ant-design/icons-vue'
import { Empty } from 'ant-design-vue'
import FileUploadModal from '@/components/FileUploadModal.vue';

import { talentApi } from '@/apis/talent_api'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const talentId = route.params.id

// 响应式数据
const files = ref([])
const searchKeyword = ref('')
const fileTypeFilter = ref(null)
const statusFilter = ref(null)
const viewMode = ref('grid')
const selectedFiles = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const showUpload = ref(false)

const state = reactive({
  loading: false,
  renameInput: ''
})

// 计算属性
const totalFiles = computed(() => files.value.length)

const parsedCount = computed(() => {
  return files.value.filter(file => file.parsed).length
})

const graphCount = computed(() => {
  return files.value.filter(file => file.graphExtracted).length
})

const filteredFiles = computed(() => {
  let filtered = files.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(file =>
        file.filename.toLowerCase().includes(keyword) ||
        file.description?.toLowerCase().includes(keyword)
    )
  }

  // 文件类型过滤
  if (fileTypeFilter.value) {
    filtered = filtered.filter(file => file.fileType === fileTypeFilter.value)
  }

  // 状态过滤
  if (statusFilter.value) {
    switch (statusFilter.value) {
      case 'parsed':
        filtered = filtered.filter(file => file.parsed)
        break
      case 'unparsed':
        filtered = filtered.filter(file => !file.parsed && !isTextFile(file.fileType))
        break
      case 'error':
        filtered = filtered.filter(file => file.parseError)
        break
    }
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const rowSelection = computed(() => ({
  selectedRowKeys: selectedFiles.value,
  onChange: (selectedRowKeys) => {
    selectedFiles.value = selectedRowKeys
  }
}))

const tableColumns = computed(() => [
  {
    title: '文件名',
    key: 'filename',
    width: 300
  },
  {
    title: '文件类型',
    key: 'fileType',
    width: 100
  },
  {
    title: '文件大小',
    key: 'fileSize',
    width: 100
  },
  {
    title: '解析状态',
    key: 'status',
    width: 100
  },
  {
    title: '上传时间',
    key: 'uploadTime',
    width: 150
  },
  {
    title: '操作',
    key: 'actions',
    width: 120
  }
])

// 工具函数
const formatFileSize = (size) => {
  if (!size) return '未知'
  if (size < 1024) return size + ' B'
  else if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  else return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatRelativeTime = (dateTime) => {
  if (!dateTime) return ''
  return dayjs(dateTime).fromNow()
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const getFileTypeIcon = (type) => {
  const icons = {
    pdf: 'PDF',
    doc: 'DOC',
    docx: 'DOCX',
    xls: 'XLS',
    xlsx: 'XLSX',
    txt: 'TXT',
    md: 'MD'
  }
  return icons[type?.toLowerCase()] || 'FILE'
}

const getFileTypeClass = (type) => {
  const classes = {
    pdf: 'pdf',
    doc: 'word',
    docx: 'word',
    xls: 'excel',
    xlsx: 'excel',
    txt: 'text',
    md: 'markdown'
  }
  return classes[type?.toLowerCase()] || 'default'
}

const getFileStatusColor = (file) => {
  if (file.parseError) return 'error'
  if (file.parsed) return 'success'
  if (isTextFile(file.fileType)) return 'processing'
  return 'default'
}

const getFileStatusLabel = (file) => {
  if (file.parseError) return '解析失败'
  if (file.parsed) return '已解析'
  if (isTextFile(file.fileType)) return '可直接查看'
  return '待解析'
}

const isTextFile = (fileType) => {
  const textTypes = ['txt', 'md']
  return textTypes.includes(fileType?.toLowerCase())
}

// 业务函数
const loadFiles = async () => {
  state.loading = true
  try {
    const response = await talentApi.getTalentFilesByTalent(talentId)
    files.value = response.files || []
  } catch (error) {
    console.error('加载文件列表失败:', error)
    message.error('加载文件列表失败')
  } finally {
    state.loading = false
  }
}

const showUploadModal = () => {
  showUpload.value = true
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const toggleSelectFile = (fileId) => {
  const index = selectedFiles.value.indexOf(fileId)
  if (index === -1) {
    selectedFiles.value.push(fileId)
  } else {
    selectedFiles.value.splice(index, 1)
  }
}

const viewFileDetail = (file) => {
  router.push(`/talent/${talentId}/files/${file.id}`)
}

const downloadFile = async (file) => {
  try {
    const response = await talentApi.downloadTalentFile(file.id)
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载文件失败:', error)
    message.error('下载文件失败')
  }
}

const parseFile = async (file) => {
  if (isTextFile(file.fileType)) {
    message.info('文本文件可直接查看，无需解析')
    return
  }

  try {
    message.loading('正在解析文件...', 0)
    await talentApi.parseFileToMarkdown(file.id)
    message.destroy()
    message.success('文件解析成功')

    // 更新文件状态
    file.parsed = true
    file.parseError = false
  } catch (error) {
    message.destroy()
    console.error('解析文件失败:', error)
    file.parseError = true
    message.error('解析文件失败')
  }
}

const renameFile = (file) => {
  const renameInput = ref(file.filename)

  Modal.confirm({
    title: '重命名文件',
    content: () => h('div', [
      h('a-input', {
        value: renameInput.value,
        'onUpdate:value': (val) => { renameInput.value = val },
        placeholder: "请输入新文件名",
        style: { marginTop: '10px', width: '100%' }
      })
    ]),
    onOk: async () => {
      if (!renameInput.value.trim()) {
        message.error('文件名不能为空')
        return
      }

      try {
        await talentApi.renameTalentFile(file.id, renameInput.value)
        message.success('文件重命名成功')
        loadFiles()
      } catch (error) {
        message.error('重命名失败')
      }
    }
  })
}

const deleteFile = (file) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除文件 "${file.filename}" 吗？此操作不可恢复。`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await talentApi.deleteTalentFile(file.id)
        message.success('文件删除成功')

        // 从选中列表中移除
        const index = selectedFiles.value.indexOf(file.id)
        if (index > -1) {
          selectedFiles.value.splice(index, 1)
        }

        loadFiles()
      } catch (error) {
        console.error('删除文件失败:', error)
        message.error('删除文件失败')
      }
    }
  })
}

const handleUploadSuccess = () => {
  showUpload.value = false
  loadFiles()
  message.success('文件上传成功')
}

const handleBatchUpload = () => {
  message.info('批量上传功能开发中')
}

const handleBatchParse = async () => {
  if (selectedFiles.value.length === 0) {
    message.warning('请先选择文件')
    return
  }

  Modal.confirm({
    title: '批量解析',
    content: `确定要批量解析 ${selectedFiles.value.length} 个文件吗？`,
    okText: '开始解析',
    cancelText: '取消',
    onOk: async () => {
      message.loading(`正在批量解析 ${selectedFiles.value.length} 个文件...`, 0)

      let successCount = 0
      let failCount = 0

      for (const fileId of selectedFiles.value) {
        const file = files.value.find(f => f.id === fileId)
        if (file && !isTextFile(file.fileType)) {
          try {
            await talentApi.parseFileToMarkdown(file.id)
            file.parsed = true
            file.parseError = false
            successCount++
          } catch (error) {
            file.parseError = true
            failCount++
          }
        }
      }

      message.destroy()
      if (failCount === 0) {
        message.success(`成功解析 ${successCount} 个文件`)
      } else {
        message.warning(`解析完成，成功 ${successCount} 个，失败 ${failCount} 个`)
      }
    }
  })
}

const handleBatchDelete = () => {
  if (selectedFiles.value.length === 0) {
    message.warning('请先选择文件')
    return
  }

  Modal.confirm({
    title: '批量删除',
    content: `确定要删除选中的 ${selectedFiles.value.length} 个文件吗？此操作不可恢复。`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await talentApi.batchDeleteFiles(selectedFiles.value)
        message.success(`成功删除 ${selectedFiles.value.length} 个文件`)
        selectedFiles.value = []
        loadFiles()
      } catch (error) {
        console.error('批量删除失败:', error)
        message.error('批量删除失败')
      }
    }
  })
}

const handleImportSample = () => {
  message.info('导入示例文件功能开发中')
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const handleSizeChange = (current, size) => {
  currentPage.value = 1
  pageSize.value = size
}

onMounted(() => {
  loadFiles()

  // 如果URL参数包含upload，显示上传模态框
  if (route.query.upload === 'true') {
    showUploadModal()
  }
})
</script>

<style lang="less" scoped>
.talent-files {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  .header-left {
    h2 {
      margin: 0 0 8px 0;
      font-size: 20px;
      font-weight: 600;
      color: #1f1f1f;
    }

    .file-stats {
      display: flex;
      gap: 16px;

      .stat-item {
        font-size: 14px;
        color: #666;
      }
    }
  }

  .header-right {
    display: flex;
    gap: 8px;
  }
}

.files-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  .toolbar-left {
    display: flex;
    align-items: center;
  }
}

.files-content {
  .files-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;

    .file-card {
      position: relative;
      border: 1px solid #f0f0f0;
      border-radius: 8px;
      padding: 16px;
      background: #fff;
      cursor: pointer;
      transition: all 0.3s;

      &.selected {
        border-color: #1890ff;
        background: #e6f7ff;
      }

      &.parsed {
        border-left: 3px solid #52c41a;
      }

      &.error {
        border-left: 3px solid #ff4d4f;
      }

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
      }

      .card-checkbox {
        position: absolute;
        top: 8px;
        right: 8px;
        z-index: 1;
      }

      .card-content {
        .file-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;

          .file-type-icon {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: bold;
            color: white;

            &.pdf { background: #ff4d4f; }
            &.word { background: #1890ff; }
            &.excel { background: #52c41a; }
            &.text { background: #faad14; }
            &.markdown { background: #722ed1; }
            &.default { background: #666; }
          }

          .file-actions {
            :deep(.ant-btn) {
              padding: 0;
              width: 24px;
              height: 24px;
            }
          }
        }

        .file-info {
          margin-bottom: 12px;

          .file-name {
            font-weight: 500;
            color: #333;
            margin-bottom: 8px;
            line-height: 1.4;
            word-break: break-word;
          }

          .file-meta {
            .meta-item {
              display: flex;
              align-items: center;
              gap: 4px;
              font-size: 12px;
              color: #999;
              margin-bottom: 4px;

              &:last-child {
                margin-bottom: 0;
              }
            }
          }
        }

        .file-status {
          :deep(.ant-tag) {
            margin: 0;
          }
        }
      }
    }
  }

  .files-table {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    .file-cell {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;

      .file-type-icon-small {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        color: white;

        &.pdf { background: #ff4d4f; }
        &.word { background: #1890ff; }
        &.excel { background: #52c41a; }
        &.text { background: #faad14; }
        &.markdown { background: #722ed1; }
        &.default { background: #666; }
      }

      .file-name-wrapper {
        flex: 1;

        .file-name {
          font-weight: 500;
          color: #333;
          line-height: 1.4;
        }

        .file-description {
          font-size: 12px;
          color: #999;
          margin-top: 2px;
        }
      }
    }

    .action-buttons {
      display: flex;
      gap: 4px;

      .ant-btn {
        padding: 0;
        width: 24px;
        height: 24px;
      }
    }
  }

  .empty-files {
    text-align: center;
    padding: 40px 0;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    .empty-actions {
      display: flex;
      justify-content: center;
      gap: 12px;
      margin-top: 16px;
    }
  }
}

.files-pagination {
  display: flex;
  justify-content: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

@media (max-width: 768px) {
  .files-header {
    flex-direction: column;
    gap: 16px;

    .header-right {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .files-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;

    .toolbar-left {
      flex-wrap: wrap;
      gap: 8px;

      .ant-input-search, .ant-select {
        width: 100% !important;
        margin-left: 0 !important;
      }
    }
  }

  .files-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important;
  }
}

@media (max-width: 480px) {
  .files-grid {
    grid-template-columns: 1fr !important;
  }

  .empty-files .empty-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>