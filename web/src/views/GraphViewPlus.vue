<template>
  <div class="database-empty" v-if="!state.showPage">
    <a-empty>
      <template #description>
        <span>
          前往 <router-link to="/setting" style="color: var(--main-color); font-weight: bold;">设置</router-link> 页面启用知识图谱。
        </span>
      </template>
    </a-empty>
  </div>
  <div class="graph-container layout-container" v-else>
    <HeaderComponent
      title="图数据库"
    >
      <template #actions>
        <div class="status-wrapper">
          <div class="status-indicator" :class="graphStatusClass"></div>
          <span class="status-text">{{ graphStatusText }}</span>
        </div>
        <a-button type="default" @click="openLink('http://localhost:7474/')" :icon="h(GlobalOutlined)">
          Neo4j 浏览器
        </a-button>
        <a-button type="primary" @click="state.showModal = true" ><UploadOutlined/> 上传文件</a-button>
        <a-button v-if="unindexedCount > 0" type="primary" @click="indexNodes" :loading="state.indexing">
          <SyncOutlined v-if="!state.indexing"/> 为{{ unindexedCount }}个节点添加索引
        </a-button>
      </template>
    </HeaderComponent>

    <div class="container-outter">
      <GraphCanvas
        ref="graphRef"
        :graph-data="graphData"
        :highlight-keywords="[state.searchInput]"
      >
        <template #top>
          <div class="actions">
            <div class="actions-left">
              <a-input
                v-model:value="state.searchInput"
                placeholder="输入要查询的实体"
                style="width: 300px"
                @keydown.enter="onSearch"
                allow-clear
              >
                <template #suffix>
                  <component :is="state.searchLoading ? LoadingOutlined : SearchOutlined" @click="onSearch" />
                </template>
              </a-input>
            </div>
            <div class="actions-right">
              <a-button type="default" @click="state.showInfoModal = true" :icon="h(InfoCircleOutlined)">
                说明
              </a-button>
              <a-input
                v-model:value="sampleNodeCount"
                placeholder="查询三元组数量"
                style="width: 100px"
                @keydown.enter="loadSampleNodes"
                :loading="state.fetching"
              >
                <template #suffix>
                  <component :is="state.fetching ? LoadingOutlined : ReloadOutlined" @click="loadSampleNodes" />
                </template>
              </a-input>
            </div>
          </div>
        </template>
        <template #content>
          <a-empty v-show="graphData.nodes.length === 0" style="padding: 4rem 0;"/>
        </template>
        <template #bottom>
          <div class="footer">
            <GraphInfoPanel
              :graph-info="graphInfo"
              :graph-data="graphData"
              :unindexed-count="unindexedCount"
              :model-matched="modelMatched"
              @index-nodes="indexNodes"
              @export-data="exportGraphData"
            />
          </div>
        </template>
      </GraphCanvas>
    </div>

    <a-modal
      :open="state.showModal" title="上传文件"
      @ok="addDocumentByFile"
      @cancel="() => state.showModal = false"
      ok-text="添加到图数据库" cancel-text="取消"
      :confirm-loading="state.processing">
      <div class="upload">
        <div class="note">
          <p>上传的文件内容参考 test/data/A_Dream_of_Red_Mansions_tiny.jsonl 中的格式：</p>
        </div>
        <a-upload-dragger
          class="upload-dragger"
          v-model:fileList="fileList"
          name="file"
          :fileList="fileList"
          :max-count="1"
          accept=".jsonl"
          action="/api/knowledge/files/upload?allow_jsonl=true"
          :headers="getAuthHeaders()"
          @change="handleFileUpload"
          @drop="handleDrop"
        >
          <p class="ant-upload-text">点击或者把文件拖拽到这里上传</p>
          <p class="ant-upload-hint">
            目前仅支持上传 jsonl 文件。
          </p>
        </a-upload-dragger>
      </div>
    </a-modal>

    <!-- 说明弹窗 -->
    <a-modal
      :open="state.showInfoModal"
      title="图数据库说明"
      @cancel="() => state.showInfoModal = false"
      :footer="null"
      width="600px"
    >
      <div class="info-content">
        <p>本页面展示的是 Neo4j 图数据库中的知识图谱信息。</p>
        <p>具体展示内容包括：</p>
        <ul>
          <li>带有 <code>Entity</code> 标签的节点</li>
          <li>带有 <code>RELATION</code> 类型的关系边</li>
        </ul>
        <p>注意：</p>
        <ul>
          <li>这里仅展示用户上传的实体和关系，不包含知识库中自动创建的图谱。</li>
          <li>查询逻辑基于 <code>graphbase.py</code> 中的 <code>get_sample_nodes</code> 方法实现：</li>
        </ul>
        <pre><code>MATCH (n:Entity)-[r]-&gt;(m:Entity)
