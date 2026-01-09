作为前端专家，现在下面页面代码中有两个问题：一是点击常用搜索后下面的当前筛选：后面没有显示出当前选择的这里内容是空的，修复整个问题代码如下：
<template>
  <div class="talent-search-compare-container layout-container">
    <!-- 顶部导航和搜索区域 -->
    <HeaderComponent title="人才搜索与对比" :loading="state.loading">
      <template #actions>
        <div class="header-tools">
          <!-- 搜索栏 - 新设计 -->
          <div class="unified-search-bar">
            <!-- 常用搜索标签 -->
            <div class="common-search-tags">
              <span class="tags-label">常用搜索：</span>
              <div class="tags-container">
                <a-tag
                    v-for="tag in quickSearchTags"
                    :key="tag.id"
                    class="yn-grid-tag clickable-tag"
                    @click="applyQuickSearch(tag)"
                >
                  <template #icon><TagOutlined /></template>
                  {{ tag.name }}
                </a-tag>
              </div>
            </div>

            <!-- 高级搜索按钮 -->
            <a-button
                class="advanced-search-btn yn-grid-btn-secondary"
                @click="showAdvancedSearchModal"
            >
              <FilterOutlined />
              高级搜索
            </a-button>

            <!-- 搜索框 -->
            <div class="search-input-wrapper">
              <a-input
                  v-model:value="state.searchKeyword"
                  placeholder="搜索人才姓名、职位、技能..."
                  class="yn-grid-search-input"
                  allow-clear
                  @keyup.enter="handleSearch"
                  @clear="handleSearchClear"
              >
                <template #prefix>
                  <SearchOutlined style="color: #999;" />
                </template>
              </a-input>
            </div>

            <!-- 搜索按钮 -->
            <a-button
                type="primary"
                class="search-btn yn-grid-btn-primary"
                @click="handleSearch"
            >
              <SearchOutlined />
              搜索
            </a-button>
          </div>

          <!-- 搜索方案管理 -->
          <a-dropdown>
            <template #overlay>
              <a-menu class="yn-grid-dropdown-menu">
                <a-menu-item key="save_search" @click="saveSearchPreset" class="menu-item">
                  <SaveOutlined style="color: #0066b3;" />
                  <span style="color: #333;">保存当前搜索方案</span>
                </a-menu-item>
                <a-menu-divider style="border-color: #e6f0ff" />
                <div style="max-height: 300px; overflow-y: auto">
                  <a-menu-item-group title="常用搜索方案" class="menu-group">
                    <a-menu-item
                        v-for="preset in searchPresets"
                        :key="preset.id"
                        @click="applySearchPreset(preset)"
                        class="menu-item"
                    >
                      <div style="display: flex; justify-content: space-between; width: 100%">
                        <span style="color: #333;">{{ preset.name }}</span>
                        <a-tag v-if="preset.isDefault" color="#0066b3" size="small" style="color: white;">默认</a-tag>
                      </div>
                    </a-menu-item>
                  </a-menu-item-group>
                </div>
              </a-menu>
            </template>
            <a-button class="yn-grid-btn-secondary">
              <SaveOutlined />
              搜索方案
            </a-button>
          </a-dropdown>
        </div>
      </template>
    </HeaderComponent>

    <!-- 已选筛选条件展示 -->
    <div class="active-filters-bar" v-if="hasActiveFilters">
      <div class="filters-label">
        <FilterOutlined style="margin-right: 6px;" />
        当前筛选：
      </div>
      <div class="filters-tags">
        <a-tag
            v-for="filter in activeFilters"
            :key="filter.key"
            closable
            @close="removeFilter(filter.key)"
            class="yn-grid-tag active-filter-tag"
        >
          <CloseCircleOutlined style="margin-right: 4px;" />
          {{ filter.label }}: {{ filter.value }}
        </a-tag>
        <a-button type="link" size="small" @click="clearAllFilters" class="clear-all-btn">
          <DeleteOutlined />
          清空所有
        </a-button>
      </div>
    </div>

    <!-- 高级搜索模态框 -->
    <a-modal
        v-model:open="state.showAdvancedModal"
        title="高级搜索"
        width="800px"
        :footer="null"
        class="advanced-search-modal"
        :styles="{
        body: {
          padding: '20px 24px',
          maxHeight: '70vh',
          overflowY: 'auto'
        }
      }"
    >
      <div class="advanced-search-content">
        <!-- 基础信息 -->
        <div class="search-section">
          <div class="section-header">
            <TeamOutlined style="color: #0066b3; margin-right: 8px;" />
            <span class="section-title">基础信息</span>
          </div>
          <div class="search-fields">
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">公司</label>
                <a-select
                    v-model:value="state.advancedFilters.company"
                    placeholder="请选择公司"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="yunnan_grid">云南电网有限责任公司</a-select-option>
                  <a-select-option value="kunming">昆明供电局</a-select-option>
                  <a-select-option value="qujing">曲靖供电局</a-select-option>
                  <a-select-option value="yuxi">玉溪供电局</a-select-option>
                  <a-select-option value="chuxiong">楚雄供电局</a-select-option>
                </a-select>
              </div>

              <div class="field-group">
                <label class="field-label">部门</label>
                <a-select
                    v-model:value="state.advancedFilters.department"
                    placeholder="请选择部门"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option v-for="dept in departmentOptions" :key="dept.value" :value="dept.value">
                    {{ dept.label }}
                  </a-select-option>
                </a-select>
              </div>
            </div>

            <div class="field-row">
              <div class="field-group">
                <label class="field-label">年龄范围</label>
                <div class="range-inputs">
                  <a-input-number
                      v-model:value="state.advancedFilters.ageMin"
                      placeholder="最小"
                      :min="18"
                      :max="60"
                      @change="handleFilterChange"
                      class="yn-grid-input"
                  />
                  <span class="range-separator">至</span>
                  <a-input-number
                      v-model:value="state.advancedFilters.ageMax"
                      placeholder="最大"
                      :min="18"
                      :max="60"
                      @change="handleFilterChange"
                      class="yn-grid-input"
                  />
                </div>
              </div>

              <div class="field-group">
                <label class="field-label">最高学历</label>
                <a-select
                    v-model:value="state.advancedFilters.education"
                    placeholder="请选择学历"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="college">大专</a-select-option>
                  <a-select-option value="bachelor">本科</a-select-option>
                  <a-select-option value="master">硕士</a-select-option>
                  <a-select-option value="doctor">博士</a-select-option>
                </a-select>
              </div>
            </div>
          </div>
        </div>

        <!-- 工作经历 -->
        <div class="search-section">
          <div class="section-header">
            <ScheduleOutlined style="color: #0066b3; margin-right: 8px;" />
            <span class="section-title">工作经历</span>
          </div>
          <div class="search-fields">
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">司龄范围</label>
                <div class="range-inputs">
                  <a-input-number
                      v-model:value="state.advancedFilters.companyTenureMin"
                      placeholder="最小"
                      :min="0"
                      :max="40"
                      @change="handleFilterChange"
                      class="yn-grid-input"
                  />
                  <span class="range-separator">至</span>
                  <a-input-number
                      v-model:value="state.advancedFilters.companyTenureMax"
                      placeholder="最大"
                      :min="0"
                      :max="40"
                      @change="handleFilterChange"
                      class="yn-grid-input"
                  />
                </div>
              </div>

              <div class="field-group">
                <label class="field-label">职务类型</label>
                <a-select
                    v-model:value="state.advancedFilters.positionType"
                    placeholder="请选择职务类型"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="management">管理</a-select-option>
                  <a-select-option value="technical">技术</a-select-option>
                  <a-select-option value="business">业务</a-select-option>
                  <a-select-option value="support">支持</a-select-option>
                </a-select>
              </div>
            </div>
          </div>
        </div>

        <!-- 绩效标签 -->
        <div class="search-section">
          <div class="section-header">
            <RiseOutlined style="color: #0066b3; margin-right: 8px;" />
            <span class="section-title">绩效标签</span>
          </div>
          <div class="search-fields">
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">绩效等级</label>
                <a-select
                    v-model:value="state.advancedFilters.performance"
                    placeholder="请选择绩效等级"
                    mode="multiple"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="A" style="color: #0066b3">A（优秀）</a-select-option>
                  <a-select-option value="B" style="color: #0066b3">B（良好）</a-select-option>
                  <a-select-option value="C" style="color: #666">C（合格）</a-select-option>
                  <a-select-option value="D" style="color: #999">D（待改进）</a-select-option>
                </a-select>
              </div>

              <div class="field-group">
                <label class="field-label">人才层级</label>
                <a-select
                    v-model:value="state.advancedFilters.talentLevel"
                    placeholder="请选择人才层级"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="high_potential" style="color: #0066b3">高潜人才</a-select-option>
                  <a-select-option value="key_talent" style="color: #0066b3">关键人才</a-select-option>
                  <a-select-option value="backup" style="color: #666">后备人才</a-select-option>
                </a-select>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="modal-actions">
          <a-button @click="resetAdvancedFilters" class="yn-grid-btn-secondary">
            <RedoOutlined />
            重置条件
          </a-button>
          <a-space :size="16">
            <a-button @click="state.showAdvancedModal = false">
              取消
            </a-button>
            <a-button
                type="primary"
                @click="applyAdvancedSearch"
                class="yn-grid-btn-primary"
            >
              <CheckOutlined />
              应用筛选 ({{ totalTalents }})
            </a-button>
          </a-space>
        </div>
      </div>
    </a-modal>

    <!-- 统计卡片 -->
    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="!state.loading && displayedTalents.length > 0">
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6f0ff, #f0f5ff);">
            <TeamOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ displayedTalents.length }}</div>
            <div class="stat-label">搜索结果</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6f7ff, #f0f5ff);">
            <StarOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ highPotentialCount }}</div>
            <div class="stat-label">高潜人才</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f0f5ff, #e6f0ff);">
            <RiseOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ averagePerformance }}</div>
            <div class="stat-label">平均绩效</div>
          </div>
        </div>
      </a-card>
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f0f5ff, #e6f0ff);">
            <CrownOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ keyTalentCount }}</div>
            <div class="stat-label">关键人才</div>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 搜索结果区域 -->
    <div class="search-results" v-if="!state.loading && displayedTalents.length > 0">
      <!-- 搜索结果头部 -->
      <!-- 搜索结果头部 -->
      <div class="results-header yn-grid-card">
        <div class="results-info">
          <span class="total-count" style="color: #0066b3;">找到 {{ totalTalents }} 位匹配人才</span>
          <span class="match-info" v-if="state.searchKeyword" style="color: #666;">
      匹配关键词："<span style="color: #0066b3; font-weight: 500;">{{ state.searchKeyword }}</span>"
    </span>
        </div>
        <div class="results-actions">
          <!-- 所有操作按钮放在右侧 -->
          <div class="action-group">
            <!-- 选中人数提示 -->
            <div class="selected-info" v-if="state.selectedTalents.length > 0">
        <span class="selected-count" :class="{ 'exceed-limit': state.selectedTalents.length > 5 }">
          已选中 {{ state.selectedTalents.length }} 人
          <span v-if="state.selectedTalents.length > 5" class="limit-warning">(最多5人)</span>
        </span>
            </div>

            <!-- 全选复选框 -->
            <div class="select-all-wrapper">
              <a-checkbox
                  v-model:checked="state.selectAll"
                  @change="handleSelectAll"
                  :indeterminate="state.indeterminate"
                  class="yn-grid-checkbox"
              >
                全选
              </a-checkbox>
            </div>

            <!-- 添加到对比按钮 -->
            <div class="action-button-wrapper">
              <a-tooltip v-if="state.selectedTalents.length > 5" title="最多只能选择5人进行对比">
                <a-button
                    size="small"
                    class="yn-grid-btn-secondary disabled-btn"
                >
                  <BarChartOutlined />
                  添加到对比
                </a-button>
              </a-tooltip>
              <a-button
                  v-else
                  size="small"
                  @click="handleAddToCompare"
                  :disabled="state.selectedTalents.length === 0"
                  class="yn-grid-btn-secondary"
              >
                <BarChartOutlined />
                添加到对比
              </a-button>
            </div>

            <!-- 对比选中按钮 -->
            <div class="action-button-wrapper">
              <a-tooltip v-if="state.selectedTalents.length > 5" title="最多只能选择5人进行对比">
                <a-button
                    type="primary"
                    size="small"
                    class="yn-grid-btn-primary disabled-btn"
                >
                  <SwapOutlined />
                  开始对比
                </a-button>
              </a-tooltip>
              <a-button
                  v-else
                  type="primary"
                  size="small"
                  @click="handleCompareNow"
                  :disabled="state.selectedTalents.length < 2"
                  class="yn-grid-btn-primary"
              >
                <SwapOutlined />
                开始对比
              </a-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 视图切换 -->
      <div class="view-controls yn-grid-card">
        <div class="view-switcher">
          <a-radio-group v-model:value="state.viewMode" button-style="solid" size="small" class="yn-grid-view-switch">
            <a-radio-button value="card" class="view-btn">
              <AppstoreOutlined />
              卡片视图
            </a-radio-button>
            <a-radio-button value="list" class="view-btn">
              <UnorderedListOutlined />
              列表视图
            </a-radio-button>
          </a-radio-group>
        </div>

        <!-- 排序选项 -->
        <div class="sort-controls">
          <a-select
              v-model:value="state.sortField"
              style="width: 140px"
              size="small"
              @change="handleSortChange"
              class="yn-grid-select"
          >
            <a-select-option value="relevance">相关度排序</a-select-option>
            <a-select-option value="performance">绩效排序</a-select-option>
            <a-select-option value="age">年龄排序</a-select-option>
            <a-select-option value="companyTenure">司龄排序</a-select-option>
          </a-select>
          <a-button
              size="small"
              @click="toggleSortOrder"
              style="margin-left: 8px"
              class="yn-grid-btn-secondary sort-order-btn"
          >
            <template #icon>
              <SortAscendingOutlined v-if="state.sortOrder === 'asc'" />
              <SortDescendingOutlined v-else />
            </template>
          </a-button>
        </div>
      </div>

      <!-- 卡片视图 -->
      <div v-if="state.viewMode === 'card'" class="talent-cards-grid">
        <div
            v-for="talent in displayedTalents"
            :key="talent.id"
            class="talent-search-card yn-grid-card"
            :class="{
              'selected': state.selectedTalents.includes(talent.id),
              'in-comparison': isInComparisonList(talent.id)
            }"
        >
          <div class="card-header">
            <div class="selection-control">
              <!-- 超过5人时禁用选择 -->
              <a-tooltip v-if="state.selectedTalents.length >= 5 && !state.selectedTalents.includes(talent.id)"
                         title="已达到最大选择人数(5人)">
                <a-checkbox
                    :checked="false"
                    disabled
                    class="yn-grid-checkbox"
                />
              </a-tooltip>
              <a-checkbox
                  v-else
                  :checked="state.selectedTalents.includes(talent.id)"
                  @change="(e) => handleSelectTalent(talent.id, e.target.checked)"
                  class="yn-grid-checkbox"
              />
            </div>
            <div class="talent-basic-info" @click="viewTalentDetails(talent)">
              <div class="talent-avatar" :style="getAvatarStyle(talent)">
                {{ talent.name?.charAt(0) || '?' }}
              </div>
              <div class="talent-meta">
                <h4 class="talent-name" style="color: #0066b3;">{{ talent.name }}</h4>
                <div class="talent-tags">
                  <a-tag :color="getStatusColor(talent.status)" size="small" class="yn-grid-tag">
                    {{ getStatusLabel(talent.status) }}
                  </a-tag>
                  <a-tag v-if="talent.level" :color="getLevelColor(talent.level)" size="small" class="yn-grid-tag">
                    {{ getLevelLabel(talent.level) }}
                  </a-tag>
                  <a-tag v-if="talent.isHighPotential" color="#0066b3" size="small" class="yn-grid-tag high-potential-tag">
                    <StarOutlined style="margin-right: 2px;" />
                    高潜人才
                  </a-tag>
                </div>
              </div>
            </div>
            <div class="card-actions">
              <a-button
                  type="link"
                  size="small"
                  @click="toggleComparison(talent)"
                  :class="{ 'in-comparison': isInComparisonList(talent.id) }"
                  class="compare-btn"
              >
                <template #icon>
                  <PlusCircleOutlined v-if="!isInComparisonList(talent.id)" />
                  <CheckCircleOutlined v-else style="color: #0066b3;" />
                </template>
                {{ isInComparisonList(talent.id) ? '已加入' : '加入对比' }}
              </a-button>
            </div>
          </div>

          <div class="card-body" @click="viewTalentDetails(talent)">
            <!-- 匹配度评分 -->
            <div class="match-score" v-if="talent.matchScore">
              <a-progress
                  type="circle"
                  :percent="talent.matchScore"
                  :stroke-color="getMatchScoreColor(talent.matchScore)"
                  :width="60"
                  class="yn-grid-progress"
              />
              <div class="match-info">
                <div class="match-value" style="color: #0066b3;">{{ talent.matchScore }}%</div>
                <div class="match-label">匹配度</div>
              </div>
            </div>

            <!-- 关键信息 -->
            <div class="key-info">
              <div class="info-row">
                <span class="info-label">职位:</span>
                <span class="info-value" style="color: #333;">{{ talent.position || '未设置' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">部门:</span>
                <span class="info-value" style="color: #333;">{{ talent.department || '未设置' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">司龄:</span>
                <span class="info-value" style="color: #0066b3; font-weight: 500;">{{ talent.companyTenure || 0 }}年</span>
              </div>
              <div class="info-row">
                <span class="info-label">绩效:</span>
                <span class="info-value">
                  <a-tag :color="getPerformanceColor(talent.performance)" size="small" class="yn-grid-tag">
                    {{ talent.performance || '未评估' }}
                  </a-tag>
                </span>
              </div>
            </div>

            <!-- 技能标签 -->
            <div class="skills-section">
              <div class="skills-label">核心技能:</div>
              <div class="skills-tags">
                <a-tag
                    v-for="skill in (talent.skills || []).slice(0, 4)"
                    :key="skill"
                    size="small"
                    class="yn-grid-tag skill-tag"
                >
                  {{ skill }}
                </a-tag>
                <span v-if="talent.skills && talent.skills.length > 4" class="more-skills">
                  +{{ talent.skills.length - 4 }}
                </span>
              </div>
            </div>

            <!-- 人才画像标签 -->
            <div class="profile-tags" v-if="talent.profileTags && talent.profileTags.length > 0">
              <a-tag
                  v-for="tag in talent.profileTags"
                  :key="tag"
                  color="#0066b3"
                  size="small"
                  class="yn-grid-tag profile-tag"
              >
                {{ tag }}
              </a-tag>
            </div>
          </div>

          <div class="card-footer">
            <div class="action-buttons">
              <a-button
                  type="link"
                  size="small"
                  @click="viewTalentDetails(talent)"
                  class="yn-grid-link-btn"
              >
                <EyeOutlined />
                查看详情
              </a-button>
              <a-button
                  type="link"
                  size="small"
                  @click="editTalent(talent)"
                  class="yn-grid-link-btn"
              >
                <EditOutlined />
                编辑
              </a-button>
              <a-button
                  type="link"
                  size="small"
                  @click="addToTalentPool(talent)"
                  class="yn-grid-link-btn"
              >
                <FolderAddOutlined />
                加入人才库
              </a-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="talent-list-table">
        <a-table
            :data-source="displayedTalents"
            :row-selection="rowSelection"
            :columns="searchTableColumns"
            :pagination="false"
            row-key="id"
            size="middle"
            :row-class-name="getRowClassName"
            class="yn-grid-table"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'selection'">
              <div class="table-selection">
                <!-- 超过5人时禁用选择 -->
                <a-tooltip v-if="state.selectedTalents.length >= 5 && !state.selectedTalents.includes(record.id)"
                           title="已达到最大选择人数(5人)">
                  <a-checkbox
                      :checked="false"
                      disabled
                      class="yn-grid-checkbox"
                  />
                </a-tooltip>
                <a-checkbox
                    v-else
                    :checked="state.selectedTalents.includes(record.id)"
                    @change="(e) => handleSelectTalent(record.id, e.target.checked)"
                    class="yn-grid-checkbox"
                />
                <a-button
                    type="link"
                    size="small"
                    @click="toggleComparison(record)"
                    :class="{ 'in-comparison': isInComparisonList(record.id) }"
                    class="compare-btn"
                >
                  <template #icon>
                    <PlusCircleOutlined v-if="!isInComparisonList(record.id)" />
                    <CheckCircleOutlined v-else style="color: #0066b3;" />
                  </template>
                </a-button>
              </div>
            </template>

            <template v-if="column.key === 'name'">
              <div class="table-cell-name" @click="viewTalentDetails(record)">
                <div class="avatar-small" :style="getAvatarStyle(record)">
                  {{ record.name?.charAt(0) || '?' }}
                </div>
                <div class="name-info">
                  <div class="name" style="color: #0066b3; font-weight: 500;">{{ record.name }}</div>
                  <div class="employee-id">#{{ record.employeeId }}</div>
                </div>
              </div>
            </template>

            <template v-if="column.key === 'matchScore'">
              <div class="match-score-cell">
                <a-progress
                    type="circle"
                    :percent="record.matchScore || 0"
                    :stroke-color="getMatchScoreColor(record.matchScore || 0)"
                    :width="40"
                    class="yn-grid-progress"
                />
              </div>
            </template>

            <template v-if="column.key === 'status'">
              <div class="status-cell">
                <a-tag :color="getStatusColor(record.status)" size="small" class="yn-grid-tag">
                  {{ getStatusLabel(record.status) }}
                </a-tag>
                <div v-if="record.isHighPotential" style="margin-top: 4px;">
                  <a-tag color="#0066b3" size="small" class="yn-grid-tag">
                    <StarOutlined style="margin-right: 2px;" />
                    高潜人才
                  </a-tag>
                </div>
              </div>
            </template>

            <template v-if="column.key === 'performance'">
              <div class="performance-cell">
                <a-progress
                    :percent="getPerformancePercent(record.performance)"
                    :stroke-color="getPerformanceColor(record.performance)"
                    size="small"
                    :show-info="false"
                    style="width: 60px;"
                    class="yn-grid-progress"
                />
                <span class="performance-value">{{ record.performance || '未评估' }}</span>
              </div>
            </template>

            <template v-if="column.key === 'skills'">
              <div class="skills-cell">
                <a-tag
                    v-for="skill in (record.skills || []).slice(0, 2)"
                    :key="skill"
                    size="small"
                    class="yn-grid-tag skill-tag"
                >
                  {{ skill }}
                </a-tag>
                <span v-if="record.skills && record.skills.length > 2" class="more-skills">
                  +{{ record.skills.length - 2 }}
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
                      class="yn-grid-link-btn"
                  >
                    <EyeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="加入对比">
                  <a-button
                      type="link"
                      size="small"
                      @click="toggleComparison(record)"
                      :class="{ 'in-comparison': isInComparisonList(record.id) }"
                      class="yn-grid-link-btn compare-btn"
                  >
                    <template #icon>
                      <PlusCircleOutlined v-if="!isInComparisonList(record.id)" />
                      <CheckCircleOutlined v-else style="color: #0066b3;" />
                    </template>
                  </a-button>
                </a-tooltip>
                <a-tooltip title="加入人才库">
                  <a-button
                      type="link"
                      size="small"
                      @click="addToTalentPool(record)"
                      class="yn-grid-link-btn"
                  >
                    <FolderAddOutlined />
                  </a-button>
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
            :show-total="(total) => `共 ${total} 条结果`"
            @change="handlePageChange"
            @showSizeChange="handleSizeChange"
            class="yn-grid-pagination"
        />
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!state.loading" class="search-empty-state yn-grid-card">
      <div class="empty-illustration">
        <SearchOutlined style="font-size: 80px; color: #0066b3; opacity: 0.3;" />
      </div>
      <h3 class="empty-title" style="color: #333;">没有找到匹配的人才</h3>
      <p class="empty-description" style="color: #666;">
        {{
          state.searchKeyword
              ? `没有找到包含"${state.searchKeyword}"的人才`
              : '请尝试不同的搜索条件或筛选条件'
        }}
      </p>
      <div class="empty-actions">
        <a-button @click="resetSearch" style="margin-right: 12px;" class="yn-grid-btn-secondary">
          <RedoOutlined />
          重置搜索条件
        </a-button>
        <a-button type="primary" @click="state.searchMode = 'advanced'" class="yn-grid-btn-primary">
          <FilterOutlined />
          使用高级搜索
        </a-button>
      </div>
    </div>

    <!-- 保存搜索方案模态框 -->
    <a-modal
        v-model:open="state.showSaveSearchModal"
        title="保存搜索方案"
        @ok="saveSearchPresetConfirm"
        @cancel="state.showSaveSearchModal = false"
        width="400px"
        class="yn-grid-modal"
        :styles="{ body: { padding: '20px 0' } }"
    >
      <a-form :model="state.newSearchPreset" layout="vertical" class="yn-grid-form">
        <a-form-item label="方案名称" required>
          <a-input
              v-model:value="state.newSearchPreset.name"
              placeholder="请输入搜索方案名称"
              class="yn-grid-input"
          />
        </a-form-item>
        <a-form-item label="设为默认方案">
          <a-switch v-model:checked="state.newSearchPreset.isDefault" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea
              v-model:value="state.newSearchPreset.description"
              placeholder="请输入方案描述"
              :rows="3"
              class="yn-grid-textarea"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 对比页面的浮动按钮 -->
    <div class="floating-comparison-button" v-if="comparisonStore.comparisonList.length > 0">
      <a-badge :count="comparisonStore.comparisonList.length" :offset="[-5, 5]" class="yn-grid-badge">
        <a-button
            type="primary"
            shape="circle"
            size="large"
            @click="gotoComparison"
            class="floating-button yn-grid-floating-btn"
        >
          <BarChartOutlined style="font-size: 20px;" />
        </a-button>
      </a-badge>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { useComparisonStore } from '@/stores/comparison'
import {
  FilterOutlined, SortAscendingOutlined, SortDescendingOutlined,
  TeamOutlined, CheckCircleOutlined, RiseOutlined,
  StarOutlined, BarChartOutlined, SwapOutlined,
  SaveOutlined, DeleteOutlined, EyeOutlined,
  EditOutlined, FolderAddOutlined, AppstoreOutlined,
  UnorderedListOutlined, PlusCircleOutlined, SearchOutlined,
  DownOutlined, CloseCircleOutlined, CrownOutlined,
  TagOutlined, RedoOutlined, CheckOutlined,
  ScheduleOutlined, DeleteOutlined as DeleteIcon
} from '@ant-design/icons-vue'
import { talentApi } from '@/apis/talent_api'
import HeaderComponent from '@/components/HeaderComponent.vue'
import dayjs, { parseToShanghai } from '@/utils/time'

const route = useRoute()
const router = useRouter()
const comparisonStore = useComparisonStore()


const talents = ref([])
const searchPresets = ref([
  {
    id: 'high_potential',
    name: '高潜人才搜索',
    isDefault: true,
    description: '年龄段25-35+本科以上+绩效A/B+司龄2年以上',
    criteria: {
      ageMin: 25,
      ageMax: 35,
      education: ['bachelor', 'master', 'doctor'],
      performance: ['A', 'B'],
      companyTenureMin: 2,
      talentLevel: 'high_potential'
    }
  },
  {
    id: 'key_talent',
    name: '关键人才搜索',
    description: '关键岗位+5年以上经验+绩效B级以上',
    criteria: {
      positionType: ['management', 'technical'],
      companyTenureMin: 5,
      performance: ['A', 'B'],
      talentLevel: 'key_talent'
    }
  },
  {
    id: 'new_employees',
    name: '新员工搜索',
    description: '入职2年内+绩效B以上',
    criteria: {
      companyTenureMax: 2,
      performance: ['A', 'B']
    }
  }
])

const quickSearchTags = [
  { id: 'tag_high_potential', name: '高潜人才', criteria: { talentLevel: 'high_potential' } },
  { id: 'tag_key_talent', name: '关键人才', criteria: { talentLevel: 'key_talent' } },
  { id: 'tag_manager', name: '管理人员', criteria: { positionType: 'management' } },
  { id: 'tag_technical', name: '技术专家', criteria: { positionType: 'technical' } },
  { id: 'tag_new', name: '新入职员工', criteria: { companyTenureMax: 1 } },
  { id: 'tag_experienced', name: '资深员工', criteria: { companyTenureMin: 10 } }
]

const state = reactive({
  loading: false,
  searchKeyword: '',
  advancedFilters: {
    company: null,
    department: null,
    ageMin: null,
    ageMax: null,
    education: null,
    companyTenureMin: null,
    companyTenureMax: null,
    positionType: null,
    performance: [],
    talentLevel: null
  },
  currentPage: 1,
  pageSize: 12,
  viewMode: 'card',
  selectAll: false,
  indeterminate: false,
  selectedTalents: [],
  sortField: 'relevance',
  sortOrder: 'desc',
  showSaveSearchModal: false,
  showAdvancedModal: false, // 新增：控制高级搜索模态框
  newSearchPreset: {
    name: '',
    description: '',
    isDefault: false
  }
})


// 部门选项 - 云南电网架构
const departmentOptions = [
  { value: 'headquarters', label: '总部部门' },
  { value: 'office', label: '办公室' },
  { value: 'planning', label: '规划部' },
  { value: 'hr', label: '人力资源部' },
  { value: 'production', label: '生产部门' },
  { value: 'dispatching', label: '调度中心' },
  { value: 'power_transmission', label: '输电运检部' },
  { value: 'distribution', label: '配电运检部' },
  { value: 'transformation', label: '变电运检部' },
  { value: 'marketing', label: '市场营销部' },
  { value: 'customer_service', label: '客户服务中心' }
]

// 表格列定义 - 搜索版本
const searchTableColumns = [
  {
    title: '选择',
    key: 'selection',
    width: 80,
    fixed: 'left'
  },
  {
    title: '姓名',
    key: 'name',
    width: 180,
    fixed: 'left'
  },
  {
    title: '匹配度',
    key: 'matchScore',
    width: 100
  },
  {
    title: '状态',
    key: 'status',
    width: 120
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
    title: '司龄',
    key: 'companyTenure',
    width: 100
  },
  {
    title: '绩效',
    key: 'performance',
    width: 120
  },
  {
    title: '技能',
    key: 'skills',
    width: 200
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right'
  }
]

// 计算属性
const totalTalents = computed(() => {
  return filteredTalents.value.length
})

const filteredTalents = computed(() => {
  let filtered = talents.value

  // 基础搜索
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

  // 高级筛选
  if (state.advancedFilters.company) {
    filtered = filtered.filter(talent => talent.company === state.advancedFilters.company)
  }

  if (state.advancedFilters.department) {
    filtered = filtered.filter(talent => talent.department === state.advancedFilters.department)
  }

  if (state.advancedFilters.ageMin !== null) {
    filtered = filtered.filter(talent => talent.age >= state.advancedFilters.ageMin)
  }

  if (state.advancedFilters.ageMax !== null) {
    filtered = filtered.filter(talent => talent.age <= state.advancedFilters.ageMax)
  }

  if (state.advancedFilters.education) {
    filtered = filtered.filter(talent => talent.education === state.advancedFilters.education)
  }

  if (state.advancedFilters.companyTenureMin !== null) {
    filtered = filtered.filter(talent => talent.companyTenure >= state.advancedFilters.companyTenureMin)
  }

  if (state.advancedFilters.companyTenureMax !== null) {
    filtered = filtered.filter(talent => talent.companyTenure <= state.advancedFilters.companyTenureMax)
  }

  if (state.advancedFilters.positionType) {
    filtered = filtered.filter(talent => talent.positionType === state.advancedFilters.positionType)
  }

  if (state.advancedFilters.performance.length > 0) {
    filtered = filtered.filter(talent =>
        state.advancedFilters.performance.includes(talent.performance)
    )
  }

  if (state.advancedFilters.talentLevel) {
    filtered = filtered.filter(talent =>
        talent.profileTags?.includes(state.advancedFilters.talentLevel === 'high_potential' ? '高潜人才' :
            state.advancedFilters.talentLevel === 'key_talent' ? '关键人才' : '后备人才')
    )
  }

  return filtered
})

const displayedTalents = computed(() => {
  // 计算匹配度
  const talentsWithScore = filteredTalents.value.map(talent => {
    let matchScore = 0
    let matchReasons = []

    // 关键词匹配
    if (state.searchKeyword) {
      const keyword = state.searchKeyword.toLowerCase()
      if (talent.name?.toLowerCase().includes(keyword)) {
        matchScore += 30
        matchReasons.push('姓名匹配')
      }
      if (talent.position?.toLowerCase().includes(keyword)) {
        matchScore += 20
        matchReasons.push('职位匹配')
      }
      if (talent.skills?.some(skill => skill.toLowerCase().includes(keyword))) {
        matchScore += 25
        matchReasons.push('技能匹配')
      }
    }

    // 高级筛选匹配
    if (state.advancedFilters.ageMin !== null || state.advancedFilters.ageMax !== null) {
      const ageInRange = (!state.advancedFilters.ageMin || talent.age >= state.advancedFilters.ageMin) &&
          (!state.advancedFilters.ageMax || talent.age <= state.advancedFilters.ageMax)
      if (ageInRange) matchScore += 10
    }

    if (state.advancedFilters.performance.length > 0) {
      if (state.advancedFilters.performance.includes(talent.performance)) {
        matchScore += 15
      }
    }

    // 限制匹配度在0-100之间
    matchScore = Math.min(100, matchScore)

    return {
      ...talent,
      matchScore,
      matchReasons
    }
  })

  // 排序
  let sorted = [...talentsWithScore]

  switch (state.sortField) {
    case 'relevance':
      sorted.sort((a, b) => {
        const scoreDiff = b.matchScore - a.matchScore
        if (scoreDiff !== 0) return state.sortOrder === 'desc' ? scoreDiff : -scoreDiff
        return b.createTime - a.createTime
      })
      break
    case 'performance':
      sorted.sort((a, b) => {
        const perfA = getPerformanceValue(a.performance)
        const perfB = getPerformanceValue(b.performance)
        return state.sortOrder === 'desc' ? perfB - perfA : perfA - perfB
      })
      break
    case 'age':
      sorted.sort((a, b) => {
        return state.sortOrder === 'desc' ? b.age - a.age : a.age - b.age
      })
      break
    case 'companyTenure':
      sorted.sort((a, b) => {
        return state.sortOrder === 'desc' ? b.companyTenure - a.companyTenure : a.companyTenure - b.companyTenure
      })
      break
  }

  // 分页
  const start = (state.currentPage - 1) * state.pageSize
  const end = start + state.pageSize
  return sorted.slice(start, end)
})

const highPotentialCount = computed(() => {
  return filteredTalents.value.filter(talent => talent.profileTags?.includes('高潜人才')).length
})

const keyTalentCount = computed(() => {
  return filteredTalents.value.filter(talent => talent.profileTags?.includes('关键人才')).length
})

const averagePerformance = computed(() => {
  const talentsWithPerformance = filteredTalents.value.filter(t => t.performance)
  if (talentsWithPerformance.length === 0) return '未评估'

  const total = talentsWithPerformance.reduce((sum, talent) => {
    return sum + getPerformanceValue(talent.performance)
  }, 0)

  const avg = total / talentsWithPerformance.length
  return avg.toFixed(1)
})

// 修复 hasActiveFilters 计算属性
const hasActiveFilters = computed(() => {
  return state.searchKeyword.trim() !== '' ||
      Object.keys(state.advancedFilters).some(key => {
        const value = state.advancedFilters[key]
        if (Array.isArray(value)) {
          return value.length > 0
        }
        return value !== null && value !== undefined && value !== ''
      })
})

// 修复 activeFilters 计算属性
const activeFilters = computed(() => {
  const filters = []

  // 搜索关键词
  if (state.searchKeyword.trim()) {
    filters.push({
      key: 'searchKeyword',
      label: '关键词',
      value: state.searchKeyword
    })
  }

  // 公司筛选
  if (state.advancedFilters.company) {
    filters.push({
      key: 'company',
      label: '公司',
      value: getCompanyLabel(state.advancedFilters.company)
    })
  }

  // 部门筛选
  if (state.advancedFilters.department) {
    const dept = departmentOptions.find(d => d.value === state.advancedFilters.department)
    if (dept) {
      filters.push({
        key: 'department',
        label: '部门',
        value: dept.label
      })
    }
  }

  // 年龄范围筛选
  if (state.advancedFilters.ageMin !== null || state.advancedFilters.ageMax !== null) {
    const min = state.advancedFilters.ageMin !== null ? `${state.advancedFilters.ageMin}岁` : ''
    const max = state.advancedFilters.ageMax !== null ? `${state.advancedFilters.ageMax}岁` : ''
    const ageStr = min && max ? `${min}-${max}` : min || max
    filters.push({
      key: 'age',
      label: '年龄',
      value: ageStr
    })
  }

  // 学历筛选
  if (state.advancedFilters.education) {
    filters.push({
      key: 'education',
      label: '学历',
      value: getEducationLabel(state.advancedFilters.education)
    })
  }

  // 司龄范围筛选
  if (state.advancedFilters.companyTenureMin !== null || state.advancedFilters.companyTenureMax !== null) {
    const min = state.advancedFilters.companyTenureMin !== null ? `${state.advancedFilters.companyTenureMin}年` : ''
    const max = state.advancedFilters.companyTenureMax !== null ? `${state.advancedFilters.companyTenureMax}年` : ''
    const tenureStr = min && max ? `${min}-${max}` : min || max
    filters.push({
      key: 'companyTenure',
      label: '司龄',
      value: tenureStr
    })
  }

  // 职务类型筛选
  if (state.advancedFilters.positionType) {
    const positionTypes = {
      management: '管理',
      technical: '技术',
      business: '业务',
      support: '支持'
    }
    filters.push({
      key: 'positionType',
      label: '职务类型',
      value: positionTypes[state.advancedFilters.positionType] || state.advancedFilters.positionType
    })
  }

  // 绩效筛选（可能是数组）
  if (state.advancedFilters.performance && state.advancedFilters.performance.length > 0) {
    const performanceLabels = {
      'A': 'A（优秀）',
      'B': 'B（良好）',
      'C': 'C（合格）',
      'D': 'D（待改进）'
    }
    const performanceValues = state.advancedFilters.performance
        .map(p => performanceLabels[p] || p)
        .join('、')

    filters.push({
      key: 'performance',
      label: '绩效等级',
      value: performanceValues
    })
  }

  // 人才层级筛选
  if (state.advancedFilters.talentLevel) {
    const talentLevels = {
      high_potential: '高潜人才',
      key_talent: '关键人才',
      backup: '后备人才'
    }
    filters.push({
      key: 'talentLevel',
      label: '人才层级',
      value: talentLevels[state.advancedFilters.talentLevel] || state.advancedFilters.talentLevel
    })
  }

  return filters
})


const rowSelection = computed(() => ({
  selectedRowKeys: state.selectedTalents,
  onChange: (selectedRowKeys) => {
    // 限制最多选择5人
    if (selectedRowKeys.length > 5) {
      message.warning('最多只能选择5人进行对比')
      return
    }
    state.selectedTalents = selectedRowKeys
    state.indeterminate = !!selectedRowKeys.length && selectedRowKeys.length < filteredTalents.value.length
    state.selectAll = selectedRowKeys.length === filteredTalents.value.length
  }
}))

// 工具函数
const getCompanyLabel = (value) => {
  const companies = {
    yunnan_grid: '云南电网',
    kunming: '昆明供电局',
    qujing: '曲靖供电局',
    yuxi: '玉溪供电局',
    chuxiong: '楚雄供电局'
  }
  return companies[value] || value
}

const getEducationLabel = (value) => {
  const education = {
    college: '大专',
    bachelor: '本科',
    master: '硕士',
    doctor: '博士'
  }
  return education[value] || value
}

const getPerformanceValue = (performance) => {
  const values = {
    'A': 95,
    'B': 80,
    'C': 65,
    'D': 50
  }
  return values[performance] || 0
}

const getPerformancePercent = (performance) => {
  return getPerformanceValue(performance)
}

const getPerformanceColor = (performance) => {
  const colors = {
    'A': '#0066b3',
    'B': '#0088cc',
    'C': '#66a3ff',
    'D': '#99c2ff'
  }
  return colors[performance] || '#e6f0ff'
}

const getStatusColor = (status) => {
  const colors = {
    active: '#0066b3',
    probation: '#0088cc',
    leave: '#66a3ff',
    inactive: '#999'
  }
  return colors[status] || '#e6f0ff'
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

const getLevelColor = (level) => {
  const colors = {
    junior: '#66a3ff',
    intermediate: '#0088cc',
    senior: '#0066b3',
    expert: '#004d99'
  }
  return colors[level] || '#e6f0ff'
}

const getMatchScoreColor = (score) => {
  if (score >= 80) return '#0066b3'
  if (score >= 60) return '#0088cc'
  if (score >= 40) return '#66a3ff'
  return '#99c2ff'
}

const getAvatarStyle = (talent) => {
  // 根据名字生成渐变背景色
  const colors = [
    'linear-gradient(135deg, #0066b3, #0088cc)',
    'linear-gradient(135deg, #0066b3, #66a3ff)',
    'linear-gradient(135deg, #0088cc, #99c2ff)',
    'linear-gradient(135deg, #004d99, #0066b3)'
  ]

  // 根据名字的第一个字符的charCode选择颜色
  const charCode = talent.name?.charCodeAt(0) || 0
  const colorIndex = charCode % colors.length

  return {
    background: colors[colorIndex]
  }
}

const isInComparisonList = (talentId) => {
  return comparisonStore.comparisonList.some(item => item.id === talentId)
}

const getRowClassName = (record) => {
  return isInComparisonList(record.id) ? 'in-comparison-row' : ''
}

// 业务函数
const loadTalents = async () => {
  state.loading = true
  try {
    // 调用统一的API接口获取人才数据
    const data = await talentApi.getTalents()
    let talentList = []

    if (data.talents) {
      talentList = data.talents.map(talent => ({
        ...talent,
        skills: Array.isArray(talent.skills) ? talent.skills : [],
        expertise: Array.isArray(talent.expertise) ? talent.expertise : [],
        companyTenure: talent.companyTenure || calculateCompanyTenure(talent.joinDate),
        age: talent.age || calculateAge(talent.birthDate),
        performance: talent.performance || getRandomPerformance(),
        profileTags: talent.profileTags || generateProfileTags(talent),
        isHighPotential: talent.isHighPotential || Math.random() > 0.7
      }))
    }

    talents.value = talentList.sort((a, b) => b.createTime - a.createTime)
  } catch (error) {
    console.error('加载人才列表失败:', error)
    message.error('加载人才列表失败')
  } finally {
    state.loading = false
  }
}

const calculateCompanyTenure = (joinDate) => {
  if (!joinDate) return 0
  const join = dayjs(joinDate)
  const now = dayjs()
  return now.diff(join, 'year')
}

const calculateAge = (birthDate) => {
  if (!birthDate) return Math.floor(Math.random() * 25) + 25 // 随机生成25-50岁
  const birth = dayjs(birthDate)
  const now = dayjs()
  return now.diff(birth, 'year')
}

const getRandomPerformance = () => {
  const performances = ['A', 'B', 'C', 'D']
  const weights = [0.2, 0.5, 0.2, 0.1]
  const rand = Math.random()
  let cumulativeWeight = 0

  for (let i = 0; i < performances.length; i++) {
    cumulativeWeight += weights[i]
    if (rand <= cumulativeWeight) {
      return performances[i]
    }
  }
  return 'B'
}

const generateProfileTags = (talent) => {
  const tags = []

  // 基于绩效添加标签
  if (talent.performance === 'A' || talent.performance === 'B') {
    if (talent.companyTenure < 3 && talent.age < 35) {
      tags.push('高潜人才')
    } else if (talent.companyTenure >= 5) {
      tags.push('关键人才')
    }
  }

  // 基于级别添加标签
  if (talent.level === 'expert') {
    tags.push('技术专家')
  }

  // 基于技能添加标签
  if (talent.skills && talent.skills.length >= 5) {
    tags.push('多面手')
  }

  return tags
}

const handleSearch = () => {
  state.currentPage = 1
  if (state.searchMode === 'advanced') {
    applyAdvancedSearch()
  }
}

const handleSearchClear = () => {
  state.searchKeyword = ''
  state.currentPage = 1
}

// 修改applyQuickSearch函数
const applyQuickSearch = (tag) => {
  if (tag.criteria) {
    // 重置所有筛选条件
    clearAllFilters()

    // 应用快速搜索条件
    Object.keys(tag.criteria).forEach(key => {
      if (key in state.advancedFilters) {
        state.advancedFilters[key] = tag.criteria[key]
      }
    })

    // 如果包含talentLevel，需要特殊处理
    if (tag.criteria.talentLevel) {
      state.advancedFilters.talentLevel = tag.criteria.talentLevel
    }

    // 设置搜索关键词（如果有）
    if (tag.keywords) {
      state.searchKeyword = tag.keywords
    }

    // 触发搜索
    handleSearch()

    // 给用户反馈
    message.success(`已应用搜索条件: ${tag.name}`)
  }
}

const handleFilterChange = () => {
  // 可以在这里添加防抖优化
  state.currentPage = 1
}

// 新增方法：显示高级搜索模态框
const showAdvancedSearchModal = () => {
  state.showAdvancedModal = true
}

// 修改applyAdvancedSearch方法
const applyAdvancedSearch = () => {
  state.currentPage = 1
  state.showAdvancedModal = false
  message.success('应用筛选条件成功')
}


const resetAdvancedFilters = () => {
  state.advancedFilters = {
    company: null,
    department: null,
    ageMin: null,
    ageMax: null,
    education: null,
    companyTenureMin: null,
    companyTenureMax: null,
    positionType: null,
    performance: [],
    talentLevel: null
  }
}

const removeFilter = (filterKey) => {
  if (filterKey === 'searchKeyword') {
    state.searchKeyword = ''
  } else if (filterKey === 'age') {
    state.advancedFilters.ageMin = null
    state.advancedFilters.ageMax = null
  } else if (filterKey === 'companyTenure') {
    state.advancedFilters.companyTenureMin = null
    state.advancedFilters.companyTenureMax = null
  } else if (filterKey === 'performance') {
    state.advancedFilters.performance = []
  } else if (filterKey in state.advancedFilters) {
    // 重置为初始值
    if (Array.isArray(state.advancedFilters[filterKey])) {
      state.advancedFilters[filterKey] = []
    } else {
      state.advancedFilters[filterKey] = null
    }
  }
  state.currentPage = 1
  handleFilterChange()
}

const clearAllFilters = () => {
  resetAdvancedFilters()
  state.searchKeyword = ''
  state.currentPage = 1
}

const handleSelectAll = (e) => {
  if (e.target.checked) {
    // 限制最多选择5人
    const maxSelect = Math.min(5, displayedTalents.value.length)
    state.selectedTalents = displayedTalents.value.slice(0, maxSelect).map(talent => talent.id)
    state.indeterminate = false

    if (maxSelect < displayedTalents.value.length) {
      message.warning(`最多只能选择5人进行对比，已自动选择前${maxSelect}人`)
    }
  } else {
    state.selectedTalents = []
    state.indeterminate = false
  }
}

const handleSelectTalent = (talentId, checked) => {
  // 限制最多选择5人
  if (checked && state.selectedTalents.length >= 5) {
    message.warning('最多只能选择5人进行对比')
    return
  }

  const index = state.selectedTalents.indexOf(talentId)
  if (checked && index === -1) {
    state.selectedTalents.push(talentId)
  } else if (!checked && index > -1) {
    state.selectedTalents.splice(index, 1)
  }

  state.indeterminate = !!state.selectedTalents.length && state.selectedTalents.length < filteredTalents.value.length
  state.selectAll = state.selectedTalents.length === filteredTalents.value.length
}

const handleAddToCompare = () => {
  // 检查是否超过5人
  if (state.selectedTalents.length > 5) {
    message.warning('最多只能选择5人进行对比')
    return
  }

  const selectedTalents = talents.value.filter(talent =>
      state.selectedTalents.includes(talent.id)
  )

  // 检查对比列表是否已满
  const availableSlots = 5 - comparisonStore.comparisonList.length
  if (selectedTalents.length > availableSlots) {
    message.warning(`对比列表最多支持5人，当前已有${comparisonStore.comparisonList.length}人，只能再添加${availableSlots}人`)
    return
  }

  selectedTalents.forEach(talent => {
    if (!isInComparisonList(talent.id)) {
      comparisonStore.addToComparison(talent)
    }
  })

  message.success(`已添加 ${selectedTalents.length} 位人才到对比列表`)
  state.selectedTalents = []
}

const handleCompareNow = () => {
  // 检查是否超过5人
  if (state.selectedTalents.length > 5) {
    message.warning('最多只能选择5人进行对比')
    return
  }

  if (state.selectedTalents.length < 2) {
    message.warning('请至少选择2位人才进行对比')
    return
  }

  const selectedTalents = talents.value.filter(talent =>
      state.selectedTalents.includes(talent.id)
  )

  // 先清空对比列表，然后添加新选择的人才
  comparisonStore.clearComparison()
  selectedTalents.forEach(talent => {
    comparisonStore.addToComparison(talent)
  })

  gotoComparison()
}

const toggleComparison = (talent) => {
  if (isInComparisonList(talent.id)) {
    // 如果已经在对比列表中，点击跳转到对比页面
    gotoComparison()
  } else {
    // 检查对比列表是否已满
    if (comparisonStore.comparisonList.length >= 5) {
      message.warning('对比列表最多支持5位人才')
      return
    }

    comparisonStore.addToComparison(talent)

    // 询问是否立即跳转到对比页面
    Modal.confirm({
      title: '已添加到对比列表',
      content: `已将 ${talent.name} 添加到对比列表，是否立即前往对比页面？`,
      okText: '立即对比',
      cancelText: '继续浏览',
      onOk() {
        gotoComparison()
      },
      onCancel() {
        message.success('已添加到对比列表')
      }
    })
  }
}

const gotoComparison = () => {
  router.push('/search/compare')
}

const clearComparisonList = () => {
  Modal.confirm({
    title: '清空对比列表',
    content: '确定要清空对比列表吗？',
    okText: '清空',
    cancelText: '取消',
    okType: 'danger',
    async onOk() {
      comparisonStore.clearComparison()
      message.success('对比列表已清空')
    }
  })
}

const saveSearchPreset = () => {
  state.showSaveSearchModal = true
}

const saveSearchPresetConfirm = async () => {
  if (!state.newSearchPreset.name.trim()) {
    message.error('请输入方案名称')
    return
  }

  const newPreset = {
    id: `preset_${Date.now()}`,
    name: state.newSearchPreset.name,
    description: state.newSearchPreset.description,
    isDefault: state.newSearchPreset.isDefault,
    criteria: { ...state.advancedFilters },
    searchKeyword: state.searchKeyword
  }

  // 如果是默认方案，取消其他默认
  if (newPreset.isDefault) {
    searchPresets.value.forEach(preset => {
      preset.isDefault = false
    })
  }

  searchPresets.value.unshift(newPreset)

  message.success('搜索方案保存成功')
  state.showSaveSearchModal = false
  state.newSearchPreset = {
    name: '',
    description: '',
    isDefault: false
  }
}

const applySearchPreset = (preset) => {
  if (preset.criteria) {
    Object.assign(state.advancedFilters, preset.criteria)
  }
  if (preset.searchKeyword) {
    state.searchKeyword = preset.searchKeyword
  }

  state.searchMode = 'advanced'
  state.currentPage = 1
  message.success(`已应用搜索方案: ${preset.name}`)
}

const viewTalentDetails = (talent) => {
  router.push({ path: `/talent/${talent.id}` })
}

const editTalent = (talent) => {
  router.push({
    path: `/talent/${talent.id}`,
    query: { edit: 'true' }
  })
}

const addToTalentPool = (talent) => {
  message.success(`已将 ${talent.name} 添加到人才库`)
}

const resetSearch = () => {
  clearAllFilters()
  state.searchMode = 'quick'
  state.currentPage = 1
}

const handleSortChange = () => {
  state.currentPage = 1
}

const toggleSortOrder = () => {
  state.sortOrder = state.sortOrder === 'desc' ? 'asc' : 'desc'
  state.currentPage = 1
}

const handlePageChange = (page) => {
  state.currentPage = page
}

const handleSizeChange = (current, size) => {
  state.currentPage = 1
  state.pageSize = size
}

// 初始化
onMounted(() => {
  loadTalents()

  // 从URL参数初始化搜索条件
  if (route.query.search) {
    state.searchKeyword = route.query.search
  }
  if (route.query.mode === 'advanced') {
    state.searchMode = 'advanced'
  }
})
</script>

<style lang="less" scoped>
.talent-search-compare-container {
  padding: 0;
  background: var(--gray-10);
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
  width: 100%;
  position: relative;
  z-index: 1000;
}

/* 统一搜索栏样式 */
.unified-search-bar {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 12px;
  min-width: 0;
  position: relative;
  z-index: 1001;
}

/* 常用搜索标签 */
.common-search-tags {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1002;
  overflow: visible !important;

  .tags-label {
    font-size: 14px;
    color: var(--gray-600);
    margin-right: 8px;
    white-space: nowrap;
  }

  .tags-container {
    display: flex;
    gap: 6px;
    max-width: none;
    padding-bottom: 0;
    flex-wrap: wrap;
    position: relative;
    z-index: 1003;
    overflow: visible !important;

    -ms-overflow-style: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }
  }
}

/* 修复标签悬停显示问题 */
.yn-grid-tag.clickable-tag {
  position: relative;
  z-index: 1;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &::before {
    content: '';
    position: absolute;
    top: -8px;
    left: -8px;
    right: -8px;
    bottom: -8px;
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s;
  }

  &:hover {
    background: var(--main-30);
    border-color: var(--main-500);
    color: var(--main-500);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 102, 179, 0.25) !important;
    z-index: 2000 !important;

    &::before {
      opacity: 1;
    }
  }
}

/* 高级搜索按钮 */
.advanced-search-btn {
  flex-shrink: 0;
  white-space: nowrap;
  height: 36px;
  padding: 0 16px;
  border-radius: 4px;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px var(--shadow-2);
  }
}

/* 搜索框 */
.search-input-wrapper {
  flex: 1;
  min-width: 200px;
  max-width: 400px;

  :deep(.ant-input) {
    height: 36px;
    border-radius: 4px;
    border-color: var(--main-30);
    background: var(--main-0);

    &:hover, &:focus {
      border-color: var(--main-500);
      box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
    }

    &::placeholder {
      color: var(--gray-500);
    }
  }
}

/* 搜索按钮 */
.search-btn {
  flex-shrink: 0;
  height: 36px;
  padding: 0 20px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--shadow-3);
  }
}

