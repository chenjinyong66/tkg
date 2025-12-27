<template>
  <div class="talent-search-compare-container layout-container">
    <!-- 顶部导航和搜索区域 -->
    <HeaderComponent title="人才搜索与对比" :loading="state.loading">
      <template #actions>
        <div class="header-tools">
          <!-- 搜索模式切换 -->
          <a-radio-group v-model:value="state.searchMode" button-style="solid" size="small" class="yn-grid-mode-switch">
            <a-radio-button value="quick" class="mode-btn">
              <template #icon><SearchOutlined /></template>
              快速搜索
            </a-radio-button>
            <a-radio-button value="advanced" class="mode-btn">
              <template #icon><FilterOutlined /></template>
              高级搜索
            </a-radio-button>
          </a-radio-group>

          <!-- 快速搜索 -->
          <div v-if="state.searchMode === 'quick'" class="quick-search-container">
            <a-input-search
                v-model:value="state.searchKeyword"
                placeholder="搜索人才姓名、职位、技能..."
                style="width: 300px"
                @search="handleSearch"
                allow-clear
                @clear="handleSearchClear"
                class="yn-grid-search-input"
            >
              <template #enterButton>
                <a-button type="primary" class="yn-grid-btn-primary">
                  <SearchOutlined />
                </a-button>
              </template>
            </a-input-search>

            <!-- 常用搜索标签 -->
            <div class="quick-search-tags">
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

          <!-- 高级搜索 -->
          <div v-else class="advanced-search-container">
            <a-dropdown trigger="click" placement="bottomLeft">
              <template #overlay>
                <div class="advanced-search-panel yn-grid-dropdown-panel">
                  <div class="search-section">
                    <div class="section-title">
                      <TeamOutlined style="color: #0066b3; margin-right: 6px;" />
                      基础信息
                    </div>
                    <div class="search-row">
                      <a-select
                          v-model:value="state.advancedFilters.company"
                          placeholder="公司"
                          style="width: 180px"
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

                      <a-select
                          v-model:value="state.advancedFilters.department"
                          placeholder="部门"
                          style="width: 180px; margin-left: 10px"
                          allow-clear
                          @change="handleFilterChange"
                          class="yn-grid-select"
                      >
                        <a-select-option v-for="dept in departmentOptions" :key="dept.value" :value="dept.value">
                          {{ dept.label }}
                        </a-select-option>
                      </a-select>
                    </div>

                    <div class="search-row" style="margin-top: 10px">
                      <a-input-number
                          v-model:value="state.advancedFilters.ageMin"
                          placeholder="最小年龄"
                          :min="18"
                          :max="60"
                          style="width: 85px"
                          @change="handleFilterChange"
                          class="yn-grid-input"
                      />
                      <span style="margin: 0 5px; color: #0066b3">-</span>
                      <a-input-number
                          v-model:value="state.advancedFilters.ageMax"
                          placeholder="最大年龄"
                          :min="18"
                          :max="60"
                          style="width: 85px"
                          @change="handleFilterChange"
                          class="yn-grid-input"
                      />

                      <a-select
                          v-model:value="state.advancedFilters.education"
                          placeholder="最高学历"
                          style="width: 120px; margin-left: 10px"
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

                  <div class="search-section" style="margin-top: 15px">
                    <div class="section-title">
                      <ScheduleOutlined style="color: #0066b3; margin-right: 6px;" />
                      工作经历
                    </div>
                    <div class="search-row">
                      <a-input-number
                          v-model:value="state.advancedFilters.companyTenureMin"
                          placeholder="最小司龄"
                          :min="0"
                          :max="40"
                          style="width: 100px"
                          @change="handleFilterChange"
                          class="yn-grid-input"
                      />
                      <span style="margin: 0 5px; color: #0066b3">-</span>
                      <a-input-number
                          v-model:value="state.advancedFilters.companyTenureMax"
                          placeholder="最大司龄"
                          :min="0"
                          :max="40"
                          style="width: 100px"
                          @change="handleFilterChange"
                          class="yn-grid-input"
                      />

                      <a-select
                          v-model:value="state.advancedFilters.positionType"
                          placeholder="职务类型"
                          style="width: 120px; margin-left: 10px"
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

                  <div class="search-section" style="margin-top: 15px">
                    <div class="section-title">
                      <RiseOutlined style="color: #0066b3; margin-right: 6px;" />
                      绩效标签
                    </div>
                    <div class="search-row">
                      <a-select
                          v-model:value="state.advancedFilters.performance"
                          placeholder="绩效等级"
                          mode="multiple"
                          style="width: 200px"
                          allow-clear
                          @change="handleFilterChange"
                          class="yn-grid-select"
                      >
                        <a-select-option value="A" style="color: #0066b3">A（优秀）</a-select-option>
                        <a-select-option value="B" style="color: #0066b3">B（良好）</a-select-option>
                        <a-select-option value="C" style="color: #666">C（合格）</a-select-option>
                        <a-select-option value="D" style="color: #999">D（待改进）</a-select-option>
                      </a-select>

                      <a-select
                          v-model:value="state.advancedFilters.talentLevel"
                          placeholder="人才层级"
                          style="width: 120px; margin-left: 10px"
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

                  <a-divider style="margin: 15px 0; border-color: #e6f0ff" />

                  <div class="search-actions">
                    <a-button @click="resetAdvancedFilters" size="small" class="yn-grid-btn-secondary">
                      <RedoOutlined />
                      重置条件
                    </a-button>
                    <a-button type="primary" @click="applyAdvancedSearch" size="small" style="margin-left: 10px" class="yn-grid-btn-primary">
                      <CheckOutlined />
                      应用筛选
                    </a-button>
                  </div>
                </div>
              </template>
              <a-button class="yn-grid-btn-primary">
                <FilterOutlined />
                高级筛选
                <DownOutlined />
              </a-button>
            </a-dropdown>

            <!-- 已选筛选条件 -->
            <div class="selected-filters" v-if="hasActiveFilters">
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

          <!-- 搜索方案管理 -->
          <a-dropdown v-if="state.searchMode === 'advanced'">
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

          <!-- 批量操作按钮 -->
          <div class="batch-actions" v-if="state.selectedTalents.length > 0">
            <a-button @click="handleAddToCompare" class="yn-grid-btn-secondary">
              <BarChartOutlined />
              添加到对比 ({{ state.selectedTalents.length }})
            </a-button>
            <a-button type="primary" @click="handleCompareNow" class="yn-grid-btn-primary compare-now-btn">
              <SwapOutlined />
              立即对比
            </a-button>
          </div>

          <!-- 对比管理 -->
          <a-dropdown v-if="comparisonStore.comparisonList.length > 0">
            <template #overlay>
              <a-menu class="yn-grid-dropdown-menu">
                <a-menu-item key="go_compare" @click="gotoComparison" class="menu-item">
                  <BarChartOutlined style="color: #0066b3;" />
                  <span style="color: #333;">查看对比列表 ({{ comparisonStore.comparisonList.length }}人)</span>
                </a-menu-item>
                <a-menu-divider style="border-color: #e6f0ff" />
                <a-menu-item key="clear_all" @click="clearComparisonList" class="menu-item" style="color: #ff4d4f;">
                  <DeleteOutlined />
                  清空对比列表
                </a-menu-item>
              </a-menu>
            </template>
            <a-badge :count="comparisonStore.comparisonList.length" :offset="[-5, 5]" class="yn-grid-badge">
              <a-button type="primary" class="yn-grid-btn-primary comparison-manage-btn">
                <BarChartOutlined />
                对比管理
              </a-button>
            </a-badge>
          </a-dropdown>
        </div>
      </template>
    </HeaderComponent>

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
      <div class="results-header yn-grid-card">
        <div class="results-info">
          <span class="total-count" style="color: #0066b3;">找到 {{ totalTalents }} 位匹配人才</span>
          <span class="match-info" v-if="state.searchKeyword" style="color: #666;">
            匹配关键词："<span style="color: #0066b3; font-weight: 500;">{{ state.searchKeyword }}</span>"
          </span>
        </div>
        <div class="results-actions">
          <a-checkbox
              v-model:checked="state.selectAll"
              @change="handleSelectAll"
              :indeterminate="state.indeterminate"
              class="yn-grid-checkbox"
          >
            全选
          </a-checkbox>
          <a-button
              size="small"
              @click="handleAddToCompare"
              :disabled="state.selectedTalents.length === 0"
              class="yn-grid-btn-secondary"
          >
            <BarChartOutlined />
            添加到对比 ({{ state.selectedTalents.length }})
          </a-button>
          <a-button
              type="primary"
              size="small"
              @click="handleCompareNow"
              :disabled="state.selectedTalents.length < 2"
              class="yn-grid-btn-primary"
          >
            <SwapOutlined />
            对比选中的 ({{ state.selectedTalents.length }})
          </a-button>
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
              <a-checkbox
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
                <a-checkbox
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
  searchMode: 'quick', // 'quick' or 'advanced'
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

