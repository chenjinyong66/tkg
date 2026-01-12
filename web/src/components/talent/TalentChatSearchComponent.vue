<template>
  <div class="talent-chat-search-container" ref="chatContainerRef">
    <div class="talent-chat-layout">
      <!-- 左侧聊天区域 -->
      <div class="talent-chat-main" :class="{
        'expanded': !showResultsPanel || shouldHideResultsPanel,
        'hide-border': shouldHideResultsPanel
      }">

        <!-- 侧边栏抽屉 -->
        <div class="sidebar-drawer" :class="{ 'open': showSidebar }">
          <div class="drawer-header">
            <h3>对话历史</h3>
            <Button type="text" @click="toggleSidebar" class="close-btn">
              <X size="16" />
            </Button>
          </div>
          <div class="drawer-content">
            <div class="chats-list">
              <div
                  v-for="chat in chatsList"
                  :key="chat.id"
                  class="chat-item"
                  :class="{ active: chat.id === currentChatId }"
                  @click="selectChat(chat.id)"
              >
                <div class="chat-title">{{ chat.title }}</div>
                <div class="chat-time">{{ formatTime(chat.created_at || chat.created_at) }}</div>
              </div>
            </div>
            <Button
                type="primary"
                block
                @click="createNewChat"
                :loading="chatUIStore.creatingNewChat"
            >
              <Plus size="14" />
              新建对话
            </Button>
          </div>
        </div>


        <div class="chat-header">
          <div class="header__left">
            <div class="agent-nav-btn" @click="toggleSidebar">
              <PanelLeftOpen class="nav-btn-icon" size="18"/>
            </div>
            <div class="agent-nav-btn" @click="createNewChat">
              <LoaderCircle v-if="chatUIStore.creatingNewChat" class="nav-btn-icon loading-icon" size="18"/>
              <MessageCirclePlus v-else class="nav-btn-icon" size="18"/>
              <span class="text">新对话</span>
            </div>
          </div>
          <div class="header__right">
            <slot name="header-right"></slot>
          </div>
        </div>

        <!-- 聊天消息区域 -->
        <div class="chat-box" ref="messagesContainer">
          <div class="conv-box" v-for="(conv, index) in conversations" :key="index">
            <AgentMessageComponent
                v-for="(message, msgIndex) in conv.messages"
                :message="message"
                :key="msgIndex"
                :is-processing="isProcessing && conv.status === 'streaming' && msgIndex === conv.messages.length - 1"
                :show-refs="showMsgRefs(message)"
                @retry="retryMessage(message)"
            >
            </AgentMessageComponent>
            <!-- 显示对话最后一个消息使用的模型 -->
            <RefsComponent
                v-if="shouldShowRefs(conv)"
                :message="getLastMessage(conv)"
                :show-refs="['model', 'copy']"
                :is-latest-message="false"
            />
          </div>

          <!-- 生成中的加载状态 -->
          <div class="generating-status" v-if="isProcessing && conversations.length > 0">
            <div class="generating-indicator">
              <div class="loading-dots">
                <div></div>
                <div></div>
                <div></div>
              </div>
              <span class="generating-text">正在生成回复...</span>
            </div>
          </div>
        </div>

        <!-- 消息输入区域 -->
        <div class="bottom">
          <!-- 人工审批弹窗 -->
          <HumanApprovalModal
              :visible="approvalState.showModal"
              :question="approvalState.question"
              :operation="approvalState.operation"
              @approve="handleApprove"
              @reject="handleReject"
          />

          <div class="message-input-wrapper">
            <AgentInputArea
                ref="messageInputRef"
                v-model="userInput"
                :is-loading="isProcessing"
                :disabled="!currentAgent"
                :send-button-disabled="(!userInput || !currentAgent) && !isProcessing"
                placeholder="输入问题..."
                :supports-file-upload="supportsFileUpload"
                :agent-id="currentAgentId"
                :thread-id="currentChatId"
                :ensure-thread="ensureActiveThread"
                @send="handleSendOrStop"
            />

            <!-- 示例问题 -->
            <div class="example-questions" v-if="!conversations.length && exampleQuestions.length > 0">
              <div class="example-chips">
                <div
                    v-for="question in exampleQuestions"
                    :key="question.id"
                    class="example-chip"
                    @click="handleExampleClick(question.text)"
                >
                  {{ question.text }}
                </div>
              </div>
            </div>

            <div class="bottom-actions" v-else>
              <p class="note">请注意辨别内容的可靠性</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧结果表格区域 -->
      <div
          class="talent-results-panel"
          :class="{
          'collapsed': !showResultsPanel,
          'hidden': shouldHideResultsPanel,
          'expanded': showResultsPanel && !shouldHideResultsPanel
        }"
      >
        <div class="results-header">
          <h3 v-if="!shouldHideResultsPanel">查询结果</h3>
          <div class="results-header-right" v-if="!shouldHideResultsPanel">
            <span class="results-count" v-if="searchResults.length > 0">
              共 {{ searchResults.length }} 条结果
            </span>
            <Button
                type="text"
                @click="toggleResultsPanel"
                class="toggle-btn"
            >
              <PanelRightClose v-if="showResultsPanel" size="16" />
              <PanelRightOpen v-else size="16" />
            </Button>
          </div>
        </div>

        <div class="results-content" v-if="showResultsPanel && !shouldHideResultsPanel">
          <div class="results-controls">
            <div class="results-filters">
              <span class="filter-label">匹配度筛选:</span>
              <Select
                  v-model:value="matchScoreFilter"
                  style="width: 120px"
                  size="small"
              >
                <SelectOption value="all">全部</SelectOption>
                <SelectOption value="high">高(≥80%)</SelectOption>
                <SelectOption value="medium">中(≥60%)</SelectOption>
                <SelectOption value="low">低(≥40%)</SelectOption>
              </Select>
              <Button
                  size="small"
                  @click="refreshResults"
                  :disabled="loadingResults"
                  :loading="loadingResults"
              >
                <RefreshCw size="14" />
                刷新
              </Button>
            </div>
          </div>

          <div class="results-table-container">
            <Table
                :columns="filteredTableColumns"
                :data-source="filteredSearchResults"
                :loading="loadingResults"
                :pagination="{ pageSize: 10, showSizeChanger: true }"
                row-key="id"
                :scroll="{ y: 400 }"
            >
              <template #bodyCell="{ column, text, record }">
                <template v-if="column.key === 'matchScore'">
                  <div class="match-score-cell">
                    <div class="match-score-bar">
                      <div
                          class="match-score-fill"
                          :style="{ width: text + '%' }"
                          :class="getMatchScoreClass(text)"
                      ></div>
                      <span class="match-score-text">{{ text }}%</span>
                    </div>
                  </div>
                </template>
                <template v-else-if="column.key === 'matchStatus'">
                  <span :class="getMatchStatusClass(record.matchScore)">
                    {{ getMatchStatusText(record.matchScore) }}
                  </span>
                </template>
                <template v-else-if="column.key === 'actions'">
                  <Space size="middle">
                    <Button type="link" size="small" @click="viewTalentDetail(record)">
                      查看详情
                    </Button>
                    <Button
                        type="link"
                        size="small"
                        @click="addToShortlist(record)"
                        v-if="!record.isShortlisted"
                    >
                      加入候选
                    </Button>
                    <Button
                        type="link"
                        size="small"
                        @click="removeFromShortlist(record)"
                        v-else
                        class="shortlisted"
                    >
                      已候选
                    </Button>
                  </Space>
                </template>
              </template>
            </Table>
          </div>

          <!-- 候选列表摘要 -->
          <div class="shortlist-summary" v-if="shortlist.length > 0">
            <div class="shortlist-header">
              <h4>候选名单 ({{ shortlist.length }}人)</h4>
              <Button
                  type="link"
                  size="small"
                  @click="clearShortlist"
                  :disabled="loadingResults"
              >
                清空
              </Button>
            </div>
            <div class="shortlist-items">
              <div
                  v-for="talent in shortlist"
                  :key="talent.id"
                  class="shortlist-item"
              >
                <span class="shortlist-name">{{ talent.name }}</span>
                <span class="shortlist-match">{{ talent.matchScore }}%</span>
                <Button
                    type="text"
                    size="small"
                    @click="removeFromShortlist(talent)"
                    class="remove-btn"
                >
                  <X size="12" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, computed, onUnmounted } from 'vue';