/* 已选筛选条件栏 */
.active-filters-bar {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 20px;
  background: var(--main-0);
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: 20px;
  flex-wrap: wrap;

  .filters-label {
    display: flex;
    align-items: center;
    font-size: 14px;
    color: var(--gray-600);
    font-weight: 500;
    flex-shrink: 0;
    margin-top: 4px;
    white-space: nowrap;
  }

  .filters-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    flex: 1;

    .active-filter-tag {
      display: flex;
      align-items: center;
      height: 28px;
      margin: 2px 0;

      :deep(.ant-tag-close-icon) {
        margin-left: 4px;
        font-size: 12px;
        color: var(--main-500);

        &:hover {
          color: var(--color-error-500);
        }
      }
    }

    .clear-all-btn {
      height: 28px;
      padding: 0 8px;
      font-size: 13px;
      align-self: center;
    }
  }
}

/* 高级搜索模态框样式 */
.advanced-search-modal {
  :deep(.ant-modal-content) {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 8px 32px var(--shadow-5);
  }

  :deep(.ant-modal-header) {
    padding: 20px 24px;
    background: linear-gradient(135deg, var(--main-500), var(--main-400));
    border-bottom: none;

    .ant-modal-title {
      color: var(--main-0);
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.ant-modal-close) {
    top: 20px;
    right: 24px;

    .ant-modal-close-x {
      color: rgba(255, 255, 255, 0.85);

      &:hover {
        color: var(--main-0);
      }
    }
  }
}

.advanced-search-content {
  .search-section {
    margin-bottom: 24px;

    .section-header {
      display: flex;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--gray-200);

      .section-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--gray-900);
      }
    }

    .search-fields {
      .field-row {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }
      }

      .field-group {
        .field-label {
          display: block;
          margin-bottom: 6px;
          font-size: 14px;
          color: var(--gray-600);
          font-weight: 500;
        }

        .range-inputs {
          display: flex;
          align-items: center;
          gap: 8px;

          :deep(.ant-input-number) {
            flex: 1;
            min-width: 0;
          }

          .range-separator {
            color: var(--gray-500);
            font-size: 14px;
            flex-shrink: 0;
          }
        }
      }
    }
  }

  .modal-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 20px;
    border-top: 1px solid var(--gray-200);
    margin-top: 8px;

    :deep(.ant-btn) {
      height: 40px;
      padding: 0 24px;
      font-size: 14px;
      border-radius: 4px;
    }
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .common-search-tags {
    .tags-container {
      max-width: 300px;
      flex-wrap: nowrap;
      overflow-x: auto !important;
      overflow-y: hidden;

      &::-webkit-scrollbar {
        height: 4px;
        display: block;
      }

      &::-webkit-scrollbar-track {
        background: var(--gray-100);
        border-radius: 2px;
      }

      &::-webkit-scrollbar-thumb {
        background: var(--gray-400);
        border-radius: 2px;
      }
    }
  }
}

