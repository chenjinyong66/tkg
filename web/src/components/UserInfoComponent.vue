<template>
  <div class="user-info-component" :class="{ 'expanded': expanded }">
    <a-dropdown :trigger="['hover']" v-if="userStore.isLoggedIn">
      <div class="user-info-dropdown">
        <div class="user-avatar">
          <img v-if="userStore.avatar" :src="userStore.avatar" :alt="userStore.username" class="avatar-image" />
          <CircleUser v-else />
        </div>
        <div class="user-details" v-if="expanded">
          <div class="username">{{ userStore.username }}</div>
          <div class="user-role">{{ userRoleText }}</div>
        </div>
      </div>
      <template #overlay>
        <a-menu class="user-menu">
          <a-menu-item key="user-info" @click="openProfile">
            <div class="user-menu-header">
              <div class="user-menu-avatar">
                <img v-if="userStore.avatar" :src="userStore.avatar" :alt="userStore.username" />
                <CircleUser v-else />
              </div>
              <div class="user-menu-info">
                <div class="user-menu-username">{{ userStore.username }}</div>
                <div class="user-menu-id">ID: {{ userStore.userIdLogin }}</div>
              </div>
            </div>
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item key="theme" @click="toggleTheme" class="menu-item">
            <div class="menu-item-content">
              <component :is="themeStore.isDark ? Sun : Moon" size="16" class="menu-icon" />
              <span class="menu-text">{{ themeStore.isDark ? '浅色模式' : '深色模式' }}</span>
            </div>
          </a-menu-item>
          <a-menu-divider v-if="userStore.isAdmin" />
          <a-menu-item v-if="userStore.isAdmin" key="setting" @click="goToSetting" class="menu-item">
            <div class="menu-item-content">
              <Settings size="16" class="menu-icon" />
              <span class="menu-text">系统设置</span>
            </div>
          </a-menu-item>
          <a-menu-item key="logout" @click="logout" class="menu-item logout-item">
            <div class="menu-item-content">
              <LogOut size="16" class="menu-icon" />
              <span class="menu-text">退出登录</span>
            </div>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
    <a-button v-else-if="showButton" type="primary" @click="goToLogin" class="login-button">
      登录
    </a-button>

    <!-- 个人资料弹窗 -->
    <a-modal
        v-model:open="profileModalVisible"
        title="个人资料"
        :footer="null"
        width="520px"
        class="profile-modal"
    >
      <div class="profile-content">
        <!-- 头像区域 -->
        <div class="avatar-section">
          <div class="avatar-container">
            <div class="avatar-display">
              <img v-if="userStore.avatar" :src="userStore.avatar" :alt="userStore.username" class="large-avatar" />
              <div v-else class="default-avatar">
                <CircleUser :size="60" />
              </div>
            </div>
            <div class="avatar-actions">
              <a-upload
                  :show-upload-list="false"
                  :before-upload="beforeUpload"
                  @change="handleAvatarChange"
                  accept="image/*"
              >
                <a-button type="primary" size="small" :loading="avatarUploading">
                  <template #icon><Upload size="14"/></template>
                  {{ userStore.avatar ? '更换头像' : '上传头像' }}
                </a-button>
              </a-upload>
              <div class="avatar-tips">
                支持 JPG、PNG 格式，文件不超过 5MB
              </div>
            </div>
          </div>
        </div>

        <!-- 用户信息区域 -->
        <div class="info-section">
          <div class="info-item">
            <div class="info-label">用户名</div>
            <div class="info-value" v-if="!profileEditing">{{ userStore.username || '未设置' }}</div>
            <div class="info-value" v-else>
              <a-input
                  v-model:value="editedProfile.username"
                  placeholder="请输入用户名（2-20个字符）"
                  :max-length="20"
                  style="width: 240px;"
              />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">用户ID</div>
            <div class="info-value user-id" v-if="!profileEditing">{{ userStore.userIdLogin || '未设置' }}</div>
            <div class="info-value" v-else>
              <a-input
                  :value="userStore.userIdLogin || ''"
                  disabled
                  style="width: 240px;"
              />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">手机号</div>
            <div class="info-value" v-if="!profileEditing">
              {{ userStore.phoneNumber || '未设置' }}
            </div>
            <div class="info-value" v-else>
              <a-input
                  v-model:value="editedProfile.phone_number"
                  placeholder="请输入手机号"
                  :max-length="11"
                  style="width: 200px;"
              />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">角色</div>
            <div class="info-value">
              <a-tag :color="getRoleColor(userStore.userRole)" class="role-tag">
                {{ userRoleText }}
              </a-tag>
            </div>
          </div>
        </div>

        <!-- 操作区域 -->
        <div class="actions-section">
          <a-space>
            <template v-if="!profileEditing">
              <a-button type="primary" @click="startEdit">
                编辑资料
              </a-button>
              <a-button @click="profileModalVisible = false">
                关闭
              </a-button>
            </template>
            <template v-else>
              <a-button type="primary" @click="saveProfile" :loading="avatarUploading">
                保存
              </a-button>
              <a-button @click="cancelEdit">
                取消
              </a-button>
            </template>
          </a-space>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { computed, ref, inject } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { message } from 'ant-design-vue';