import { message, Table, Button, Space, Select, SelectOption } from 'ant-design-vue';
import AgentInputArea from '@/components/AgentInputArea.vue'
import AgentMessageComponent from '@/components/AgentMessageComponent.vue'
import RefsComponent from '@/components/RefsComponent.vue'
import { PanelLeftOpen, MessageCirclePlus, LoaderCircle, PanelRightOpen, PanelRightClose, RefreshCw, X, Plus } from 'lucide-vue-next';
import { handleChatError, handleValidationError } from '@/utils/errorHandler';
import { ScrollController } from '@/utils/scrollController';
import { AgentValidator } from '@/utils/agentValidator';
import { useAgentStore } from '@/stores/agent';
import { useChatUIStore } from '@/stores/chatUI';
import { storeToRefs } from 'pinia';
import { MessageProcessor } from '@/utils/messageProcessor';
import { agentApi, threadApi } from '@/apis';
import { talentSearchApi } from '@/apis/talentSearchApi';
import { formatTalentSearchResults, parseSearchQueryFilters } from '@/utils/talentSearchUtils';
import HumanApprovalModal from '@/components/HumanApprovalModal.vue';
import { useApproval } from '@/composables/useApproval';
import { useAgentStreamHandler } from '@/composables/useAgentStreamHandler';

// ==================== PROPS & EMITS ====================
const props = defineProps({
  agentId: { type: String, default: '' },
  singleMode: { type: Boolean, default: true }
});
const emit = defineEmits(['open-config', 'open-agent-modal']);

// ==================== STORE MANAGEMENT ====================
const agentStore = useAgentStore();
const chatUIStore = useChatUIStore();
const {
  agents,
  selectedAgentId,
  defaultAgentId,
} = storeToRefs(agentStore);

// ==================== LOCAL CHAT & UI STATE ====================
const userInput = ref('');
// 默认显示结果面板，但有对话时才显示
const showResultsPanel = ref(true);
const showSidebar = ref(false);
const searchResults = ref([]);
const loadingResults = ref(false);
const matchScoreFilter = ref('all');
const shortlist = ref([]); // 候选名单

// ==================== COMPUTED PROPERTIES ====================
// 计算是否应该隐藏结果面板
const shouldHideResultsPanel = computed(() => {
  // 当没有对话历史且没有进行中的对话时，隐藏右侧面板
  return conversations.value.length === 0 && onGoingConvMessages.value.length === 0;
});

// 过滤后的搜索结果
const filteredSearchResults = computed(() => {
  let results = [...searchResults.value];

  // 根据匹配度筛选
  if (matchScoreFilter.value !== 'all') {
    results = results.filter(talent => {
      const score = talent.matchScore || 0;
      switch (matchScoreFilter.value) {
        case 'high': return score >= 80;
        case 'medium': return score >= 60;
        case 'low': return score >= 40;
        default: return true;
      }
    });
  }

  return results;
});

// 从智能体元数据获取示例问题
const exampleQuestions = computed(() => {
  const agentId = currentAgentId.value;
  let examples = [];
  if (agentId && agents.value && agents.value.length > 0) {
    const agent = agents.value.find(a => a.id === agentId);
    examples = agent ? (agent.examples || []) : [];
  }
  return examples.map((text, index) => ({
    id: index + 1,
    text: text
  }));
});

// Keep per-thread streaming scratch data in a consistent shape.
const createOnGoingConvState = () => ({
  msgChunks: {},
  currentRequestKey: null,
  currentAssistantKey: null,
  toolCallBuffers: {}
});

// 业务状态（保留在组件本地）
const chatState = reactive({
  currentThreadId: null,
  // 以threadId为键的线程状态
  threadStates: {}
});

// 组件级别的线程和消息状态
const threads = ref([]);
const threadMessages = ref({});

// 本地 UI 状态（仅在本组件使用）
const localUIState = reactive({
  isInitialRender: true,
  containerWidth: 0,
});

// ==================== COMPUTED PROPERTIES ====================
const currentAgentId = computed(() => {
  if (props.singleMode) {
    return props.agentId || defaultAgentId.value;
  } else {
    return selectedAgentId.value;
  }
});

const currentAgentName = computed(() => {
  const agentId = currentAgentId.value;
  if (agentId && agents.value && agents.value.length > 0) {
    const agent = agents.value.find(a => a.id === agentId);
    return agent ? agent.name : '智能体';
  }
  return '智能体加载中……';
});

const currentAgent = computed(() => {
  if (!currentAgentId.value || !agents.value || !agents.value.length) return null;
  return agents.value.find(a => a.id === currentAgentId.value) || null;
});
const chatsList = computed(() => threads.value || []);
const currentChatId = computed(() => chatState.currentThreadId);
const currentThread = computed(() => {
  if (!currentChatId.value) return null;
  return threads.value.find(thread => thread.id === currentChatId.value) || null;
});

// 检查当前智能体是否支持文件上传
const supportsFileUpload = computed(() => {
  if (!currentAgent.value) return false;
  const capabilities = currentAgent.value.capabilities || [];
  return capabilities.includes('file_upload');
});

// 当前线程状态的computed属性
const currentThreadState = computed(() => {
  return getThreadState(currentChatId.value);
});

const onGoingConvMessages = computed(() => {
  const threadState = currentThreadState.value;
  if (!threadState || !threadState.onGoingConv) return [];

  const msgs = Object.values(threadState.onGoingConv.msgChunks).map(MessageProcessor.mergeMessageChunk);
  return msgs.length > 0
      ? MessageProcessor.convertToolResultToMessages(msgs).filter(msg => msg.type !== 'tool')
      : [];
});
const currentThreadMessages = computed(() => threadMessages.value[currentChatId.value] || []);

const historyConversations = computed(() => {
  return MessageProcessor.convertServerHistoryToMessages(currentThreadMessages.value);
});