@media (max-width: 992px) {
  .header-tools {
    flex-wrap: wrap;
  }

  .unified-search-bar {
    order: 1;
    width: 100%;
    margin-bottom: 12px;

    .search-input-wrapper {
      max-width: none;
    }
  }
}

@media (max-width: 768px) {
  .unified-search-bar {
    flex-wrap: wrap;

    .common-search-tags {
      width: 100%;
      margin-bottom: 12px;

      .tags-container {
        max-width: none;
        flex-wrap: nowrap;
        overflow-x: auto !important;
        padding-right: 20px;
      }
    }

    .search-input-wrapper {
      flex: 1;
      min-width: 150px;
    }
  }

  .advanced-search-content {
    .search-fields {
      .field-row {
        grid-template-columns: 1fr;
        gap: 16px;
      }
    }
  }

  .modal-actions {
    flex-direction: column;
    gap: 12px;

    :deep(.ant-btn) {
      width: 100%;
    }

    .ant-space {
      width: 100%;
      justify-content: space-between;
    }
  }
}

/* 云南电网主题样式 */
.yn-grid-mode-switch {
  .mode-btn {
    border-color: var(--main-30);
    color: var(--gray-600);

    &:hover {
      color: var(--main-500);
      border-color: var(--main-200);
    }

    &.ant-radio-button-wrapper-checked {
      background: var(--main-500);
      color: var(--main-0);
      border-color: var(--main-500);

      &:hover {
        background: var(--main-400);
        border-color: var(--main-400);
      }
    }
  }
}

