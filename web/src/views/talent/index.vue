<template>
  <div class="talent-container layout-container">
    <!-- 顶部导航和搜索区域 -->
    <HeaderComponent title="人才管理" :loading="state.loading">
      <template #actions>
        <div class="header-tools">
          <a-input-search
              v-model:value="state.searchKeyword"
              placeholder="搜索人才姓名、职位、技能..."
              style="width: 300px"
              @search="handleSearch"
              allow-clear
              @clear="handleSearchClear"
          />
          <a-dropdown>
            <template #overlay>
              <a-menu @click="handleFilterClick">
                <a-menu-item key="status_all">
                  <span>全部状态</span>
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="status_active">
                  <a-tag color="green">在职</a-tag>
                </a-menu-item>
                <a-menu-item key="status_probation">
                  <a-tag color="orange">试用期</a-tag>
                </a-menu-item>
                <a-menu-item key="status_inactive">
                  <a-tag color="red">离职</a-tag>
                </a-menu-item>
                <a-menu-item key="status_leave">
                  <a-tag color="blue">休假</a-tag>
                </a-menu-item>
              </a-menu>
            </template>
            <a-button>
              <FilterOutlined />
              筛选
            </a-button>
          </a-dropdown>
          <a-dropdown>
            <template #overlay>
              <a-menu @click="handleSortClick">
                <a-menu-item key="sort_time_desc">
                  <ClockCircleOutlined />
                  按添加时间排序（最新）
                </a-menu-item>
                <a-menu-item key="sort_time_asc">
                  <ClockCircleOutlined />
                  按添加时间排序（最早）
                </a-menu-item>
                <a-menu-item key="sort_name_asc">
                  <SortAscendingOutlined />
                  按姓名排序（A-Z）
                </a-menu-item>
                <a-menu-item key="sort_name_desc">
                  <SortDescendingOutlined />
                  按姓名排序（Z-A）
                </a-menu-item>
              </a-menu>
            </template>
            <a-button>
              <SortAscendingOutlined />
              排序
            </a-button>
          </a-dropdown>
          <a-button type="primary" @click="state.showCreateModal = true">
            <template #icon>
              <UserAddOutlined />
            </template>
            新增人才
          </a-button>
        </div>
      </template>
    </HeaderComponent>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="!state.loading && talents.length > 0">
      <a-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: var(--yn-power-blue-50);">
            <TeamOutlined style="color: var(--yn-power-blue-600); font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalTalents }}</div>
            <div class="stat-label">人才总数</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: var(--yn-power-blue-50);">
            <FileDoneOutlined style="color: var(--yn-power-blue-600); font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.parsedFiles || 0 }}</div>
            <div class="stat-label">已解析文件</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: var(--yn-power-blue-50);">
            <RiseOutlined style="color: var(--yn-power-blue-600); font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.averageRating || 0 }}/10</div>
            <div class="stat-label">平均评分</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: var(--yn-power-blue-50);">
            <ClusterOutlined style="color: var(--yn-power-blue-600); font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.graphExtracted || 0 }}</div>
            <div class="stat-label">图谱已抽取</div>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 新增/编辑人才模态框 -->
    <a-modal
        :open="state.showCreateModal"
        :title="state.isEdit ? '编辑人才信息' : '新增人才'"
        @ok="saveTalent"
        @cancel="cancelTalentOperation"
        class="talent-modal"
        width="800px"
        :confirm-loading="state.saving"
    >
      <a-form :model="state.currentTalent" layout="vertical" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="姓名" :required="true">
              <a-input
                  v-model:value="state.currentTalent.name"
                  placeholder="请输入人才姓名"
                  size="large"
                  :maxlength="20"
                  show-count
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="员工编号" :required="true">
              <a-input
                  v-model:value="state.currentTalent.employeeId"
                  placeholder="请输入员工编号"
                  size="large"
                  :maxlength="20"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="部门">
              <a-cascader
                  v-model:value="state.currentTalent.department"
                  :options="departmentOptions"
                  placeholder="请选择部门"
                  size="large"
                  allow-clear
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="职位">
              <a-input
                  v-model:value="state.currentTalent.position"
                  placeholder="请输入职位"
                  size="large"
                  :maxlength="50"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="人才级别">
          <a-radio-group v-model:value="state.currentTalent.level" button-style="solid" size="large">
            <a-radio-button value="junior">初级</a-radio-button>
            <a-radio-button value="intermediate">中级</a-radio-button>
            <a-radio-button value="senior">高级</a-radio-button>
            <a-radio-button value="expert">专家</a-radio-button>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="专业领域">
          <a-select
              v-model:value="state.currentTalent.expertise"
              mode="multiple"
              placeholder="请选择专业领域"
              size="large"
              :options="expertiseOptions"
              :max-tag-count="3"
          />
        </a-form-item>

        <a-form-item label="技能标签">
          <a-select
              v-model:value="state.currentTalent.skills"
              mode="tags"
              placeholder="请输入技能标签，支持逗号分隔或回车"
              size="large"
              :token-separators="[',']"
              :max-tag-count="5"
          >
            <a-select-option v-for="skill in commonSkills" :key="skill" :value="skill">
              {{ skill }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="联系方式">
              <a-input
                  v-model:value="state.currentTalent.contact"
                  placeholder="请输入手机号"
                  size="large"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="电子邮箱">
              <a-input
                  v-model:value="state.currentTalent.email"
                  placeholder="请输入邮箱地址"
                  size="large"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="工作地点">
          <a-input
              v-model:value="state.currentTalent.location"
              placeholder="请输入工作地点"
              size="large"
          />
        </a-form-item>

        <a-form-item label="入职时间">
          <a-date-picker
              v-model:value="state.currentTalent.joinDate"
              placeholder="请选择入职时间"
              size="large"
              style="width: 100%"
              :disabled-date="disabledFutureDate"
          />
        </a-form-item>

        <a-form-item label="人才状态">
          <a-select
              v-model:value="state.currentTalent.status"
              placeholder="请选择人才状态"
              size="large"
          >
            <a-select-option value="active">在职</a-select-option>
            <a-select-option value="probation">试用期</a-select-option>
            <a-select-option value="leave">休假</a-select-option>
            <a-select-option value="inactive">离职</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="备注信息">
          <a-textarea
              v-model:value="state.currentTalent.remarks"
              placeholder="请输入备注信息"
              :rows="3"
              show-count
              :maxlength="500"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 批量操作模态框 -->
    <a-modal
        v-model:open="state.showBatchModal"
        title="批量操作"
        @ok="handleBatchAction"
        @cancel="state.showBatchModal = false"
        width="400px"
    >
      <div class="batch-modal-content">
        <div class="batch-selected">
          <span>已选择 {{ state.selectedTalents.length }} 个人才</span>
        </div>
        <a-divider />
        <div class="batch-actions">
          <a-button block @click="handleBatchExport" :disabled="state.selectedTalents.length === 0">
            <ExportOutlined />
            导出选中人才
          </a-button>
          <a-button block @click="handleBatchAssign" :disabled="state.selectedTalents.length === 0" style="margin-top: 10px;">
            <TeamOutlined />
            分配考核人
          </a-button>
          <a-button block @click="handleBatchTag" :disabled="state.selectedTalents.length === 0" style="margin-top: 10px;">
            <TagOutlined />
            批量添加标签
          </a-button>
          <a-button block danger @click="handleBatchDelete" :disabled="state.selectedTalents.length === 0" style="margin-top: 10px;">
            <DeleteOutlined />
            批量删除
          </a-button>
        </div>
      </div>
    </a-modal>

    <!-- 加载状态 -->
    <div v-if="state.loading" class="loading-container">
      <a-spin size="large" />
      <p>正在加载人才信息...</p>
    </div>

    <!-- 空状态显示 -->
    <div v-else-if="!talents || talents.length === 0" class="empty-state">
      <div class="empty-illustration">
        <TeamOutlined style="font-size: 80px; color: #bfbfbf;" />
      </div>
      <h3 class="empty-title">暂无人才信息</h3>
      <p class="empty-description">添加您的第一个人才，开始人才管理</p>
      <div class="empty-actions">
        <a-button type="primary" size="large" @click="state.showCreateModal = true">
          <template #icon>
            <UserAddOutlined />
          </template>
          添加人才
        </a-button>
        <a-button size="large" style="margin-left: 12px;" @click="handleImportExcel">
          <template #icon>
            <UploadOutlined />
          </template>
          批量导入
        </a-button>
      </div>
    </div>

    <!-- 人才列表 -->
    <div v-else class="talents-content">
      <div class="talents-header">
        <div class="talents-info">
          <span class="total-count">共 {{ totalTalents }} 位人才</span>
          <a-checkbox
              v-model:checked="state.selectAll"
              @change="handleSelectAll"
              :indeterminate="state.indeterminate"
              style="margin-left: 16px;"
          >
            全选
          </a-checkbox>
          <a-button
              v-if="state.selectedTalents.length > 0"
              size="small"
              @click="state.showBatchModal = true"
              style="margin-left: 16px;"
          >
            批量操作 ({{ state.selectedTalents.length }})
          </a-button>
        </div>
        <div class="view-switcher">
          <a-radio-group v-model:value="state.viewMode" button-style="solid" size="small">
            <a-radio-button value="card">
              <AppstoreOutlined />
              卡片视图
            </a-radio-button>
            <a-radio-button value="list">
              <UnorderedListOutlined />
              列表视图
            </a-radio-button>
          </a-radio-group>
        </div>
      </div>

      <!-- 卡片视图 -->
      <div v-if="state.viewMode === 'card'" class="talents-grid">
        <div
            v-for="talent in displayedTalents"
            :key="talent.id"
            class="talent-card"
            :class="{ 'selected': state.selectedTalents.includes(talent.id) }"
        >
          <div class="card-checkbox">
            <a-checkbox
                :checked="state.selectedTalents.includes(talent.id)"
                @change="(e) => handleSelectTalent(talent.id, e.target.checked)"
            />
          </div>
          <div class="card-content" @click="viewTalentDetails(talent)">
            <div class="card-header">
              <div class="talent-avatar">
                {{ talent.name?.charAt(0) || '?' }}
              </div>
              <div class="talent-basic">
                <h3 class="talent-name">{{ talent.name }}</h3>
                <div class="talent-meta">
                  <span class="employee-id">#{{ talent.employeeId }}</span>
                  <a-tag :color="getStatusColor(talent.status)" size="small">
                    {{ getStatusLabel(talent.status) }}
                  </a-tag>
                  <a-tag v-if="talent.level" color="var(--yn-power-blue-500)" size="small">
                    {{ getLevelLabel(talent.level) }}
                  </a-tag>
                </div>
              </div>
            </div>

            <div class="card-body">
              <div class="talent-info">
                <div class="info-item">
                  <UserOutlined />
                  <span>{{ talent.position || '职位未设置' }}</span>
                </div>
                <div class="info-item">
                  <ApartmentOutlined />
                  <span>{{ talent.department || '部门未设置' }}</span>
                </div>
                <div class="info-item">
                  <EnvironmentOutlined />
                  <span>{{ talent.location || '未设置' }}</span>
                </div>
                <div class="info-item">
                  <CalendarOutlined />
                  <span v-if="talent.joinDate">{{ formatDate(talent.joinDate) }}</span>
                  <span v-else>未设置</span>
                </div>
              </div>

              <div class="skills-section">
                <div class="skills-title">专业技能</div>
                <div class="skills-tags">
                  <a-tag
                      v-for="skill in (talent.skills || []).slice(0, 3)"
                      :key="skill"
                      color="var(--yn-power-blue-100)"
                      style="color: var(--yn-power-blue-600); border-color: var(--yn-power-blue-300);"
                      size="small"
                  >
                    {{ skill }}
                  </a-tag>
                  <a-tag v-if="talent.skills && talent.skills.length > 3" color="default" size="small">
                    +{{ talent.skills.length - 3 }}
                  </a-tag>
                  <div v-if="!(talent.skills && talent.skills.length)" class="no-skills">
                    暂无技能
                  </div>
                </div>
              </div>

              <div class="rating-section" v-if="talent.rating">
                <div class="rating-label">综合评分</div>
                <a-progress
                    :percent="talent.rating * 10"
                    :stroke-color="getRatingColor(talent.rating)"
                    size="small"
                    :show-info="false"
                />
                <span class="rating-value">{{ talent.rating }}/10</span>
              </div>

              <div class="file-stats">
                <div class="stat-item">
                  <FileTextOutlined />
                  <span class="stat-value">{{ talent.fileCount || 0 }}</span>
                  <span class="stat-label">文件</span>
                </div>
                <div class="stat-item">
                  <CheckCircleOutlined />
                  <span class="stat-value">{{ talent.parsedCount || 0 }}</span>
                  <span class="stat-label">已解析</span>
                </div>
                <div class="stat-item">
                  <ClusterOutlined />
                  <span class="stat-value">{{ talent.graphCount || 0 }}</span>
                  <span class="stat-label">图谱</span>
                </div>
              </div>
            </div>

            <div class="card-footer">
              <div class="create-time">
                <ClockCircleOutlined />
                {{ formatCreatedTime(talent.createTime) }}
              </div>
              <div class="card-actions">
                <a-tooltip title="查看详情">
                  <a-button
                      type="text"
                      size="small"
                      @click.stop="viewTalentDetails(talent)"
                  >
                    <EyeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="编辑">
                  <a-button
                      type="text"
                      size="small"
                      @click.stop="editTalent(talent)"
                  >
                    <EditOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="删除">
                  <a-button
                      type="text"
                      size="small"
                      @click.stop="deleteTalent(talent.id)"
                      danger
                  >
                    <DeleteOutlined />
                  </a-button>
                </a-tooltip>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="talents-table">
        <a-table
            :data-source="displayedTalents"
            :row-selection="rowSelection"
            :columns="tableColumns"
            :pagination="false"
            row-key="id"
            size="middle"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'name'">
              <div class="table-cell-name">
                <div class="avatar-small" style="background: linear-gradient(135deg, var(--yn-power-blue-500) 0%, var(--yn-power-blue-600) 100%);">
                  {{ record.name?.charAt(0) || '?' }}
                </div>
                <div class="name-info">
                  <div class="name">{{ record.name }}</div>
                  <div class="employee-id">#{{ record.employeeId }}</div>
                </div>
              </div>
            </template>

            <template v-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)" size="small">
                {{ getStatusLabel(record.status) }}
              </a-tag>
            </template>

            <template v-if="column.key === 'level'">
              <span v-if="record.level">{{ getLevelLabel(record.level) }}</span>
              <span v-else class="text-muted">未设置</span>
            </template>

            <template v-if="column.key === 'skills'">
              <div class="skills-cell">
                <a-tag
                    v-for="skill in (record.skills || []).slice(0, 2)"
                    :key="skill"
                    :color="skillColor"
                    size="small"
                >
                  {{ skill }}
                </a-tag>
                <span v-if="record.skills && record.skills.length > 2" class="more-skills">
                  +{{ record.skills.length - 2 }}
                </span>
                <span v-if="!(record.skills && record.skills.length)" class="text-muted">
                  无
                </span>
              </div>
            </template>

            <template v-if="column.key === 'rating'">
              <div class="rating-cell" v-if="record.rating">
                <a-progress
                    :percent="record.rating * 10"
                    :stroke-color="getRatingColor(record.rating)"
                    size="small"
                    :show-info="false"
                    style="width: 80px;"
                />
                <span class="rating-value">{{ record.rating }}</span>
              </div>
              <span v-else class="text-muted">未评估</span>
            </template>

            <template v-if="column.key === 'files'">
              <div class="files-cell">
                <span class="file-count">{{ record.fileCount || 0 }}</span>
                <span class="file-parsed" v-if="record.parsedCount">
                  ({{ record.parsedCount }}已解析)
                </span>
              </div>
            </template>

            <template v-if="column.key === 'actions'">
              <div class="table-actions">
                <a-tooltip title="查看详情">
                  <a-button
                      type="link"
                      size="small"
                      @click="viewTalentDetails(record)"
                  >
                    <EyeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="编辑">
                  <a-button
                      type="link"
                      size="small"
                      @click="editTalent(record)"
                  >
                    <EditOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="上传文件">
                  <a-button
                      type="link"
                      size="small"
                      @click="handleQuickUpload(record)"
                  >
                    <UploadOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="删除">
                  <a-popconfirm
                      title="确定要删除这个人才吗？"
                      @confirm="deleteTalent(record.id)"
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

      <!-- 分页 -->
      <div class="pagination-container" v-if="displayedTalents.length > 0">
        <a-pagination
            v-model:current="state.currentPage"
            v-model:pageSize="state.pageSize"
            :total="totalTalents"
            show-size-changer
            show-quick-jumper
            :show-total="(total) => `共 ${total} 位人才`"
            @change="handlePageChange"
            @showSizeChange="handleSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  UserAddOutlined, UserOutlined, TeamOutlined,
  FilterOutlined, SortAscendingOutlined, SortDescendingOutlined,
  ClockCircleOutlined, AppstoreOutlined, UnorderedListOutlined,
  EyeOutlined, EditOutlined, DeleteOutlined,
  FileTextOutlined, CheckCircleOutlined, ClusterOutlined,
  UploadOutlined, ExportOutlined, TagOutlined,
  EnvironmentOutlined, CalendarOutlined, ApartmentOutlined,
  FileDoneOutlined, RiseOutlined, FileExcelOutlined,
  DownloadOutlined, CopyOutlined
} from '@ant-design/icons-vue'
import { talentApi } from '@/apis/talent_api'
import HeaderComponent from '@/components/HeaderComponent.vue'
import dayjs, { parseToShanghai } from '@/utils/time'