const conversations = computed(() => {
  const historyConvs = historyConversations.value;

  // 如果有进行中的消息且线程状态显示正在流式处理，添加进行中的对话
  if (onGoingConvMessages.value.length > 0) {
    const onGoingConv = {
      messages: onGoingConvMessages.value,
      status: 'streaming'
    };
    return [...historyConvs, onGoingConv];
  }
  return historyConvs;
});

const isLoadingMessages = computed(() => chatUIStore.isLoadingMessages);
const isStreaming = computed(() => {
  const threadState = currentThreadState.value;
  return threadState ? threadState.isStreaming : false;
});
const isProcessing = computed(() => isStreaming.value);
const isSmallContainer = computed(() => localUIState.containerWidth <= 520);
const isMediumContainer = computed(() => localUIState.containerWidth <= 768);

// 表格列定义（添加匹配度相关列）
const tableColumns = [
  {
    title: '姓名',
    dataIndex: 'name',
    key: 'name',
    width: 100,
    fixed: 'left',
  },
  {
    title: '匹配度',
    dataIndex: 'matchScore',
    key: 'matchScore',
    width: 120,
    sorter: (a, b) => (a.matchScore || 0) - (b.matchScore || 0),
    sortDirections: ['descend', 'ascend'],
  },
  {
    title: '匹配状态',
    dataIndex: 'matchStatus',
    key: 'matchStatus',
    width: 100,
    filters: [
      { text: '高度匹配', value: 'high' },
      { text: '中度匹配', value: 'medium' },
      { text: '低度匹配', value: 'low' },
      { text: '不匹配', value: 'none' },
    ],
    onFilter: (value, record) => {
      const score = record.matchScore || 0;
      if (value === 'high') return score >= 80;
      if (value === 'medium') return score >= 60 && score < 80;
      if (value === 'low') return score >= 40 && score < 60;
      return score < 40;
    },
  },
  {
    title: '职位',
    dataIndex: 'position',
    key: 'position',
    width: 120,
  },
  {
    title: '部门',
    dataIndex: 'department',
    key: 'department',
    width: 100,
  },
  {
    title: '职称',
    dataIndex: 'title',
    key: 'title',
    width: 100,
  },
  {
    title: '技术专家等级',
    dataIndex: 'expertLevel',
    key: 'expertLevel',
    width: 120,
  },
  {
    title: '项目经验',
    dataIndex: 'projectExperience',
    key: 'projectExperience',
    width: 150,
    ellipsis: true,
  },
  {
    title: '专利/论文',
    dataIndex: 'patentsPapers',
    key: 'patentsPapers',
    width: 120,
    ellipsis: true,
  },
  {
    title: '技能',
    dataIndex: 'skills',
    key: 'skills',
    width: 150,
    ellipsis: true,
    customRender: ({ text }) => Array.isArray(text) ? text.join(', ') : text || '-'
  },
  {
    title: '经验',
    dataIndex: 'experience',
    key: 'experience',
    width: 80,
  },
  {
    title: '学历',
    dataIndex: 'education',
    key: 'education',
    width: 80,
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    fixed: 'right',
  },
];

// 根据屏幕宽度动态调整列
const filteredTableColumns = computed(() => {
  if (isSmallContainer.value) {
    // 小屏幕只显示关键列
    return tableColumns.filter(col =>
        ['name', 'matchScore', 'matchStatus', 'position', 'actions'].includes(col.key)
    ).map(col => ({
      ...col,
      width: col.key === 'name' ? 80 :
          col.key === 'matchScore' ? 100 :
              col.key === 'matchStatus' ? 90 :
                  col.key === 'position' ? 100 :
                      col.key === 'actions' ? 120 : col.width
    }));
  } else if (isMediumContainer.value) {
    // 中等屏幕显示部分列
    return tableColumns.filter(col =>
        ['name', 'matchScore', 'matchStatus', 'position', 'department', 'expertLevel', 'actions'].includes(col.key)
    );
  }
  return tableColumns;
});

// 计算是否显示Refs组件的条件
const shouldShowRefs = computed(() => {
  return (conv) => {
    return getLastMessage(conv) &&
        conv.status !== 'streaming' &&
        !approvalState.showModal &&
        !(approvalState.threadId &&
            chatState.currentThreadId === approvalState.threadId &&
            isProcessing.value);
  };
});

// ==================== SCROLL & RESIZE HANDLING ====================
const chatContainerRef = ref(null);
const scrollController = new ScrollController('.talent-chat-main');
let resizeObserver = null;

onMounted(() => {
  nextTick(() => {
    if (chatContainerRef.value) {
      localUIState.containerWidth = chatContainerRef.value.offsetWidth;
      resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
          localUIState.containerWidth = entry.contentRect.width;
        }
      });
      resizeObserver.observe(chatContainerRef.value);
    }
    const chatContainer = document.querySelector('.talent-chat-main');
    if (chatContainer) {
      chatContainer.addEventListener('scroll', scrollController.handleScroll, { passive: true });
    }
  });
  setTimeout(() => { localUIState.isInitialRender = false; }, 300);
});

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect();
  scrollController.cleanup();
  // 清理所有线程状态
  resetOnGoingConv();
});

// ==================== THREAD STATE MANAGEMENT ====================
// 获取指定线程的状态，如果不存在则创建
const getThreadState = (threadId) => {
  if (!threadId) return null;
  if (!chatState.threadStates[threadId]) {
    chatState.threadStates[threadId] = {
      isStreaming: false,
      streamAbortController: null,
      onGoingConv: createOnGoingConvState(),
      agentState: null  // 添加 agentState 字段
    };
  }
  return chatState.threadStates[threadId];
};

// 清理指定线程的状态
const cleanupThreadState = (threadId) => {
  if (!threadId) return;
  const threadState = chatState.threadStates[threadId];
  if (threadState) {
    if (threadState.streamAbortController) {
      threadState.streamAbortController.abort();
    }
    delete chatState.threadStates[threadId];
  }
};

// ==================== STREAM HANDLING LOGIC ====================
const resetOnGoingConv = (threadId = null) => {
  console.log(`🔄 [RESET] Resetting on going conversation: ${new Date().toLocaleTimeString()}.${new Date().getMilliseconds()}`, threadId);

  const targetThreadId = threadId || currentChatId.value;

  if (targetThreadId) {
    // 清理指定线程的状态
    const threadState = getThreadState(targetThreadId);
    if (threadState) {
      if (threadState.streamAbortController) {
        threadState.streamAbortController.abort();
        threadState.streamAbortController = null;
      }

      // 直接重置对话状态
      threadState.onGoingConv = createOnGoingConvState();
    }
  } else {
    // 如果没有当前线程，清理所有线程状态
    Object.keys(chatState.threadStates).forEach(tid => {
      cleanupThreadState(tid);
    });
  }
};

// ==================== 匹配度相关方法 ====================
// 获取匹配度样式类
const getMatchScoreClass = (score) => {
  if (score >= 80) return 'match-high';
  if (score >= 60) return 'match-medium';
  if (score >= 40) return 'match-low';
  return 'match-none';
};