import { CircleUser, Sun, Moon, LogOut, Upload, Settings } from 'lucide-vue-next';
import { useThemeStore } from '@/stores/theme'

const router = useRouter();
const userStore = useUserStore();
const themeStore = useThemeStore();

// Inject settings modal methods
const { openSettingsModal } = inject('settingsModal', {});

// 个人资料弹窗状态
const profileModalVisible = ref(false);
const avatarUploading = ref(false);
const profileEditing = ref(false);
const editedProfile = ref({
  username: '',
  phone_number: ''
});

const props = defineProps({
  expanded: {
    type: Boolean,
    default: false
  },
  showButton: {
    type: Boolean,
    default: false
  }
})

// 用户角色显示文本
const userRoleText = computed(() => {
  switch (userStore.userRole) {
    case 'superadmin':
      return '超级管理员';
    case 'admin':
      return '管理员';
    case 'user':
      return '普通用户';
    default:
      return '未知角色';
  }
});

// 退出登录
const logout = () => {
  userStore.logout();
  message.success('已退出登录');
  // 跳转到首页
  router.push('/login');
};

// 前往登录页
const goToLogin = () => {
  router.push('/login');
};

const toggleTheme = () => {
  themeStore.toggleTheme()
}

// 前往设置页
const goToSetting = () => {
  if (openSettingsModal) {
    openSettingsModal()
  }
}

// 打开个人资料页面
const openProfile = async () => {
  profileModalVisible.value = true;
  profileEditing.value = false;

  // 刷新用户信息并初始化编辑表单
  try {
    await userStore.getCurrentUser();
    editedProfile.value = {
      username: userStore.username || '',
      phone_number: userStore.phoneNumber || ''
    };
  } catch (error) {
    console.error('刷新用户信息失败:', error);
  }
};

// 角色标签颜色
const getRoleColor = (role) => {
  switch (role) {
    case 'superadmin': return 'red';
    case 'admin': return 'blue';
    case 'user': return 'green';
    default: return 'default';
  }
};

// 开始编辑个人资料
const startEdit = () => {
  profileEditing.value = true;
  editedProfile.value = {
    username: userStore.username || '',
    phone_number: userStore.phoneNumber || ''
  };
};

// 取消编辑
const cancelEdit = () => {
  profileEditing.value = false;
  editedProfile.value = {
    username: userStore.username || '',
    phone_number: userStore.phoneNumber || ''
  };
};

// 保存个人资料
const saveProfile = async () => {
  try {
    // 验证用户名
    if (editedProfile.value.username && (editedProfile.value.username.trim().length < 2 || editedProfile.value.username.trim().length > 20)) {
      message.error('用户名长度必须在 2-20 个字符之间');
      return;
    }

    // 验证手机号格式
    if (editedProfile.value.phone_number && !validatePhoneNumber(editedProfile.value.phone_number)) {
      message.error('请输入正确的手机号格式');
      return;
    }

    await userStore.updateProfile({
      username: editedProfile.value.username?.trim() || undefined,
      phone_number: editedProfile.value.phone_number || undefined,
    });
    message.success('个人资料更新成功！');
    profileEditing.value = false;
  } catch (error) {
    console.error('更新个人资料失败:', error);
    message.error('更新失败：' + (error.message || '请稍后重试'));
  }
};

// 手机号验证
const validatePhoneNumber = (phone) => {
  if (!phone) return true; // 空手机号允许
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
};

// 头像上传前验证
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/');
  if (!isImage) {
    message.error('只能上传图片文件！');
    return false;
  }

  const isLt5M = file.size / 1024 / 1024 < 5;
  if (!isLt5M) {
    message.error('图片大小不能超过 5MB！');
    return false;
  }

  return true;
};

