<template>
  <div class="talent-search-compare-container layout-container">
    <!-- 顶部导航和搜索区域 -->
    <HeaderComponent title="人才库" :loading="state.loading">
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
                  placeholder="搜索人才姓名、工号、专业领域..."
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

          <!-- 新增人才按钮 -->
          <a-button
              type="primary"
              @click="createTalent"
              class="yn-grid-btn-primary"
              style="flex-shrink: 0;"
          >
            <template #icon>
              <UserAddOutlined />
            </template>
            新增人才
          </a-button>

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
        width="900px"
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
                <label class="field-label">所属单位</label>
                <a-select
                    v-model:value="state.advancedFilters.company"
                    placeholder="请选择所属单位"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="yunnan_grid">云南电网有限责任公司</a-select-option>
                  <a-select-option value="electric_power_research">云南电网电力科学研究院</a-select-option>
                  <a-select-option value="kunming">昆明供电局</a-select-option>
                  <a-select-option value="qujing">曲靖供电局</a-select-option>
                  <a-select-option value="yuxi">玉溪供电局</a-select-option>
                </a-select>
              </div>

              <div class="field-group">
                <label class="field-label">职称</label>
                <a-select
                    v-model:value="state.advancedFilters.title"
                    placeholder="请选择职称"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="senior_engineer">高级工程师</a-select-option>
                  <a-select-option value="engineer">工程师</a-select-option>
                  <a-select-option value="assistant_engineer">助理工程师</a-select-option>
                  <a-select-option value="technician">技师</a-select-option>
                </a-select>
              </div>
            </div>

            <div class="field-row">
              <div class="field-group">
                <label class="field-label">最高学历</label>
                <a-select
                    v-model:value="state.advancedFilters.education"
                    placeholder="请选择最高学历"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="doctor">博士</a-select-option>
                  <a-select-option value="master">硕士</a-select-option>
                  <a-select-option value="bachelor">本科</a-select-option>
                  <a-select-option value="college">大专</a-select-option>
                </a-select>
              </div>

              <div class="field-group">
                <label class="field-label">院校类别</label>
                <a-select
                    v-model:value="state.advancedFilters.universityCategory"
                    placeholder="请选择院校类别"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="985">985</a-select-option>
                  <a-select-option value="211">211</a-select-option>
                  <a-select-option value="double_first_class">双一流</a-select-option>
                  <a-select-option value="ordinary">普通院校</a-select-option>
                </a-select>
              </div>
            </div>
          </div>
        </div>

        <!-- 人才标签 -->
        <div class="search-section">
          <div class="section-header">
            <TagOutlined style="color: #0066b3; margin-right: 8px;" />
            <span class="section-title">人才标签</span>
          </div>
          <div class="search-fields">
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">人才类型</label>
                <a-select
                    v-model:value="state.advancedFilters.talentType"
                    placeholder="请选择人才类型"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="technical_expert">技术专家</a-select-option>
                  <a-select-option value="skilled_expert">技能专家</a-select-option>
                  <a-select-option value="young_talent">青年托举人才</a-select-option>
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
                  <a-select-option value="strategic">战略级</a-select-option>
                  <a-select-option value="leadership">领军级</a-select-option>
                  <a-select-option value="pinnacle">拔尖级</a-select-option>
                  <a-select-option value="backbone">骨干</a-select-option>
                </a-select>
              </div>
            </div>

            <div class="field-row">
              <div class="field-group">
                <label class="field-label">专业领域（一级）</label>
                <a-select
                    v-model:value="state.advancedFilters.primaryDomain"
                    placeholder="请选择专业领域"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="smart_transmission">智能输变电</a-select-option>
                  <a-select-option value="power_ai">电力人工智能</a-select-option>
                  <a-select-option value="new_energy">新能源</a-select-option>
                  <a-select-option value="power_system">电力系统</a-select-option>
                </a-select>
              </div>

              <div class="field-group">
                <label class="field-label">技术专家等级</label>
                <a-select
                    v-model:value="state.advancedFilters.technicalExpertLevel"
                    placeholder="请选择技术专家等级"
                    style="width: 100%"
                    allow-clear
                    @change="handleFilterChange"
                    class="yn-grid-select"
                >
                  <a-select-option value="national">国家级</a-select-option>
                  <a-select-option value="provincial">省部级</a-select-option>
                  <a-select-option value="company">公司级</a-select-option>
                </a-select>
              </div>
            </div>
          </div>
        </div>

        <!-- 能力与成果 -->
        <div class="search-section">
          <div class="section-header">
            <RiseOutlined style="color: #0066b3; margin-right: 8px;" />
            <span class="section-title">能力与成果</span>
          </div>
          <div class="search-fields">
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">专利数量（≥）</label>
                <a-input-number
                    v-model:value="state.advancedFilters.patentMin"
                    placeholder="最小数量"
                    :min="0"
                    :max="100"
                    @change="handleFilterChange"
                    class="yn-grid-input"
                    style="width: 100%"
                />
              </div>

              <div class="field-group">
                <label class="field-label">论文数量（≥）</label>
                <a-input-number
                    v-model:value="state.advancedFilters.paperMin"
                    placeholder="最小数量"
                    :min="0"
                    :max="100"
                    @change="handleFilterChange"
                    class="yn-grid-input"
                    style="width: 100%"
                />
              </div>
            </div>

            <div class="field-row">
              <div class="field-group">
                <label class="field-label">近三年主持项目（≥）</label>
                <a-input-number
                    v-model:value="state.advancedFilters.hostedProjectsMin"
                    placeholder="最小数量"
                    :min="0"
                    :max="50"
                    @change="handleFilterChange"
                    class="yn-grid-input"
                    style="width: 100%"
                />
              </div>

              <div class="field-group">
                <label class="field-label">技术标准（≥）</label>
                <a-input-number
                    v-model:value="state.advancedFilters.standardsMin"
                    placeholder="最小数量"
                    :min="0"
                    :max="20"
                    @change="handleFilterChange"
                    class="yn-grid-input"
                    style="width: 100%"
                />
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

    <!-- 新增/编辑人才模态框 -->
    <a-modal
        :open="state.showCreateModal"
        :title="state.isEdit ? '编辑人才信息' : '新增人才'"
        @ok="saveTalent"
        @cancel="cancelTalentOperation"
        class="talent-modal yn-grid-modal"
        width="1200px"
        :confirm-loading="state.saving"
    >
      <a-form :model="state.currentTalent" layout="vertical" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <!-- 基本信息 -->
        <div class="form-section-title">
          <TeamOutlined style="color: #0066b3; margin-right: 8px;" />
          <span style="font-weight: 600; color: #333;">基本信息</span>
        </div>
        <a-row :gutter="24">
          <a-col :span="8">
            <a-form-item label="员工工号" :required="true">
              <a-input
                  v-model:value="state.currentTalent.employeeId"
                  placeholder="请输入员工工号"
                  size="large"
                  :maxlength="20"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="姓名" :required="true">
              <a-input
                  v-model:value="state.currentTalent.name"
                  placeholder="请输入姓名"
                  size="large"
                  :maxlength="20"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="性别">
              <a-radio-group v-model:value="state.currentTalent.gender" size="large" class="yn-grid-radio-group">
                <a-radio value="male">男</a-radio>
                <a-radio value="female">女</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="8">
            <a-form-item label="出生年月">
              <a-date-picker
                  v-model:value="state.currentTalent.birthDate"
                  placeholder="请选择出生年月"
                  size="large"
                  picker="month"
                  style="width: 100%"
                  class="yn-grid-datepicker"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="最高学历">
              <a-select
                  v-model:value="state.currentTalent.education"
                  placeholder="请选择最高学历"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="doctor">博士</a-select-option>
                <a-select-option value="master">硕士</a-select-option>
                <a-select-option value="bachelor">本科</a-select-option>
                <a-select-option value="college">大专</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="毕业院校">
              <a-input
                  v-model:value="state.currentTalent.graduatedFrom"
                  placeholder="请输入毕业院校"
                  size="large"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="8">
            <a-form-item label="所学专业">
              <a-input
                  v-model:value="state.currentTalent.major"
                  placeholder="请输入所学专业"
                  size="large"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="院校类别">
              <a-select
                  v-model:value="state.currentTalent.universityCategory"
                  placeholder="请选择院校类别"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="985">985</a-select-option>
                <a-select-option value="211">211</a-select-option>
                <a-select-option value="double_first_class">双一流</a-select-option>
                <a-select-option value="ordinary">普通院校</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="职称">
              <a-select
                  v-model:value="state.currentTalent.title"
                  placeholder="请选择职称"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="senior_engineer">高级工程师</a-select-option>
                <a-select-option value="engineer">工程师</a-select-option>
                <a-select-option value="assistant_engineer">助理工程师</a-select-option>
                <a-select-option value="technician">技师</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="职务">
              <a-input
                  v-model:value="state.currentTalent.position"
                  placeholder="请输入职务"
                  size="large"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="所属单位">
              <a-select
                  v-model:value="state.currentTalent.company"
                  placeholder="请选择所属单位"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="yunnan_grid">云南电网有限责任公司</a-select-option>
                <a-select-option value="electric_power_research">云南电网电力科学研究院</a-select-option>
                <a-select-option value="kunming">昆明供电局</a-select-option>
                <a-select-option value="qujing">曲靖供电局</a-select-option>
                <a-select-option value="yuxi">玉溪供电局</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="入职时间">
              <a-date-picker
                  v-model:value="state.currentTalent.joinDate"
                  placeholder="请选择入职时间"
                  size="large"
                  picker="month"
                  style="width: 100%"
                  class="yn-grid-datepicker"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 人才标签 -->
        <div class="form-section-title" style="margin-top: 24px;">
          <TagOutlined style="color: #0066b3; margin-right: 8px;" />
          <span style="font-weight: 600; color: #333;">人才标签</span>
        </div>
        <a-row :gutter="24">
          <a-col :span="8">
            <a-form-item label="人才类型">
              <a-select
                  v-model:value="state.currentTalent.talentType"
                  placeholder="请选择人才类型"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="technical_expert">技术专家</a-select-option>
                <a-select-option value="skilled_expert">技能专家</a-select-option>
                <a-select-option value="young_talent">青年托举人才</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="人才层级">
              <a-select
                  v-model:value="state.currentTalent.talentLevel"
                  placeholder="请选择人才层级"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="strategic">战略级</a-select-option>
                <a-select-option value="leadership">领军级</a-select-option>
                <a-select-option value="pinnacle">拔尖级</a-select-option>
                <a-select-option value="backbone">骨干</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="是否技术专家">
              <a-switch
                  v-model:checked="state.currentTalent.isTechnicalExpert"
                  checked-children="是"
                  un-checked-children="否"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="8">
            <a-form-item label="技术专家等级">
              <a-select
                  v-model:value="state.currentTalent.technicalExpertLevel"
                  placeholder="请选择技术专家等级"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="national">国家级</a-select-option>
                <a-select-option value="provincial">省部级</a-select-option>
                <a-select-option value="company">公司级</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="是否技能专家">
              <a-switch
                  v-model:checked="state.currentTalent.isSkilledExpert"
                  checked-children="是"
                  un-checked-children="否"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="专业领域（一级）">
              <a-select
                  v-model:value="state.currentTalent.primaryDomain"
                  placeholder="请选择专业领域"
                  size="large"
                  allow-clear
                  class="yn-grid-select"
              >
                <a-select-option value="smart_transmission">智能输变电</a-select-option>
                <a-select-option value="power_ai">电力人工智能</a-select-option>
                <a-select-option value="new_energy">新能源</a-select-option>
                <a-select-option value="power_system">电力系统</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="专业领域（二级）">
              <a-input
                  v-model:value="state.currentTalent.secondaryDomain"
                  placeholder="请输入专业领域（二级）"
                  size="large"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="入选人才支持计划">
              <a-textarea
                  v-model:value="state.currentTalent.talentSupportPlan"
                  placeholder="请输入入选的人才支持计划，用分号分隔"
                  size="large"
                  :rows="2"
                  class="yn-grid-textarea"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item label="获得人才荣誉">
              <a-textarea
                  v-model:value="state.currentTalent.talentHonors"
                  placeholder="请输入获得的人才荣誉，用分号分隔"
                  size="large"
                  :rows="2"
                  class="yn-grid-textarea"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 能力与成果 -->
        <div class="form-section-title" style="margin-top: 24px;">
          <RiseOutlined style="color: #0066b3; margin-right: 8px;" />
          <span style="font-weight: 600; color: #333;">能力与成果</span>
        </div>
        <a-row :gutter="24">
          <a-col :span="6">
            <a-form-item label="近三年主持项目数">
              <a-input-number
                  v-model:value="state.currentTalent.hostedProjectsCount"
                  placeholder="请输入数量"
                  size="large"
                  :min="0"
                  :max="100"
                  style="width: 100%"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="近三年参与项目数">
              <a-input-number
                  v-model:value="state.currentTalent.participatedProjectsCount"
                  placeholder="请输入数量"
                  size="large"
                  :min="0"
                  :max="100"
                  style="width: 100%"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="授权发明专利数">
              <a-input-number
                  v-model:value="state.currentTalent.patentCount"
                  placeholder="请输入数量"
                  size="large"
                  :min="0"
                  :max="100"
                  style="width: 100%"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="发表SCI/EI论文数">
              <a-input-number
                  v-model:value="state.currentTalent.paperCount"
                  placeholder="请输入数量"
                  size="large"
                  :min="0"
                  :max="100"
                  style="width: 100%"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="6">
            <a-form-item label="技术标准制定">
              <a-input-number
                  v-model:value="state.currentTalent.standardsCount"
                  placeholder="请输入数量"
                  size="large"
                  :min="0"
                  :max="20"
                  style="width: 100%"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="18">
            <a-form-item label="代表性项目">
              <a-textarea
                  v-model:value="state.currentTalent.representativeProjects"
                  placeholder="请输入代表性项目，用分号分隔"
                  size="large"
                  :rows="2"
                  class="yn-grid-textarea"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item label="科技奖励">
              <a-textarea
                  v-model:value="state.currentTalent.techAwards"
                  placeholder="请输入科技奖励"
                  size="large"
                  :rows="3"
                  class="yn-grid-textarea"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 发展与社会关系 -->
        <div class="form-section-title" style="margin-top: 24px;">
          <ShareAltOutlined style="color: #0066b3; margin-right: 8px;" />
          <span style="font-weight: 600; color: #333;">发展与社会关系</span>
        </div>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="导师">
              <a-input
                  v-model:value="state.currentTalent.mentor"
                  placeholder="请输入导师姓名"
                  size="large"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="所属团队">
              <a-input
                  v-model:value="state.currentTalent.team"
                  placeholder="请输入所属团队"
                  size="large"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="8">
            <a-form-item label="国际合作经历">
              <a-switch
                  v-model:checked="state.currentTalent.hasInternationalExperience"
                  checked-children="有"
                  un-checked-children="无"
              />
            </a-form-item>
          </a-col>
          <a-col :span="16">
            <a-form-item label="兴趣方向标签">
              <a-select
                  v-model:value="state.currentTalent.interestTags"
                  mode="tags"
                  placeholder="请输入兴趣方向标签，支持逗号分隔或回车"
                  size="large"
                  :token-separators="[',']"
                  :max-tag-count="5"
                  class="yn-grid-select"
              >
                <a-select-option v-for="tag in interestOptions" :key="tag" :value="tag">
                  {{ tag }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item label="职业发展意愿">
              <a-textarea
                  v-model:value="state.currentTalent.careerDevelopment"
                  placeholder="请输入职业发展意愿"
                  size="large"
                  :rows="3"
                  class="yn-grid-textarea"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 评估结果 -->
        <div class="form-section-title" style="margin-top: 24px;">
          <StarOutlined style="color: #0066b3; margin-right: 8px;" />
          <span style="font-weight: 600; color: #333;">评估结果</span>
        </div>
        <a-row :gutter="24">
          <a-col :span="6">
            <a-form-item label="评估总分">
              <a-input-number
                  v-model:value="state.currentTalent.evaluationScore"
                  placeholder="请输入评估总分"
                  size="large"
                  :min="0"
                  :max="100"
                  style="width: 100%"
                  class="yn-grid-input"
              />
            </a-form-item>
          </a-col>
          <a-col :span="18">
            <a-form-item label="AI评语">
              <a-textarea
                  v-model:value="state.currentTalent.aiEvaluation"
                  placeholder="请输入AI评语"
                  size="large"
                  :rows="3"
                  class="yn-grid-textarea"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="备注信息">
          <a-textarea
              v-model:value="state.currentTalent.remarks"
              placeholder="请输入其他补充信息"
              :rows="4"
              show-count
              :maxlength="1000"
              class="yn-grid-textarea"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="!state.loading && displayedTalents.length > 0">
      <!-- 人才总数 -->
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6f0ff, #f0f5ff);">
            <TeamOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ totalTalents }}</div>
            <div class="stat-label">人才总数</div>
          </div>
        </div>
      </a-card>

      <!-- 战略级专家 -->
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6f7ff, #f0f5ff);">
            <CrownOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ strategicExpertCount }}</div>
            <div class="stat-label">战略级专家</div>
          </div>
        </div>
      </a-card>

      <!-- 技术专家 -->
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f0f5ff, #e6f0ff);">
            <ExperimentOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ technicalExpertCount }}</div>
            <div class="stat-label">技术专家</div>
          </div>
        </div>
      </a-card>

      <!-- 平均专利数 -->
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6f0ff, #f0f5ff);">
            <FileTextOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ averagePatents }}</div>
            <div class="stat-label">领军级专家</div>
          </div>
        </div>
      </a-card>

      <!-- 平均论文数 -->
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f0f5ff, #e6f0ff);">
            <ReadOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ averagePapers }}</div>
            <div class="stat-label">拔尖级专家</div>
          </div>
        </div>
      </a-card>

      <!-- 985/211人才 -->
      <a-card class="stat-card yn-grid-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6f7ff, #f0f5ff);">
            <BankOutlined style="color: #0066b3; font-size: 24px;" />
          </div>
          <div class="stat-info">
            <div class="stat-value" style="color: #0066b3;">{{ topUniversityCount }}</div>
            <div class="stat-label">985/211人才</div>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 搜索结果区域 -->
    <div class="search-results" v-if="!state.loading && displayedTalents.length > 0">
      <!-- 搜索结果头部 -->
      <div class="results-header yn-grid-card">
        <div class="results-info">
          <span class="total-count" style="color: #0066b3;">共 {{ totalTalents }} 位人才</span>
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
            <a-select-option value="evaluationScore">评估分排序</a-select-option>
            <a-select-option value="patentCount">专利数排序</a-select-option>
            <a-select-option value="paperCount">论文数排序</a-select-option>
            <a-select-option value="hostedProjectsCount">主持项目排序</a-select-option>
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
                  <a-tag :color="getLevelColor(talent.talentLevel)" size="small" class="yn-grid-tag">
                    {{ getLevelLabel(talent.talentLevel) }}
                  </a-tag>
                  <a-tag v-if="talent.isTechnicalExpert" color="#0066b3" size="small" class="yn-grid-tag">
                    <ExperimentOutlined style="margin-right: 2px;" />
                    技术专家
                  </a-tag>
                  <a-tag v-if="talent.universityCategory === '985' || talent.universityCategory === '211'"
                         color="#52c41a" size="small" class="yn-grid-tag">
                    <BankOutlined style="margin-right: 2px;" />
                    {{ talent.universityCategory === '985' ? '985' : '211' }}
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
            <!-- 关键信息 -->
            <div class="key-info">
              <div class="info-row">
                <span class="info-label">工号:</span>
                <span class="info-value" style="color: #333;">{{ talent.employeeId || '未设置' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">职务:</span>
                <span class="info-value" style="color: #333;">{{ talent.position || '未设置' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">专业领域:</span>
                <span class="info-value" style="color: #0066b3; font-weight: 500;">{{ talent.primaryDomain || '未设置' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">评估分:</span>
                <span class="info-value">
                  <a-tag :color="getScoreColor(talent.evaluationScore)" size="small" class="yn-grid-tag">
                    {{ talent.evaluationScore || '未评估' }}
                  </a-tag>
                </span>
              </div>
            </div>

            <!-- 成果展示 -->
            <div class="achievements-section">
              <div class="achievements-row">
                <div class="achievement-item">
                  <span class="achievement-label">专利:</span>
                  <span class="achievement-value" style="color: #0066b3; font-weight: 600;">{{ talent.patentCount || 0 }}</span>
                </div>
                <div class="achievement-item">
                  <span class="achievement-label">论文:</span>
                  <span class="achievement-value" style="color: #0066b3; font-weight: 600;">{{ talent.paperCount || 0 }}</span>
                </div>
                <div class="achievement-item">
                  <span class="achievement-label">主持项目:</span>
                  <span class="achievement-value" style="color: #0066b3; font-weight: 600;">{{ talent.hostedProjectsCount || 0 }}</span>
                </div>
              </div>
            </div>

            <!-- 荣誉标签 -->
            <div class="honor-tags" v-if="talent.talentHonors && talent.talentHonors.length > 0">
              <a-tag
                  v-for="(honor, index) in talent.talentHonors.split(';').slice(0, 2)"
                  :key="index"
                  color="#0066b3"
                  size="small"
                  class="yn-grid-tag honor-tag"
              >
                {{ honor.trim() }}
              </a-tag>
              <span v-if="talent.talentHonors.split(';').length > 2" class="more-honors">
                +{{ talent.talentHonors.split(';').length - 2 }}
              </span>
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
                  <div class="employee-id">{{ record.employeeId }}</div>
                </div>
              </div>
            </template>

            <template v-if="column.key === 'talentLevel'">
              <div class="level-cell">
                <a-tag :color="getLevelColor(record.talentLevel)" size="small" class="yn-grid-tag">
                  {{ getLevelLabel(record.talentLevel) }}
                </a-tag>
              </div>
            </template>

            <template v-if="column.key === 'technicalExpert'">
              <div class="expert-cell">
                <a-tag v-if="record.isTechnicalExpert" color="#0066b3" size="small" class="yn-grid-tag">
                  技术专家
                </a-tag>
                <span v-else>-</span>
              </div>
            </template>

            <template v-if="column.key === 'achievements'">
              <div class="achievements-cell">
                <div class="achievement-item">
                  <span class="achievement-label">专利:</span>
                  <span class="achievement-value">{{ record.patentCount || 0 }}</span>
                </div>
                <div class="achievement-item">
                  <span class="achievement-label">论文:</span>
                  <span class="achievement-value">{{ record.paperCount || 0 }}</span>
                </div>
                <div class="achievement-item">
                  <span class="achievement-label">主持项目:</span>
                  <span class="achievement-value">{{ record.hostedProjectsCount || 0 }}</span>
                </div>
              </div>
            </template>

            <template v-if="column.key === 'evaluationScore'">
              <div class="score-cell">
                <a-progress
                    :percent="record.evaluationScore || 0"
                    :stroke-color="getScoreColor(record.evaluationScore)"
                    size="small"
                    :show-info="false"
                    style="width: 60px;"
                    class="yn-grid-progress"
                />
                <span class="score-value">{{ record.evaluationScore || '未评估' }}</span>
              </div>
            </template>

            <!-- 列表视图的操作列 -->
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
                <a-tooltip title="编辑">
                  <a-button
                      type="link"
                      size="small"
                      @click="editTalent(record)"
                      class="yn-grid-link-btn"
                  >
                    <EditOutlined />
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
        <a-button type="primary" @click="state.showAdvancedModal = true" class="yn-grid-btn-primary">
          <FilterOutlined />
          使用高级搜索
        </a-button>
        <a-button type="primary" @click="createTalent" style="margin-left: 12px;" class="yn-grid-btn-primary">
          <UserAddOutlined />
          新增人才
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
  EditOutlined, AppstoreOutlined, ExperimentOutlined,
  UnorderedListOutlined, PlusCircleOutlined, SearchOutlined,
  CloseCircleOutlined, CrownOutlined, FileTextOutlined,
  TagOutlined, RedoOutlined, CheckOutlined,
  ScheduleOutlined, DeleteOutlined as DeleteIcon, ReadOutlined,
  UserAddOutlined, ShareAltOutlined, BankOutlined
} from '@ant-design/icons-vue'
import { talentApi } from '@/apis/talent_api'
import HeaderComponent from '@/components/HeaderComponent.vue'
import dayjs from '@/utils/time'

const route = useRoute()
const router = useRouter()
const comparisonStore = useComparisonStore()

const talents = ref([])
const searchPresets = ref([
  {
    id: 'strategic_expert',
    name: '战略级专家搜索',
    isDefault: true,
    description: '战略级技术专家，专利≥5，论文≥3，主持项目≥2',
    criteria: {
      talentLevel: 'strategic',
      patentMin: 5,
      paperMin: 3,
      hostedProjectsMin: 2
    }
  },
  {
    id: 'technical_expert',
    name: '技术专家搜索',
    description: '技术专家，专利≥3，论文≥2，985/211院校',
    criteria: {
      talentType: 'technical_expert',
      patentMin: 3,
      paperMin: 2,
      universityCategory: { in: ['985', '211'] }
    }
  },
  {
    id: 'young_talent',
    name: '青年人才搜索',
    description: '青年托举人才，硕士以上，近3年有成果',
    criteria: {
      talentType: 'young_talent',
      education: { min: 'master' },
      patentMin: 1,
      paperMin: 1
    }
  }
])

const quickSearchTags = [
  {
    id: 'tag_strategic_expert',
    name: '战略级专家',
    criteria: {
      talentLevel: 'strategic'
    },
    description: '战略级技术专家'
  },
  {
    id: 'tag_leadership_expert',
    name: '领军级专家',
    criteria: {
      talentLevel: 'leadership'
    },
    description: '领军级技术专家'
  },
  {
    id: 'tag_pinnacle_expert',
    name: '拔尖级专家',
    criteria: {
      talentLevel: 'pinnacle'
    },
    description: '拔尖级技术专家'
  },
  {
    id: 'tag_top_university',
    name: '985/211人才',
    criteria: {
      universityCategory: { in: ['985', '211'] }
    },
    description: '985/211院校毕业生'
  },
  {
    id: 'tag_patent_rich',
    name: '专利达人',
    criteria: {
      patentMin: 5
    },
    description: '专利数量≥5项'
  }
]

const interestOptions = [
  '数字孪生', '深度学习', '故障诊断', '大语言模型', '知识图谱',
  '负荷预测', '电力系统稳定', '新能源接入', '智能运维', '边缘计算'
]

const state = reactive({
  loading: false,
  searchKeyword: '',
  advancedFilters: {
    company: null,
    title: null,
    education: null,
    universityCategory: null,
    talentType: null,
    talentLevel: null,
    primaryDomain: null,
    technicalExpertLevel: null,
    patentMin: null,
    paperMin: null,
    hostedProjectsMin: null,
    standardsMin: null
  },
  currentPage: 1,
  pageSize: 12,
  viewMode: 'card',
  selectAll: false,
  indeterminate: false,
  selectedTalents: [],
  sortField: 'evaluationScore',
  sortOrder: 'desc',
  showSaveSearchModal: false,
  showAdvancedModal: false,
  showCreateModal: false,
  isEdit: false,
  saving: false,
  newSearchPreset: {
    name: '',
    description: '',
    isDefault: false
  },
  currentTalent: {
    id: null,
    employeeId: '',
    name: '',
    gender: 'male',
    birthDate: null,
    education: null,
    graduatedFrom: '',
    major: '',
    universityCategory: null,
    title: null,
    position: '',
    company: null,
    joinDate: null,
    talentType: null,
    talentLevel: null,
    primaryDomain: null,
    secondaryDomain: '',
    isTechnicalExpert: false,
    technicalExpertLevel: null,
    isSkilledExpert: false,
    talentSupportPlan: '',
    talentHonors: '',
    hostedProjectsCount: 0,
    participatedProjectsCount: 0,
    representativeProjects: '',
    patentCount: 0,
    paperCount: 0,
    standardsCount: 0,
    techAwards: '',
    mentor: '',
    team: '',
    hasInternationalExperience: false,
    interestTags: [],
    careerDevelopment: '',
    evaluationScore: null,
    aiEvaluation: '',
    remarks: ''
  }
})

// 表格列定义 - 根据业务需求调整
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
    width: 120,
    fixed: 'left',
    sorter: (a, b) => a.name.localeCompare(b.name)
  },
  {
    title: '员工工号',
    key: 'employeeId',
    width: 100,
    sorter: (a, b) => a.employeeId.localeCompare(b.employeeId)
  },
  {
    title: '人才层级',
    key: 'talentLevel',
    width: 100,
    filters: [
      { text: '战略级', value: 'strategic' },
      { text: '领军级', value: 'leadership' },
      { text: '拔尖级', value: 'pinnacle' },
      { text: '骨干', value: 'backbone' }
    ],
    onFilter: (value, record) => record.talentLevel === value
  },
  {
    title: '技术专家',
    key: 'technicalExpert',
    width: 100,
    filters: [
      { text: '是', value: true },
      { text: '否', value: false }
    ],
    onFilter: (value, record) => record.isTechnicalExpert === value
  },
  {
    title: '职称',
    key: 'title',
    width: 100,
    filters: [
      { text: '高级工程师', value: 'senior_engineer' },
      { text: '工程师', value: 'engineer' },
      { text: '助理工程师', value: 'assistant_engineer' }
    ],
    onFilter: (value, record) => record.title === value
  },
  {
    title: '最高学历',
    key: 'education',
    width: 100,
    filters: [
      { text: '博士', value: 'doctor' },
      { text: '硕士', value: 'master' },
      { text: '本科', value: 'bachelor' }
    ],
    onFilter: (value, record) => record.education === value
  },
  {
    title: '所属单位',
    key: 'company',
    width: 150,
    filters: [
      { text: '云南电网电力科学研究院', value: 'electric_power_research' },
      { text: '昆明供电局', value: 'kunming' },
      { text: '曲靖供电局', value: 'qujing' }
    ],
    onFilter: (value, record) => record.company === value
  },
  {
    title: '专业领域',
    key: 'primaryDomain',
    width: 120,
    filters: [
      { text: '智能输变电', value: 'smart_transmission' },
      { text: '电力人工智能', value: 'power_ai' },
      { text: '新能源', value: 'new_energy' }
    ],
    onFilter: (value, record) => record.primaryDomain === value
  },
  {
    title: '成果展示',
    key: 'achievements',
    width: 180
  },
  {
    title: '评估分',
    key: 'evaluationScore',
    width: 120,
    sorter: (a, b) => (a.evaluationScore || 0) - (b.evaluationScore || 0)
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right'
  }
];

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
        talent.employeeId?.toLowerCase().includes(keyword) ||
        talent.position?.toLowerCase().includes(keyword) ||
        talent.primaryDomain?.toLowerCase().includes(keyword) ||
        talent.graduatedFrom?.toLowerCase().includes(keyword)
    )
  }

  // 高级筛选
  const filters = state.advancedFilters

  if (filters.company) {
    filtered = filtered.filter(talent => talent.company === filters.company)
  }

  if (filters.title) {
    filtered = filtered.filter(talent => talent.title === filters.title)
  }

  if (filters.education) {
    filtered = filtered.filter(talent => talent.education === filters.education)
  }

  if (filters.universityCategory) {
    filtered = filtered.filter(talent => talent.universityCategory === filters.universityCategory)
  }

  if (filters.talentType) {
    filtered = filtered.filter(talent => talent.talentType === filters.talentType)
  }

  if (filters.talentLevel) {
    filtered = filtered.filter(talent => talent.talentLevel === filters.talentLevel)
  }

  if (filters.primaryDomain) {
    filtered = filtered.filter(talent => talent.primaryDomain === filters.primaryDomain)
  }

  if (filters.technicalExpertLevel) {
    filtered = filtered.filter(talent => talent.technicalExpertLevel === filters.technicalExpertLevel)
  }

  if (filters.patentMin !== null) {
    filtered = filtered.filter(talent => talent.patentCount >= filters.patentMin)
  }

  if (filters.paperMin !== null) {
    filtered = filtered.filter(talent => talent.paperCount >= filters.paperMin)
  }

  if (filters.hostedProjectsMin !== null) {
    filtered = filtered.filter(talent => talent.hostedProjectsCount >= filters.hostedProjectsMin)
  }

  if (filters.standardsMin !== null) {
    filtered = filtered.filter(talent => talent.standardsCount >= filters.standardsMin)
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
      if (talent.employeeId?.toLowerCase().includes(keyword)) {
        matchScore += 20
        matchReasons.push('工号匹配')
      }
      if (talent.primaryDomain?.toLowerCase().includes(keyword)) {
        matchScore += 25
        matchReasons.push('专业领域匹配')
      }
    }

    // 高级筛选匹配
    if (state.advancedFilters.talentLevel) {
      if (talent.talentLevel === state.advancedFilters.talentLevel) {
        matchScore += 15
      }
    }

    if (state.advancedFilters.patentMin !== null) {
      if (talent.patentCount >= state.advancedFilters.patentMin) {
        matchScore += 10
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
    case 'evaluationScore':
      sorted.sort((a, b) => {
        const scoreA = a.evaluationScore || 0
        const scoreB = b.evaluationScore || 0
        return state.sortOrder === 'desc' ? scoreB - scoreA : scoreA - scoreB
      })
      break
    case 'patentCount':
      sorted.sort((a, b) => {
        return state.sortOrder === 'desc' ? b.patentCount - a.patentCount : a.patentCount - b.patentCount
      })
      break
    case 'paperCount':
      sorted.sort((a, b) => {
        return state.sortOrder === 'desc' ? b.paperCount - a.paperCount : a.paperCount - b.paperCount
      })
      break
    case 'hostedProjectsCount':
      sorted.sort((a, b) => {
        return state.sortOrder === 'desc' ? b.hostedProjectsCount - a.hostedProjectsCount : a.hostedProjectsCount - b.hostedProjectsCount
      })
      break
  }

  // 分页
  const start = (state.currentPage - 1) * state.pageSize
  const end = start + state.pageSize
  return sorted.slice(start, end)
})