// 获取匹配状态文本
const getMatchStatusText = (score) => {
  if (score >= 80) return '高度匹配';
  if (score >= 60) return '中度匹配';
  if (score >= 40) return '低度匹配';
  return '不匹配';
};

// 获取匹配状态样式类
const getMatchStatusClass = (score) => {
  const baseClass = 'match-status';
  if (score >= 80) return `${baseClass} status-high`;
  if (score >= 60) return `${baseClass} status-medium`;
  if (score >= 40) return `${baseClass} status-low`;
  return `${baseClass} status-none`;
};

// ==================== 候选名单管理 ====================
// 添加到候选名单
const addToShortlist = (talent) => {
  if (!shortlist.value.find(item => item.id === talent.id)) {
    const talentWithStatus = {
      ...talent,
      isShortlisted: true,
      shortlistedAt: new Date().toISOString()
    };
    shortlist.value.push(talentWithStatus);

    // 更新搜索结果中的状态
    const index = searchResults.value.findIndex(item => item.id === talent.id);
    if (index !== -1) {
      searchResults.value[index].isShortlisted = true;
    }

    message.success(`已将 ${talent.name} 加入候选名单`);
  }
};

// 从候选名单移除
const removeFromShortlist = (talent) => {
  shortlist.value = shortlist.value.filter(item => item.id !== talent.id);

  // 更新搜索结果中的状态
  const index = searchResults.value.findIndex(item => item.id === talent.id);
  if (index !== -1) {
    searchResults.value[index].isShortlisted = false;
  }

  message.info(`已将 ${talent.name} 从候选名单移除`);
};

// 清空候选名单
const clearShortlist = () => {
  // 清除所有人才的候选状态
  searchResults.value.forEach(talent => {
    talent.isShortlisted = false;
  });
  shortlist.value = [];
  message.info('已清空候选名单');
};

// ==================== 线程管理方法 ====================
// 获取当前智能体的线程列表
const fetchThreads = async (agentId = null) => {
  const targetAgentId = agentId || currentAgentId.value;
  if (!targetAgentId) return;

  chatUIStore.isLoadingThreads = true;
  try {
    const fetchedThreads = await threadApi.getThreads(targetAgentId);
    threads.value = fetchedThreads || [];
  } catch (error) {
    console.error('Failed to fetch threads:', error);
    handleChatError(error, 'fetch');
    throw error;
  } finally {
    chatUIStore.isLoadingThreads = false;
  }
};

// 创建新线程
const createThread = async (agentId, title = '新的对话') => {
  if (!agentId) return null;

  chatState.isCreatingThread = true;
  try {
    const thread = await threadApi.createThread(agentId, title);
    if (thread) {
      threads.value.unshift(thread);
      threadMessages.value[thread.id] = [];
    }
    return thread;
  } catch (error) {
    console.error('Failed to create thread:', error);
    handleChatError(error, 'create');
    throw error;
  } finally {
    chatState.isCreatingThread = false;
  }
};

// 删除线程
const deleteThread = async (threadId) => {
  if (!threadId) return;

  chatState.isDeletingThread = true;
  try {
    await threadApi.deleteThread(threadId);
    threads.value = threads.value.filter(thread => thread.id !== threadId);
    delete threadMessages.value[threadId];

    if (chatState.currentThreadId === threadId) {
      chatState.currentThreadId = null;
    }
  } catch (error) {
    console.error('Failed to delete thread:', error);
    handleChatError(error, 'delete');
    throw error;
  } finally {
    chatState.isDeletingThread = false;
  }
};

// 更新线程标题
const updateThread = async (threadId, title) => {
  if (!threadId || !title) return;

  chatState.isRenamingThread = true;
  try {
    await threadApi.updateThread(threadId, title);
    const thread = threads.value.find(t => t.id === threadId);
    if (thread) {
      thread.title = title;
    }
  } catch (error) {
    console.error('Failed to update thread:', error);
    handleChatError(error, 'update');
    throw error;
  } finally {
    chatState.isRenamingThread = false;
  }
};

