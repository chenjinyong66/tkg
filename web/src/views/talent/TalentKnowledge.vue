<template>
  <div class="talent-knowledge">
    <!-- 页面标题 -->
    <div class="knowledge-header">
      <h2>知识图谱</h2>
      <div class="header-actions">
        <a-select
            v-model:value="layoutType"
            placeholder="布局方式"
            style="width: 120px; margin-right: 8px;"
            @change="handleLayoutChange"
        >
          <a-select-option value="force">力导向布局</a-select-option>
          <a-select-option value="circular">环形布局</a-select-option>
          <a-select-option value="radial">辐射布局</a-select-option>
          <a-select-option value="tree">树状布局</a-select-option>
        </a-select>
        <a-button @click="handleAutoExtract">
          <ClusterOutlined />
          自动抽取
        </a-button>
        <a-button type="primary" @click="handleExportGraph">
          <ExportOutlined />
          导出图谱
        </a-button>
      </div>
    </div>

    <!-- 知识图谱展示区 -->
    <div class="graph-container">
      <div class="graph-main">
        <GraphCanvas
            ref="graphCanvas"
            :data="graphData"
            :layout="layoutType"
            :height="graphHeight"
            @node-click="handleNodeClick"
            @edge-click="handleEdgeClick"
            @canvas-click="handleCanvasClick"
        />
      </div>
      <div class="graph-sidebar">
        <a-card title="图谱信息" size="small" class="sidebar-card">
          <div class="graph-stats">
            <div class="stat-item">
              <span class="stat-label">节点数</span>
              <span class="stat-value">{{ graphStats.nodes }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">关系数</span>
              <span class="stat-value">{{ graphStats.edges }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">密度</span>
              <span class="stat-value">{{ graphStats.density }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">直径</span>
              <span class="stat-value">{{ graphStats.diameter }}</span>
            </div>
          </div>
        </a-card>

        <a-card title="选中节点" size="small" class="sidebar-card" v-if="selectedNode">
          <div class="node-info">
            <div class="node-header">
              <div class="node-type-tag">
                <a-tag :color="getNodeTypeColor(selectedNode.type)" size="small">
                  {{ getNodeTypeLabel(selectedNode.type) }}
                </a-tag>
              </div>
              <h4 class="node-name">{{ selectedNode.label }}</h4>
            </div>

            <div class="node-properties">
              <div class="property-item" v-if="selectedNode.properties">
                <span class="property-label">描述：</span>
                <span class="property-value">{{ selectedNode.properties.description }}</span>
              </div>
              <div class="property-item" v-if="selectedNode.properties?.level">
                <span class="property-label">等级：</span>
                <span class="property-value">{{ selectedNode.properties.level }}</span>
              </div>
              <div class="property-item" v-if="selectedNode.properties?.confidence">
                <span class="property-label">置信度：</span>
                <span class="property-value">{{ selectedNode.properties.confidence }}</span>
              </div>
            </div>

            <div class="node-connections">
              <div class="connections-header">
                <span>关联关系</span>
                <span class="connections-count">({{ nodeConnections.length }})</span>
              </div>
              <div class="connections-list">
                <div
                    v-for="(conn, index) in nodeConnections"
                    :key="index"
                    class="connection-item"
                >
                  <div class="connection-type">
                    <a-tag size="small">{{ conn.type }}</a-tag>
                  </div>
                  <div class="connection-target">
                    {{ conn.targetLabel }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </a-card>

        <a-card title="图谱操作" size="small" class="sidebar-card">
          <div class="graph-actions">
            <a-button block @click="handleZoomIn">
              <ZoomInOutlined />
              放大
            </a-button>
            <a-button block @click="handleZoomOut" style="margin-top: 8px;">
              <ZoomOutOutlined />
              缩小
            </a-button>
            <a-button block @click="handleFitView" style="margin-top: 8px;">
              <AimOutlined />
              适应视图
            </a-button>
            <a-button block @click="handleClearSelection" style="margin-top: 8px;">
              <ClearOutlined />
              清除选择
            </a-button>
            <a-button block @click="showAddNodeModal = true" style="margin-top: 8px;">
              <PlusOutlined />
              添加节点
            </a-button>
            <a-button block @click="showAddEdgeModal = true" style="margin-top: 8px;">
              <LinkOutlined />
              添加关系
            </a-button>
          </div>
        </a-card>
      </div>
    </div>

    <!-- 知识分类统计 -->
    <a-card class="knowledge-stats" title="知识分类统计">
      <div class="stats-content">
        <div class="category-stats">
          <div
              v-for="category in categoryStats"
              :key="category.type"
              class="category-item"
          >
            <div class="category-header">
              <span class="category-name">{{ category.label }}</span>
              <span class="category-count">{{ category.count }}</span>
            </div>
            <a-progress
                :percent="category.percentage"
                :stroke-color="category.color"
                size="small"
            />
          </div>
        </div>
      </div>
    </a-card>

    <!-- 知识列表 -->
    <a-card class="knowledge-list" title="知识条目">
      <template #extra>
        <a-input-search
            v-model:value="knowledgeSearch"
            placeholder="搜索知识..."
            style="width: 200px"
            @search="handleKnowledgeSearch"
        />
      </template>
      <a-table
          :data-source="filteredKnowledge"
          :columns="knowledgeColumns"
          :pagination="{
          current: knowledgePage.current,
          pageSize: knowledgePage.pageSize,
          total: knowledgePage.total
        }"
          @change="handleKnowledgePageChange"
          size="middle"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <div class="knowledge-item">
              <div class="knowledge-type">
                <a-tag :color="getNodeTypeColor(record.type)" size="small">
                  {{ getNodeTypeLabel(record.type) }}
                </a-tag>
              </div>
              <div class="knowledge-content">
                <div class="knowledge-name">{{ record.name }}</div>
                <div class="knowledge-desc" v-if="record.description">
                  {{ record.description }}
                </div>
              </div>
            </div>
          </template>

          <template v-if="column.key === 'confidence'">
            <div class="confidence-cell">
              <a-progress
                  :percent="record.confidence * 100"
                  :stroke-color="getConfidenceColor(record.confidence)"
                  size="small"
                  :show-info="false"
              />
              <span class="confidence-value">{{ (record.confidence * 100).toFixed(1) }}%</span>
            </div>
          </template>

          <template v-if="column.key === 'actions'">
            <div class="knowledge-actions">
              <a-tooltip title="定位节点">
                <a-button type="link" size="small" @click="locateNode(record.id)">
                  <AimOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="编辑">
                <a-button type="link" size="small" @click="editKnowledge(record)">
                  <EditOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="删除">
                <a-popconfirm
                    title="确定要删除这个知识吗？"
                    @confirm="deleteKnowledge(record.id)"
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

    <!-- 添加节点模态框 -->
    <a-modal
        v-model:open="showAddNodeModal"
        title="添加知识节点"
        @ok="handleAddNode"
        @cancel="showAddNodeModal = false"
        width="600px"
    >
      <a-form :model="newNode" layout="vertical">
        <a-form-item label="节点类型" required>
          <a-select
              v-model:value="newNode.type"
              placeholder="请选择节点类型"
              @change="handleNodeTypeChange"
          >
            <a-select-option value="skill">技能</a-select-option>
            <a-select-option value="knowledge">知识点</a-select-option>
            <a-select-option value="experience">经验</a-select-option>
            <a-select-option value="project">项目</a-select-option>
            <a-select-option value="achievement">成果</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="节点名称" required>
          <a-input
              v-model:value="newNode.label"
              placeholder="请输入节点名称"
              :maxlength="50"
              show-count
          />
        </a-form-item>

        <a-form-item label="描述">
          <a-textarea
              v-model:value="newNode.description"
              placeholder="请输入节点描述"
              :rows="3"
              :maxlength="200"
              show-count
          />
        </a-form-item>

        <a-form-item label="等级" v-if="newNode.type === 'skill'">
          <a-select v-model:value="newNode.level" placeholder="请选择等级">
            <a-select-option value="beginner">初级</a-select-option>
            <a-select-option value="intermediate">中级</a-select-option>
            <a-select-option value="advanced">高级</a-select-option>
            <a-select-option value="expert">专家</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="置信度">
          <a-slider
              v-model:value="newNode.confidence"
              :min="0"
              :max="1"
              :step="0.1"
              :marks="{ 0: '0', 0.5: '0.5', 1: '1' }"
          />
          <span class="slider-value">{{ (newNode.confidence * 100).toFixed(0) }}%</span>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 添加关系模态框 -->
    <a-modal
        v-model:open="showAddEdgeModal"
        title="添加知识关系"
        @ok="handleAddEdge"
        @cancel="showAddEdgeModal = false"
        width="600px"
    >
      <a-form :model="newEdge" layout="vertical">
        <a-form-item label="源节点" required>
          <a-select
              v-model:value="newEdge.source"
              placeholder="请选择源节点"
              show-search
              option-filter-prop="label"
          >
            <a-select-option
                v-for="node in graphData.nodes"
                :key="node.id"
                :value="node.id"
                :label="node.label"
            >
              {{ node.label }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="关系类型" required>
          <a-select v-model:value="newEdge.type" placeholder="请选择关系类型">
            <a-select-option value="has">拥有</a-select-option>
            <a-select-option value="requires">需要</a-select-option>
            <a-select-option value="related_to">相关</a-select-option>
            <a-select-option value="part_of">属于</a-select-option>
            <a-select-option value="similar_to">类似</a-select-option>
            <a-select-option value="depends_on">依赖</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="目标节点" required>
          <a-select
              v-model:value="newEdge.target"
              placeholder="请选择目标节点"
              show-search
              option-filter-prop="label"
          >
            <a-select-option
                v-for="node in graphData.nodes"
                :key="node.id"
                :value="node.id"
                :label="node.label"
            >
              {{ node.label }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="关系强度">
          <a-slider
              v-model:value="newEdge.strength"
              :min="0"
              :max="1"
              :step="0.1"
              :marks="{ 0: '弱', 0.5: '中', 1: '强' }"
          />
          <span class="slider-value">{{ (newEdge.strength * 100).toFixed(0) }}%</span>
        </a-form-item>

        <a-form-item label="关系描述">
          <a-input
              v-model:value="newEdge.label"
              placeholder="请输入关系描述"
              :maxlength="100"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  ExportOutlined, ClusterOutlined, ZoomInOutlined,
  ZoomOutOutlined, AimOutlined, ClearOutlined,
  PlusOutlined, LinkOutlined, EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import GraphCanvas from '@/components/GraphCanvas.vue';

import { talentApi } from '@/apis/talent_api'

const route = useRoute()
const talentId = route.params.id

// 响应式数据
const graphCanvas = ref(null)
const layoutType = ref('force')
const graphHeight = ref(600)
const showAddNodeModal = ref(false)
const showAddEdgeModal = ref(false)
const knowledgeSearch = ref('')
const selectedNode = ref(null)

// 图谱数据
const graphData = reactive({
  nodes: [],
  edges: []
})

// 知识列表数据
const knowledgeList = ref([])
const knowledgePage = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 新增节点数据
const newNode = reactive({
  type: 'skill',
  label: '',
  description: '',
  level: 'intermediate',
  confidence: 0.8
})

// 新增关系数据
const newEdge = reactive({
  source: '',
  type: 'has',
  target: '',
  strength: 0.5,
  label: ''
})

const state = reactive({
  loading: false,
  extracting: false
})

// 计算属性
const graphStats = computed(() => {
  const nodes = graphData.nodes.length
  const edges = graphData.edges.length
  const density = edges > 0 && nodes > 1 ? ((2 * edges) / (nodes * (nodes - 1))).toFixed(3) : 0
  const diameter = 0 // 需要计算图直径，这里简化处理

  return {
    nodes,
    edges,
    density,
    diameter
  }
})

const nodeConnections = computed(() => {
  if (!selectedNode.value) return []

  const connections = []
  graphData.edges.forEach(edge => {
    if (edge.source === selectedNode.value.id) {
      const targetNode = graphData.nodes.find(n => n.id === edge.target)
      if (targetNode) {
        connections.push({
          type: edge.type,
          targetId: edge.target,
          targetLabel: targetNode.label
        })
      }
    }
    if (edge.target === selectedNode.value.id) {
      const sourceNode = graphData.nodes.find(n => n.id === edge.source)
      if (sourceNode) {
        connections.push({
          type: edge.type,
          targetId: edge.source,
          targetLabel: sourceNode.label
        })
      }
    }
  })

  return connections
})

const categoryStats = computed(() => {
  const stats = {}
  graphData.nodes.forEach(node => {
    if (!stats[node.type]) {
      stats[node.type] = {
        type: node.type,
        label: getNodeTypeLabel(node.type),
        count: 0,
        color: getNodeTypeColor(node.type)
      }
    }
    stats[node.type].count++
  })

  const total = graphData.nodes.length
  const categories = Object.values(stats).map(cat => ({
    ...cat,
    percentage: total > 0 ? Math.round((cat.count / total) * 100) : 0
  }))

  return categories.sort((a, b) => b.count - a.count)
})

const filteredKnowledge = computed(() => {
  let filtered = knowledgeList.value

  if (knowledgeSearch.value) {
    const keyword = knowledgeSearch.value.toLowerCase()
    filtered = filtered.filter(k =>
        k.name?.toLowerCase().includes(keyword) ||
        k.description?.toLowerCase().includes(keyword) ||
        getNodeTypeLabel(k.type)?.toLowerCase().includes(keyword)
    )
  }

  // 分页
  const start = (knowledgePage.current - 1) * knowledgePage.pageSize
  const end = start + knowledgePage.pageSize
  return filtered.slice(start, end)
})

// 表格列定义
const knowledgeColumns = [
  {
    title: '知识条目',
    key: 'name',
    width: 300
  },
  {
    title: '类型',
    key: 'type',
    width: 100
  },
  {
    title: '置信度',
    key: 'confidence',
    width: 120
  },
  {
    title: '创建时间',
    key: 'createTime',
    width: 150
  },
  {
    title: '操作',
    key: 'actions',
    width: 120
  }
]

// 工具函数
const getNodeTypeColor = (type) => {
  const colors = {
    skill: 'blue',
    knowledge: 'green',
    experience: 'orange',
    project: 'purple',
    achievement: 'magenta'
  }
  return colors[type] || 'default'
}

const getNodeTypeLabel = (type) => {
  const labels = {
    skill: '技能',
    knowledge: '知识点',
    experience: '经验',
    project: '项目',
    achievement: '成果'
  }
  return labels[type] || type
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#52c41a'
  if (confidence >= 0.6) return '#faad14'
  return '#ff4d4f'
}

// 业务函数
const loadKnowledgeGraph = async () => {
  state.loading = true
  try {
    const response = await talentApi.getKnowledgeGraph(talentId)
    if (response.graphData) {
      graphData.nodes = response.graphData.nodes || []
      graphData.edges = response.graphData.edges || []
      knowledgeList.value = response.knowledgeList || []
      knowledgePage.total = knowledgeList.value.length
    }
  } catch (error) {
    console.error('加载知识图谱失败:', error)
    message.error('加载知识图谱失败')
  } finally {
    state.loading = false
  }
}

const handleLayoutChange = (value) => {
  layoutType.value = value
  if (graphCanvas.value) {
    graphCanvas.value.changeLayout(value)
  }
}

const handleAutoExtract = async () => {
  state.extracting = true
  try {
    message.loading('正在自动抽取知识图谱...', 0)
    await talentApi.extractKnowledgeGraph(talentId)
    message.destroy()
    message.success('知识图谱抽取成功')
    loadKnowledgeGraph()
  } catch (error) {
    message.destroy()
    console.error('抽取知识图谱失败:', error)
    message.error('抽取知识图谱失败')
  } finally {
    state.extracting = false
  }
}

const handleExportGraph = async () => {
  try {
    const response = await talentApi.exportKnowledgeGraph(talentId)
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `知识图谱_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    message.success('图谱导出成功')
  } catch (error) {
    console.error('导出图谱失败:', error)
    message.error('导出图谱失败')
  }
}

const handleNodeClick = (node) => {
  selectedNode.value = node
  if (graphCanvas.value) {
    graphCanvas.value.highlightNode(node.id)
  }
}

const handleEdgeClick = (edge) => {
  // 处理边点击
  console.log('Edge clicked:', edge)
}

const handleCanvasClick = () => {
  selectedNode.value = null
  if (graphCanvas.value) {
    graphCanvas.value.clearHighlight()
  }
}

const handleZoomIn = () => {
  if (graphCanvas.value) {
    graphCanvas.value.zoomIn()
  }
}

const handleZoomOut = () => {
  if (graphCanvas.value) {
    graphCanvas.value.zoomOut()
  }
}

const handleFitView = () => {
  if (graphCanvas.value) {
    graphCanvas.value.fitView()
  }
}

const handleClearSelection = () => {
  selectedNode.value = null
  if (graphCanvas.value) {
    graphCanvas.value.clearSelection()
  }
}

const handleNodeTypeChange = (value) => {
  newNode.type = value
}

const handleAddNode = async () => {
  if (!newNode.label.trim()) {
    message.error('请输入节点名称')
    return
  }

  try {
    const nodeData = {
      id: `node_${Date.now()}`,
      label: newNode.label,
      type: newNode.type,
      properties: {
        description: newNode.description,
        level: newNode.level,
        confidence: newNode.confidence
      }
    }

    await talentApi.addKnowledgeNode(talentId, nodeData)

    // 添加节点到图谱
    graphData.nodes.push({
      id: nodeData.id,
      label: nodeData.label,
      type: nodeData.type,
      properties: nodeData.properties
    })

    // 添加节点到知识列表
    knowledgeList.value.unshift({
      id: nodeData.id,
      name: nodeData.label,
      type: nodeData.type,
      description: newNode.description,
      confidence: newNode.confidence,
      createTime: new Date().toISOString()
    })

    knowledgePage.total = knowledgeList.value.length

    // 重置表单
    Object.assign(newNode, {
      type: 'skill',
      label: '',
      description: '',
      level: 'intermediate',
      confidence: 0.8
    })

    showAddNodeModal.value = false
    message.success('节点添加成功')
  } catch (error) {
    console.error('添加节点失败:', error)
    message.error('添加节点失败')
  }
}

const handleAddEdge = async () => {
  if (!newEdge.source || !newEdge.target) {
    message.error('请选择源节点和目标节点')
    return
  }

  if (newEdge.source === newEdge.target) {
    message.error('源节点和目标节点不能相同')
    return
  }

  try {
    const edgeData = {
      id: `edge_${Date.now()}`,
      source: newEdge.source,
      target: newEdge.target,
      type: newEdge.type,
      label: newEdge.label || newEdge.type,
      strength: newEdge.strength
    }

    await talentApi.addKnowledgeEdge(talentId, edgeData)

    // 添加关系到图谱
    graphData.edges.push(edgeData)

    // 重置表单
    Object.assign(newEdge, {
      source: '',
      type: 'has',
      target: '',
      strength: 0.5,
      label: ''
    })

    showAddEdgeModal.value = false
    message.success('关系添加成功')
  } catch (error) {
    console.error('添加关系失败:', error)
    message.error('添加关系失败')
  }
}

const handleKnowledgeSearch = () => {
  knowledgePage.current = 1
}

const handleKnowledgePageChange = (pagination) => {
  knowledgePage.current = pagination.current
  knowledgePage.pageSize = pagination.pageSize
}

const locateNode = (nodeId) => {
  const node = graphData.nodes.find(n => n.id === nodeId)
  if (node) {
    selectedNode.value = node
    if (graphCanvas.value) {
      graphCanvas.value.centerNode(nodeId)
      graphCanvas.value.highlightNode(nodeId)
    }
  }
}

const editKnowledge = (record) => {
  message.info('编辑功能开发中')
}

const deleteKnowledge = async (knowledgeId) => {
  try {
    await talentApi.deleteKnowledgeNode(talentId, knowledgeId)

    // 从图谱中移除节点
    const nodeIndex = graphData.nodes.findIndex(n => n.id === knowledgeId)
    if (nodeIndex !== -1) {
      graphData.nodes.splice(nodeIndex, 1)
    }

    // 移除关联的边
    graphData.edges = graphData.edges.filter(edge =>
        edge.source !== knowledgeId && edge.target !== knowledgeId
    )

    // 从知识列表中移除
    const knowledgeIndex = knowledgeList.value.findIndex(k => k.id === knowledgeId)
    if (knowledgeIndex !== -1) {
      knowledgeList.value.splice(knowledgeIndex, 1)
    }

    knowledgePage.total = knowledgeList.value.length
    message.success('知识删除成功')
  } catch (error) {
    console.error('删除知识失败:', error)
    message.error('删除知识失败')
  }
}

onMounted(() => {
  loadKnowledgeGraph()
})
</script>

<style lang="less" scoped>
.talent-knowledge {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #1f1f1f;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.graph-container {
  display: flex;
  gap: 16px;

  .graph-main {
    flex: 1;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    overflow: hidden;
    background: #fff;
  }

  .graph-sidebar {
    width: 280px;
    display: flex;
    flex-direction: column;
    gap: 16px;

    .sidebar-card {
      .graph-stats {
        .stat-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #f0f0f0;

          &:last-child {
            border-bottom: none;
          }

          .stat-label {
            color: #666;
          }

          .stat-value {
            font-weight: 500;
          }
        }
      }

      .node-info {
        .node-header {
          margin-bottom: 12px;

          .node-type-tag {
            margin-bottom: 8px;
          }

          .node-name {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
            color: #333;
          }
        }

        .node-properties {
          margin-bottom: 16px;

          .property-item {
            display: flex;
            margin-bottom: 8px;
            font-size: 14px;

            .property-label {
              color: #666;
              min-width: 60px;
            }

            .property-value {
              color: #333;
              flex: 1;
            }
          }
        }

        .node-connections {
          .connections-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 14px;

            .connections-count {
              color: #999;
            }
          }

          .connections-list {
            max-height: 200px;
            overflow-y: auto;

            .connection-item {
              display: flex;
              align-items: center;
              gap: 8px;
              padding: 8px;
              border-bottom: 1px solid #f0f0f0;

              &:last-child {
                border-bottom: none;
              }

              .connection-type {
                min-width: 60px;
              }

              .connection-target {
                flex: 1;
                font-size: 14px;
                color: #333;
              }
            }
          }
        }
      }

      .graph-actions {
        .ant-btn {
          text-align: left;
        }
      }
    }
  }
}

.knowledge-stats {
  .stats-content {
    .category-stats {
      .category-item {
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }

        .category-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .category-name {
            font-weight: 500;
            color: #333;
          }

          .category-count {
            font-weight: 500;
            color: #1890ff;
          }
        }
      }
    }
  }
}

.knowledge-list {
  :deep(.ant-table) {
    .knowledge-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;

      .knowledge-type {
        flex-shrink: 0;
      }

      .knowledge-content {
        flex: 1;
        min-width: 0;

        .knowledge-name {
          font-weight: 500;
          color: #333;
          margin-bottom: 4px;
          word-break: break-word;
        }

        .knowledge-desc {
          font-size: 12px;
          color: #999;
          line-height: 1.4;
          word-break: break-word;
        }
      }
    }

    .confidence-cell {
      display: flex;
      align-items: center;
      gap: 8px;

      .confidence-value {
        min-width: 40px;
        text-align: right;
        font-size: 12px;
        color: #666;
      }
    }

    .knowledge-actions {
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

.quick-assess-modal, .slider-value {
  margin-left: 12px;
  color: #666;
  font-size: 14px;
}

@media (max-width: 1200px) {
  .graph-container {
    flex-direction: column;

    .graph-sidebar {
      width: 100%;
      flex-direction: row;
      flex-wrap: wrap;

      .sidebar-card {
        flex: 1;
        min-width: 250px;
      }
    }
  }
}

@media (max-width: 768px) {
  .knowledge-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;

    .header-actions {
      justify-content: flex-end;
    }
  }

  .graph-sidebar {
    .sidebar-card {
      min-width: 100% !important;
    }
  }
}
</style>