// 统计计算属性
const strategicExpertCount = computed(() => {
  return filteredTalents.value.filter(talent => talent.talentLevel === 'strategic').length
})

const technicalExpertCount = computed(() => {
  return filteredTalents.value.filter(talent => talent.isTechnicalExpert).length
})

const averagePatents = computed(() => {
  if (filteredTalents.value.length === 0) return '0.0'
  const total = filteredTalents.value.reduce((sum, talent) => sum + (talent.patentCount || 0), 0)
  return (total / filteredTalents.value.length).toFixed(1)
})

const averagePapers = computed(() => {
  if (filteredTalents.value.length === 0) return '0.0'
  const total = filteredTalents.value.reduce((sum, talent) => sum + (talent.paperCount || 0), 0)
  return (total / filteredTalents.value.length).toFixed(1)
})

const topUniversityCount = computed(() => {
  return filteredTalents.value.filter(talent =>
      talent.universityCategory === '985' || talent.universityCategory === '211'
  ).length
})

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

  // 单位筛选
  if (state.advancedFilters.company) {
    const companies = {
      electric_power_research: '云南电网电力科学研究院',
      kunming: '昆明供电局',
      qujing: '曲靖供电局',
      yuxi: '玉溪供电局',
      yunnan_grid: '云南电网有限责任公司'
    }
    filters.push({
      key: 'company',
      label: '所属单位',
      value: companies[state.advancedFilters.company] || state.advancedFilters.company
    })
  }

  // 职称筛选
  if (state.advancedFilters.title) {
    const titles = {
      senior_engineer: '高级工程师',
      engineer: '工程师',
      assistant_engineer: '助理工程师',
      technician: '技师'
    }
    filters.push({
      key: 'title',
      label: '职称',
      value: titles[state.advancedFilters.title] || state.advancedFilters.title
    })
  }

  // 学历筛选
  if (state.advancedFilters.education) {
    const education = {
      doctor: '博士',
      master: '硕士',
      bachelor: '本科',
      college: '大专'
    }
    filters.push({
      key: 'education',
      label: '最高学历',
      value: education[state.advancedFilters.education] || state.advancedFilters.education
    })
  }

  // 人才层级筛选
  if (state.advancedFilters.talentLevel) {
    const levels = {
      strategic: '战略级',
      leadership: '领军级',
      pinnacle: '拔尖级',
      backbone: '骨干'
    }
    filters.push({
      key: 'talentLevel',
      label: '人才层级',
      value: levels[state.advancedFilters.talentLevel] || state.advancedFilters.talentLevel
    })
  }

  // 专利数量筛选
  if (state.advancedFilters.patentMin !== null) {
    filters.push({
      key: 'patentMin',
      label: '专利数量',
      value: `≥${state.advancedFilters.patentMin}项`
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
const getLevelLabel = (level) => {
  const labels = {
    strategic: '战略级',
    leadership: '领军级',
    pinnacle: '拔尖级',
    backbone: '骨干'
  }
  return labels[level] || level
}

const getLevelColor = (level) => {
  const colors = {
    strategic: '#f5222d',
    leadership: '#fa8c16',
    pinnacle: '#0066b3',
    backbone: '#52c41a'
  }
  return colors[level] || '#e6f0ff'
}

const getScoreColor = (score) => {
  if (!score) return '#d9d9d9'
  if (score >= 90) return '#0066b3'
  if (score >= 80) return '#0088cc'
  if (score >= 70) return '#66a3ff'
  return '#99c2ff'
}

const getAvatarStyle = (talent) => {
  const colors = [
    'linear-gradient(135deg, #0066b3, #0088cc)',
    'linear-gradient(135deg, #0066b3, #66a3ff)',
    'linear-gradient(135deg, #0088cc, #99c2ff)',
    'linear-gradient(135deg, #004d99, #0066b3)'
  ]

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

// 新增人才相关函数
const resetTalentForm = () => {
  state.currentTalent = {
    id: null,
    employeeId: '',
    name: '',
    gender: 'male',
    birthDate: null,
    education: null,
    graduatedFrom: '',
    major: '',
    universityCategory: null,
    title: null,
    position: '',
    company: null,
    joinDate: null,
    talentType: null,
    talentLevel: null,
    primaryDomain: null,
    secondaryDomain: '',
    isTechnicalExpert: false,
    technicalExpertLevel: null,
    isSkilledExpert: false,
    talentSupportPlan: '',
    talentHonors: '',
    hostedProjectsCount: 0,
    participatedProjectsCount: 0,
    representativeProjects: '',
    patentCount: 0,
    paperCount: 0,
    standardsCount: 0,
    techAwards: '',
    mentor: '',
    team: '',
    hasInternationalExperience: false,
    interestTags: [],
    careerDevelopment: '',
    evaluationScore: null,
    aiEvaluation: '',
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
    birthDate: talent.birthDate ? dayjs(talent.birthDate) : null,
    joinDate: talent.joinDate ? dayjs(talent.joinDate) : null,
    interestTags: Array.isArray(talent.interestTags) ? talent.interestTags : []
  })
  state.showCreateModal = true
}

const saveTalent = async () => {
  if (!state.currentTalent.employeeId?.trim()) {
    message.error('员工工号不能为空')
    return
  }

  if (!state.currentTalent.name?.trim()) {
    message.error('姓名不能为空')
    return
  }

  state.saving = true
  try {
    const talentData = {
      ...state.currentTalent,
      birthDate: state.currentTalent.birthDate ? dayjs(state.currentTalent.birthDate).format('YYYY-MM') : null,
      joinDate: state.currentTalent.joinDate ? dayjs(state.currentTalent.joinDate).format('YYYY-MM') : null
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

const cancelTalentOperation = () => {
  state.showCreateModal = false
  resetTalentForm()
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
        interestTags: Array.isArray(talent.interestTags) ? talent.interestTags : [],
        hostedProjectsCount: talent.hostedProjectsCount || 0,
        participatedProjectsCount: talent.participatedProjectsCount || 0,
        patentCount: talent.patentCount || 0,
        paperCount: talent.paperCount || 0,
        standardsCount: talent.standardsCount || 0,
        evaluationScore: talent.evaluationScore || null
      }))
    }

    talents.value = talentList.sort((a, b) => (b.evaluationScore || 0) - (a.evaluationScore || 0))
  } catch (error) {
    console.error('加载人才列表失败:', error)
    message.error('加载人才列表失败')
  } finally {
    state.loading = false
  }
}

const handleSearch = () => {
  state.currentPage = 1
}

const handleSearchClear = () => {
  state.searchKeyword = ''
  state.currentPage = 1
}

const applyQuickSearch = (tag) => {
  if (tag.criteria) {
    clearAllFilters()

    Object.keys(tag.criteria).forEach(key => {
      if (key in state.advancedFilters) {
        state.advancedFilters[key] = tag.criteria[key]
      }
    })

    if (tag.keywords) {
      state.searchKeyword = tag.keywords
    }

    handleSearch()
    message.success(`已应用搜索条件: ${tag.name}`)
  }
}

const handleFilterChange = () => {
  state.currentPage = 1
}

const showAdvancedSearchModal = () => {
  state.showAdvancedModal = true
}

const applyAdvancedSearch = () => {
  state.currentPage = 1
  state.showAdvancedModal = false
  message.success('应用筛选条件成功')
}

const resetAdvancedFilters = () => {
  state.advancedFilters = {
    company: null,
    title: null,
    education: null,
    universityCategory: null,
    talentType: null,
    talentLevel: null,
    primaryDomain: null,
    technicalExpertLevel: null,
    patentMin: null,
    paperMin: null,
    hostedProjectsMin: null,
    standardsMin: null
  }
}

const removeFilter = (filterKey) => {
  if (filterKey === 'searchKeyword') {
    state.searchKeyword = ''
  } else if (filterKey in state.advancedFilters) {
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
  if (state.selectedTalents.length > 5) {
    message.warning('最多只能选择5人进行对比')
    return
  }

  const selectedTalents = talents.value.filter(talent =>
      state.selectedTalents.includes(talent.id)
  )

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

  comparisonStore.clearComparison()
  selectedTalents.forEach(talent => {
    comparisonStore.addToComparison(talent)
  })

  gotoComparison()
}

const toggleComparison = (talent) => {
  if (isInComparisonList(talent.id)) {
    gotoComparison()
  } else {
    if (comparisonStore.comparisonList.length >= 5) {
      message.warning('对比列表最多支持5位人才')
      return
    }

    comparisonStore.addToComparison(talent)

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
  router.push('/talent/compare')
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

  state.currentPage = 1
  message.success(`已应用搜索方案: ${preset.name}`)
}

const viewTalentDetails = (talent) => {
  router.push({ path: `/talent/${talent.id}` })
}

const resetSearch = () => {
  clearAllFilters()
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

  if (route.query.search) {
    state.searchKeyword = route.query.search
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

.unified-search-bar {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 12px;
  min-width: 0;
  position: relative;
  z-index: 1001;
}

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
  }
}

.yn-grid-tag.clickable-tag {
  position: relative;
  z-index: 1;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: var(--main-30);
    border-color: var(--main-500);
    color: var(--main-500);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 102, 179, 0.25) !important;
    z-index: 2000 !important;
  }
}

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
  }
}

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