const route = useRoute()
const router = useRouter()
const talents = ref([])
const stats = ref({})

const state = reactive({
  loading: false,
  saving: false,
  showCreateModal: false,
  showBatchModal: false,
  isEdit: false,
  searchKeyword: '',
  currentPage: 1,
  pageSize: 12,
  viewMode: 'card',
  selectAll: false,
  indeterminate: false,
  selectedTalents: [],
  sortField: 'createTime',
  sortOrder: 'desc',
  statusFilter: null,
  currentTalent: {
    id: null,
    name: '',
    employeeId: '',
    department: '',
    position: '',
    level: 'intermediate',
    expertise: [],
    skills: [],
    contact: '',
    email: '',
    location: '',
    joinDate: null,
    status: 'active',
    remarks: ''
  }
})

// 部门选项（云南电网架构）
const departmentOptions = [
  {
    value: 'headquarters',
    label: '总部部门',
    children: [
      { value: 'office', label: '办公室' },
      { value: 'planning', label: '规划部' },
      { value: 'hr', label: '人力资源部' },
      { value: 'finance', label: '财务部' },
    ]
  },
  {
    value: 'production',
    label: '生产部门',
    children: [
      { value: 'dispatching', label: '调度中心' },
      { value: 'power_transmission', label: '输电运检部' },
      { value: 'distribution', label: '配电运检部' },
      { value: 'transformation', label: '变电运检部' },
    ]
  },
  {
    value: 'business',
    label: '业务部门',
    children: [
      { value: 'marketing', label: '市场营销部' },
      { value: 'customer_service', label: '客户服务中心' },
      { value: 'emergency', label: '应急管理部' },
      { value: 'quality', label: '质量管理部' },
    ]
  }
]