// 获取线程消息
const fetchThreadMessages = async ({ agentId, threadId, delay = 0 }) => {
  if (!threadId || !agentId) return;

  // 如果指定了延迟，等待指定时间（用于确保后端数据库事务提交）
  if (delay > 0) {
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  try {
    const response = await agentApi.getAgentHistory(agentId, threadId);
    console.log(`🔄 [FETCH] Thread messages: ${new Date().toLocaleTimeString()}.${new Date().getMilliseconds()}`, response);
    threadMessages.value[threadId] = response.history || [];
  } catch (error) {
    handleChatError(error, 'load');
    throw error;
  }
};

const fetchAgentState = async (agentId, threadId) => {
  if (!agentId || !threadId) return;
  try {
    const res = await agentApi.getAgentState(agentId, threadId);
    const ts = getThreadState(threadId);
    if (ts) ts.agentState = res.agent_state || null;
  } catch (error) {}
};

const ensureActiveThread = async (title = '新的对话') => {
  if (currentChatId.value) return currentChatId.value;
  try {
    const newThread = await createThread(currentAgentId.value, title || '新的对话');
    if (newThread) {
      chatState.currentThreadId = newThread.id;
      return newThread.id;
    }
  } catch (error) {
    // createThread 已处理错误提示
  }
  return null;
};

// ==================== 审批功能管理 ====================
const { approvalState, handleApproval, processApprovalInStream } = useApproval({
  getThreadState,
  resetOnGoingConv,
  fetchThreadMessages
});

const { handleAgentResponse } = useAgentStreamHandler({
  getThreadState,
  processApprovalInStream,
  currentAgentId,
});

// 发送消息并处理流式响应
const sendMessage = async ({ agentId, threadId, text, signal = undefined, imageData = undefined }) => {
  if (!agentId || !threadId || !text) {
    const error = new Error("Missing agent, thread, or message text");
    handleChatError(error, 'send');
    return Promise.reject(error);
  }

  // 如果是新对话，用消息内容作为标题
  if ((threadMessages.value[threadId] || []).length === 0) {
    updateThread(threadId, text);
  }

  const requestData = {
    query: text,
    config: {
      thread_id: threadId,
    },
  };

  // 如果有图片，添加到请求中
  if (imageData && imageData.imageContent) {
    requestData.image_content = imageData.imageContent;
  }

  try {
    return await agentApi.sendAgentMessage(agentId, requestData, signal ? { signal } : undefined);
  } catch (error) {
    handleChatError(error, 'send');
    throw error;
  }
};

// ==================== 聊天操作方法 ====================

// 检查第一个对话是否为空
const isFirstChatEmpty = () => {
  if (threads.value.length === 0) return false;
  const firstThread = threads.value[0];
  const firstThreadMessages = threadMessages.value[firstThread.id] || [];
  return firstThreadMessages.length === 0;
};

// 如果第一个对话为空，直接切换到第一个对话
const switchToFirstChatIfEmpty = async () => {
  if (threads.value.length > 0 && isFirstChatEmpty()) {
    await selectChat(threads.value[0].id);
    return true;
  }
  return false;
};

const createNewChat = async () => {
  if (!AgentValidator.validateAgentId(currentAgentId.value, '创建对话') || chatUIStore.creatingNewChat) return;

  // 如果第一个对话为空，直接切换到第一个对话而不是创建新对话
  if (await switchToFirstChatIfEmpty()) return;

  // 只有当当前对话是第一个对话且为空时，才阻止创建新对话
  const currentThreadIndex = threads.value.findIndex(thread => thread.id === currentChatId.value);
  if (currentChatId.value && conversations.value.length === 0 && currentThreadIndex === 0) return;

  chatUIStore.creatingNewChat = true;
  try {
    const newThread = await createThread(currentAgentId.value, '新的对话');
    if (newThread) {
      // 中断之前线程的流式输出（如果存在）
      const previousThreadId = chatState.currentThreadId;
      if (previousThreadId) {
        const previousThreadState = getThreadState(previousThreadId);
        if (previousThreadState?.isStreaming && previousThreadState.streamAbortController) {
          previousThreadState.streamAbortController.abort();
          previousThreadState.isStreaming = false;
          previousThreadState.streamAbortController = null;
        }
      }

      chatState.currentThreadId = newThread.id;
    }
  } catch (error) {
    handleChatError(error, 'create');
  } finally {
    chatUIStore.creatingNewChat = false;
  }
};

const selectChat = async (chatId) => {
  if (!AgentValidator.validateAgentIdWithError(currentAgentId.value, '选择对话', handleValidationError)) return;

  // 中断之前线程的流式输出（如果存在）
  const previousThreadId = chatState.currentThreadId;
  if (previousThreadId && previousThreadId !== chatId) {
    const previousThreadState = getThreadState(previousThreadId);
    if (previousThreadState?.isStreaming && previousThreadState.streamAbortController) {
      previousThreadState.streamAbortController.abort();
      previousThreadState.isStreaming = false;
      previousThreadState.streamAbortController = null;
    }
  }

  chatState.currentThreadId = chatId;
  chatUIStore.isLoadingMessages = true;
  try {
    await fetchThreadMessages({ agentId: currentAgentId.value, threadId: chatId });
  } catch (error) {
    handleChatError(error, 'load');
  } finally {
    chatUIStore.isLoadingMessages = false;
  }

  await nextTick();
  scrollController.scrollToBottomStaticForce();
  await fetchAgentState(currentAgentId.value, chatId);
};

const deleteChat = async (chatId) => {
  if (!AgentValidator.validateAgentIdWithError(currentAgentId.value, '删除对话', handleValidationError)) return;
  try {
    await deleteThread(chatId);
    if (chatState.currentThreadId === chatId) {
      chatState.currentThreadId = null;
      // 如果删除的是当前对话，自动创建新对话
      await createNewChat();
    } else if (chatsList.value.length > 0) {
      // 如果删除的不是当前对话，选择第一个可用对话
      await selectChat(chatsList.value[0].id);
    }
  } catch (error) {
    handleChatError(error, 'delete');
  }
};

const renameChat = async (data) => {
  let { chatId, title } = data;
  if (!AgentValidator.validateRenameOperation(chatId, title, currentAgentId.value, handleValidationError)) return;
  if (title.length > 30) title = title.slice(0, 30);
  try {
    await updateThread(chatId, title);
  } catch (error) {
    handleChatError(error, 'rename');
  }
};

// ==================== 人才查询结果相关方法 ====================

// 更新搜索结果
const updateSearchResults = (results) => {
  searchResults.value = formatTalentSearchResults(results);
};

// 刷新结果
const refreshResults = async () => {
  if (!currentChatId.value) return;

  loadingResults.value = true;
  try {
    // 从当前对话历史中获取最近的查询，用于重新执行搜索
    if (conversations.value.length > 0) {
      const lastUserMessage = conversations.value[conversations.value.length - 1]?.messages?.find(m => m.type === 'human');
      if (lastUserMessage) {
        const query = lastUserMessage.content || '';
        const filters = parseSearchQueryFilters(query);

        // 执行实际的搜索API调用
        const response = await talentSearchApi.searchTalents({
          query: query,
          filters: filters,
          page: 1,
          limit: 50
        });

        if (response && response.data) {
          // 格式化结果，计算匹配度
          const results = response.data.results || response.data;
          searchResults.value = formatTalentSearchResults(results).map(talent => {
            // 根据查询条件计算匹配度（这里应该是后端计算，这里只是示例）
            const matchScore = calculateMatchScore(talent, query);
            return {
              ...talent,
              matchScore,
              isShortlisted: shortlist.value.some(item => item.id === talent.id)
            };
          });
        } else {
          searchResults.value = [];
        }
      } else {
        // 如果没有找到用户消息，使用默认搜索
        const response = await talentSearchApi.getTalentList({
          page: 1,
          limit: 20
        });

        if (response && response.data) {
          searchResults.value = formatTalentSearchResults(response.data.results || response.data);
        } else {
          searchResults.value = [];
        }
      }
    }
  } catch (error) {
    console.error('Failed to refresh results:', error);
    message.error('刷新结果失败');
    // 设置空结果
    searchResults.value = [];
  } finally {
    loadingResults.value = false;
  }
};

// 计算匹配度（示例函数，实际应该由后端计算）
const calculateMatchScore = (talent, query) => {
  let score = 0;

  // 检查职称匹配
  if (query.includes('高级工程师') && talent.title && talent.title.includes('高级工程师')) {
    score += 30;
  }

  // 检查项目经验匹配
  if (query.includes('省部级') && talent.projectExperience && talent.projectExperience.includes('省部级')) {
    score += 25;
  }

  // 检查专利匹配
  if (query.includes('专利') && talent.patentsPapers && talent.patentsPapers.includes('专利')) {
    score += 20;
  }

  // 检查专业领域匹配
  if (query.includes('配电') &&
      (talent.department?.includes('配电') ||
          talent.position?.includes('配电') ||
          talent.skills?.some(skill => skill.includes('配电')))) {
    score += 25;
  }

  return Math.min(score, 100);
};

// 查看人才详情
const viewTalentDetail = (talent) => {
  // 这里可以导航到人才详情页
  console.log('View talent detail:', talent);
  message.info(`查看人才详情: ${talent.name}`);

  // 可以emit事件给父组件处理
  emit('view-talent-detail', talent);
};

// ==================== 聊天发送方法 ====================

const handleSendMessage = async ({ image } = {}) => {
  console.log('TalentChatSearchComponent: handleSendMessage payload image:', image);
  const text = userInput.value.trim();
  if ((!text && !image) || !currentAgent.value || isProcessing.value) return;

  let threadId = currentChatId.value;
  if (!threadId) {
    threadId = await ensureActiveThread(text);
    if (!threadId) {
      message.error('创建对话失败，请重试');
      return;
    }
  }

  userInput.value = '';

  await nextTick();
  scrollController.scrollToBottom(true);

  const threadState = getThreadState(threadId);
  if (!threadState) return;

  threadState.isStreaming = true;
  resetOnGoingConv(threadId);
  threadState.streamAbortController = new AbortController();

  try {
    const response = await sendMessage({
      agentId: currentAgentId.value,
      threadId: threadId,
      text: text,
      signal: threadState.streamAbortController?.signal,
      imageData: image
    });

    await handleAgentResponse(response, threadId);

    // 检查是否是人才搜索相关的查询
    const lowerText = text.toLowerCase();
    if (lowerText.includes('人才') || lowerText.includes('talent') ||
        lowerText.includes('搜索') || lowerText.includes('查询') ||
        lowerText.includes('查找') || lowerText.includes('find') ||
        lowerText.includes('技能') || lowerText.includes('skill') ||
        lowerText.includes('工程师') || lowerText.includes('engineer') ||
        lowerText.includes('专家') || lowerText.includes('项目') ||
        lowerText.includes('匹配') || lowerText.includes('条件')) {

      // 延迟更新搜索结果，确保AI响应已处理完成
      setTimeout(() => {
        refreshResults();
      }, 1500);
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      console.error('Stream error:', error);
      handleChatError(error, 'send');
    } else {
      console.warn("[Interrupted] Catch");
    }
    threadState.isStreaming = false;
  } finally {
    threadState.streamAbortController = null;
    // 异步加载历史记录，保持当前消息显示直到历史记录加载完成
    fetchThreadMessages({ agentId: currentAgentId.value, threadId: threadId, delay: 500 })
        .finally(() => {
          // 历史记录加载完成后，安全地清空当前进行中的对话
          resetOnGoingConv(threadId);
          scrollController.scrollToBottom();
        });
  }
};

// 发送或中断
const handleSendOrStop = async (payload) => {
  const threadId = currentChatId.value;
  const threadState = getThreadState(threadId);
  if (isProcessing.value && threadState && threadState.streamAbortController) {
    // 中断生成
    threadState.streamAbortController.abort();

    // 中断后刷新消息历史，确保显示最新的状态
    try {
      await fetchThreadMessages({ agentId: currentAgentId.value, threadId: threadId, delay: 500 });
      message.info('已中断对话生成');
    } catch (error) {
      console.error('刷新消息历史失败:', error);
      message.info('已中断对话生成');
    }
    return;
  }
  await handleSendMessage(payload);
};

// ==================== 人工审批处理 ====================
const handleApprovalWithStream = async (approved) => {
  console.log('🔄 [STREAM] Starting resume stream processing');

  const threadId = approvalState.threadId;
  if (!threadId) {
    message.error('无效的审批请求');
    approvalState.showModal = false;
    return;
  }

  const threadState = getThreadState(threadId);
  if (!threadState) {
    message.error('无法找到对应的对话线程');
    approvalState.showModal = false;
    return;
  }

  try {
    // 使用审批 composable 处理审批
    const response = await handleApproval(approved, currentAgentId.value);

    if (!response) return; // 如果 handleApproval 抛出错误，这里不会执行

    console.log('🔄 [STREAM] Processing resume streaming response');

    // 处理流式响应
    await handleAgentResponse(response, threadId, (chunk) => {
      console.log('🔄 [STREAM] Processing chunk:', chunk);
    });

    console.log('🔄 [STREAM] Resume stream processing completed');

  } catch (error) {
    console.error('❌ [STREAM] Resume stream failed:', error);
    if (error.name !== 'AbortError') {
      console.error('Resume approval error:', error);
      // handleChatError 已在 useApproval 中调用
    }
  } finally {
    console.log('🔄 [STREAM] Cleaning up streaming state');
    if (threadState) {
      threadState.isStreaming = false;
      threadState.streamAbortController = null;
    }

    // 异步加载历史记录，保持当前消息显示直到历史记录加载完成
    fetchThreadMessages({ agentId: currentAgentId.value, threadId: threadId, delay: 500 })
        .finally(() => {
          // 历史记录加载完成后，安全地清空当前进行中的对话
          resetOnGoingConv(threadId);
          scrollController.scrollToBottom();
        });
  }
};

const handleApprove = () => {
  handleApprovalWithStream(true);
};

const handleReject = () => {
  handleApprovalWithStream(false);
};

// 处理示例问题点击
const handleExampleClick = (questionText) => {
  userInput.value = questionText;
  nextTick(() => {
    handleSendMessage();
  });
};

const buildExportPayload = () => {
  const agentId = currentAgentId.value;
  let agentDescription = '';
  if (agentId && agents.value && agents.value.length > 0) {
    const agent = agents.value.find(a => a.id === agentId);
    agentDescription = agent ? (agent.description || '') : '';
  }

  const payload = {
    chatTitle: currentThread.value?.title || '新对话',
    agentName: currentAgentName.value || currentAgent.value?.name || '智能助手',
    agentDescription: agentDescription || currentAgent.value?.description || '',
    messages: conversations.value ? JSON.parse(JSON.stringify(conversations.value)) : [],
    onGoingMessages: onGoingConvMessages.value ? JSON.parse(JSON.stringify(onGoingConvMessages.value)) : [],
    searchResults: searchResults.value,
    shortlist: shortlist.value
  };

  return payload;
};

defineExpose({
  getExportPayload: buildExportPayload,
  updateSearchResults,
  getShortlist: () => shortlist.value,
  clearShortlist
});

// ==================== UI 控制方法 ====================

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value;
};