.yn-grid-search-input {
  :deep(.ant-input) {
    border-color: var(--main-30);
    border-radius: 4px;

    &:hover, &:focus {
      border-color: var(--main-500);
      box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
    }
  }
}

.yn-grid-btn-primary {
  background: var(--main-500);
  border-color: var(--main-500);
  color: var(--main-0);

  &:hover, &:focus {
    background: var(--main-400);
    border-color: var(--main-400);
    color: var(--main-0);
  }

  &:disabled {
    background: var(--main-100);
    border-color: var(--main-100);
    color: var(--main-0);
  }
}

.yn-grid-btn-secondary {
  background: var(--main-0);
  border-color: var(--main-30);
  color: var(--main-500);

  &:hover, &:focus {
    background: var(--main-30);
    border-color: var(--main-200);
    color: var(--main-500);
  }
}

.yn-grid-tag {
  border-radius: 4px;
  border-color: var(--main-30);
  background: var(--gray-10);
  color: var(--gray-600);

  &.active-filter-tag {
    background: var(--main-30);
    color: var(--main-500);
    border-color: var(--main-200);
  }
}

.yn-grid-dropdown-panel {
  background: var(--main-0);
  border-radius: 8px;
  box-shadow: 0 6px 16px var(--shadow-3);
  border: 1px solid var(--main-30);

  .search-section {
    .section-title {
      font-weight: 500;
      color: var(--main-500);
      margin-bottom: 8px;
      font-size: 14px;
      display: flex;
      align-items: center;
    }

    .search-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .search-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }
}