// 专业领域选项
const expertiseOptions = [
  { label: '电网规划', value: 'grid_planning' },
  { label: '电力调度', value: 'power_dispatching' },
  { label: '输变电技术', value: 'transmission_technology' },
  { label: '配电自动化', value: 'distribution_automation' },
  { label: '继电保护', value: 'relay_protection' },
  { label: '电力市场', value: 'power_market' },
  { label: '新能源接入', value: 'renewable_energy' },
  { label: '智能电网', value: 'smart_grid' },
  { label: '电力安全', value: 'power_safety' },
  { label: '电力经济', value: 'power_economics' }
]

// 常用技能
const commonSkills = [
  '电网调度', '继电保护', '变电运行', '线路运维',
  '配网自动化', '电力市场', '项目管理', '技术管理',
  '安全生产', '应急处理', '数据分析', '系统规划'
]

// 表格列定义
const tableColumns = [
  {
    title: '姓名',
    key: 'name',
    width: 200
  },
  {
    title: '状态',
    key: 'status',
    width: 100
  },
  {
    title: '级别',
    key: 'level',
    width: 100
  },
  {
    title: '部门',
    key: 'department',
    width: 150
  },
  {
    title: '职位',
    key: 'position',
    width: 150
  },
  {
    title: '技能',
    key: 'skills',
    width: 200
  },
  {
    title: '评分',
    key: 'rating',
    width: 120
  },
  {
    title: '文件',
    key: 'files',
    width: 100
  },
  {
    title: '操作',
    key: 'actions',
    width: 150
  }
]