const toggleResultsPanel = () => {
  showResultsPanel.value = !showResultsPanel.value;
};

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleDateString();
};

// ==================== HELPER FUNCTIONS ====================
const getLastMessage = (conv) => {
  if (!conv?.messages?.length) return null;
  for (let i = conv.messages.length - 1; i >= 0; i--) {
    if (conv.messages[i].type === 'ai') return conv.messages[i];
  }
  return null;
};

const showMsgRefs = (msg) => {
  // 如果正在审批中，不显示 refs
  if (approvalState.showModal) {
    return false;
  }

  // 如果当前线程ID与审批线程ID匹配，但审批框已关闭（说明刚刚处理完审批）
  // 且当前有新的流式处理正在进行，则不显示之前被中断的消息的 refs
  if (approvalState.threadId &&
      chatState.currentThreadId === approvalState.threadId &&
      !approvalState.showModal &&
      isProcessing) {
    return false;
  }

  // 只有真正完成的消息才显示 refs
  if (msg.isLast && msg.status === 'finished') {
    return ['copy'];
  }
  return false;
};

// ==================== LIFECYCLE & WATCHERS ====================
const loadChatsList = async () => {
  const agentId = currentAgentId.value;
  if (!agentId) {
    console.warn('No agent selected, cannot load chats list');
    threads.value = [];
    chatState.currentThreadId = null;
    return;
  }

  try {
    await fetchThreads(agentId);
    if (currentAgentId.value !== agentId) return;

    // 如果当前线程不在线程列表中，清空当前线程
    if (chatState.currentThreadId && !threads.value.find(t => t.id === chatState.currentThreadId)) {
      chatState.currentThreadId = null;
    }

    // 如果有线程但没有选中任何线程，自动选择第一个
    if (threads.value.length > 0 && !chatState.currentThreadId) {
      await selectChat(threads.value[0].id);
    }
  } catch (error) {
    handleChatError(error, 'load');
  }
};

const initAll = async () => {
  try {
    if (!agentStore.isInitialized) {
      await agentStore.initialize();
    }
  } catch (error) {
    handleChatError(error, 'load');
  }
};