.yn-grid-select {
  :deep(.ant-select-selector) {
    border-color: var(--main-30) !important;
    border-radius: 4px !important;

    &:hover {
      border-color: var(--main-500) !important;
    }
  }

  :deep(.ant-select-selection-item) {
    color: var(--gray-900);
  }
}

.yn-grid-input {
  :deep(.ant-input-number) {
    border-color: var(--main-30);
    border-radius: 4px;

    &:hover, &:focus {
      border-color: var(--main-500);
      box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
    }
  }
}

.yn-grid-dropdown-menu {
  border-radius: 8px;
  box-shadow: 0 6px 16px var(--shadow-3);
  border: 1px solid var(--main-30);

  .menu-item {
    &:hover {
      background: var(--main-30);
    }
  }

  .menu-group {
    :deep(.ant-menu-item-group-title) {
      color: var(--main-500);
      font-weight: 500;
    }
  }
}

.clear-all-btn {
  color: var(--main-500);

  &:hover {
    color: var(--main-400);
  }
}

.compare-now-btn {
  background: linear-gradient(135deg, var(--main-500), var(--main-400));
  border: none;

  &:hover {
    background: linear-gradient(135deg, var(--main-400), var(--main-300));
  }
}

.yn-grid-badge {
  :deep(.ant-badge-count) {
    background: var(--color-error-500);
    box-shadow: 0 0 0 1px var(--main-0);
  }
}