// 计算属性
const totalTalents = computed(() => talents.value.length)

const displayedTalents = computed(() => {
  let filtered = talents.value

  // 搜索过滤
  if (state.searchKeyword) {
    const keyword = state.searchKeyword.toLowerCase()
    filtered = filtered.filter(talent =>
        talent.name?.toLowerCase().includes(keyword) ||
        talent.position?.toLowerCase().includes(keyword) ||
        talent.department?.toLowerCase().includes(keyword) ||
        (talent.skills?.some(skill => skill.toLowerCase().includes(keyword))) ||
        talent.employeeId?.toLowerCase().includes(keyword)
    )
  }

  // 状态过滤
  if (state.statusFilter) {
    filtered = filtered.filter(talent => talent.status === state.statusFilter)
  }

  // 排序
  filtered = [...filtered].sort((a, b) => {
    let aValue = a[state.sortField]
    let bValue = b[state.sortField]

    if (state.sortField === 'name') {
      aValue = a.name || ''
      bValue = b.name || ''
      return state.sortOrder === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
    }

    if (state.sortField === 'rating') {
      aValue = a.rating || 0
      bValue = b.rating || 0
    }

    if (state.sortField === 'createTime') {
      aValue = parseToShanghai(a.createTime)?.valueOf() || 0
      bValue = parseToShanghai(b.createTime)?.valueOf() || 0
    }

    return state.sortOrder === 'asc' ? aValue - bValue : bValue - aValue
  })

  // 分页
  const start = (state.currentPage - 1) * state.pageSize
  const end = start + state.pageSize
  return filtered.slice(start, end)
})