onMounted(async () => {
  await initAll();
  scrollController.enableAutoScroll();
});

watch(currentAgentId, async (newAgentId, oldAgentId) => {
  if (newAgentId !== oldAgentId) {
    // 清理当前线程状态
    chatState.currentThreadId = null;
    threadMessages.value = {};
    // 清理所有线程状态
    resetOnGoingConv();

    if (newAgentId) {
      await loadChatsList();
    } else {
      threads.value = [];
    }
  }
}, { immediate: true });

watch(conversations, () => {
  if (isProcessing.value) {
    scrollController.scrollToBottom();
  }
}, { deep: true, flush: 'post' });

</script>

<style lang="less" scoped>
@import '@/assets/css/main.css';
@import '@/assets/css/animations.less';

.talent-chat-search-container {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.talent-chat-layout {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
}

/* 聊天区域样式 */
.talent-chat-main {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  box-sizing: border-box;
  background: var(--gray-0);
  border-right: 1px solid var(--gray-200);
  transition: flex 0.3s ease, border-right 0.3s ease;

  /* 扩展状态 - 当右侧面板隐藏或收起时 */
  &.expanded {
    flex: 1;
  }

  /* 隐藏边框 - 当右侧面板完全隐藏时 */
  &.hide-border {
    border-right: none;
  }

  /* 当侧边栏打开时，聊天内容向右移动 */
  &:has(.sidebar-drawer.open) {
    .chat-header,
    .chat-box,
    .bottom {
      transform: translateX(300px);
      transition: transform 0.3s ease;
    }
  }
}

/* 侧边栏抽屉样式 - 相对于聊天区域定位 */
.sidebar-drawer {
  position: absolute;
  top: 0;
  left: -300px;
  width: 300px;
  height: 100%;
  background: var(--gray-0);
  z-index: 1001;
  transition: transform 0.3s ease;
  border-right: 1px solid var(--gray-200);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);

  /* 确保侧边栏在所有内容之上 */
  &.open {
    transform: translateX(300px);
    z-index: 1002;
  }

  .drawer-header {
    padding: 16px;
    border-bottom: 1px solid var(--gray-200);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--gray-50);
    min-height: 56px; /* 添加最小高度，与聊天头部一致 */

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }

    .close-btn {
      border: none;
      background: none;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        background-color: var(--gray-100);
      }
    }
  }

  .drawer-content {
    flex: 1;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;

    .chats-list {
      flex: 1;
      overflow-y: auto;

      .chat-item {
        padding: 12px;
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          border-color: var(--main-500);
          background-color: var(--main-25);
        }

        &.active {
          border-color: var(--main-500);
          background-color: var(--main-50);
        }

        .chat-title {
          font-weight: 500;
          margin-bottom: 4px;
          font-size: 14px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .chat-time {
          font-size: 12px;
          color: var(--gray-600);
        }
      }
    }
  }
}

/* 聊天头部、聊天框、底部区域添加过渡效果 */
.chat-header,
.chat-box,
.bottom {
  transition: transform 0.3s ease;
}

/* 调整聊天头部高度，与右侧结果头部保持一致 */
.chat-header {
  user-select: none;
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  background-color: var(--gray-0);
  border-bottom: 1px solid var(--gray-100);
  min-height: 56px; /* 与右侧结果头部保持一致 */
  box-sizing: border-box;

  /* 确保头部内容垂直居中 */
  .header__left,
  .header__right {
    display: flex;
    align-items: center;
    height: 100%; /* 填充整个头部高度 */
  }

  .header__left {
    gap: 8px;
  }

  .agent-nav-btn {
    display: flex;
    gap: 6px;
    padding: 0 12px;
    justify-content: center;
    align-items: center;
    border-radius: 8px;
    color: var(--gray-900);
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
    border: none;
    background: transparent;
    height: 40px; /* 固定按钮高度 */

    &:hover:not(.is-disabled) {
      background-color: var(--gray-50);
    }

    .nav-btn-icon {
      height: 18px;
      width: 18px;
    }

    .loading-icon {
      animation: spin 1s linear infinite;
    }

    .text {
      white-space: nowrap;
      line-height: 1; /* 确保文本不额外增加高度 */
    }
  }
}