const hasActiveFilters = computed(() => {
  return Object.values(state.advancedFilters).some(value =>
      (Array.isArray(value) && value.length > 0) ||
      (!Array.isArray(value) && value !== null && value !== '')
  )
})

const activeFilters = computed(() => {
  const filters = []

  if (state.advancedFilters.company) {
    filters.push({
      key: 'company',
      label: '公司',
      value: getCompanyLabel(state.advancedFilters.company)
    })
  }

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

  if (state.advancedFilters.ageMin !== null || state.advancedFilters.ageMax !== null) {
    const ageStr = `${state.advancedFilters.ageMin || ''}-${state.advancedFilters.ageMax || ''}岁`
    filters.push({
      key: 'age',
      label: '年龄',
      value: ageStr
    })
  }

  if (state.advancedFilters.education) {
    filters.push({
      key: 'education',
      label: '学历',
      value: getEducationLabel(state.advancedFilters.education)
    })
  }

  return filters
})

const rowSelection = computed(() => ({
  selectedRowKeys: state.selectedTalents,
  onChange: (selectedRowKeys) => {
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

const applyQuickSearch = (tag) => {
  if (tag.criteria) {
    // 应用快速搜索条件
    Object.assign(state.advancedFilters, tag.criteria)
    state.searchMode = 'advanced'
    applyAdvancedSearch()
  }
}

const handleFilterChange = () => {
  // 可以在这里添加防抖优化
  state.currentPage = 1
}

const applyAdvancedSearch = () => {
  state.currentPage = 1
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
  state.advancedFilters[filterKey] = Array.isArray(state.advancedFilters[filterKey])
      ? []
      : null
  state.currentPage = 1
}

const clearAllFilters = () => {
  resetAdvancedFilters()
  state.searchKeyword = ''
  state.currentPage = 1
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

  state.indeterminate = !!state.selectedTalents.length && state.selectedTalents.length < filteredTalents.value.length
  state.selectAll = state.selectedTalents.length === filteredTalents.value.length
}

const handleAddToCompare = () => {
  const selectedTalents = talents.value.filter(talent =>
      state.selectedTalents.includes(talent.id)
  )

  selectedTalents.forEach(talent => {
    if (!isInComparisonList(talent.id)) {
      comparisonStore.addToComparison(talent)
    }
  })

  message.success(`已添加 ${selectedTalents.length} 位人才到对比列表`)
  state.selectedTalents = []
}

const handleCompareNow = () => {
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
    comparisonStore.removeFromComparison(talent.id)
    message.success('已从对比列表中移除')
  } else {
    if (comparisonStore.comparisonList.length >= 5) {
      message.warning('对比列表最多支持5位人才')
      return
    }
    comparisonStore.addToComparison(talent)
    message.success('已添加到对比列表')
  }
}

const gotoComparison = () => {
  router.push('/talent/compare')
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
  background: #f8fafc;
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* 云南电网主题样式 */
.yn-grid-mode-switch {
  .mode-btn {
    border-color: #e6f0ff;
    color: #666;

    &:hover {
      color: #0066b3;
      border-color: #b3d1ff;
    }

    &.ant-radio-button-wrapper-checked {
      background: #0066b3;
      color: white;
      border-color: #0066b3;

      &:hover {
        background: #0088cc;
        border-color: #0088cc;
      }
    }
  }
}

.yn-grid-search-input {
  :deep(.ant-input) {
    border-color: #e6f0ff;
    border-radius: 4px;

    &:hover, &:focus {
      border-color: #0066b3;
      box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
    }
  }
}

.yn-grid-btn-primary {
  background: #0066b3;
  border-color: #0066b3;
  color: white;

  &:hover, &:focus {
    background: #0088cc;
    border-color: #0088cc;
    color: white;
  }

  &:disabled {
    background: #99c2ff;
    border-color: #99c2ff;
    color: white;
  }
}

.yn-grid-btn-secondary {
  background: white;
  border-color: #e6f0ff;
  color: #0066b3;

  &:hover, &:focus {
    background: #e6f0ff;
    border-color: #b3d1ff;
    color: #0066b3;
  }
}

.yn-grid-tag {
  border-radius: 4px;
  border-color: #e6f0ff;
  background: #f8fafc;
  color: #666;

  &.clickable-tag {
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: #e6f0ff;
      border-color: #0066b3;
      color: #0066b3;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 102, 179, 0.15);
    }
  }

  &.active-filter-tag {
    background: #e6f0ff;
    color: #0066b3;
    border-color: #b3d1ff;
  }
}

.yn-grid-dropdown-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 6px 16px rgba(0, 102, 179, 0.15);
  border: 1px solid #e6f0ff;

  .search-section {
    .section-title {
      font-weight: 500;
      color: #0066b3;
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
    border-color: #e6f0ff !important;
    border-radius: 4px !important;

    &:hover {
      border-color: #0066b3 !important;
    }
  }

  :deep(.ant-select-selection-item) {
    color: #333;
  }
}

.yn-grid-input {
  :deep(.ant-input-number) {
    border-color: #e6f0ff;
    border-radius: 4px;

    &:hover, &:focus {
      border-color: #0066b3;
      box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
    }
  }
}

.yn-grid-dropdown-menu {
  border-radius: 8px;
  box-shadow: 0 6px 16px rgba(0, 102, 179, 0.15);
  border: 1px solid #e6f0ff;

  .menu-item {
    &:hover {
      background: #e6f0ff;
    }
  }

  .menu-group {
    :deep(.ant-menu-item-group-title) {
      color: #0066b3;
      font-weight: 500;
    }
  }
}

.clear-all-btn {
  color: #0066b3;

  &:hover {
    color: #0088cc;
  }
}

.compare-now-btn {
  background: linear-gradient(135deg, #0066b3, #0088cc);
  border: none;

  &:hover {
    background: linear-gradient(135deg, #0088cc, #0099e6);
  }
}

.yn-grid-badge {
  :deep(.ant-badge-count) {
    background: #ff4d4f;
    box-shadow: 0 0 0 1px white;
  }
}

.comparison-manage-btn {
  background: linear-gradient(135deg, #0066b3, #0088cc);
  border: none;

  &:hover {
    background: linear-gradient(135deg, #0088cc, #0099e6);
  }
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  padding: 20px;
  background: white;

  .stat-card {
    border-radius: 8px;
    border: 1px solid #e6f0ff;
    box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);
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
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 24px;
          font-weight: 600;
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
      box-shadow: 0 8px 24px rgba(0, 102, 179, 0.1);
      border-color: #b3d1ff;
    }
  }
}

.search-results {
  padding: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e6f0ff;
  box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);

  .results-info {
    .total-count {
      font-size: 16px;
      font-weight: 600;
    }

    .match-info {
      margin-left: 12px;
      font-size: 14px;
    }
  }

  .results-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.yn-grid-checkbox {
  :deep(.ant-checkbox-inner) {
    border-color: #e6f0ff;
    border-radius: 4px;
  }

  :deep(.ant-checkbox-checked .ant-checkbox-inner) {
    background: #0066b3;
    border-color: #0066b3;
  }
}

.view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e6f0ff;
  box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);

  .sort-controls {
    display: flex;
    align-items: center;
  }
}

.yn-grid-view-switch {
  .view-btn {
    border-color: #e6f0ff;
    color: #666;

    &:hover {
      color: #0066b3;
      border-color: #b3d1ff;
    }

    &.ant-radio-button-wrapper-checked {
      background: #0066b3;
      color: white;
      border-color: #0066b3;

      &:hover {
        background: #0088cc;
        border-color: #0088cc;
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
}

.talent-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.talent-search-card {
  background: white;
  border-radius: 12px;
  border: 2px solid #e6f0ff;
  box-shadow: 0 2px 12px rgba(0, 102, 179, 0.08);
  transition: all 0.3s;
  overflow: hidden;

  &.selected {
    border-color: #0066b3;
    box-shadow: 0 4px 16px rgba(0, 102, 179, 0.2);
  }

  &.in-comparison {
    border-color: #0066b3;
    box-shadow: 0 4px 16px rgba(0, 102, 179, 0.2);
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 102, 179, 0.15);
    border-color: #b3d1ff;
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
        color: white;
        font-size: 18px;
        font-weight: 600;
        flex-shrink: 0;
      }

      .talent-meta {
        .talent-name {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          line-height: 1.2;
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
        color: #666;

        &:hover {
          color: #0066b3;
        }

        &.in-comparison {
          color: #0066b3;
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
        }

        .match-label {
          font-size: 12px;
          color: #999;
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
          color: #666;
          min-width: 50px;
        }

        .info-value {
          margin-left: 8px;
          flex: 1;
        }
      }
    }

    .skills-section {
      margin-bottom: 16px;

      .skills-label {
        font-size: 12px;
        color: #999;
        margin-bottom: 6px;
      }

      .skills-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;

        .skill-tag {
          background: #e6f0ff;
          color: #0066b3;
          border-color: #b3d1ff;
        }

        .more-skills {
          font-size: 12px;
          color: #999;
          align-self: center;
        }
      }
    }

    .profile-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;

      .profile-tag {
        color: white;
        border-color: #0066b3;
      }
    }
  }

  .card-footer {
    padding: 12px 16px;
    background: #f8fafc;
    border-top: 1px solid #e6f0f0;

    .action-buttons {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }
}

.yn-grid-link-btn {
  color: #0066b3;
  padding: 0;

  &:hover {
    color: #0088cc;
  }
}

.high-potential-tag {
  background: #0066b3;
  color: white !important;
  border-color: #0066b3;
}

.talent-list-table {
  margin-bottom: 20px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e6f0ff;
  box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);

  :deep(.in-comparison-row) {
    background-color: #e6f0ff !important;
  }

  .table-selection {
    display: flex;
    align-items: center;
    gap: 8px;

    .in-comparison {
      color: #0066b3;
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
      color: white;
      font-size: 14px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .name-info {
      .name {
        font-weight: 500;
        line-height: 1.2;
      }

      .employee-id {
        font-size: 12px;
        color: #999;
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

  .table-actions {
    display: flex;
    gap: 4px;

    .ant-btn {
      padding: 4px;
      width: 28px;
      height: 28px;

      &.in-comparison {
        color: #0066b3;
      }
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  background: white;
  border-radius: 8px;
  border: 1px solid #e6f0ff;
  box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);
}

.yn-grid-pagination {
  :deep(.ant-pagination-item) {
    border-color: #e6f0ff;

    &:hover {
      border-color: #0066b3;

      a {
        color: #0066b3;
      }
    }

    &.ant-pagination-item-active {
      background: #0066b3;
      border-color: #0066b3;

      a {
        color: white;
      }
    }
  }

  :deep(.ant-pagination-prev, .ant-pagination-next) {
    .ant-pagination-item-link {
      border-color: #e6f0ff;
      color: #666;

      &:hover {
        border-color: #0066b3;
        color: #0066b3;
      }
    }
  }

  :deep(.ant-pagination-jump-prev, .ant-pagination-jump-next) {
    .ant-pagination-item-link {
      color: #666;

      &:hover {
        color: #0066b3;
      }
    }
  }
}

.yn-grid-progress {
  :deep(.ant-progress-inner) {
    background-color: #e6f0ff;
  }

  :deep(.ant-progress-circle-path) {
    stroke-linecap: round;
  }
}

.search-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: white;
  border-radius: 12px;
  border: 1px solid #e6f0ff;
  box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);

  .empty-illustration {
    margin-bottom: 24px;
  }

  .empty-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 12px 0;
    letter-spacing: -0.02em;
  }

  .empty-description {
    font-size: 14px;
    margin: 0 0 32px 0;
    line-height: 1.5;
    max-width: 320px;
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
    background: #f8fafc;
    border-bottom: 1px solid #e6f0ff;

    .ant-modal-title {
      color: #0066b3;
      font-weight: 600;
    }
  }

  :deep(.ant-modal-footer) {
    border-top: 1px solid #e6f0ff;
    padding: 16px 24px;
  }
}

.yn-grid-form {
  :deep(.ant-form-item-label) {
    label {
      color: #333;
      font-weight: 500;
    }
  }
}

.yn-grid-textarea {
  border-color: #e6f0ff;
  border-radius: 4px;

  &:hover, &:focus {
    border-color: #0066b3;
    box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
  }
}

.floating-comparison-button {
  position: fixed;
  right: 32px;
  bottom: 32px;
  z-index: 1000;

  .floating-button {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, #0066b3, #0088cc);
    border: none;
    box-shadow: 0 6px 16px rgba(0, 102, 179, 0.3);

    &:hover {
      transform: scale(1.1);
      transition: transform 0.3s;
      background: linear-gradient(135deg, #0088cc, #0099e6);
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .header-tools {
    flex-direction: column;
    align-items: stretch;

    .batch-actions {
      margin-left: 0;
      justify-content: center;
    }
  }

  .advanced-search-panel {
    min-width: auto;
    width: 90vw;
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