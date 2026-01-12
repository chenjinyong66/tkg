<script setup>
import { ref, reactive, onMounted, useTemplateRef, computed, provide, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { Bot, Waypoints, LibraryBig, BarChart3, CircleCheck, Search, Database, Users, ChevronDown, ChevronRight } from 'lucide-vue-next';
import { onLongPress } from '@vueuse/core'

import { useConfigStore } from '@/stores/config'
import { useDatabaseStore } from '@/stores/database'
import { useInfoStore } from '@/stores/info'
import { useTaskerStore } from '@/stores/tasker'
import { storeToRefs } from 'pinia'
import UserInfoComponent from '@/components/UserInfoComponent.vue'
import DebugComponent from '@/components/DebugComponent.vue'
import TaskCenterDrawer from '@/components/TaskCenterDrawer.vue'
import SettingsModal from '@/components/SettingsModal.vue'

const configStore = useConfigStore()
const databaseStore = useDatabaseStore()
const infoStore = useInfoStore()
const taskerStore = useTaskerStore()
const { activeCount: activeCountRef, isDrawerOpen } = storeToRefs(taskerStore)

const layoutSettings = reactive({
  showDebug: false,
  useTopBar: false, // 是否使用顶栏
})

// Add state for debug modal
const showDebugModal = ref(false)
const htmlRefHook = useTemplateRef('htmlRefHook')

// Add state for settings modal
const showSettingsModal = ref(false)

// Provide settings modal methods to child components
const openSettingsModal = () => {
  showSettingsModal.value = true
}

// Setup long press for debug modal
onLongPress(
    htmlRefHook,
    () => {
      console.log('long press')
      showDebugModal.value = true
    },
    {
      delay: 1000, // 1秒长按
      modifiers: {
        prevent: true
      }
    }
)

// Handle debug modal close
const handleDebugModalClose = () => {
  showDebugModal.value = false
}

const getRemoteConfig = () => {
  configStore.refreshConfig()
}

const getRemoteDatabase = () => {
  databaseStore.getDatabaseInfo(undefined, false) // Explicitly load query params for remote database
}

onMounted(async () => {
  // 加载信息配置
  await infoStore.loadInfoConfig()
  // 加载其他配置
  getRemoteConfig()
  getRemoteDatabase()
  // 预加载任务数据，确保任务中心打开时有内容
  taskerStore.loadTasks()
})

// 打印当前页面的路由信息，使用 vue3 的 setup composition API
const route = useRoute()
console.log(route)

const activeTaskCount = computed(() => activeCountRef.value || 0)

// 下面是导航菜单部分，添加智能体项
const mainList = [
  {
    name: '智能体',
    path: '/agent',
    icon: Bot,
    activeIcon: Bot,
  },
  {
    name: '人才图谱',
    path: '/graph',
    icon: Waypoints,
    activeIcon: Waypoints,
  },
  {
    name: '人才库',
    path: '/talent',
    icon: Users,
    activeIcon: Users,
    /*children: [
      {
        name: '技能专家',
        path: '/talent/skill',
        icon: Users,
      },
      {
        name: '技术专家',
        path: '/talent/tech',
        icon: Users,
      }
    ]*/
  },

  {
    name: 'AI寻人',
    path: '/aisearch',
    icon: Search,
    activeIcon: Search,
  },
  {
    name: '文档库',
    path: '/database',
    icon: Database,
    activeIcon: Database,
  },
  {
    name: '数据看板',
    path: '/dashboard',
    icon: BarChart3,
    activeIcon: BarChart3,
  }
]

// 展开/折叠状态
const expandedMenus = ref({
  '人才库': true // 默认展开人才库二级菜单
})

// 检查当前路由是否属于某个菜单项或其子项
const isMenuItemActive = (item) => {
  if (item.path) {
    return route.path.startsWith(item.path)
  }

  // 检查子菜单
  if (item.children) {
    return item.children.some(child => route.path.startsWith(child.path))
  }

  return false
}

// 切换二级菜单展开状态
const toggleSubMenu = (menuName) => {
  expandedMenus.value[menuName] = !expandedMenus.value[menuName]
}

// Provide settings modal methods to child components
provide('settingsModal', {
  openSettingsModal
})
</script>

<template>
  <div class="app-layout" :class="{ 'use-top-bar': layoutSettings.useTopBar }">
    <div class="header" :class="{ 'top-bar': layoutSettings.useTopBar }">
      <div class="logo">
        <router-link to="/">
          <img :src="infoStore.organization.avatar">
          <span class="logo-text">{{ infoStore.organization.name }}</span>
        </router-link>
      </div>
      <div class="nav">
        <!-- 使用mainList渲染导航项 -->
        <template v-for="(item, index) in mainList" :key="index">
          <!-- 有子菜单的项 -->
          <div
              v-if="item.children"
              class="nav-item parent-item"
              :class="{ active: isMenuItemActive(item) }"
          >
            <div class="nav-item-content" @click="toggleSubMenu(item.name)">
              <component class="icon" :is="isMenuItemActive(item) ? item.activeIcon : item.icon" size="20"/>
              <span class="nav-text">{{ item.name }}</span>
              <component
                  class="chevron"
                  :is="expandedMenus[item.name] ? ChevronDown : ChevronRight"
                  size="16"
              />
            </div>

            <!-- 二级菜单 -->
            <div v-show="expandedMenus[item.name]" class="sub-menu">
              <RouterLink
                  v-for="(child, childIndex) in item.children"
                  :key="childIndex"
                  :to="child.path"
                  class="sub-menu-item"
                  active-class="active"
              >
                <div class="sub-menu-content">
                  <component class="sub-icon" :is="child.icon" size="16"/>
                  <span class="sub-text">{{ child.name }}</span>
                </div>
              </RouterLink>
            </div>
          </div>

          <!-- 没有子菜单的项 -->
          <RouterLink
              v-else
              :to="item.path"
              v-show="!item.hidden"
              class="nav-item"
              active-class="active"
          >
            <div class="nav-item-content">
              <component class="icon" :is="isMenuItemActive(item) ? item.activeIcon : item.icon" size="20"/>
              <span class="nav-text">{{ item.name }}</span>
            </div>
          </RouterLink>
        </template>

        <!-- 任务中心 -->
        <div
            class="nav-item task-center"
            :class="{ active: isDrawerOpen }"
            @click="taskerStore.openDrawer()"
        >
          <div class="nav-item-content">
            <a-badge
                :count="activeTaskCount"
                :overflow-count="99"
                class="task-center-badge"
                size="small"
            >
              <CircleCheck class="icon" size="20" />
            </a-badge>
            <span class="nav-text">任务中心</span>
          </div>
        </div>
      </div>
      <div
          ref="htmlRefHook"
          class="fill debug-trigger"
      ></div>

      <div class="bottom-section">
        <!-- 用户信息组件 -->
        <div class="nav-item user-info">
          <UserInfoComponent :expanded="true" />
        </div>
      </div>
    </div>
    <div class="header-mobile">
      <RouterLink to="/agent" class="nav-item" active-class="active">对话</RouterLink>
      <RouterLink to="/database" class="nav-item" active-class="active">知识</RouterLink>
    </div>
    <router-view v-slot="{ Component, route }" id="app-router-view">
      <keep-alive v-if="route.meta.keepAlive !== false">
        <component :is="Component" />
      </keep-alive>
      <component :is="Component" v-else />
    </router-view>

    <!-- Debug Modal -->
    <a-modal
        v-model:open="showDebugModal"
        title="调试面板"
        width="90%"
        :footer="null"
        @cancel="handleDebugModalClose"
        :maskClosable="true"
        :destroyOnClose="true"
        class="debug-modal"
    >
      <DebugComponent />
    </a-modal>
    <TaskCenterDrawer />
    <SettingsModal
        v-model:visible="showSettingsModal"
        @close="() => showSettingsModal = false"
    />
  </div>
</template>

<style lang="less" scoped>
// Less 变量定义
@header-width: 200px; // 增加宽度确保菜单名完全显示

.app-layout {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100vh;
  min-width: var(--min-width);

  .header-mobile {
    display: none;
  }

  .debug-panel {
    position: absolute;
    z-index: 100;
    right: 0;
    bottom: 50px;
    border-radius: 20px 0 0 20px;
    cursor: pointer;
  }
}

div.header, #app-router-view {
  height: 100%;
  max-width: 100%;
  user-select: none;
}