const skillColor = computed(() => {
  return 'var(--yn-power-blue-100)'
})

const rowSelection = computed(() => ({
  selectedRowKeys: state.selectedTalents,
  onChange: (selectedRowKeys) => {
    state.selectedTalents = selectedRowKeys
    state.indeterminate = !!selectedRowKeys.length && selectedRowKeys.length < talents.value.length
    state.selectAll = selectedRowKeys.length === talents.value.length
  },
  getCheckboxProps: (record) => ({
    disabled: record.status === 'inactive'
  })
}))

// 工具函数
const formatDate = (date) => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD')
}

const formatCreatedTime = (createdAt) => {
  if (!createdAt) return ''
  const parsed = parseToShanghai(createdAt)
  if (!parsed) return ''

  const now = dayjs()
  const diffInHours = now.diff(parsed, 'hour')

  if (diffInHours < 1) {
    return '刚刚'
  }
  if (diffInHours < 24) {
    return `${diffInHours}小时前`
  }
  const diffInDays = now.diff(parsed, 'day')
  if (diffInDays < 7) {
    return `${diffInDays}天前`
  }
  if (diffInDays < 30) {
    return `${Math.floor(diffInDays / 7)}周前`
  }
  return parsed.format('YYYY-MM-DD')
}

const getStatusColor = (status) => {
  const colors = {
    active: 'var(--yn-power-blue-500)',
    probation: 'orange',
    leave: 'blue',
    inactive: 'red'
  }
  return colors[status] || 'default'
}