.comparison-manage-btn {
  background: linear-gradient(135deg, var(--main-500), var(--main-400));
  border: none;

  &:hover {
    background: linear-gradient(135deg, var(--main-400), var(--main-300));
  }
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  padding: 20px;
  background: var(--main-0);

  .stat-card {
    border-radius: 8px;
    border: 1px solid var(--main-30);
    box-shadow: 0 2px 8px var(--shadow-1);
    transition: all 0.3s;

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
        background: linear-gradient(135deg, var(--main-30), var(--main-20));
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          line-height: 1.2;
          color: var(--main-500);
        }

        .stat-label {
          font-size: 14px;
          color: var(--gray-600);
          margin-top: 4px;
        }
      }
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px var(--shadow-3);
      border-color: var(--main-200);
    }
  }
}

.search-results {
  padding: 20px;
}

/* 结果头部样式 */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--main-0);
  border-radius: 8px;
  border: 1px solid var(--main-30);
  box-shadow: 0 2px 8px var(--shadow-1);

  .results-info {
    .total-count {
      font-size: 16px;
      font-weight: 600;
      color: var(--main-500);
    }

    .match-info {
      margin-left: 12px;
      font-size: 14px;
      color: var(--gray-600);

      span {
        color: var(--main-500);
        font-weight: 500;
      }
    }
  }

  .results-actions {
    .action-group {
      display: flex;
      align-items: center;
      gap: 16px;

      .selected-info {
        .selected-count {
          font-size: 13px;
          color: var(--gray-600);
          background: var(--main-20);
          padding: 4px 10px;
          border-radius: 4px;
          border: 1px solid var(--main-30);

          &.exceed-limit {
            color: var(--color-error-500);
            background: var(--color-error-50);
            border-color: var(--color-error-100);

            .limit-warning {
              color: var(--color-error-500);
              font-size: 12px;
            }
          }
        }
      }

      .select-all-wrapper {
        .yn-grid-checkbox {
          :deep(.ant-checkbox-inner) {
            border-color: var(--main-30);
            border-radius: 4px;
          }

          :deep(.ant-checkbox-checked .ant-checkbox-inner) {
            background: var(--main-500);
            border-color: var(--main-500);
          }
        }
      }

      .action-button-wrapper {
        .ant-btn {
          height: 32px;
          padding: 0 16px;
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          border-radius: 4px;
          transition: all 0.3s;

          &:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px var(--shadow-3);
          }
        }

        .yn-grid-btn-primary {
          background: linear-gradient(135deg, var(--main-500), var(--main-400));
          border: none;

          &:hover:not(:disabled) {
            background: linear-gradient(135deg, var(--main-400), var(--main-300));
          }
        }

        .disabled-btn {
          opacity: 0.5;
          cursor: not-allowed;

          &:hover {
            transform: none !important;
            box-shadow: none !important;
          }
        }
      }
    }
  }
}

