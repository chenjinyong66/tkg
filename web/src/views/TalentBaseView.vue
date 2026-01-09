<template>
  <div class="talent-base-container">
    <FileDetailModal />
    <FileUploadModal v-model:visible="addFilesModalVisible" />

    <div class="unified-layout">
      <!-- 左侧面板：文件上传和解析 -->
      <div class="left-panel" :style="{ width: leftPanelWidth + '%' }">
        <div class="upload-section">
          <a-card title="文件上传与解析" :bordered="false" size="small">
            <div class="upload-controls">
              <a-button type="primary" @click="showAddFilesModal">
                <UploadOutlined /> 上传文件
              </a-button>
              <a-button @click="refreshFileList" :loading="refreshing">
                <ReloadOutlined /> 刷新
              </a-button>
            </div>
            
            <div class="file-stats" v-if="databaseId">
              <span>总文件数: {{ fileCount }}</span>
              <span>已解析: {{ parsedCount }}</span>
              <span>处理中: {{ processingCount }}</span>
            </div>
          </a-card>
          
          <FileTable
            :right-panel-visible="state.rightPanelVisible"
            @show-add-files-modal="showAddFilesModal"
            @toggle-right-panel="toggleRightPanel"
          />
        </div>
      </div>

      <!-- 调整手柄 -->
      <div class="resize-handle" ref="resizeHandle"></div>

      <!-- 右侧面板：知识图谱展示 -->
      <div class="right-panel" :style="{ width: (100 - leftPanelWidth) + '%' }">
        <a-card :bordered="false" size="small" class="graph-card">
          <template #title>
            <div class="graph-header">
              <span>知识图谱</span>
              <div class="graph-controls">
                <a-button 
                  size="small" 
                  @click="refreshGraph" 
                  :loading="graphLoading"
                  :disabled="!isGraphSupported"
                >
                  <ReloadOutlined /> 刷新
                </a-button>
                <a-switch 
                  v-model:checked="autoRefreshGraph" 
                  size="small" 
                  checked-children="自动" 
                  un-checked-children="手动" 
                />
              </div>
            </div>
          </template>
          
          <div class="graph-container" v-if="isGraphSupported">
            <KnowledgeGraphViewer
              ref="graphViewerRef"
              :initial-database-id="databaseId"
              :hide-db-selector="true"
              :initial-limit="graphLimit"
              :initial-depth="graphDepth"
            />
          </div>
          
          <div v-else class="graph-placeholder">
            <a-empty description="当前知识库不支持知识图谱功能">
              <p>请选择 LightRAG 类型的知识库以启用知识图谱功能</p>
            </a-empty>
          </div>
        </a-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, onUnmounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useDatabaseStore } from '@/stores/database';
import { UploadOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import FileTable from '@/components/FileTable.vue';
import FileDetailModal from '@/components/FileDetailModal.vue';
import FileUploadModal from '@/components/FileUploadModal.vue';
import KnowledgeGraphViewer from '@/components/KnowledgeGraphViewer.vue';
import { message } from 'ant-design-vue';

const route = useRoute();
const store = useDatabaseStore();

// 响应式引用
const addFilesModalVisible = ref(false);
const refreshing = ref(false);
const graphLoading = ref(false);
const autoRefreshGraph = ref(true);
const graphViewerRef = ref(null);
const graphLimit = ref(100);
const graphDepth = ref(2);

// 面板宽度控制
const leftPanelWidth = ref(40);
const isDragging = ref(false);
const resizeHandle = ref(null);

// 计算属性
const databaseId = computed(() => store.databaseId);
const database = computed(() => store.database);
const state = computed(() => store.state);

const isGraphSupported = computed(() => {
  const kbType = database.value.kb_type?.toLowerCase();
  return kbType === 'lightrag';
});

const fileCount = computed(() => {
  return database.value?.files ? Object.keys(database.value.files).length : 0;
});

const parsedCount = computed(() => {
  if (!database.value?.files) return 0;
  return Object.values(database.value.files).filter(file => file.status === 'parsed').length;
});

const processingCount = computed(() => {
  if (!database.value?.files) return 0;
  return Object.values(database.value.files).filter(file => file.status === 'processing').length;
});

// 方法定义
const showAddFilesModal = () => {
  addFilesModalVisible.value = true;
};

const refreshFileList = async () => {
  refreshing.value = true;
  try {
    await store.getDatabaseInfo(databaseId.value, false);
    message.success('文件列表已刷新');
  } catch (error) {
    console.error('刷新文件列表失败:', error);
    message.error('刷新文件列表失败');
  } finally {
    refreshing.value = false;
  }
};

const refreshGraph = async () => {
  if (!isGraphSupported.value) return;
  
  graphLoading.value = true;
  try {
    if (graphViewerRef.value && typeof graphViewerRef.value.loadFullGraph === 'function') {
      await graphViewerRef.value.loadFullGraph();
      message.success('知识图谱已刷新');
    }
  } catch (error) {
    console.error('刷新知识图谱失败:', error);
    message.error('刷新知识图谱失败');
  } finally {
    graphLoading.value = false;
  }
};

const toggleRightPanel = () => {
  store.state.rightPanelVisible = !store.state.rightPanelVisible;
};

// 拖拽调整大小功能
const handleMouseDown = () => {
  isDragging.value = true;
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
};

const handleMouseMove = (e) => {
  if (!isDragging.value) return;

  const container = document.querySelector('.unified-layout');
  if (!container) return;

  const containerRect = container.getBoundingClientRect();
  const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
  leftPanelWidth.value = Math.max(20, Math.min(80, newWidth));
};

const handleMouseUp = () => {
  isDragging.value = false;
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', handleMouseUp);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
};

// 自动刷新图谱
let autoRefreshInterval = null;

const startAutoRefresh = () => {
  if (autoRefreshInterval) clearInterval(autoRefreshInterval);
  autoRefreshInterval = setInterval(() => {
    if (autoRefreshGraph.value && isGraphSupported.value) {
      refreshGraph();
    }
  }, 30000); // 30秒自动刷新一次
};

const stopAutoRefresh = () => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
};

// 监听数据库变化
watch(databaseId, async (newId) => {
  if (newId) {
    await store.getDatabaseInfo(newId, false);
    // 刷新图谱
    if (isGraphSupported.value) {
      setTimeout(() => {
        refreshGraph();
      }, 1000);
    }
  }
});

// 监听文件变化，自动刷新图谱
watch(() => database.value?.files, () => {
  if (autoRefreshGraph.value && isGraphSupported.value) {
    // 延迟刷新，等待文件处理完成
    setTimeout(() => {
      refreshGraph();
    }, 5000);
  }
}, { deep: true });

// 组件生命周期
onMounted(() => {
  store.databaseId = route.params.database_id || 'default'; // 设置默认数据库ID或从路由获取
  refreshFileList();
  startAutoRefresh();

  // 添加拖拽事件监听
  if (resizeHandle.value) {
    resizeHandle.value.addEventListener('mousedown', handleMouseDown);
  }
});

onUnmounted(() => {
  stopAutoRefresh();
  if (resizeHandle.value) {
    resizeHandle.value.removeEventListener('mousedown', handleMouseDown);
  }
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', handleMouseUp);
});
</script>

<style lang="less" scoped>
.talent-base-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.unified-layout {
  display: flex;
  height: 100%;
  background-color: var(--gray-0);
  gap: 0;

  .left-panel,
  .right-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 8px;
  }

  .left-panel {
    display: flex;
    flex-shrink: 0;
    flex-grow: 1;
    padding-right: 0;
  }

  .right-panel {
    flex-grow: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding-left: 0;
  }

  .resize-handle {
    width: 4px;
    cursor: col-resize;
    background-color: var(--gray-200);
    position: relative;
    z-index: 10;
    flex-shrink: 0;
    height: 30px;
    top: 40%;
    margin: 0 2px;
    border-radius: 4px;

    &:hover {
      background-color: var(--main-color);
    }
  }
}

.upload-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;

  :deep(.ant-card) {
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  .upload-controls {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    
    .ant-btn {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .file-stats {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: var(--gray-600);
    margin-bottom: 12px;
  }
}

.graph-card {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.ant-card-body) {
    flex: 1;
    padding: 0;
    overflow: hidden;
  }
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.graph-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.graph-container {
  height: 100%;
  width: 100%;
}

.graph-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* Responsive design */
@media (max-width: 768px) {
  .unified-layout {
    flex-direction: column;
  }

  .unified-layout .left-panel {
    border-right: none;
    border-bottom: 1px solid var(--gray-200);
  }

  .unified-layout .resize-handle {
    width: 100%;
    height: 2px;
    cursor: row-resize;
  }
}
</style>