const getStatusLabel = (status) => {
  const labels = {
    active: '在职',
    probation: '试用期',
    leave: '休假',
    inactive: '离职'
  }
  return labels[status] || '未知'
}

const getLevelLabel = (level) => {
  const labels = {
    junior: '初级',
    intermediate: '中级',
    senior: '高级',
    expert: '专家'
  }
  return labels[level] || level
}

const getRatingColor = (rating) => {
  if (!rating) return 'var(--yn-power-blue-300)'
  if (rating >= 8) return '#52c41a'
  if (rating >= 6) return '#faad14'
  return 'var(--yn-power-blue-500)'
}

const disabledFutureDate = (current) => {
  return current && current > dayjs().endOf('day')
}

// 业务函数
const loadTalents = async () => {
  state.loading = true
  try {
    const data = await talentApi.getTalents()
    let talentList = []

    if (data.talents) {
      talentList = data.talents.map(talent => ({
        ...talent,
        skills: Array.isArray(talent.skills) ? talent.skills : [],
        expertise: Array.isArray(talent.expertise) ? talent.expertise : [],
        fileCount: talent.fileCount || 0,
        parsedCount: talent.parsedCount || 0,
        graphCount: talent.graphCount || 0,
        rating: talent.rating || null
      }))
    } else if (data.files) {
      talentList = data.files.map(file => ({
        id: file.id,
        name: file.employeeInfo?.name || file.filename?.split('.')[0] || '未知',
        employeeId: file.employeeInfo?.employeeId || '',
        department: file.employeeInfo?.department || '',
        position: file.employeeInfo?.position || '',
        skills: file.employeeInfo?.skills || [],
        expertise: file.employeeInfo?.expertise || [],
        contact: file.employeeInfo?.contact || '',
        email: file.employeeInfo?.email || '',
        location: file.employeeInfo?.location || '',
        joinDate: file.employeeInfo?.joinDate || null,
        status: file.employeeInfo?.status || 'active',
        remarks: file.employeeInfo?.remarks || file.description || '',
        createTime: file.uploadTime,
        fileCount: 1,
        parsedCount: file.parsed ? 1 : 0,
        graphCount: file.graphExtracted ? 1 : 0,
        rating: file.rating || null
      }))
    }

    talents.value = talentList.sort((a, b) => {
      const timeA = parseToShanghai(a.createTime)
      const timeB = parseToShanghai(b.createTime)
      if (!timeA && !timeB) return 0
      if (!timeA) return 1
      if (!timeB) return -1
      return timeB.valueOf() - timeA.valueOf()
    })

    // 加载统计数据
    loadStats()
  } catch (error) {
    console.error('加载人才列表失败:', error)
    message.error('加载人才列表失败')
  } finally {
    state.loading = false
  }
}