RETURN
    {id: elementId(n), name: n.name} AS h,
    {type: r.type, source_id: elementId(n), target_id: elementId(m)} AS r,
    {id: elementId(m), name: m.name} AS t
LIMIT $num</code></pre>
        <p>如需查看完整的 Neo4j 数据库内容，请使用 "Neo4j 浏览器" 按钮访问原生界面。</p>
      </div>
    </a-modal>
  </div>

  <!-- 人员能力详情面板 -->
  <div v-if="selectedPersonData" class="person-capability-panel">
    <div class="panel-header">
      <h3>{{ selectedPersonData.name }} - 能力画像</h3>
      <a-button @click="closePersonPanel" type="text" :icon="h(CloseOutlined)"></a-button>
    </div>

    <div class="capability-sections">
      <div class="capability-section">
        <h4>技术技能</h4>
        <div class="skills-chart">
          <div ref="skillsChartRef" style="width: 100%; height: 300px;"></div>
        </div>
        <div class="skills-list">
          <a-tag v-for="skill in selectedPersonData.capabilities.technical_skills" 
                 :key="skill.skill" 
                 :color="getSkillColor(skill.proficiency)">
            {{ skill.skill }} ({{ Math.round(skill.proficiency * 100) }}%)
          </a-tag>
        </div>
      </div>

      <div class="capability-section">
        <h4>领域专长</h4>
        <div class="domain-expertise">
          <a-list :data-source="selectedPersonData.capabilities.domain_expertise" size="small">
            <template #renderItem="{ item }">
              <a-list-item>
                <div class="domain-item">
                  <span class="domain-name">{{ item.domain }}</span>
                  <a-progress 
                    :percent="item.project_count * 20" 
                    :show-info="false" 
                    :stroke-color="getDomainColor(item.project_count)" />
                  <span class="project-count">{{ item.project_count }}个项目</span>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </div>

      <div class="capability-section">
        <h4>潜在能力</h4>
        <div class="hidden-capabilities">
          <a-list :data-source="selectedPersonData.capabilities.hidden_capabilities" size="small">
            <template #renderItem="{ item }">
              <a-list-item>
                <div class="capability-item">
                  <span>{{ item.skill }}</span>
                  <a-tag color="orange">推测</a-tag>
                  <span class="confidence">置信度: {{ Math.round(item.confidence * 100) }}%</span>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </div>

      <div class="capability-section">
        <h4>综合评估</h4>
        <div class="overall-assessment">
          <div class="assessment-item">
            <span>领导潜力:</span>
            <a-rate :value="selectedPersonData.capabilities.leadership_potential" disabled />
          </div>
          <div class="assessment-item">
            <span>创新能力:</span>
            <a-rate :value="selectedPersonData.capabilities.innovation_ability" disabled />
          </div>
          <div class="assessment-item">
            <span>协作能力:</span>
            <a-rate :value="selectedPersonData.capabilities.collaboration_strength" disabled />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, h, onUnmounted, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import * as echarts from 'echarts';