.yn-grid-checkbox {
  :deep(.ant-checkbox-inner) {
    border-color: var(--main-30);
    border-radius: 4px;
  }

  :deep(.ant-checkbox-checked .ant-checkbox-inner) {
    background: var(--main-500);
    border-color: var(--main-500);
  }
}

.view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--main-0);
  border-radius: 8px;
  border: 1px solid var(--main-30);
  box-shadow: 0 2px 8px var(--shadow-1);

  .sort-controls {
    display: flex;
    align-items: center;
  }
}

.yn-grid-view-switch {
  .view-btn {
    border-color: var(--main-30);
    color: var(--gray-600);

    &:hover {
      color: var(--main-500);
      border-color: var(--main-200);
    }

    &.ant-radio-button-wrapper-checked {
      background: var(--main-500);
      color: var(--main-0);
      border-color: var(--main-500);

      &:hover {
        background: var(--main-400);
        border-color: var(--main-400);
      }
    }
  }
}

.sort-order-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--main-0);
  border-color: var(--main-30);
  color: var(--gray-600);

  &:hover {
    border-color: var(--main-500);
    color: var(--main-500);
  }
}

/* 卡片视图样式 */
.talent-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.talent-search-card {
  background: var(--main-0);
  border-radius: 12px;
  border: 2px solid var(--main-30);
  box-shadow: 0 2px 12px var(--shadow-2);
  transition: all 0.3s;
  overflow: hidden;

  &.selected {
    border-color: var(--main-500);
    box-shadow: 0 4px 16px var(--shadow-4);
  }

  &.in-comparison {
    border-color: var(--main-500);
    box-shadow: 0 4px 16px var(--shadow-4);
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px var(--shadow-3);
    border-color: var(--main-200);
  }

  .card-header {
    display: flex;
    align-items: center;
    padding: 16px 16px 0;
    gap: 12px;

    .selection-control {
      flex-shrink: 0;
    }

    .talent-basic-info {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;

      .talent-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--main-0);
        font-size: 18px;
        font-weight: 600;
        flex-shrink: 0;
        background: linear-gradient(135deg, var(--main-500), var(--main-400));
      }

      .talent-meta {
        .talent-name {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          line-height: 1.2;
          color: var(--main-500);
        }

        .talent-tags {
          display: flex;
          gap: 4px;
          flex-wrap: wrap;
        }
      }
    }

    .card-actions {
      .compare-btn {
        color: var(--gray-600);

        &:hover {
          color: var(--main-500);
        }

        &.in-comparison {
          color: var(--main-500);
          font-weight: 500;
        }
      }
    }
  }

  .card-body {
    padding: 16px;
    cursor: pointer;

    .match-score {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 16px;

      .match-info {
        .match-value {
          font-size: 20px;
          font-weight: 600;
          color: var(--main-500);
        }

        .match-label {
          font-size: 12px;
          color: var(--gray-500);
          margin-top: 2px;
        }
      }
    }

    .key-info {
      margin-bottom: 16px;

      .info-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-size: 14px;

        &:last-child {
          margin-bottom: 0;
        }

        .info-label {
          color: var(--gray-600);
          min-width: 50px;
        }

        .info-value {
          margin-left: 8px;
          flex: 1;

          &.highlight {
            color: var(--main-500);
            font-weight: 500;
          }

          &:not(.highlight) {
            color: var(--gray-900);
          }
        }
      }
    }

    .skills-section {
      margin-bottom: 16px;

      .skills-label {
        font-size: 12px;
        color: var(--gray-500);
        margin-bottom: 6px;
      }

      .skills-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;

        .skill-tag {
          background: var(--main-30);
          color: var(--main-500);
          border-color: var(--main-200);
        }

        .more-skills {
          font-size: 12px;
          color: var(--gray-500);
          align-self: center;
        }
      }
    }

    .profile-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;

      .profile-tag {
        background: var(--main-500);
        color: var(--main-0);
        border-color: var(--main-500);
      }
    }
  }

  .card-footer {
    padding: 12px 16px;
    background: var(--gray-10);
    border-top: 1px solid var(--gray-200);

    .action-buttons {
      display: flex;
      justify-content: flex-end;
      gap: 12px;

      .yn-grid-link-btn {
        color: var(--main-500);

        &:hover {
          color: var(--main-400);
        }
      }
    }
  }
}