// 处理头像上传
const handleAvatarChange = async (info) => {
  if (info.file.status === 'uploading') {
    avatarUploading.value = true;
    return;
  }

  if (info.file.status === 'done') {
    avatarUploading.value = false;
    return;
  }

  // 手动处理文件上传
  try {
    avatarUploading.value = true;
    const result = await userStore.uploadAvatar(info.file.originFileObj || info.file);
    message.success('头像上传成功！');
  } catch (error) {
    console.error('头像上传失败:', error);
    message.error('头像上传失败：' + (error.message || '请稍后重试'));
  } finally {
    avatarUploading.value = false;
  }
};
</script>

<style lang="less" scoped>
.user-info-component {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0 8px;

  &.expanded {
    justify-content: flex-start;
  }

  .login-button {
    width: 100%;
  }
}

.user-info-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;

  &:hover {
    background-color: var(--main-10);
  }
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--main-50);
  color: var(--main-500);
  flex-shrink: 0;
  overflow: hidden;
  border: 2px solid var(--gray-150);

  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.user-details {
  flex: 1;
  min-width: 0;

  .username {
    font-size: 14px;
    font-weight: 500;
    color: var(--gray-800);
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .user-role {
    font-size: 12px;
    color: var(--gray-600);
    line-height: 1.2;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

// 下拉菜单样式
:deep(.user-menu) {
  min-width: 220px;
  padding: 12px 0;

  .ant-dropdown-menu-item {
    padding: 8px 16px;

    &:hover {
      background-color: var(--main-10);
    }
  }

  .ant-dropdown-menu-item-selected {
    background-color: var(--main-20);
  }
}

.user-menu-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;

  .user-menu-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: var(--main-50);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--main-500);
    flex-shrink: 0;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .user-menu-info {
    flex: 1;
    min-width: 0;

    .user-menu-username {
      font-size: 14px;
      font-weight: 600;
      color: var(--gray-800);
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .user-menu-id {
      font-size: 12px;
      color: var(--gray-600);
      line-height: 1.2;
      margin-top: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

.menu-item {
  .menu-item-content {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .menu-icon {
    color: var(--gray-700);
    flex-shrink: 0;
  }

  .menu-text {
    font-size: 14px;
    color: var(--gray-800);
  }

  &.logout-item {
    .menu-icon {
      color: var(--color-error-500);
    }

    .menu-text {
      color: var(--color-error-500);
    }
  }
}

// 个人资料弹窗样式
.profile-modal {
  :deep(.ant-modal-header) {
    padding: 20px 24px;
    border-bottom: 1px solid var(--gray-150);

    .ant-modal-title {
      font-size: 18px;
      font-weight: 600;
      color: var(--gray-800);
    }
  }

  :deep(.ant-modal-body) {
    padding: 24px;
  }
}

.profile-content {
  .avatar-section {
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--gray-150);

    .avatar-container {
      display: inline-block;

      .avatar-display {
        margin-bottom: 16px;

        .large-avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          object-fit: cover;
          border: 3px solid var(--gray-150);
          box-shadow: 0 2px 8px var(--shadow-2);
        }

        .default-avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: var(--gray-50);
          display: flex;
          margin: 0 auto;
          align-items: center;
          justify-content: center;
          border: 3px solid var(--gray-150);
          box-shadow: 0 2px 8px var(--shadow-2);

          :deep(svg) {
            color: var(--gray-400);
          }
        }
      }

      .avatar-actions {
        .avatar-tips {
          margin-top: 8px;
          font-size: 12px;
          color: var(--gray-500);
          line-height: 1.4;
        }
      }
    }
  }

  .info-section {
    margin-bottom: 24px;

    .info-item {
      display: flex;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid var(--gray-50);

      &:last-child {
        border-bottom: none;
      }

      .info-label {
        width: 80px;
        font-weight: 500;
        color: var(--gray-600);
        flex-shrink: 0;
      }

      .info-value {
        flex: 1;
        color: var(--gray-800);
        font-size: 14px;

        &.user-id {
          font-family: 'Monaco', 'Consolas', monospace;
          color: var(--gray-700);
        }
      }

      .role-tag {
        font-weight: 500;
        border-radius: 4px;
        padding: 4px 12px;
      }
    }
  }

  .actions-section {
    text-align: center;
    padding-top: 16px;
    border-top: 1px solid var(--gray-150);
  }
}
</style>