const loadStats = async () => {
  try {
    const response = await talentApi.getStats()
    stats.value = response.stats || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const resetTalentForm = () => {
  state.currentTalent = {
    id: null,
    name: '',
    employeeId: '',
    department: '',
    position: '',
    level: 'intermediate',
    expertise: [],
    skills: [],
    contact: '',
    email: '',
    location: '',
    joinDate: null,
    status: 'active',
    remarks: ''
  }
}

const createTalent = () => {
  state.isEdit = false
  resetTalentForm()
  state.showCreateModal = true
}

const editTalent = (talent) => {
  state.isEdit = true
  Object.assign(state.currentTalent, {
    ...talent,
    joinDate: talent.joinDate ? dayjs(talent.joinDate) : null
  })
  state.showCreateModal = true
}

const saveTalent = async () => {
  if (!state.currentTalent.name?.trim()) {
    message.error('姓名不能为空')
    return
  }

  if (!state.currentTalent.employeeId?.trim()) {
    message.error('员工编号不能为空')
    return
  }

  state.saving = true
  try {
    const talentData = {
      ...state.currentTalent,
      joinDate: state.currentTalent.joinDate ? dayjs(state.currentTalent.joinDate).format('YYYY-MM-DD') : null
    }

    if (state.isEdit && state.currentTalent.id) {
      await talentApi.updateTalent(state.currentTalent.id, talentData)
      message.success('人才信息更新成功')
    } else {
      await talentApi.createTalent(talentData)
      message.success('人才添加成功')
    }

    state.showCreateModal = false
    resetTalentForm()
    loadTalents()
  } catch (error) {
    console.error('保存人才信息失败:', error)
    message.error(error.message || '保存失败')
  } finally {
    state.saving = false
  }
}

const deleteTalent = async (talentId) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个人才吗？此操作将删除所有相关文件和数据，且不可恢复。',
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await talentApi.deleteTalent(talentId)
        message.success('人才删除成功')

        // 从选中列表中移除
        const index = state.selectedTalents.indexOf(talentId)
        if (index > -1) {
          state.selectedTalents.splice(index, 1)
        }

        loadTalents()
      } catch (error) {
        console.error('删除人才失败:', error)
        message.error(error.message || '删除失败')
      }
    }
  })
}

const viewTalentDetails = (talent) => {
  router.push({ path: `/talent/${talent.id}` })
}

const cancelTalentOperation = () => {
  state.showCreateModal = false
  resetTalentForm()
}

const handleSearch = () => {
  state.currentPage = 1
  // 搜索逻辑已在计算属性中处理
}

const handleSearchClear = () => {
  state.searchKeyword = ''
  state.currentPage = 1
}

const handleFilterClick = ({ key }) => {
  if (key.startsWith('status_')) {
    const status = key.replace('status_', '')
    if (status === 'all') {
      state.statusFilter = null
    } else {
      state.statusFilter = status
    }
    state.currentPage = 1
  }
}

const handleSortClick = ({ key }) => {
  switch (key) {
    case 'sort_time_desc':
      state.sortField = 'createTime'
      state.sortOrder = 'desc'
      break
    case 'sort_time_asc':
      state.sortField = 'createTime'
      state.sortOrder = 'asc'
      break
    case 'sort_name_asc':
      state.sortField = 'name'
      state.sortOrder = 'asc'
      break
    case 'sort_name_desc':
      state.sortField = 'name'
      state.sortOrder = 'desc'
      break
  }
}

const handleSelectAll = (e) => {
  if (e.target.checked) {
    state.selectedTalents = displayedTalents.value.map(talent => talent.id)
    state.indeterminate = false
  } else {
    state.selectedTalents = []
    state.indeterminate = false
  }
}

const handleSelectTalent = (talentId, checked) => {
  const index = state.selectedTalents.indexOf(talentId)
  if (checked && index === -1) {
    state.selectedTalents.push(talentId)
  } else if (!checked && index > -1) {
    state.selectedTalents.splice(index, 1)
  }

  state.indeterminate = !!state.selectedTalents.length && state.selectedTalents.length < talents.value.length
  state.selectAll = state.selectedTalents.length === talents.value.length
}

const handleBatchAction = () => {
  // 批量操作逻辑
  state.showBatchModal = false
}

const handleBatchExport = async () => {
  try {
    const response = await talentApi.exportTalents(state.selectedTalents)
    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `人才列表_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    message.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    message.error('导出失败')
  }
}

const handleBatchAssign = () => {
  message.info('批量分配功能开发中')
}

const handleBatchTag = () => {
  message.info('批量添加标签功能开发中')
}

const handleBatchDelete = async () => {
  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${state.selectedTalents.length} 个人才吗？此操作不可恢复。`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await talentApi.batchDeleteTalents(state.selectedTalents)
        message.success('批量删除成功')
        state.selectedTalents = []
        loadTalents()
      } catch (error) {
        console.error('批量删除失败:', error)
        message.error('批量删除失败')
      }
    }
  })
}

const handleQuickUpload = (talent) => {
  router.push({
    path: `/talent/${talent.id}`,
    query: { showUpload: 'true' }
  })
}

const handleImportExcel = () => {
  message.info('Excel导入功能开发中')
}

const handlePageChange = (page) => {
  state.currentPage = page
}

const handleSizeChange = (current, size) => {
  state.currentPage = 1
  state.pageSize = size
}

watch(() => route.path, (newPath) => {
  if (newPath === '/talent') {
    loadTalents()
  }
})

onMounted(() => {
  loadTalents()
})
</script>