import { useConfigStore } from '@/stores/config';
import { 
  UploadOutlined, 
  SyncOutlined, 
  GlobalOutlined, 
  InfoCircleOutlined, 
  SearchOutlined, 
  ReloadOutlined, 
  LoadingOutlined, 
  CloseOutlined 
} from '@ant-design/icons-vue';
import HeaderComponent from '@/components/HeaderComponent.vue';
import { neo4jApi } from '@/apis/graph_api';
import { useUserStore } from '@/stores/user';
import GraphCanvas from '@/components/GraphCanvas.vue';
import GraphInfoPanel from '@/components/GraphInfoPanel.vue';

const configStore = useConfigStore();
const cur_embed_model = computed(() => configStore.config?.embed_model);
const modelMatched = computed(() => !graphInfo?.value?.embed_model_name || graphInfo.value.embed_model_name === cur_embed_model.value)

const graphRef = ref(null)
const graphInfo = ref(null)
const fileList = ref([]);
const sampleNodeCount = ref(100);
const graphData = reactive({
  nodes: [],
  edges: [],
});

// 人员能力面板相关
const selectedPersonData = ref(null);
const skillsChartRef = ref(null);
let skillsChart = null;

const state = reactive({
  fetching: false,
  loadingGraphInfo: false,
  searchInput: '',
  searchLoading: false,
  showModal: false,
  showInfoModal: false,
  processing: false,
  indexing: false,
  showPage: true,
})

// 计算未索引节点数量
const unindexedCount = computed(() => {
  return graphInfo.value?.unindexed_node_count || 0;
});

const loadGraphInfo = () => {
  state.loadingGraphInfo = true
  neo4jApi.getInfo()
    .then(data => {
      console.log(data)
      graphInfo.value = data.data
      state.loadingGraphInfo = false
    })
    .catch(error => {
      console.error(error)
      message.error(error.message || '加载图数据库信息失败')
      state.loadingGraphInfo = false
    })
}

const addDocumentByFile = () => {
  state.processing = true
  const files = fileList.value.filter(file => file.status === 'done').map(file => file.response.file_path)
  neo4jApi.addEntities(files[0])
    .then((data) => {
      if (data.status === 'success') {
        message.success(data.message);
        state.showModal = false;
      } else {
        throw new Error(data.message);
      }
    })
    .catch((error) => {
      console.error(error)
      message.error(error.message || '添加文件失败');
    })
    .finally(() => state.processing = false)
};

const loadSampleNodes = () => {
  state.fetching = true
  neo4jApi.getSampleNodes('neo4j', sampleNodeCount.value)
    .then((data) => {
      graphData.nodes = data.result.nodes
      graphData.edges = data.result.edges
      console.log(graphData)
      // 初次加载后兜底刷新一次，避免容器初次可见尺寸未稳定
      setTimeout(() => graphRef.value?.refreshGraph?.(), 500)
    })
    .catch((error) => {
      console.error(error)
      message.error(error.message || '加载节点失败');
    })
    .finally(() => state.fetching = false)
}

const onSearch = () => {
  if (state.searchLoading) {
    message.error('请稍后再试')
    return
  }

  if (graphInfo?.value?.embed_model_name !== cur_embed_model.value) {
    // 可选：提示模型不一致
  }

  if (!state.searchInput) {
    message.error('请输入要查询的实体')
    return
  }

  state.searchLoading = true
  neo4jApi.queryNode(state.searchInput)
    .then((data) => {
      if (!data.result || !data.result.nodes || !data.result.edges) {
        throw new Error('返回数据格式不正确');
      }
      graphData.nodes = data.result.nodes
      graphData.edges = data.result.edges
      if (graphData.nodes.length === 0) {
        message.info('未找到相关实体')
      }
      console.log(data)
      console.log(graphData)
      graphRef.value?.refreshGraph?.()
    })
    .catch((error) => {
      console.error('查询错误:', error);
      message.error(`查询出错：${error.message || '未知错误'}`);
    })
    .finally(() => state.searchLoading = false)
};