.chat-box {
  flex-grow: 1;
  padding: 12px 20px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.conv-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bottom {
  position: sticky;
  bottom: 0;
  width: 100%;
  margin: 0 auto;
  padding: 4px 20px 0 20px;
  background: var(--gray-0);
  z-index: 1000;

  .message-input-wrapper {
    width: 100%;
    max-width: 700px;
    margin: 0 auto;

    .bottom-actions {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .note {
      font-size: small;
      color: var(--gray-300);
      margin: 4px 0;
      user-select: none;
    }
  }
}

/* 右侧结果面板 */
.talent-results-panel {
  flex: 0 0 60%;
  min-width: 350px;
  background: var(--gray-0);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border-left: 1px solid var(--gray-200);

  /* 收起状态 */
  &.collapsed {
    flex: 0 0 48px;
    min-width: 48px;

    .results-content {
      display: none;
    }

    .results-header {
      justify-content: center;

      h3 {
        display: none;
      }
    }
  }

  /* 隐藏状态 - 当没有对话时 */
  &.hidden {
    display: none;
    flex: 0;
    min-width: 0;
    width: 0;
    border-left: none;
  }

  /* 展开状态 - 当有对话且面板展开时 */
  &.expanded {
    flex: 0 0 60%;
    min-width: 350px;
  }

  /* 调整结果头部高度，与左侧聊天头部一致 */
  .results-header {
    padding: 0 16px;
    border-bottom: 1px solid var(--gray-200);
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 56px; /* 与左侧聊天头部保持一致 */
    box-sizing: border-box;
    background: var(--gray-50);

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      white-space: nowrap;
    }

    .results-header-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .results-count {
      font-size: 12px;
      color: var(--gray-600);
    }

    .toggle-btn {
      border: none;
      background: none;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 32px;
      height: 32px; /* 固定按钮高度 */

      &:hover {
        background-color: var(--gray-100);
      }
    }
  }

  .results-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px;
    overflow: hidden;

    .results-controls {
      margin-bottom: 16px;

      .results-filters {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;

        .filter-label {
          font-size: 12px;
          color: var(--gray-700);
          font-weight: 500;
        }
      }
    }

    .results-table-container {
      flex: 1;
      overflow: hidden;
      margin-bottom: 16px;

      :deep(.ant-table-wrapper) {
        height: 100%;

        .ant-spin-container {
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .ant-table {
          height: 100%;
          font-size: 12px;

          .ant-table-container {
            height: 100%;
          }

          .ant-table-body {
            height: calc(100% - 56px);
          }

          .ant-table-cell {
            padding: 6px 8px !important;
          }

          .ant-table-thead > tr > th {
            background-color: var(--gray-50);
            font-weight: 600;
            font-size: 12px;
          }

          .ant-table-tbody > tr:hover > td {
            background-color: var(--main-25);
          }
        }
      }

      /* 匹配度样式 */
      .match-score-cell {
        .match-score-bar {
          position: relative;
          width: 100%;
          height: 20px;
          background-color: var(--gray-100);
          border-radius: 10px;
          overflow: hidden;

          .match-score-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;

            &.match-high {
              background: linear-gradient(90deg, #10b981, #34d399);
            }
            &.match-medium {
              background: linear-gradient(90deg, #f59e0b, #fbbf24);
            }
            &.match-low {
              background: linear-gradient(90deg, #f97316, #fb923c);
            }
            &.match-none {
              background: linear-gradient(90deg, #ef4444, #f87171);
            }
          }

          .match-score-text {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 600;
            color: white;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
          }
        }
      }

      /* 匹配状态样式 */
      .match-status {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;

        &.status-high {
          background-color: rgba(16, 185, 129, 0.1);
          color: #047857;
          border: 1px solid rgba(16, 185, 129, 0.3);
        }
        &.status-medium {
          background-color: rgba(245, 158, 11, 0.1);
          color: #92400e;
          border: 1px solid rgba(245, 158, 11, 0.3);
        }
        &.status-low {
          background-color: rgba(249, 115, 22, 0.1);
          color: #9a3412;
          border: 1px solid rgba(249, 115, 22, 0.3);
        }
        &.status-none {
          background-color: rgba(239, 68, 68, 0.1);
          color: #991b1b;
          border: 1px solid rgba(239, 68, 68, 0.3);
        }
      }

      /* 操作按钮样式 */
      :deep(.ant-table-cell) {
        .shortlisted {
          color: var(--main-600) !important;
          font-weight: 500;
        }

        .remove-btn {
          color: var(--gray-400);
          padding: 0;
          min-width: 20px;
          height: 20px;

          &:hover {
            color: var(--gray-600);
          }
        }
      }
    }

    /* 候选名单摘要 */
    .shortlist-summary {
      border-top: 1px solid var(--gray-200);
      padding-top: 16px;
      margin-top: 8px;

      .shortlist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        h4 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--gray-800);
        }
      }

      .shortlist-items {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .shortlist-item {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 8px;
          background-color: var(--main-50);
          border: 1px solid var(--main-200);
          border-radius: 6px;
          font-size: 12px;

          .shortlist-name {
            font-weight: 500;
            color: var(--gray-800);
          }

          .shortlist-match {
            color: var(--main-600);
            font-weight: 600;
          }

          .remove-btn {
            color: var(--gray-400);
            padding: 0;
            min-width: 16px;
            height: 16px;

            &:hover {
              color: var(--gray-600);
            }
          }
        }
      }
    }
  }
}

/* 示例问题样式 */
.example-questions {
  margin-top: 12px;
  text-align: center;

  .example-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
  }

  .example-chip {
    padding: 5px 10px;
    background: var(--gray-25);
    border-radius: 14px;
    cursor: pointer;
    font-size: 0.75rem;
    color: var(--gray-700);
    transition: all 0.15s ease;
    white-space: nowrap;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;

    &:hover {
      border-color: var(--main-200);
      color: var(--main-700);
      box-shadow: 0 0px 4px rgba(0, 0, 0, 0.03);
    }

    &:active {
      transform: translateY(0);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
  }
}

/* 生成状态样式 */
.generating-status {
  display: flex;
  justify-content: flex-start;
  padding: 1rem 0;
  animation: fadeInUp 0.4s ease-out;
  transition: all 0.2s;
}

.generating-indicator {
  display: flex;
  align-items: center;
  padding: 0.75rem 0rem;

  .generating-text {
    margin-left: 12px;
    color: var(--gray-700);
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.025em;
  }
}

.loading-dots {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.loading-dots div {
  width: 6px;
  height: 6px;
  background: linear-gradient(135deg, var(--main-color), var(--main-700));
  border-radius: 50%;
  animation: dotPulse 1.4s infinite ease-in-out both;
}

.loading-dots div:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots div:nth-child(2) {
  animation-delay: -0.16s;
}

.loading-dots div:nth-child(3) {
  animation-delay: 0s;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .talent-chat-layout {
    flex-direction: column;
  }

  .talent-chat-main {
    flex: 0 0 40%;
    min-height: 400px;

    &.expanded {
      flex: 1;
    }
  }

  .talent-results-panel {
    flex: 0 0 60%;
    min-height: 300px;
    min-width: 100%;
    border-left: none;
    border-top: 1px solid var(--gray-200);

    &.collapsed {
      flex: 0 0 48px;
      min-height: 48px;

      .results-header {
        h3 {
          display: block;
          font-size: 14px;
        }
      }
    }

    &.hidden {
      display: none;
      min-height: 0;
    }
  }
}

@media (max-width: 768px) {
  .talent-chat-main {
    flex: 1;

    /* 移动端调整侧边栏宽度 */
    .sidebar-drawer {
      width: 280px;
      left: -280px;

      &.open {
        transform: translateX(280px);
      }

      /* 移动端侧边栏打开时，聊天内容移动 */
      & ~ .chat-header,
      & ~ .chat-box,
      & ~ .bottom {
        transition: transform 0.3s ease;
      }

      &.open ~ .chat-header,
      &.open ~ .chat-box,
      &.open ~ .bottom {
        transform: translateX(280px);
      }
    }
  }

  .talent-results-panel {
    flex: 1;
    min-height: 300px;

    &.hidden {
      display: none;
      min-height: 0;
    }

    .results-content {
      .results-filters {
        flex-direction: column;
        align-items: flex-start;
      }
    }
  }

  /* 移动端调整聊天头部 */
  .chat-header {
    flex-direction: column;
    align-items: stretch;
    height: auto;
    min-height: 64px; /* 移动端稍微增加高度以适应多行 */
    padding: 8px 12px;

    .header__left {
      justify-content: space-between;
      margin-bottom: 8px;
      height: auto;
    }

    .agent-nav-btn {
      flex: 1;
      justify-content: center;
      height: 36px; /* 移动端调整按钮高度 */

      .text {
        display: none;
      }
    }
  }

  .chat-box {
    padding: 8px 12px;
  }

  .bottom {
    padding: 4px 12px 0 12px;
  }

  /* 移动端调整结果头部 */
  .results-header {
    min-height: 56px; /* 移动端保持相同高度 */
    padding: 0 12px;
  }
}

/* 移动端小屏幕适配 */
@media (max-width: 480px) {
  .sidebar-drawer {
    width: 100%;
    left: -100%;

    &.open {
      transform: translateX(100%);
    }

    &.open ~ .chat-header,
    &.open ~ .chat-box,
    &.open ~ .bottom {
      transform: translateX(100%);
    }
  }

  .chat-header {
    padding: 6px 8px;
    min-height: 56px;

    .agent-nav-btn {
      padding: 0 8px;
      font-size: 12px;
      height: 32px;
    }
  }

  .chat-box {
    padding: 4px 8px;
  }

  .bottom {
    padding: 4px 8px 0 8px;
  }

  .example-chip {
    font-size: 0.7rem;
    max-width: 150px;
  }

  .results-header {
    padding: 0 8px;
    min-height: 56px;

    h3 {
      font-size: 14px;
    }

    .toggle-btn {
      height: 28px;
      min-width: 28px;
    }
  }

  .shortlist-items {
    flex-direction: column;
  }
}
</style>