<style lang="less" scoped>
.talent-container {
  padding: 0;
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  padding: 20px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;

  .stat-card {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: #1f1f1f;
          line-height: 1.2;
        }

        .stat-label {
          font-size: 14px;
          color: #666;
          margin-top: 4px;
        }
      }
    }

    &:hover {
      transform: translateY(-2px);
      transition: transform 0.3s;
    }
  }
}

.talents-content {
  padding: 20px;
}

.talents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .talents-info {
    display: flex;
    align-items: center;

    .total-count {
      font-size: 16px;
      color: #333;
      font-weight: 500;
    }
  }

  .view-switcher {
    display: flex;
    align-items: center;
  }
}

.talents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.talent-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;

  &.selected {
    border-color: #1890ff;
    box-shadow: 0 2px 12px rgba(24, 144, 255, 0.2);
  }

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  .card-checkbox {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 1;
  }

  .card-content {
    padding: 20px;
    cursor: pointer;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f0f0;

    .talent-avatar {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 20px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .talent-basic {
      flex: 1;

      .talent-name {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 600;
        color: #1f1f1f;
        line-height: 1.2;
      }

      .talent-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
      }
    }
  }

  .card-body {
    .talent-info {
      margin-bottom: 16px;

      .info-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 14px;
        color: #666;

        &:last-child {
          margin-bottom: 0;
        }

        span {
          flex: 1;
        }
      }
    }

    .skills-section {
      margin-bottom: 16px;

      .skills-title {
        font-size: 14px;
        font-weight: 500;
        color: #333;
        margin-bottom: 8px;
      }

      .skills-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;

        .no-skills {
          color: #bfbfbf;
          font-style: italic;
          font-size: 14px;
        }
      }
    }

    .rating-section {
      margin-bottom: 16px;
      padding: 12px;
      background: #fafafa;
      border-radius: 6px;

      .rating-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 8px;
      }

      .rating-value {
        font-size: 14px;
        font-weight: 500;
        color: #1890ff;
        margin-left: 8px;
      }
    }

    .file-stats {
      display: flex;
      justify-content: space-around;
      padding: 12px;
      background: #f6ffed;
      border-radius: 6px;
      margin-bottom: 16px;

      .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;

        .stat-value {
          font-size: 16px;
          font-weight: 600;
          color: #52c41a;
        }

        .stat-label {
          font-size: 12px;
          color: #666;
        }
      }
    }
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;

    .create-time {
      font-size: 12px;
      color: #999;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .card-actions {
      display: flex;
      gap: 4px;

      .ant-btn {
        padding: 4px;
        width: 32px;
        height: 32px;
      }
    }
  }
}

.talents-table {
  margin-bottom: 20px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  .table-cell-name {
    display: flex;
    align-items: center;
    gap: 12px;

    .avatar-small {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 14px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .name-info {
      .name {
        font-weight: 500;
        color: #333;
        line-height: 1.2;
      }

      .employee-id {
        font-size: 12px;
        color: #999;
        margin-top: 2px;
      }
    }
  }

  .skills-cell {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-wrap: wrap;

    .more-skills {
      font-size: 12px;
      color: #999;
    }
  }

  .rating-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .rating-value {
      font-size: 14px;
      font-weight: 500;
      min-width: 20px;
    }
  }

  .files-cell {
    .file-count {
      font-weight: 500;
      color: #333;
    }

    .file-parsed {
      font-size: 12px;
      color: #52c41a;
    }
  }

  .table-actions {
    display: flex;
    gap: 4px;

    .ant-btn {
      padding: 4px;
      width: 28px;
      height: 28px;
    }
  }

  .text-muted {
    color: #999;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 400px;
  gap: 16px;

  p {
    color: #666;
    margin-top: 12px;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;

  .empty-illustration {
    margin-bottom: 24px;
    opacity: 0.6;
  }

  .empty-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin: 0 0 12px 0;
    letter-spacing: -0.02em;
  }

  .empty-description {
    font-size: 14px;
    color: #666;
    margin: 0 0 32px 0;
    line-height: 1.5;
    max-width: 320px;
  }

  .empty-actions {
    display: flex;
    gap: 12px;
  }
}

.batch-modal-content {
  .batch-selected {
    padding: 12px;
    background: #f6ffed;
    border-radius: 6px;
    text-align: center;
    font-weight: 500;
  }

  .batch-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.talent-modal {
  :deep(.ant-modal-body) {
    max-height: 70vh;
    overflow-y: auto;
    padding: 24px;
  }
}

// 响应式调整
@media (max-width: 768px) {
  .header-tools {
    flex-wrap: wrap;

    .ant-input-search {
      width: 100%;
    }
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .talents-grid {
    grid-template-columns: 1fr;
  }

  .talents-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;

    .view-switcher {
      justify-content: flex-start;
    }
  }
}
</style>