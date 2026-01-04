<template>
  <div class="talent-chat-search-view">
    <div class="view-header">
      <h1>AI人才搜索</h1>
      <div class="header-actions">
        <Button @click="refreshData" :loading="refreshing">
          <RefreshCw :size="16" />
          刷新
        </Button>
      </div>
    </div>
    
    <div class="view-content">
      <TalentChatSearchComponent 
        :agent-id="agentId"
        :single-mode="true"
        ref="talentChatSearchRef"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Button } from 'ant-design-vue';
import { RefreshCw } from 'lucide-vue-next';
import TalentChatSearchComponent from '@/components/talent/TalentChatSearchComponent.vue';

// 定义属性
const props = defineProps({
  agentId: {
    type: String,
    default: 'talent-search-agent' // 默认人才搜索智能体ID
  }
});

// 响应式数据
const refreshing = ref(false);
const talentChatSearchRef = ref(null);

// 刷新数据方法
const refreshData = async () => {
  refreshing.value = true;
  try {
    // 这里可以调用刷新数据的逻辑
    // 如果talentChatSearchRef有更新结果的方法，可以在这里调用
    if (talentChatSearchRef.value && typeof talentChatSearchRef.value.updateSearchResults === 'function') {
      // 示例：可以传递一些数据或触发结果更新
      talentChatSearchRef.value.updateSearchResults([]);
    }
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
  } catch (error) {
    console.error('刷新数据失败:', error);
  } finally {
    refreshing.value = false;
  }
};

// 组件挂载后执行
onMounted(() => {
  console.log('TalentChatSearchView mounted');
});

// 如果需要导出方法供父组件使用
defineExpose({
  refreshData
});
</script>

<style lang="less" scoped>
.talent-chat-search-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 允许flex子元素收缩 */

  .view-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--gray-200);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--gray-0);

    h1 {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 600;
      color: var(--gray-900);
    }

    .header-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .view-content {
    flex: 1;
    overflow: hidden;
    display: flex;
    min-height: 0; /* 允许内容区域收缩 */

    :deep(.talent-chat-search-container) {
      height: 100%;
      width: 100%;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .header-actions {
      align-self: flex-end;
    }
  }
}
</style>