#app-router-view {
  flex: 1 1 auto;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0; // 防止内容溢出
}

.header {
  display: flex;
  flex-direction: column;
  flex: 0 0 @header-width;
  justify-content: flex-start;
  align-items: center;
  background-color: var(--main-0);
  height: 100%;
  width: @header-width;
  border-right: 1px solid var(--gray-100);
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.05);
  z-index: 10;

  .logo {
    width: 100%;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 0 20px;
    border-bottom: 1px solid var(--gray-100);
    flex-shrink: 0;
    background-color: var(--main-10);

    a {
      display: flex;
      align-items: center;
      text-decoration: none;
      width: 100%;
      color: var(--gray-1000);
    }

    img {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      flex-shrink: 0;
      object-fit: cover;
    }

    .logo-text {
      display: inline;
      font-size: 16px;
      font-weight: 600;
      color: var(--main-800);
      margin-left: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: calc(@header-width - 80px);
    }
  }

  .nav {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-start;
    flex: 1;
    width: 100%;
    padding: 16px 0;
    gap: 2px;
    overflow-y: auto;
    overflow-x: hidden;

    /* 自定义滚动条样式 */
    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background: var(--gray-200);
      border-radius: 2px;
    }

    &::-webkit-scrollbar-thumb:hover {
      background: var(--gray-300);
    }
  }

  .nav-item {
    display: flex;
    align-items: center;
    width: 100%;
    min-height: 46px;
    padding: 0 16px;
    border-radius: 8px;
    background-color: transparent;
    color: var(--gray-800);
    font-size: 14px;
    transition: all 0.2s ease-in-out;
    margin: 2px 8px;
    text-decoration: none;
    cursor: pointer;
    outline: none;
    flex-shrink: 0;
    flex-direction: column;
    align-items: flex-start;

    &:hover:not(.parent-item) {
      background-color: var(--main-10);
      color: var(--main-700);
    }

    &.parent-item {
      padding: 0;
      margin: 2px 8px 0;

      &:hover .nav-item-content {
        background-color: var(--main-10);
        color: var(--main-700);
      }

      &.active {
        .nav-item-content {
          background-color: var(--main-20);
          color: var(--main-700);
          font-weight: 600;
          position: relative;

          &::before {
            content: '';
            position: absolute;
            left: 0;
            top: 12px;
            bottom: 12px;
            width: 4px;
            background-color: var(--main-500);
            border-radius: 0 2px 2px 0;
          }
        }
      }
    }

    &.active:not(.parent-item) {
      background-color: var(--main-20);
      color: var(--main-700);
      font-weight: 600;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 12px;
        bottom: 12px;
        width: 4px;
        background-color: var(--main-500);
        border-radius: 0 2px 2px 0;
      }
    }

    .nav-item-content {
      display: flex;
      align-items: center;
      width: 100%;
      height: 46px;
      padding: 0 16px;
      cursor: pointer;
      border-radius: 8px;

      .icon {
        color: inherit;
        flex-shrink: 0;
        margin-right: 12px;
      }

      .nav-text {
        display: inline;
        font-size: 14px;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
        min-width: 0; // 防止flex布局溢出
      }

      .chevron {
        color: var(--gray-500);
        flex-shrink: 0;
        margin-left: 4px;
        transition: transform 0.2s ease;
      }
    }

    &.task-center {
      .nav-item-content {
        padding: 0 16px;
      }

      .task-center-badge {
        width: auto;
        margin-right: 12px;
        :deep(.ant-badge-count) {
          font-size: 12px;
          height: 18px;
          min-width: 18px;
          line-height: 18px;
          box-shadow: none;
          background-color: var(--color-error-500);
          color: white;
        }
      }
    }
  }

  // 二级菜单样式
  .sub-menu {
    width: 100%;
    padding-left: 24px;
    margin-top: 2px;
    margin-bottom: 8px;

    .sub-menu-item {
      display: flex;
      align-items: center;
      width: 100%;
      height: 36px;
      padding: 0 12px;
      border-radius: 6px;
      background-color: transparent;
      color: var(--gray-700);
      font-size: 13px;
      transition: all 0.2s ease-in-out;
      margin: 1px 0;
      text-decoration: none;
      cursor: pointer;

      &:hover {
        background-color: var(--main-5);
        color: var(--main-600);
      }

      &.active {
        background-color: var(--main-10);
        color: var(--main-700);
        font-weight: 500;

        .sub-text {
          font-weight: 500;
        }
      }

      .sub-menu-content {
        display: flex;
        align-items: center;
        width: 100%;
        height: 100%;
      }

      .sub-icon {
        color: inherit;
        flex-shrink: 0;
        margin-right: 8px;
        opacity: 0.8;
      }

      .sub-text {
        display: inline;
        font-size: 13px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
        min-width: 0;
      }
    }
  }

  // 添加debug触发器样式
  .debug-trigger {
    position: relative;
    height: 20px;
    width: 100%;
    flex-shrink: 0;
    min-height: 20px;
  }

  .bottom-section {
    width: 100%;
    padding: 20px 0;
    border-top: 1px solid var(--gray-100);
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-shrink: 0;

    .user-info {
      margin-bottom: 0;
      width: 100%;
      display: flex;
      justify-content: center;
      padding: 0 16px;
    }
  }
}