.yn-grid-btn-primary {
  background: var(--main-500);
  border-color: var(--main-500);
  color: var(--main-0);

  &:hover, &:focus {
    background: var(--main-400);
    border-color: var(--main-400);
    color: var(--main-0);
  }
}

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

.talent-modal {
  :deep(.ant-modal-body) {
    max-height: 70vh;
    overflow-y: auto;
    padding: 24px;
  }
}

.yn-grid-radio-group {
  :deep(.ant-radio-button-wrapper) {
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

.yn-grid-datepicker {
  :deep(.ant-picker) {
    border-color: var(--main-30);
    border-radius: 4px;

    &:hover, &:focus {
      border-color: var(--main-500);
      box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
    }
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
  border-color: var(--main-30);
  border-radius: 4px;

  &:hover, &:focus {
    border-color: var(--main-500);
    box-shadow: 0 0 0 2px rgba(0, 102, 179, 0.1);
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
}

.clear-all-btn {
  color: var(--main-500);

  &:hover {
    color: var(--main-400);
  }
}

.yn-grid-badge {
  :deep(.ant-badge-count) {
    background: var(--color-error-500);
    box-shadow: 0 0 0 1px var(--main-0);
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

.talent-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
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
          min-width: 70px;
        }

        .info-value {
          margin-left: 8px;
          flex: 1;
        }
      }
    }

    .achievements-section {
      margin-bottom: 16px;

      .achievements-row {
        display: flex;
        justify-content: space-between;
        background: var(--main-5);
        padding: 12px;
        border-radius: 8px;

        .achievement-item {
          display: flex;
          flex-direction: column;
          align-items: center;

          .achievement-label {
            font-size: 12px;
            color: var(--gray-500);
            margin-bottom: 4px;
          }

          .achievement-value {
            font-size: 16px;
          }
        }
      }
    }

    .honor-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;

      .honor-tag {
        background: var(--main-500);
        color: var(--main-0);
        border-color: var(--main-500);
      }

      .more-honors {
        font-size: 12px;
        color: var(--gray-500);
        align-self: center;
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

  .level-cell {
    .ant-tag {
      margin-bottom: 4px;
    }
  }

  .achievements-cell {
    .achievement-item {
      display: flex;
      align-items: center;
      margin-bottom: 4px;

      .achievement-label {
        color: var(--gray-600);
        min-width: 40px;
        font-size: 12px;
      }

      .achievement-value {
        margin-left: 8px;
        font-weight: 500;
        color: var(--main-500);
      }
    }
  }

  .score-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .score-value {
      font-size: 14px;
      font-weight: 500;
      min-width: 30px;
      color: var(--gray-900);
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
}

.yn-grid-progress {
  :deep(.ant-progress-inner) {
    background-color: var(--main-30);
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  height: auto;
  transition: all 0.3s ease;
  border: 1px solid #e6f0ff;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 102, 179, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  height: 10%;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #333;
  font-weight: 600;
  margin-bottom: 2px;
}

/* 卡片悬停效果增强 */
.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0066b3, #0088cc);
  border-radius: 4px 4px 0 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover::before {
  opacity: 1;
}

/* 图标动画效果 */
.stat-icon svg {
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-icon svg {
  transform: scale(1.1);
}

@media (max-width: 1600px) {
  .stats-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