// 模拟人员能力分析
const simulatePersonAnalysis = (personName) => {
  // 使用假数据模拟分析结果
  selectedPersonData.value = {
    name: personName,
    capabilities: {
      technical_skills: [
        { skill: "Python", proficiency: 0.95 },
        { skill: "机器学习", proficiency: 0.88 },
        { skill: "数据分析", proficiency: 0.92 },
        { skill: "深度学习", proficiency: 0.85 },
        { skill: "Java", proficiency: 0.75 },
        { skill: "云计算", proficiency: 0.80 }
      ],
      domain_expertise: [
        { domain: "金融科技", project_count: 5 },
        { domain: "电商推荐", project_count: 3 },
        { domain: "医疗影像", project_count: 2 },
        { domain: "智能客服", project_count: 4 }
      ],
      hidden_capabilities: [
        { skill: "区块链技术", confidence: 0.75 },
        { skill: "自然语言处理", confidence: 0.82 },
        { skill: "边缘计算", confidence: 0.68 }
      ],
      leadership_potential: 4,
      innovation_ability: 5,
      collaboration_strength: 4
    }
  };
  
  // 在下次DOM更新后初始化图表
  nextTick(() => {
    initSkillsChart();
  });
};

// 初始化技能雷达图
const initSkillsChart = () => {
  if (skillsChartRef.value) {
    if (skillsChart) {
      skillsChart.dispose();
    }
    
    skillsChart = echarts.init(skillsChartRef.value);
    
    const skills = selectedPersonData.value.capabilities.technical_skills;
    const option = {
      radar: {
        indicator: skills.map(skill => ({
          name: skill.skill,
          max: 100
        })),
        shape: 'polygon',
        splitNumber: 5,
        axisName: {
          color: 'var(--gray-700)',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            color: 'var(--gray-200)'
          }
        },
        splitArea: {
          show: false
        },
        axisLine: {
          lineStyle: {
            color: 'var(--gray-200)'
          }
        }
      },
      series: [{
        name: '技能雷达图',
        type: 'radar',
        lineStyle: {
          width: 2,
          color: '#4096ff'
        },
        data: [
          {
            value: skills.map(skill => Math.round(skill.proficiency * 100)),
            name: '技能熟练度',
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: '#4096ff'
            },
            areaStyle: {
              color: 'rgba(64, 150, 255, 0.3)'
            }
          }
        ]
      }]
    };
    
    skillsChart.setOption(option);
  }
};

// 获取技能标签颜色
const getSkillColor = (proficiency) => {
  if (proficiency >= 0.9) return 'green';
  if (proficiency >= 0.7) return 'blue';
  if (proficiency >= 0.5) return 'orange';
  return 'red';
};

// 获取领域专长进度条颜色
const getDomainColor = (count) => {
  if (count >= 4) return '#52c41a';
  if (count >= 3) return '#1890ff';
  if (count >= 2) return '#faad14';
  return '#ff4d4f';
};

// 关闭人员面板
const closePersonPanel = () => {
  selectedPersonData.value = null;
  if (skillsChart) {
    skillsChart.dispose();
    skillsChart = null;
  }
};

onMounted(() => {
  loadGraphInfo();
  loadSampleNodes();
  
  // 模拟点击某个人员节点来展示能力面板
  setTimeout(() => {
    simulatePersonAnalysis("张三");
  }, 1000);
});

onUnmounted(() => {
  if (skillsChart) {
    skillsChart.dispose();
  }
});

const handleFileUpload = (event) => {
  console.log(event)
  console.log(fileList.value)
}

const handleDrop = (event) => {
  console.log(event)
  console.log(fileList.value)
}

const graphStatusClass = computed(() => {
  if (state.loadingGraphInfo) return 'loading';
  return graphInfo.value?.status === 'open' ? 'open' : 'closed';
});

const graphStatusText = computed(() => {
  if (state.loadingGraphInfo) return '加载中';
  return graphInfo.value?.status === 'open' ? '已连接' : '已关闭';
});


