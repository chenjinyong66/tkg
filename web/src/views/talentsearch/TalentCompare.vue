<template>
  <div class="talent-comparison-container layout-container">
    <!-- 顶部导航 -->
    <HeaderComponent title="人才对比分析" :loading="loading">
      <template #actions>
        <div class="compare-actions">
          <a-button @click="handleBack" class="yn-grid-btn-secondary">
            <ArrowLeftOutlined />
            返回搜索
          </a-button>

          <a-button
              @click="handleAddTalent"
              style="margin-left: 12px;"
              class="yn-grid-btn-secondary"
              :loading="loading"
              :disabled="comparisonData.length >= 5"
          >
            <PlusOutlined />
            添加对比人员
            <span v-if="comparisonData.length >= 5" class="max-limit-badge">(已满)</span>
          </a-button>

          <a-dropdown>
            <template #overlay>
              <a-menu @click="handleCompareActions" class="yn-grid-dropdown-menu">
                <a-menu-item key="export" class="menu-item">
                  <ExportOutlined style="color: #0066b3;" />
                  <span style="color: #333;">导出对比结果</span>
                </a-menu-item>
                <a-menu-item key="save" class="menu-item">
                  <SaveOutlined style="color: #0066b3;" />
                  <span style="color: #333;">保存对比方案</span>
                </a-menu-item>
                <a-menu-divider style="border-color: #e6f0ff" />
                <a-menu-item key="clear" danger class="menu-item">
                  <DeleteOutlined />
                  清空对比列表
                </a-menu-item>
              </a-menu>
            </template>
            <a-button type="primary" class="yn-grid-btn-primary">
              <SettingOutlined />
              对比设置
            </a-button>
          </a-dropdown>
        </div>
      </template>
    </HeaderComponent>

    <!-- 对比人员区域 -->
    <div class="compare-participants yn-grid-card" v-if="comparisonData.length > 0">
      <div class="participants-header">
        <h3 style="color: #0066b3;">对比人员 ({{ comparisonData.length }}/5)</h3>
        <a-tooltip v-if="comparisonData.length >= 5" title="对比列表已满，最多支持5人">
          <a-button
              type="link"
              class="add-participant-link disabled-btn"
          >
            <PlusOutlined />
            添加人员
          </a-button>
        </a-tooltip>
        <a-button
            v-else
            type="link"
            @click="handleAddTalent"
            class="add-participant-link"
            :loading="loading"
        >
          <PlusOutlined />
          添加人员
        </a-button>
      </div>

      <div class="participants-list">
        <div
            v-for="(talent, index) in comparisonData"
            :key="talent.id"
            class="participant-card"
            :class="`participant-card-${index}`"
        >
          <div class="card-header">
            <div class="participant-avatar" :style="getAvatarStyle(talent)">
              {{ talent.name?.charAt(0) || '?' }}
            </div>
            <div class="participant-info">
              <div class="info-row">
                <span class="participant-name" :style="{ color: getTalentColor(index) }">{{ talent.name }}</span>
                <a-tag
                    v-if="talent.talentLevel === 'strategic'"
                    color="#f5222d"
                    size="small"
                    class="talent-tag"
                >
                  <CrownOutlined />
                  战略级
                </a-tag>
              </div>
              <div class="info-row">
                <span class="participant-position">{{ talent.position || '未设置' }}</span>
                <span class="participant-department">{{ getCompanyLabel(talent.company) }}</span>
              </div>
            </div>
            <a-button
                type="text"
                size="small"
                @click="handleRemoveTalent(talent.id)"
                class="remove-btn"
            >
              <CloseOutlined />
            </a-button>
          </div>

          <div class="card-tags">
            <div class="tags-section">
              <span class="tags-label">学历标签：</span>
              <div class="tags-container">
                <a-tag
                    v-if="talent.universityCategory === '985' || talent.universityCategory === '211'"
                    color="#0066b3"
                    size="small"
                    class="talent-tag"
                >
                  {{ talent.universityCategory === '985' ? '985' : '211' }}
                </a-tag>
                <a-tag
                    v-if="talent.education === 'master' || talent.education === 'doctor'"
                    color="#0088cc"
                    size="small"
                    class="talent-tag"
                >
                  {{ talent.education === 'master' ? '研究生' : '博士' }}
                </a-tag>
                <a-tag
                    v-if="talent.hasInternationalExperience"
                    color="#66a3ff"
                    size="small"
                    class="talent-tag"
                >
                  国际经验
                </a-tag>
              </div>
            </div>

            <div class="tags-section">
              <span class="tags-label">能力标签：</span>
              <div class="tags-container">
                <a-tag
                    v-if="talent.isTechnicalExpert"
                    color="#0066b3"
                    size="small"
                    class="talent-tag"
                >
                  技术专家
                </a-tag>
                <a-tag
                    v-if="talent.isSkilledExpert"
                    color="#52c41a"
                    size="small"
                    class="talent-tag"
                >
                  技能专家
                </a-tag>
                <a-tag
                    v-for="(tag, tagIndex) in (talent.interestTags || []).slice(0, 2)"
                    :key="tagIndex"
                    :color="getTagColor(tagIndex)"
                    size="small"
                    class="talent-tag"
                >
                  {{ tag }}
                </a-tag>
                <span v-if="talent.interestTags?.length > 2" class="more-tags">
                  +{{ talent.interestTags.length - 2 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 添加人员卡片 -->
        <div
            v-if="comparisonData.length < 5"
            class="add-participant-card"
            @click="handleAddTalent"
        >
          <PlusOutlined style="font-size: 24px; color: #0066b3; opacity: 0.6;" />
          <div class="add-text" style="color: #0066b3;">添加人员</div>
          <div class="add-subtext" style="color: #999;">还可添加 {{ 5 - comparisonData.length }} 人</div>
        </div>
      </div>
    </div>

    <!-- 对比维度选择 -->
    <div class="compare-dimensions yn-grid-card" v-if="comparisonData.length > 0">
      <div class="dimensions-header">
        <h3 style="color: #0066b3;">对比维度</h3>
        <a-switch
            v-model:checked="showAllDimensions"
            checked-children="显示全部"
            un-checked-children="常用维度"
            size="small"
            class="yn-grid-switch"
        />
      </div>

      <div class="dimensions-list">
        <a-checkbox-group
            v-model:value="selectedDimensions"
            :options="dimensionOptions"
            class="dimensions-checkbox-group"
        />
      </div>
    </div>

    <!-- 对比表格 -->
    <div class="compare-table-container yn-grid-card" v-if="comparisonData.length > 0">
      <div class="table-wrapper" ref="tableWrapper">
        <table class="compare-table">
          <thead>
          <tr>
            <th class="dimension-col" style="background: #f8fafc; color: #0066b3;">对比维度</th>
            <th
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                class="talent-col"
                :class="`talent-col-${index}`"
            >
              <div class="talent-header">
                <div class="talent-avatar" :style="getAvatarStyle(talent)">
                  {{ talent.name?.charAt(0) || '?' }}
                </div>
                <div class="talent-info">
                  <div class="talent-name" :style="{ color: getTalentColor(index) }">{{ talent.name }}</div>
                  <div class="talent-position">{{ talent.position || '未设置' }}</div>
                  <div class="talent-tags">
                    <a-tag
                        v-if="talent.talentLevel === 'strategic'"
                        color="#f5222d"
                        size="small"
                        class="header-tag"
                    >
                      战略级
                    </a-tag>
                    <a-tag
                        v-if="talent.isTechnicalExpert"
                        color="#0066b3"
                        size="small"
                        class="header-tag"
                    >
                      技术专家
                    </a-tag>
                  </div>
                </div>
              </div>
            </th>
          </tr>
          </thead>
          <tbody>
          <!-- 基本信息 -->
          <tr class="dimension-group" v-if="showDimension('basic')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <TeamOutlined style="margin-right: 8px;" />
              基本信息
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">所属单位</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value">{{ getCompanyLabel(talent.company) || '未设置' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">职称</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value">{{ getTitleLabel(talent.title) || '未设置' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">学历</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <div class="education-cell">
                <span class="compare-value">{{ getEducationLabel(talent.education) || '未设置' }}</span>
                <a-tag
                    v-if="talent.universityCategory === '985' || talent.universityCategory === '211'"
                    color="#0066b3"
                    size="small"
                    class="inline-tag"
                >
                  {{ talent.universityCategory === '985' ? '985' : '211' }}
                </a-tag>
              </div>
            </td>
          </tr>
          <tr v-if="showDimension('basic')">
            <td class="dimension-name">专业领域</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value">{{ getDomainLabel(talent.primaryDomain) || '未设置' }}</span>
            </td>
          </tr>

          <!-- 人才标签 -->
          <tr class="dimension-group" v-if="showDimension('talent')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <TagOutlined style="margin-right: 8px;" />
              人才标签
            </td>
          </tr>
          <tr v-if="showDimension('talent')">
            <td class="dimension-name">人才层级</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <a-tag :color="getLevelColor(talent.talentLevel)" size="small" class="yn-grid-tag">
                {{ getLevelLabel(talent.talentLevel) }}
              </a-tag>
            </td>
          </tr>
          <tr v-if="showDimension('talent')">
            <td class="dimension-name">人才类型</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value">{{ getTalentTypeLabel(talent.talentType) || '未设置' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('talent')">
            <td class="dimension-name">技术专家等级</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value">{{ getTechnicalExpertLevelLabel(talent.technicalExpertLevel) || '未设置' }}</span>
            </td>
          </tr>

          <!-- 能力与成果 -->
          <tr class="dimension-group" v-if="showDimension('achievement')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <RiseOutlined style="margin-right: 8px;" />
              能力与成果
            </td>
          </tr>
          <tr v-if="showDimension('achievement')">
            <td class="dimension-name">评估总分</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <div class="score-cell">
                <a-progress
                    :percent="talent.evaluationScore || 0"
                    :stroke-color="getScoreColor(talent.evaluationScore)"
                    size="small"
                    :show-info="false"
                    style="width: 60px;"
                    class="yn-grid-progress"
                />
                <span class="score-value">{{ talent.evaluationScore || '未评估' }}</span>
              </div>
            </td>
          </tr>
          <tr v-if="showDimension('achievement')">
            <td class="dimension-name">专利数量</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value" style="color: #0066b3; font-weight: 600;">{{ talent.patentCount || 0 }}项</span>
            </td>
          </tr>
          <tr v-if="showDimension('achievement')">
            <td class="dimension-name">论文数量</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value" style="color: #0066b3; font-weight: 600;">{{ talent.paperCount || 0 }}篇</span>
            </td>
          </tr>
          <tr v-if="showDimension('achievement')">
            <td class="dimension-name">主持项目</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value" style="color: #0066b3; font-weight: 600;">{{ talent.hostedProjectsCount || 0 }}个</span>
            </td>
          </tr>
          <tr v-if="showDimension('achievement')">
            <td class="dimension-name">技术标准</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value" style="color: #0066b3; font-weight: 600;">{{ talent.standardsCount || 0 }}项</span>
            </td>
          </tr>

          <!-- 发展与社会关系 -->
          <tr class="dimension-group" v-if="showDimension('development')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <ShareAltOutlined style="margin-right: 8px;" />
              发展与社会关系
            </td>
          </tr>
          <tr v-if="showDimension('development')">
            <td class="dimension-name">导师</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value">{{ talent.mentor || '未设置' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('development')">
            <td class="dimension-name">所属团队</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <span class="compare-value">{{ talent.team || '未设置' }}</span>
            </td>
          </tr>
          <tr v-if="showDimension('development')">
            <td class="dimension-name">兴趣方向</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <div class="skills-cell">
                <a-tag
                    v-for="(tag, tagIndex) in (talent.interestTags || []).slice(0, 3)"
                    :key="tagIndex"
                    size="small"
                    class="yn-grid-tag skill-tag"
                >
                  {{ tag }}
                </a-tag>
                <span v-if="talent.interestTags && talent.interestTags.length > 3" class="more-skills">
                  +{{ talent.interestTags.length - 3 }}
                </span>
              </div>
            </td>
          </tr>

          <!-- 人才荣誉 -->
          <tr class="dimension-group" v-if="showDimension('honor')">
            <td colspan="6" class="group-header" style="background: #e6f0ff; color: #0066b3;">
              <StarOutlined style="margin-right: 8px;" />
              人才荣誉
            </td>
          </tr>
          <tr v-if="showDimension('honor')">
            <td class="dimension-name">获得荣誉</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <div class="honor-cell">
                <template v-if="talent.talentHonors && talent.talentHonors.length > 0">
                  <span class="honor-text">{{ getFirstHonor(talent.talentHonors) }}</span>
                  <span v-if="getHonorCount(talent.talentHonors) > 1" class="more-honors">
                    +{{ getHonorCount(talent.talentHonors) - 1 }}
                  </span>
                </template>
                <span v-else class="no-data">无荣誉</span>
              </div>
            </td>
          </tr>
          <tr v-if="showDimension('honor')">
            <td class="dimension-name">支持计划</td>
            <td
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                :class="`talent-cell-${index}`"
            >
              <div class="support-plan-cell">
                <span class="plan-text">{{ talent.talentSupportPlan ? getFirstSupportPlan(talent.talentSupportPlan) : '无支持计划' }}</span>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 对比分析结果 -->
    <div class="analysis-results yn-grid-card" v-if="comparisonData.length >= 2">
      <div class="analysis-header">
        <h3 style="color: #0066b3;">对比分析结果</h3>
      </div>

      <div class="analysis-content">
        <!-- 雷达图 -->
        <div class="radar-chart-section" v-if="comparisonData.length >= 2">
          <h4 style="color: #0066b3;">能力雷达图对比</h4>
          <div id="radarChart" style="width: 100%; height: 400px;"></div>
        </div>

        <!-- 综合评分 -->
        <div class="score-summary">
          <h4 style="color: #0066b3;">综合评分对比</h4>
          <div class="score-bars">
            <div
                v-for="(talent, index) in comparisonData"
                :key="talent.id"
                class="score-bar-item"
            >
              <div class="score-bar-label">
                <div class="talent-name" :style="{ color: getTalentColor(index) }">{{ talent.name }}</div>
                <div class="score-value" style="color: #0066b3;">{{ calculateTotalScore(talent) }}/100</div>
              </div>
              <a-progress
                  :percent="calculateTotalScore(talent)"
                  :stroke-color="getScoreColor(calculateTotalScore(talent))"
                  class="yn-grid-progress"
              />
            </div>
          </div>
        </div>

        <!-- 推荐建议 -->
        <div class="recommendations" v-if="analysisData.recommendations.length > 0">
          <h4 style="color: #0066b3;">推荐建议</h4>
          <div class="recommendation-list">
            <a-card
                v-for="(recommendation, index) in analysisData.recommendations"
                :key="index"
                class="recommendation-card yn-grid-card"
                :style="{ borderLeft: `4px solid ${recommendation.color}` }"
            >
              <template #title>
                <div style="display: flex; align-items: center; gap: 8px">
                  <StarOutlined :style="{ color: recommendation.color }" />
                  <span style="color: #333;">{{ recommendation.title }}</span>
                </div>
              </template>
              <p style="color: #666;">{{ recommendation.content }}</p>
              <div class="recommended-talents">
                <span style="margin-right: 8px; color: #999;">推荐人员:</span>
                <a-tag
                    v-for="talentId in recommendation.talentIds"
                    :key="talentId"
                    color="#0066b3"
                    class="yn-grid-tag"
                >
                  {{ getTalentById(talentId)?.name }}
                </a-tag>
              </div>
            </a-card>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加人员模态框 -->
    <a-modal
        v-model:open="showAddModal"
        title="添加对比人员"
        width="1000px"
        :footer="null"
        class="yn-grid-modal add-talent-modal"
        :destroy-on-close="true"
        :mask-closable="false"
    >
      <div class="talent-search-modal">
        <div class="modal-search-header">
          <div class="search-mode-container">
            <a-radio-group v-model:value="searchModalState.searchMode" button-style="solid" size="small" class="yn-grid-mode-switch">
              <a-radio-button value="quick" class="mode-btn">
                <SearchOutlined />
                快速搜索
              </a-radio-button>
              <a-radio-button value="advanced" class="mode-btn">
                <FilterOutlined />
                高级搜索
              </a-radio-button>
            </a-radio-group>
          </div>

          <div v-if="searchModalState.searchMode === 'quick'" class="modal-quick-search">
            <a-input-search
                v-model:value="searchModalState.searchKeyword"
                placeholder="搜索人才姓名、职位、专业领域..."
                style="width: 320px"
                @search="handleModalSearch"
                allow-clear
                @clear="handleModalSearchClear"
                class="yn-grid-search-input"
            >
              <template #enterButton>
                <a-button type="primary" class="yn-grid-btn-primary">
                  <SearchOutlined />
                </a-button>
              </template>
            </a-input-search>
          </div>

          <div v-else class="modal-advanced-filters">
            <div class="filter-row">
              <a-select
                  v-model:value="searchModalState.filters.company"
                  placeholder="所属单位"
                  style="width: 200px"
                  allow-clear
                  @change="handleModalFilterChange"
                  class="yn-grid-select"
              >
                <a-select-option value="yunnan_grid">云南电网有限责任公司</a-select-option>
                <a-select-option value="electric_power_research">云南电网电力科学研究院</a-select-option>
                <a-select-option value="kunming">昆明供电局</a-select-option>
                <a-select-option value="qujing">曲靖供电局</a-select-option>
                <a-select-option value="yuxi">玉溪供电局</a-select-option>
              </a-select>

              <a-select
                  v-model:value="searchModalState.filters.education"
                  placeholder="学历"
                  style="width: 120px; margin-left: 10px"
                  allow-clear
                  @change="handleModalFilterChange"
                  class="yn-grid-select"
              >
                <a-select-option value="doctor">博士</a-select-option>
                <a-select-option value="master">硕士</a-select-option>
                <a-select-option value="bachelor">本科</a-select-option>
                <a-select-option value="college">大专</a-select-option>
              </a-select>

              <a-select
                  v-model:value="searchModalState.filters.talentLevel"
                  placeholder="人才层级"
                  style="width: 120px; margin-left: 10px"
                  allow-clear
                  @change="handleModalFilterChange"
                  class="yn-grid-select"
              >
                <a-select-option value="strategic">战略级</a-select-option>
                <a-select-option value="leadership">领军级</a-select-option>
                <a-select-option value="pinnacle">拔尖级</a-select-option>
                <a-select-option value="backbone">骨干</a-select-option>
              </a-select>

              <a-button
                  type="link"
                  @click="resetModalFilters"
                  style="margin-left: 10px"
                  class="reset-filters-btn"
              >
                <RedoOutlined />
                重置
              </a-button>
            </div>
          </div>
        </div>

        <div class="modal-results-info" v-if="modalFilteredTalents.length > 0">
          <span style="color: #0066b3;">找到 {{ modalFilteredTalents.length }} 位人才</span>
          <span style="color: #666; margin-left: 12px;">
            已选择 <span style="color: #0066b3; font-weight: 500;">{{ searchModalState.selectedTalents.length }}</span> 人
            <span v-if="availableSlots <= 0" style="color: #ff4d4f; margin-left: 8px;">
              (对比列表已满，无法添加更多)
            </span>
            <span v-else-if="searchModalState.selectedTalents.length > availableSlots" style="color: #ff4d4f; margin-left: 8px;">
              (最多还能选择{{ availableSlots }}人)
            </span>
            <span v-else style="color: #52c41a; margin-left: 8px;">
              (还可选择{{ availableSlots - searchModalState.selectedTalents.length }}人)
            </span>
          </span>
        </div>

        <div class="modal-talents-list">
          <a-table
              :data-source="modalDisplayedTalents"
              :columns="modalTableColumns"
              :pagination="{
                current: searchModalState.currentPage,
                pageSize: searchModalState.pageSize,
                total: modalFilteredTalents.length,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条结果`
              }"
              row-key="id"
              size="middle"
              :row-class-name="getModalRowClassName"
              class="modal-talents-table"
              @change="handleModalTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'selection'">
                <div class="modal-selection-control">
                  <template v-if="isInComparisonList(record.id)">
                    <a-tag color="#0066b3" size="small">已在对比</a-tag>
                  </template>
                  <template v-else-if="availableSlots <= 0">
                    <a-tooltip title="对比列表已满（最多5人）">
                      <a-checkbox disabled />
                    </a-tooltip>
                  </template>
                  <template v-else-if="searchModalState.selectedTalents.length >= availableSlots">
                    <a-tooltip :title="`最多还能选择${availableSlots}人`">
                      <a-checkbox disabled />
                    </a-tooltip>
                  </template>
                  <template v-else>
                    <a-checkbox
                        :checked="searchModalState.selectedTalents.includes(record.id)"
                        @change="(e) => handleModalSelectTalent(record.id, e.target.checked)"
                    />
                  </template>
                </div>
              </template>

              <template v-if="column.key === 'name'">
                <div class="modal-talent-name">
                  <div class="avatar-small" :style="getModalAvatarStyle(record)">
                    {{ record.name?.charAt(0) || '?' }}
                  </div>
                  <div class="name-info">
                    <div class="name" style="color: #0066b3; font-weight: 500;">{{ record.name }}</div>
                    <div class="employee-id">#{{ record.employeeId }}</div>
                  </div>
                </div>
              </template>

              <template v-if="column.key === 'position'">
                <span>{{ record.position || '未设置' }}</span>
              </template>

              <template v-if="column.key === 'company'">
                <span>{{ getCompanyLabel(record.company) || '未设置' }}</span>
              </template>

              <template v-if="column.key === 'talentLevel'">
                <a-tag :color="getLevelColor(record.talentLevel)" size="small">
                  {{ getLevelLabel(record.talentLevel) }}
                </a-tag>
              </template>

              <template v-if="column.key === 'evaluationScore'">
                <div class="score-cell">
                  <span class="score-value">{{ record.evaluationScore || '未评估' }}</span>
                </div>
              </template>
            </template>
          </a-table>
        </div>

        <div class="modal-actions">
          <div class="selected-summary">
            <span v-if="searchModalState.selectedTalents.length > 0">
              已选择 <span style="color: #0066b3; font-weight: 500;">{{ searchModalState.selectedTalents.length }}</span> 位人才
              <span v-if="availableSlots <= 0" style="color: #ff4d4f; margin-left: 8px;">
                (无法添加，对比列表已满)
              </span>
              <span v-else-if="searchModalState.selectedTalents.length > availableSlots" style="color: #ff4d4f; margin-left: 8px;">
                (最多只能添加{{ availableSlots }}人)
              </span>
              <span v-else style="color: #52c41a; margin-left: 8px;">
                (将添加到对比列表)
              </span>
            </span>
            <span v-else style="color: #999;">请选择要添加的人才</span>
          </div>

          <div class="action-buttons">
            <a-button @click="handleModalCancel" class="yn-grid-btn-secondary">
              取消
            </a-button>
            <a-button
                type="primary"
                @click="handleModalAddSelected"
                :disabled="searchModalState.selectedTalents.length === 0 || availableSlots <= 0 || searchModalState.selectedTalents.length > availableSlots"
                class="yn-grid-btn-primary"
                :loading="searchModalState.loading"
            >
              添加选中人才 ({{ searchModalState.selectedTalents.length }})
            </a-button>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- 空状态提示 -->
    <div v-if="comparisonData.length === 0" class="empty-comparison-state yn-grid-card">
      <div class="empty-illustration">
        <BarChartOutlined style="font-size: 80px; color: #0066b3; opacity: 0.3;" />
      </div>
      <h3 class="empty-title" style="color: #333;">暂无对比人员</h3>
      <p class="empty-description" style="color: #666;">
        请从搜索结果中添加人才进行对比分析
      </p>
      <div class="empty-actions">
        <a-button @click="handleAddTalent" class="yn-grid-btn-primary">
          <PlusOutlined />
          添加对比人员
        </a-button>
        <a-button @click="handleBack" style="margin-left: 12px;" class="yn-grid-btn-secondary">
          返回搜索页面
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch, nextTick, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { useComparisonStore } from '@/stores/comparison'
import * as echarts from 'echarts'
import {
  ArrowLeftOutlined,
  PlusOutlined,
  SettingOutlined,
  ExportOutlined,
  SaveOutlined,
  DeleteOutlined,
  CloseOutlined,
  StarOutlined,
  TeamOutlined,
  FileTextOutlined,
  RiseOutlined,
  TagOutlined,
  UserOutlined,
  SearchOutlined,
  FilterOutlined,
  RedoOutlined,
  BarChartOutlined,
  CrownOutlined,
  ShareAltOutlined
} from '@ant-design/icons-vue'
import HeaderComponent from '@/components/HeaderComponent.vue'
import { talentApi } from '@/apis/talent_api'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const comparisonStore = useComparisonStore()

// ============== 响应式状态 ==============
const loading = ref(false)
const showAddModal = ref(false)
const showAllDimensions = ref(false)

// 对比数据 - 直接从comparisonStore获取
const comparisonData = computed(() => {
  return comparisonStore.comparisonList
})

// 分析结果数据
const analysisData = reactive({
  radarData: null,
  scores: [],
  recommendations: []
})

// 维度选择
const selectedDimensions = ref([
  'basic', 'talent', 'achievement', 'development', 'honor'
])

// 添加人才模态框状态
const searchModalState = reactive({
  loading: false,
  searchMode: 'quick',
  searchKeyword: '',
  filters: {
    company: null,
    education: null,
    talentLevel: null
  },
  currentPage: 1,
  pageSize: 10,
  selectedTalents: [],
  allTalents: []
})

// ============== 常量定义 ==============
// 维度选项
const dimensionOptions = [
  { label: '基本信息', value: 'basic' },
  { label: '人才标签', value: 'talent' },
  { label: '能力与成果', value: 'achievement' },
  { label: '发展与社会关系', value: 'development' },
  { label: '人才荣誉', value: 'honor' }
]

// 人才颜色方案
const talentColors = [
  { primary: '#0066b3', light: '#e6f0ff', avatar: '#0066b3' },
  { primary: '#0088cc', light: '#e6f7ff', avatar: '#0088cc' },
  { primary: '#66a3ff', light: '#f0f5ff', avatar: '#66a3ff' },
  { primary: '#99c2ff', light: '#f8fafc', avatar: '#99c2ff' },
  { primary: '#004d99', light: '#e6e6ff', avatar: '#004d99' }
]

// 模态框表格列定义
const modalTableColumns = [
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
    title: '职位',
    key: 'position',
    width: 150
  },
  {
    title: '所属单位',
    key: 'company',
    width: 180
  },
  {
    title: '人才层级',
    key: 'talentLevel',
    width: 100
  },
  {
    title: '评估分',
    key: 'evaluationScore',
    width: 100
  }
]

// ============== 计算属性 ==============
// 可用名额计算
const availableSlots = computed(() => {
  return 5 - comparisonData.value.length
})

// 模态框过滤后的人才
const modalFilteredTalents = computed(() => {
  let filtered = searchModalState.allTalents

  // 排除已经在对比列表中的人才
  const comparisonIds = comparisonData.value.map(t => t.id)
  filtered = filtered.filter(talent => !comparisonIds.includes(talent.id))

  // 关键词搜索
  if (searchModalState.searchKeyword) {
    const keyword = searchModalState.searchKeyword.toLowerCase()
    filtered = filtered.filter(talent =>
        talent.name?.toLowerCase().includes(keyword) ||
        talent.position?.toLowerCase().includes(keyword) ||
        talent.primaryDomain?.toLowerCase().includes(keyword) ||
        talent.employeeId?.toLowerCase().includes(keyword)
    )
  }

  // 单位筛选
  if (searchModalState.filters.company) {
    filtered = filtered.filter(talent => talent.company === searchModalState.filters.company)
  }

  // 学历筛选
  if (searchModalState.filters.education) {
    filtered = filtered.filter(talent => talent.education === searchModalState.filters.education)
  }

  // 人才层级筛选
  if (searchModalState.filters.talentLevel) {
    filtered = filtered.filter(talent => talent.talentLevel === searchModalState.filters.talentLevel)
  }

  return filtered
})

// 模态框显示的人才（分页后）
const modalDisplayedTalents = computed(() => {
  const start = (searchModalState.currentPage - 1) * searchModalState.pageSize
  const end = start + searchModalState.pageSize
  return modalFilteredTalents.value.slice(start, end)
})

// ============== 工具函数 ==============
// 获取人才颜色
const getTalentColor = (index) => {
  return talentColors[index % talentColors.length].primary
}

// 获取头像样式
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
    background: colors[colorIndex],
    color: 'white'
  }
}

// 获取模态框头像样式
const getModalAvatarStyle = (talent) => {
  const colors = [
    'linear-gradient(135deg, #0066b3, #0088cc)',
    'linear-gradient(135deg, #0066b3, #66a3ff)',
    'linear-gradient(135deg, #0088cc, #99c2ff)',
    'linear-gradient(135deg, #004d99, #0066b3)'
  ]

  const charCode = talent.name?.charCodeAt(0) || 0
  const colorIndex = charCode % colors.length

  return {
    background: colors[colorIndex],
    color: 'white'
  }
}

// 获取标签颜色
const getTagColor = (index) => {
  const tagColors = ['#0066b3', '#0088cc', '#66a3ff', '#99c2ff', '#004d99']
  return tagColors[index % tagColors.length]
}

// 显示维度检查
const showDimension = (dimension) => {
  return selectedDimensions.value.includes(dimension)
}

// 格式化函数
const getCompanyLabel = (company) => {
  const companies = {
    yunnan_grid: '云南电网有限责任公司',
    electric_power_research: '云南电网电力科学研究院',
    kunming: '昆明供电局',
    qujing: '曲靖供电局',
    yuxi: '玉溪供电局'
  }
  return companies[company] || company
}

const getTitleLabel = (title) => {
  const titles = {
    senior_engineer: '高级工程师',
    engineer: '工程师',
    assistant_engineer: '助理工程师',
    technician: '技师'
  }
  return titles[title] || title
}

const getEducationLabel = (education) => {
  const educationMap = {
    doctor: '博士',
    master: '硕士',
    bachelor: '本科',
    college: '大专'
  }
  return educationMap[education] || education
}

const getDomainLabel = (domain) => {
  const domains = {
    smart_transmission: '智能输变电',
    power_ai: '电力人工智能',
    new_energy: '新能源',
    power_system: '电力系统'
  }
  return domains[domain] || domain
}

const getTalentTypeLabel = (type) => {
  const types = {
    technical_expert: '技术专家',
    skilled_expert: '技能专家',
    young_talent: '青年托举人才'
  }
  return types[type] || type
}

const getTechnicalExpertLevelLabel = (level) => {
  const levels = {
    national: '国家级',
    provincial: '省部级',
    company: '公司级'
  }
  return levels[level] || level
}

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

const getFirstHonor = (honors) => {
  if (!honors) return ''
  const honorList = honors.split(';')
  return honorList[0]?.trim() || ''
}

const getHonorCount = (honors) => {
  if (!honors) return 0
  return honors.split(';').length
}

const getFirstSupportPlan = (plans) => {
  if (!plans) return ''
  const planList = plans.split(';')
  return planList[0]?.trim() || ''
}

const getTalentById = (id) => {
  return comparisonData.value.find(t => t.id === id)
}

const isInComparisonList = (talentId) => {
  return comparisonData.value.some(item => item.id === talentId)
}

// ============== 业务函数 ==============
const calculateTotalScore = (talent) => {
  let score = 0
  let factors = 0

  // 评估分
  if (talent.evaluationScore) {
    score += talent.evaluationScore
    factors++
  }

  // 专利加分
  if (talent.patentCount) {
    score += Math.min(talent.patentCount * 2, 20)
    factors++
  }

  // 论文加分
  if (talent.paperCount) {
    score += Math.min(talent.paperCount * 1.5, 15)
    factors++
  }

  // 项目加分
  if (talent.hostedProjectsCount) {
    score += Math.min(talent.hostedProjectsCount * 3, 15)
    factors++
  }

  // 人才层级加分
  const levelBonus = {
    strategic: 15,
    leadership: 10,
    pinnacle: 5,
    backbone: 0
  }
  if (talent.talentLevel) {
    score += levelBonus[talent.talentLevel] || 0
    factors++
  }

  return factors > 0 ? Math.round(score / factors) : 0
}

// ============== 事件处理函数 ==============
const handleBack = () => {
  comparisonStore.clearComparison()

  router.back()
}

const handleAddTalent = () => {
  if (comparisonData.value.length >= 5) {
    message.warning('对比列表最多支持5位人才')
    return
  }
  showAddModal.value = true
}

const handleRemoveTalent = async (talentId) => {
  try {
    loading.value = true

    // 从对比store中移除
    comparisonStore.removeFromComparison(talentId)

    message.success('已移除对比人员')
    await fetchAnalysisData()
  } catch (error) {
    console.error('移除失败:', error)
    message.error('移除失败')
  } finally {
    loading.value = false
  }
}

const handleCompareActions = ({ key }) => {
  switch (key) {
    case 'export':
      exportComparison()
      break
    case 'save':
      saveComparison()
      break
    case 'clear':
      clearComparison()
      break
  }
}

const exportComparison = async () => {
  try {
    // TODO: 调用导出接口
    message.info('导出功能开发中')
  } catch (error) {
    console.error('导出失败:', error)
    message.error('导出失败')
  }
}

const saveComparison = async () => {
  try {
    // TODO: 调用保存接口
    message.info('保存对比方案功能开发中')
  } catch (error) {
    console.error('保存失败:', error)
    message.error('保存失败')
  }
}

const clearComparison = () => {
  Modal.confirm({
    title: '清空对比列表',
    content: '确定要清空所有对比人员吗？',
    okText: '清空',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        comparisonStore.clearComparison()
        message.success('对比列表已清空')
      } catch (error) {
        console.error('清空失败:', error)
        message.error('清空失败')
      }
    }
  })
}

// ============== 模态框相关函数 ==============
const loadModalTalents = async () => {
  searchModalState.loading = true
  try {
    const data = await talentApi.getTalents()
    let talentList = []

    if (data.talents) {
      talentList = data.talents.map(talent => ({
        ...talent,
        interestTags: Array.isArray(talent.interestTags) ? talent.interestTags : [],
        hostedProjectsCount: talent.hostedProjectsCount || 0,
        patentCount: talent.patentCount || 0,
        paperCount: talent.paperCount || 0,
        standardsCount: talent.standardsCount || 0,
        evaluationScore: talent.evaluationScore || null
      }))
    }

    searchModalState.allTalents = talentList
  } catch (error) {
    console.error('加载人才列表失败:', error)
    message.error('加载人才列表失败')
  } finally {
    searchModalState.loading = false
  }
}

const handleModalSearch = () => {
  searchModalState.currentPage = 1
}

const handleModalSearchClear = () => {
  searchModalState.searchKeyword = ''
  searchModalState.currentPage = 1
}

const handleModalFilterChange = () => {
  searchModalState.currentPage = 1
}

const resetModalFilters = () => {
  searchModalState.filters = {
    company: null,
    education: null,
    talentLevel: null
  }
  searchModalState.searchKeyword = ''
  searchModalState.currentPage = 1
}

const handleModalSelectTalent = (talentId, checked) => {
  // 检查对比列表是否已满
  if (checked && searchModalState.selectedTalents.length >= availableSlots.value) {
    message.warning(`对比列表最多支持5人，当前已有${comparisonData.value.length}人，只能再选择${availableSlots.value}人`)
    return
  }

  const index = searchModalState.selectedTalents.indexOf(talentId)
  if (checked && index === -1) {
    searchModalState.selectedTalents.push(talentId)
  } else if (!checked && index > -1) {
    searchModalState.selectedTalents.splice(index, 1)
  }
}

const handleModalAddSelected = async () => {
  if (searchModalState.selectedTalents.length === 0) {
    message.warning('请选择要添加的人才')
    return
  }

  // 检查是否超过最大限制
  if (searchModalState.selectedTalents.length > availableSlots.value) {
    message.warning(`对比列表最多支持5人，当前已有${comparisonData.value.length}人，只能再添加${availableSlots.value}人`)
    return
  }

  const selectedTalents = searchModalState.allTalents.filter(talent =>
      searchModalState.selectedTalents.includes(talent.id)
  )

  try {
    loading.value = true

    // 添加到对比store
    selectedTalents.forEach(talent => {
      if (!isInComparisonList(talent.id)) {
        comparisonStore.addToComparison(talent)
      }
    })

    message.success(`已添加 ${selectedTalents.length} 位人才到对比列表`)

    // 重置模态框状态
    searchModalState.selectedTalents = []
    searchModalState.currentPage = 1
    searchModalState.searchKeyword = ''
    resetModalFilters()

    // 关闭模态框
    showAddModal.value = false

    // 重新分析数据
    await fetchAnalysisData()
  } catch (error) {
    console.error('添加失败:', error)
    message.error('添加失败')
  } finally {
    loading.value = false
  }
}

const handleModalCancel = () => {
  showAddModal.value = false
}

const handleModalTableChange = (pagination) => {
  searchModalState.currentPage = pagination.current
  searchModalState.pageSize = pagination.pageSize
}

const getModalRowClassName = (record) => {
  if (isInComparisonList(record.id)) {
    return 'in-comparison-row'
  }
  return ''
}

// ============== API调用函数 ==============
const fetchAnalysisData = async () => {
  if (comparisonData.value.length < 2) {
    analysisData.recommendations = []
    return
  }

  try {
    // 生成分析数据
    analysisData.scores = comparisonData.value.map(talent => ({
      id: talent.id,
      name: talent.name,
      score: calculateTotalScore(talent)
    }))

    // 生成推荐建议
    analysisData.recommendations = [
      {
        title: '最适合晋升人选',
        content: '综合评估分数最高，具备较强的专业能力和成果产出',
        talentIds: comparisonData.value
            .sort((a, b) => calculateTotalScore(b) - calculateTotalScore(a))
            .slice(0, 1)
            .map(t => t.id),
        color: '#0066b3'
      },
      {
        title: '最佳项目负责人',
        content: '项目管理经验丰富，专利和论文成果突出，适合负责重点项目',
        talentIds: comparisonData.value
            .filter(t => (t.hostedProjectsCount >= 3 || t.patentCount >= 5))
            .slice(0, 2)
            .map(t => t.id),
        color: '#0088cc'
      },
      {
        title: '重点培养对象',
        content: '青年人才，发展潜力大，建议纳入重点培养计划',
        talentIds: comparisonData.value
            .filter(t => t.talentType === 'young_talent' || (t.education === 'master' || t.education === 'doctor'))
            .slice(0, 2)
            .map(t => t.id),
        color: '#66a3ff'
      }
    ]

    // 初始化雷达图
    nextTick(() => {
      initRadarChart()
    })
  } catch (error) {
    console.error('获取分析数据失败:', error)
  }
}

// ============== 图表相关 ==============
let radarChart = null
const initRadarChart = () => {
  if (comparisonData.value.length < 2) return

  const chartDom = document.getElementById('radarChart')
  if (!chartDom) return

  if (radarChart) {
    radarChart.dispose()
  }

  radarChart = echarts.init(chartDom)

  const indicator = [
    { name: '专业能力', max: 100 },
    { name: '创新能力', max: 100 },
    { name: '项目经验', max: 100 },
    { name: '学术成果', max: 100 },
    { name: '发展潜力', max: 100 },
    { name: '团队协作', max: 100 }
  ]

  const seriesData = comparisonData.value.map((talent, index) => ({
    name: talent.name,
    value: [
      talent.evaluationScore || Math.random() * 80 + 20,
      (talent.patentCount || 0) * 10 + (talent.standardsCount || 0) * 5,
      (talent.hostedProjectsCount || 0) * 15 + (talent.participatedProjectsCount || 0) * 5,
      (talent.paperCount || 0) * 8 + (talent.standardsCount || 0) * 4,
      70, // 发展潜力 - 模拟数据
      75  // 团队协作 - 模拟数据
    ].map(v => Math.min(v, 100)),
    itemStyle: {
      color: talentColors[index % talentColors.length].primary
    }
  }))

  const option = {
    title: {
      text: '能力维度对比',
      left: 'center',
      textStyle: {
        color: '#0066b3',
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      data: comparisonData.value.map(t => t.name),
      bottom: 10,
      textStyle: {
        color: '#333'
      }
    },
    radar: {
      indicator: indicator,
      center: ['50%', '50%'],
      radius: '65%',
      shape: 'polygon',
      splitNumber: 4,
      axisLine: {
        lineStyle: {
          color: '#e6f0ff'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e6f0ff'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(0,102,179,0.05)', 'rgba(0,102,179,0.02)']
        }
      },
      name: {
        textStyle: {
          color: '#333'
        }
      }
    },
    series: [{
      type: 'radar',
      data: seriesData,
      emphasis: {
        lineStyle: {
          width: 4
        },
        areaStyle: {
          opacity: 0.5
        }
      },
      areaStyle: {
        opacity: 0.3
      },
      lineStyle: {
        width: 2
      }
    }]
  }

  radarChart.setOption(option)

  // 响应式调整
  window.addEventListener('resize', handleChartResize)
}

const handleChartResize = () => {
  if (radarChart) {
    radarChart.resize()
  }
}

// ============== 生命周期钩子 ==============
onMounted(async () => {
  await fetchAnalysisData()

  // 如果对比列表为空，尝试从路由参数获取
  if (comparisonData.value.length === 0 && route.query.talentIds) {
    const talentIds = route.query.talentIds.split(',')
    // 可以在这里调用API获取人才数据并添加到对比
  }
})

onUnmounted(() => {
  if (radarChart) {
    radarChart.dispose()
    radarChart = null
  }
  window.removeEventListener('resize', handleChartResize)
})

// ============== 监听器 ==============
watch(showAddModal, (newVal) => {
  if (newVal) {
    // 模态框打开时加载数据
    loadModalTalents()
  } else {
    // 模态框关闭时重置状态
    searchModalState.selectedTalents = []
    searchModalState.currentPage = 1
    searchModalState.searchKeyword = ''
    resetModalFilters()
  }
})

watch(comparisonData, (newVal) => {
  if (newVal.length >= 2) {
    setTimeout(fetchAnalysisData, 100)
  } else {
    // 清空分析数据
    analysisData.recommendations = []
    analysisData.scores = []

    // 销毁图表
    if (radarChart) {
      radarChart.dispose()
      radarChart = null
    }
  }
}, { deep: true })
</script>

<style lang="less" scoped>
.talent-comparison-container {
  padding: 0;
  background: #f8fafc;
}

.compare-actions {
  display: flex;
  align-items: center;
  gap: 12px;

  .max-limit-badge {
    display: inline-block;
    background: #ff4d4f;
    color: white;
    font-size: 11px;
    padding: 1px 6px;
    border-radius: 10px;
    margin-left: 6px;
  }
}

.yn-grid-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e6f0ff;
  box-shadow: 0 2px 8px rgba(0, 102, 179, 0.06);
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 102, 179, 0.1);
  }
}

.compare-participants {
  padding: 20px;
  margin: 20px;

  .participants-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 18px;
    }

    .add-participant-link {
      color: #0066b3;

      &:hover {
        color: #0088cc;
      }

      &.disabled-btn {
        color: #999;
        cursor: not-allowed;

        &:hover {
          color: #999;
        }
      }
    }
  }

  .participants-list {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;

    .participant-card {
      display: flex;
      flex-direction: column;
      padding: 16px;
      border-radius: 8px;
      width: 280px;
      position: relative;
      transition: all 0.3s;
      border: 2px solid transparent;

      .card-header {
        display: flex;
        align-items: flex-start;
        margin-bottom: 12px;

        .participant-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          font-weight: 600;
          margin-right: 12px;
          flex-shrink: 0;
        }

        .participant-info {
          flex: 1;
          min-width: 0;

          .info-row {
            display: flex;
            align-items: center;
            margin-bottom: 4px;

            &:last-child {
              margin-bottom: 0;
            }

            .participant-name {
              font-weight: 600;
              font-size: 16px;
              margin-right: 8px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .participant-position {
              font-weight: 500;
              font-size: 14px;
              color: #333;
              margin-right: 8px;
            }

            .participant-department {
              font-size: 12px;
              color: #666;
            }
          }
        }

        .remove-btn {
          position: absolute;
          top: 8px;
          right: 8px;
          opacity: 0.5;
          color: #999;

          &:hover {
            opacity: 1;
            color: #ff4d4f;
          }
        }
      }

      .card-tags {
        padding-top: 12px;
        border-top: 1px solid #f0f0f0;

        .tags-section {
          display: flex;
          align-items: flex-start;
          margin-bottom: 8px;

          &:last-child {
            margin-bottom: 0;
          }

          .tags-label {
            font-size: 12px;
            color: #999;
            min-width: 60px;
            line-height: 24px;
          }

          .tags-container {
            flex: 1;
            display: flex;
            flex-wrap: wrap;
            gap: 4px;

            .talent-tag {
              margin: 0;
              line-height: 20px;
            }

            .more-tags {
              font-size: 12px;
              color: #999;
              line-height: 24px;
              margin-left: 4px;
            }
          }
        }
      }

      &.participant-card-0 {
        border-color: #0066b3;
        background: linear-gradient(135deg, rgba(0,102,179,0.02), rgba(0,102,179,0.05));
      }

      &.participant-card-1 {
        border-color: #0088cc;
        background: linear-gradient(135deg, rgba(0,136,204,0.02), rgba(0,136,204,0.05));
      }

      &.participant-card-2 {
        border-color: #66a3ff;
        background: linear-gradient(135deg, rgba(102,163,255,0.02), rgba(102,163,255,0.05));
      }

      &.participant-card-3 {
        border-color: #99c2ff;
        background: linear-gradient(135deg, rgba(153,194,255,0.02), rgba(153,194,255,0.05));
      }

      &.participant-card-4 {
        border-color: #004d99;
        background: linear-gradient(135deg, rgba(0,77,153,0.02), rgba(0,77,153,0.05));
      }

      &:hover {
        box-shadow: 0 4px 16px rgba(0, 102, 179, 0.15);
        transform: translateY(-2px);
      }
    }

    .add-participant-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      background: #f8fafc;
      border: 2px dashed #e6f0ff;
      border-radius: 8px;
      width: 280px;
      cursor: pointer;
      transition: all 0.3s;

      .add-text {
        margin-top: 8px;
        font-size: 14px;
      }

      .add-subtext {
        font-size: 12px;
        margin-top: 4px;
      }

      &:hover {
        border-color: #0066b3;
        background: #e6f0ff;

        .add-text {
          color: #0066b3;
        }
      }
    }
  }
}

.compare-dimensions {
  padding: 20px;
  margin: 0 20px 20px;

  .dimensions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 18px;
    }
  }

  .dimensions-checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;

    :deep(.ant-checkbox-wrapper) {
      margin: 0;
      color: #333;

      &:hover {
        .ant-checkbox-inner {
          border-color: #0066b3;
        }
      }
    }

    :deep(.ant-checkbox-checked .ant-checkbox-inner) {
      background: #0066b3;
      border-color: #0066b3;
    }

    :deep(.ant-checkbox-disabled) {
      .ant-checkbox-inner {
        background: #f5f5f5;
        border-color: #d9d9d9;
      }

      & + span {
        color: #999;
      }
    }
  }
}

.yn-grid-switch {
  :deep(.ant-switch-checked) {
    background: #0066b3;
  }
}

.compare-table-container {
  padding: 20px;
  margin: 0 20px 20px;
  overflow-x: auto;

  .table-wrapper {
    min-width: 800px;
  }

  .compare-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;

    th, td {
      padding: 12px 16px;
      text-align: center;
      border-bottom: 1px solid #e6f0ff;
    }

    th {
      font-weight: 600;
      position: sticky;
      top: 0;
      z-index: 1;

      &.dimension-col {
        width: 200px;
        min-width: 200px;
        text-align: left;
        background: #f8fafc;
        border-right: 2px solid #e6f0ff;
      }

      &.talent-col {
        min-width: 180px;
        border-right: 2px solid #e6f0ff;

        &:last-child {
          border-right: none;
        }

        .talent-header {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;

          .talent-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
            font-weight: 600;
          }

          .talent-info {
            .talent-name {
              font-weight: 600;
              font-size: 14px;
              margin-bottom: 4px;
            }

            .talent-position {
              font-size: 12px;
              color: #666;
              margin-bottom: 4px;
            }

            .talent-tags {
              display: flex;
              gap: 4px;
              justify-content: center;

              .header-tag {
                margin: 0;
                font-size: 11px;
                line-height: 18px;
                padding: 0 6px;
              }
            }
          }
        }
      }

      &.talent-col-0 {
        background: linear-gradient(135deg, rgba(0,102,179,0.08), rgba(0,102,179,0.12));
      }

      &.talent-col-1 {
        background: linear-gradient(135deg, rgba(0,136,204,0.08), rgba(0,136,204,0.12));
      }

      &.talent-col-2 {
        background: linear-gradient(135deg, rgba(102,163,255,0.08), rgba(102,163,255,0.12));
      }

      &.talent-col-3 {
        background: linear-gradient(135deg, rgba(153,194,255,0.08), rgba(153,194,255,0.12));
      }

      &.talent-col-4 {
        background: linear-gradient(135deg, rgba(0,77,153,0.08), rgba(0,77,153,0.12));
      }
    }

    td {
      &.dimension-name {
        font-weight: 500;
        background: #f8fafc;
        text-align: left;
        color: #333;
        border-right: 2px solid #e6f0ff;
      }

      &.talent-cell-0 {
        background: linear-gradient(135deg, rgba(0,102,179,0.02), rgba(0,102,179,0.05));
        border-right: 2px solid #e6f0ff;
      }

      &.talent-cell-1 {
        background: linear-gradient(135deg, rgba(0,136,204,0.02), rgba(0,136,204,0.05));
        border-right: 2px solid #e6f0ff;
      }

      &.talent-cell-2 {
        background: linear-gradient(135deg, rgba(102,163,255,0.02), rgba(102,163,255,0.05));
        border-right: 2px solid #e6f0ff;
      }

      &.talent-cell-3 {
        background: linear-gradient(135deg, rgba(153,194,255,0.02), rgba(153,194,255,0.05));
        border-right: 2px solid #e6f0ff;
      }

      &.talent-cell-4 {
        background: linear-gradient(135deg, rgba(0,77,153,0.02), rgba(0,77,153,0.05));
        border-right: 2px solid #e6f0ff;
      }
    }

    .dimension-group {
      .group-header {
        font-weight: 600;
        text-align: left;
        padding-left: 16px;
        font-size: 14px;
        border-right: 2px solid #e6f0ff;
      }
    }

    .compare-value {
      font-weight: 500;
      color: #333;
    }

    .education-cell {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;

      .inline-tag {
        margin: 0;
        font-size: 11px;
        line-height: 18px;
        padding: 0 6px;
      }
    }

    .skills-cell {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: center;

      .more-skills {
        font-size: 12px;
        color: #999;
        align-self: center;
      }
    }

    .honor-cell {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;

      .honor-text {
        font-size: 13px;
        color: #333;
      }

      .more-honors {
        font-size: 12px;
        color: #999;
      }

      .no-data {
        color: #999;
        font-size: 13px;
      }
    }

    .support-plan-cell {
      .plan-text {
        font-size: 13px;
        color: #333;
      }
    }

    .score-cell {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;

      .score-value {
        font-weight: 500;
        min-width: 30px;
        display: inline-block;
        color: #333;
      }
    }

    tr:hover {
      td:not(.dimension-name) {
        background: rgba(0, 102, 179, 0.08) !important;
      }

      td.dimension-name {
        background: #e6f0ff;
      }
    }
  }
}

.yn-grid-progress {
  :deep(.ant-progress-inner) {
    background-color: #e6f0ff;
  }

  :deep(.ant-progress-bg) {
    background: #0066b3;
  }
}

.analysis-results {
  padding: 20px;
  margin: 0 20px 20px;

  .analysis-header {
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
    }
  }

  .analysis-content {
    > div {
      margin-bottom: 30px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
    }

    .score-summary {
      .score-bars {
        .score-bar-item {
          margin-bottom: 16px;

          &:last-child {
            margin-bottom: 0;
          }

          .score-bar-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;

            .talent-name {
              font-weight: 500;
            }

            .score-value {
              font-weight: 600;
            }
          }
        }
      }
    }

    .recommendations {
      .recommendation-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;

        .recommendation-card {
          :deep(.ant-card-head-title) {
            font-size: 14px;
          }

          .recommended-talents {
            margin-top: 12px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
          }
        }
      }
    }
  }
}

.empty-comparison-state {
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
  margin: 20px;

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

/* 添加人才模态框样式 */
.add-talent-modal {
  :deep(.ant-modal-body) {
    padding: 20px;
  }
}

.talent-search-modal {
  display: flex;
  flex-direction: column;
  height: 600px;

  .modal-search-header {
    margin-bottom: 16px;

    .search-mode-container {
      margin-bottom: 12px;

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
    }

    .modal-quick-search {
      display: flex;
      justify-content: center;
    }

    .modal-advanced-filters {
      .filter-row {
        display: flex;
        align-items: center;
        gap: 10px;

        .reset-filters-btn {
          color: #0066b3;

          &:hover {
            color: #0088cc;
          }
        }
      }
    }
  }

  .modal-results-info {
    padding: 12px;
    background: #f8fafc;
    border-radius: 6px;
    margin-bottom: 16px;
    border: 1px solid #e6f0ff;
  }

  .modal-talents-list {
    flex: 1;
    overflow: auto;
    margin-bottom: 16px;

    .modal-talents-table {
      :deep(.in-comparison-row) {
        background-color: #e6f0ff !important;
      }

      .modal-selection-control {
        display: flex;
        justify-content: center;
      }

      .modal-talent-name {
        display: flex;
        align-items: center;
        gap: 12px;

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

      .modal-talent-tags {
        .ant-tag {
          margin-bottom: 4px;
        }
      }
    }
  }

  .modal-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16px;
    border-top: 1px solid #e6f0ff;

    .selected-summary {
      flex: 1;
      font-size: 14px;
    }

    .action-buttons {
      display: flex;
      gap: 12px;
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .compare-participants,
  .compare-dimensions,
  .compare-table-container,
  .analysis-results {
    margin: 10px;
    padding: 16px;
  }

  .participants-list {
    justify-content: center;

    .participant-card,
    .add-participant-card {
      width: 100%;
    }
  }

  .dimensions-checkbox-group {
    grid-template-columns: 1fr !important;
  }

  .recommendation-list {
    grid-template-columns: 1fr !important;
  }

  .compare-actions {
    flex-wrap: wrap;
  }

  .add-talent-modal {
    width: 95% !important;

    .modal-search-header {
      .modal-advanced-filters {
        .filter-row {
          flex-wrap: wrap;

          .ant-select {
            width: 100% !important;
            margin-left: 0 !important;
            margin-top: 8px;
          }
        }
      }
    }
  }
}
</style>