@media (max-width: 768px) {
  .app-layout {
    flex-direction: column-reverse;

    div.header {
      display: none;
    }

    .debug-panel {
      bottom: 10rem;
    }

  }
  .app-layout div.header-mobile {
    display: flex;
    flex-direction: row;
    width: 100%;
    padding: 0 20px;
    justify-content: space-around;
    align-items: center;
    flex: 0 0 60px;
    border-right: none;
    height: 40px;
    background-color: var(--main-0);
    border-top: 1px solid var(--gray-100);

    .nav-item {
      text-decoration: none;
      width: 40px;
      color: var(--gray-900);
      font-size: 1rem;
      font-weight: bold;
      transition: color 0.1s ease-in-out, font-size 0.1s ease-in-out;

      &.active {
        color: var(--main-700);
        font-size: 1.1rem;
      }
    }
  }
}

.app-layout.use-top-bar {
  flex-direction: column;
}

.header.top-bar {
  flex-direction: row;
  flex: 0 0 50px;
  width: 100%;
  height: 50px;
  border-right: none;
  border-bottom: 1px solid var(--main-40);
  background-color: var(--main-20);
  padding: 0 20px;
  gap: 24px;
  overflow: visible;

  .logo {
    width: fit-content;
    height: auto;
    border-bottom: none;
    padding: 0;
    margin-right: 16px;
    background-color: transparent;

    a {
      display: flex;
      align-items: center;
      text-decoration: none;
      color: inherit;
    }

    img {
      width: 28px;
      height: 28px;
      margin-right: 8px;
    }

    .logo-text {
      display: inline;
      font-size: 16px;
      font-weight: 600;
      color: var(--main-800);
      max-width: 200px;
    }
  }

  .nav {
    flex-direction: row;
    height: auto;
    padding: 0;
    gap: 8px;
    align-items: center;
  }

  .nav-item {
    flex-direction: row;
    width: auto;
    padding: 0 12px;
    margin: 0;
    height: 36px;

    .nav-item-content {
      flex-direction: row;
      justify-content: center;
    }

    .icon {
      margin-right: 6px;
      font-size: 15px;
    }

    .nav-text {
      display: inline;
      font-size: 14px;
      font-weight: 500;
      margin-left: 0;
    }

    &.task-center {
      .task-center-badge {
        width: auto;
        margin-right: 6px;
      }
    }

    &.active::before {
      display: none;
    }
  }

  // 顶栏模式下隐藏二级菜单
  .sub-menu {
    display: none;
  }

  .bottom-section {
    flex-direction: row;
    border-top: none;
    padding: 0;
    gap: 16px;
    margin-left: auto;

    .user-info {
      padding: 0;
    }
  }
}
</style>