/* 高潜人才标签 */
.high-potential-tag {
  background: var(--main-500);
  color: var(--main-0) !important;
  border-color: var(--main-500);
}

/* 列表视图样式 */
.talent-list-table {
  margin-bottom: 20px;
  background: var(--main-0);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--main-30);
  box-shadow: 0 2px 8px var(--shadow-1);

  :deep(.ant-table) {
    background: transparent;

    .ant-table-thead > tr > th {
      background: var(--main-5);
      color: var(--gray-600);
      font-weight: 600;
      border-bottom: 1px solid var(--main-30);
    }

    .ant-table-tbody > tr > td {
      border-bottom: 1px solid var(--main-30);
    }

    .ant-table-tbody > tr:hover > td {
      background: var(--main-10);
    }
  }

  :deep(.in-comparison-row) {
    background-color: var(--main-30) !important;

    &:hover > td {
      background-color: var(--main-40) !important;
    }
  }

  .table-selection {
    display: flex;
    align-items: center;
    gap: 8px;

    .in-comparison {
      color: var(--main-500);
    }
  }

  .table-cell-name {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;

    .avatar-small {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--main-0);
      font-size: 14px;
      font-weight: 600;
      flex-shrink: 0;
      background: linear-gradient(135deg, var(--main-500), var(--main-400));
    }

    .name-info {
      .name {
        font-weight: 500;
        line-height: 1.2;
        color: var(--main-500);
      }

      .employee-id {
        font-size: 12px;
        color: var(--gray-500);
        margin-top: 2px;
      }
    }
  }

  .match-score-cell {
    display: flex;
    justify-content: center;
  }

  .status-cell {
    .ant-tag {
      margin-bottom: 4px;
    }
  }

  .performance-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .performance-value {
      font-size: 14px;
      font-weight: 500;
      min-width: 30px;
      color: var(--gray-900);
    }
  }

  .skills-cell {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-wrap: wrap;

    .skill-tag {
      background: var(--main-30);
      color: var(--main-500);
      border-color: var(--main-200);
    }

    .more-skills {
      font-size: 12px;
      color: var(--gray-500);
    }
  }

  .table-actions {
    display: flex;
    gap: 4px;

    .ant-btn {
      padding: 4px;
      width: 28px;
      height: 28px;
      color: var(--gray-600);

      &:hover {
        color: var(--main-500);
      }

      &.in-comparison {
        color: var(--main-500);
      }
    }
  }
}

/* 匹配度进度条颜色函数 */
.getMatchScoreColor(@score) {
  & when (@score >= 80) { stroke: var(--main-500); }
  & when (@score >= 60) and (@score < 80) { stroke: var(--main-400); }
  & when (@score >= 40) and (@score < 60) { stroke: var(--main-300); }
  & when (@score < 40) { stroke: var(--main-200); }
}

/* 绩效颜色函数 */
.getPerformanceColor(@performance) {
  & when (@performance = 'A') { color: var(--main-500); background: var(--main-30); border-color: var(--main-200); }
  & when (@performance = 'B') { color: var(--main-400); background: var(--main-20); border-color: var(--main-100); }
  & when (@performance = 'C') { color: var(--gray-600); background: var(--gray-100); border-color: var(--gray-300); }
  & when (@performance = 'D') { color: var(--gray-500); background: var(--gray-50); border-color: var(--gray-200); }
}

/* 状态颜色函数 */
.getStatusColor(@status) {
  & when (@status = 'active') { color: var(--main-500); background: var(--main-30); border-color: var(--main-200); }
  & when (@status = 'probation') { color: var(--main-400); background: var(--main-20); border-color: var(--main-100); }
  & when (@status = 'leave') { color: var(--color-info-500); background: var(--color-info-50); border-color: var(--color-info-100); }
  & when (@status = 'inactive') { color: var(--gray-500); background: var(--gray-50); border-color: var(--gray-200); }
}

/* 级别颜色函数 */
.getLevelColor(@level) {
  & when (@level = 'junior') { color: var(--main-300); background: var(--main-30); border-color: var(--main-100); }
  & when (@level = 'intermediate') { color: var(--main-400); background: var(--main-20); border-color: var(--main-200); }
  & when (@level = 'senior') { color: var(--main-500); background: var(--main-10); border-color: var(--main-300); }
  & when (@level = 'expert') { color: var(--main-700); background: var(--main-5); border-color: var(--main-400); }
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  background: var(--main-0);
  border-radius: 8px;
  border: 1px solid var(--main-30);
  box-shadow: 0 2px 8px var(--shadow-1);
}

.yn-grid-pagination {
  :deep(.ant-pagination-item) {
    border-color: var(--main-30);

    &:hover {
      border-color: var(--main-500);

      a {
        color: var(--main-500);
      }
    }

    &.ant-pagination-item-active {
      background: var(--main-500);
      border-color: var(--main-500);

      a {
        color: var(--main-0);
      }
    }
  }

  :deep(.ant-pagination-prev, .ant-pagination-next) {
    .ant-pagination-item-link {
      border-color: var(--main-30);
      color: var(--gray-600);

      &:hover {
        border-color: var(--main-500);
        color: var(--main-500);
      }
    }
  }

  :deep(.ant-pagination-jump-prev, .ant-pagination-jump-next) {
    .ant-pagination-item-link {
      color: var(--gray-600);

      &:hover {
        color: var(--main-500);
      }
    }
  }
}

.yn-grid-progress {
  :deep(.ant-progress-inner) {
    background-color: var(--main-30);
  }

  :deep(.ant-progress-circle-path) {
    stroke-linecap: round;
  }

  :deep(.ant-progress-bg) {
    background: var(--main-500);
  }
}

.search-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: var(--main-0);
  border-radius: 12px;
  border: 1px solid var(--main-30);
  box-shadow: 0 2px 8px var(--shadow-1);

  .empty-illustration {
    margin-bottom: 24px;

    :deep(svg) {
      color: var(--main-500);
      opacity: 0.3;
    }
  }

  .empty-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 12px 0;
    letter-spacing: -0.02em;
    color: var(--gray-900);
  }

  .empty-description {
    font-size: 14px;
    margin: 0 0 32px 0;
    line-height: 1.5;
    max-width: 320px;
    color: var(--gray-600);
  }

  .empty-actions {
    display: flex;
    gap: 12px;
  }
}

.yn-grid-modal {
  :deep(.ant-modal-content) {
    border-radius: 8px;
    overflow: hidden;
  }

  :deep(.ant-modal-header) {
    background: var(--gray-10);
    border-bottom: 1px solid var(--main-30);

    .ant-modal-title {
      color: var(--main-500);
      font-weight: 600;
    }
  }

  :deep(.ant-modal-footer) {
    border-top: 1px solid var(--main-30);
    padding: 16px 24px;
  }
}

.yn-grid-form {
  :deep(.ant-form-item-label) {
    label {
      color: var(--gray-900);
      font-weight: 500;
    }
  }
}

.yn-grid-textarea {
  border-color: var(--main-30);
  border-radius: 4px;

  &:hover, &:focus {
    border-color: var(--main-500);
    box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
  }
}

.floating-comparison-button {
  position: fixed;
  right: 32px;
  bottom: 32px;
  z-index: 999;

  .floating-button {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, var(--main-500), var(--main-400));
    border: none;
    box-shadow: 0 6px 16px var(--shadow-4);
    color: var(--main-0);

    &:hover {
      transform: scale(1.1);
      transition: transform 0.3s;
      background: linear-gradient(135deg, var(--main-400), var(--main-300));
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .header-tools {
    flex-direction: column;
    align-items: stretch;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .talent-cards-grid {
    grid-template-columns: 1fr;
  }

  .results-header {
    flex-direction: column;
    gap: 12px;

    .results-actions {
      width: 100%;
      justify-content: center;
    }
  }

  .view-controls {
    flex-direction: column;
    gap: 12px;
  }

  .floating-comparison-button {
    right: 16px;
    bottom: 16px;

    .floating-button {
      width: 48px;
      height: 48px;
    }
  }
}
</style>