// 为未索引节点添加索引
const indexNodes = () => {
  // 判断 embed_model_name 是否相同
  if (!modelMatched.value) {
    message.error(`向量模型不匹配，无法添加索引，当前向量模型为 ${cur_embed_model.value}，图数据库向量模型为 ${graphInfo.value?.embed_model_name}`)
    return
  }

  if (state.processing) {
    message.error('后台正在处理，请稍后再试')
    return
  }

  state.indexing = true;
  neo4jApi.indexEntities('neo4j')
    .then(data => {
      message.success(data.message || '索引添加成功');
      // 刷新图谱信息
      loadGraphInfo();
    })
    .catch(error => {
      console.error(error);
      message.error(error.message || '添加索引失败');
    })
    .finally(() => {
      state.indexing = false;
    });
};

const exportGraphData = () => {
  const dataStr = JSON.stringify({
    nodes: graphData.nodes,
    edges: graphData.edges,
    graphInfo: graphInfo.value,
    exportTime: new Date().toISOString()
  }, null, 2);

  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `graph-data-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  message.success('图谱数据已导出');
};

const getAuthHeaders = () => {
  const userStore = useUserStore();
  return userStore.getAuthHeaders();
};

const openLink = (url) => {
  window.open(url, '_blank')
}

// 监听窗口大小变化，重新调整图表大小
window.addEventListener('resize', () => {
  if (skillsChart) {
    skillsChart.resize();
  }
});
</script>

<style lang="less" scoped>
@graph-header-height: 55px;

.graph-container {
  padding: 0;
  background-color: var(--gray-0);

  .header-container {
    height: @graph-header-height;
  }
}

.status-wrapper {
  display: flex;
  align-items: center;
  margin-right: 16px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.status-text {
  margin-left: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;

  &.loading {
    background-color: var(--color-warning);
    animation: pulse 1.5s infinite ease-in-out;
  }

  &.open {
    background-color: var(--color-success);
  }

  &.closed {
    background-color: var(--color-error);
  }
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}

.upload {
  margin-bottom: 20px;

  .upload-dragger {
    margin: 0px;
  }
}

.container-outter {
  width: 100%;
  height: calc(100vh - @graph-header-height);
  overflow: hidden;
  background: var(--gray-10);

  .actions,
  .footer {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    padding: 0 24px;
    width: 100%;
  }

  .tags {
    display: flex;
    gap: 8px;
  }
}

.actions {
  top: 0;

  .actions-left, .actions-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  :deep(.ant-input) {
    padding: 2px 10px;
  }

  button {
    height: 37px;
    box-shadow: none;
  }
}

// 人员能力面板样式
.person-capability-panel {
  position: absolute;
  top: 70px;
  right: 20px;
  width: 400px;
  max-height: calc(100vh - 100px);
  background: var(--gray-0);
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow-y: auto;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-25);

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--gray-900);
    }
  }

  .capability-sections {
    padding: 16px;

    .capability-section {
      margin-bottom: 24px;

      &:last-child {
        margin-bottom: 0;
      }

      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--gray-800);
        border-bottom: 1px solid var(--gray-100);
        padding-bottom: 8px;
      }

      .skills-chart {
        margin-bottom: 16px;
      }

      .skills-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .domain-expertise {
        .domain-item {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;

          .domain-name {
            flex: 0 0 80px;
            font-size: 12px;
          }

          :deep(.ant-progress) {
            flex: 1;
          }

          .project-count {
            flex: 0 0 60px;
            font-size: 12px;
            color: var(--gray-600);
            text-align: right;
          }
        }
      }

      .hidden-capabilities {
        .capability-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;

          .confidence {
            margin-left: auto;
            color: var(--gray-600);
          }
        }
      }

      .overall-assessment {
        .assessment-item {
          display: flex;
          align-items: center;
          margin-bottom: 12px;
          gap: 12px;

          &:last-child {
            margin-bottom: 0;
          }

          span:first-child {
            width: 80px;
            font-size: 12px;
          }

          :deep(.ant-rate) {
            font-size: 14px;
          }
        }
      }
    }
  }
}
</style>
