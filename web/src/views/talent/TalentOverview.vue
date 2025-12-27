<template>
  <div class="person-profile" >
    <!-- 第一行：头部信息 + 考核等级（有考核数据时）或统计卡（无考核数据时） -->
    <div class="row" style="display: flex; flex-wrap: wrap; margin: -20px -20px 10px;">
      <!-- 头部信息卡片 -->
      <div class="col" style="width: 66.6667%; padding: 10px;">
        <div class="header-card">
          <div class="avatar-section">
            <img :src="user.avatar" alt="Avatar" class="avatar"/>
            <div style="font-size: 18px; font-weight: 600; color: #333; margin-top: 10px;">{{ user.name }}</div>
            <div style="font-size: 14px; color: #999; margin-top: 4px;">{{ user.department }}</div>
            <div style="margin-top: 10px;">
              <span
                  v-for="(tag, index) in user.tags"
                  :key="index"
                  :style="tag.style"
              >
                {{ tag.text }}
              </span>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">性别</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.gender }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">年龄</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.age }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">籍贯</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.origin }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">民族</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.nation }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">入职时间</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.entryTime }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">职务类型</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.positionType }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">政治面貌</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.politicalStatus }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">毕业大学</span>
              <div class="info-separator"></div>
              <span class="info-value">{{ user.university }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">电话号码</span>
              <div class="info-separator"></div>
              <span class="info-value phone">{{ user.phone }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">电子邮箱</span>
              <div class="info-separator"></div>
              <span class="info-value email">{{ user.email }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：根据是否有考核数据显示不同内容 -->
      <div class="col" style="width: 33.3333%; padding: 10px;">
        <!-- 有考核数据时显示考核等级 -->
        <div v-if="hasAssessment" class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 20px; height: 100%;">
          <div style="display: flex; height: 100%;">
            <!-- 左侧：考核等级 -->
            <div style="flex: 1; padding-right: 20px; border-right: 1px solid #e6f0ff; display: flex; flex-direction: column; justify-content: center; align-items: center;">
              <!-- 奖杯图标 - 使用云南电网主题蓝色 -->
              <div style="margin-bottom: 12px; position: relative;">
                <!-- 奖杯主体 -->
                <svg width="44" height="44" viewBox="0 0 100 100" style="color: #0066b3;">
                  <!-- 奖杯底座 -->
                  <rect x="30" y="75" width="40" height="10" rx="2" fill="#0066b3" opacity="0.8"/>
                  <rect x="25" y="70" width="50" height="5" rx="2" fill="#0066b3" opacity="0.9"/>

                  <!-- 奖杯主体 -->
                  <path d="M35,20 L65,20 L70,50 L60,50 L60,65 L40,65 L40,50 L30,50 Z" fill="#0066b3"/>

                  <!-- 奖杯手柄左侧 -->
                  <path d="M35,25 L25,25 Q20,30 20,40 L20,50 Q25,45 30,50 L30,45 Q27,42 30,30 Z" fill="#0066b3" opacity="0.7"/>

                  <!-- 奖杯手柄右侧 -->
                  <path d="M65,25 L75,25 Q80,30 80,40 L80,50 Q75,45 70,50 L70,45 Q73,42 70,30 Z" fill="#0066b3" opacity="0.7"/>

                  <!-- 奖杯顶部装饰 -->
                  <circle cx="50" cy="15" r="5" fill="#0066b3" opacity="0.9"/>
                  <circle cx="50" cy="15" r="2" fill="#fff"/>

                  <!-- 星星装饰 -->
                  <path d="M50,5 L52,10 L57,10 L53,13 L55,18 L50,15 L45,18 L47,13 L43,10 L48,10 Z" fill="#fff"/>
                </svg>

                <!-- 光效装饰 -->
                <div style="position: absolute; top: 0; left: 0; width: 44px; height: 44px;">
                  <svg width="44" height="44" viewBox="0 0 100 100">
                    <!-- 光晕效果 -->
                    <ellipse cx="50" cy="15" rx="8" ry="3" fill="#fff" opacity="0.3"/>
                    <!-- 高光效果 -->
                    <path d="M40,25 L45,22 L48,27 L42,30 Z" fill="#fff" opacity="0.4"/>
                    <path d="M60,25 L55,22 L52,27 L58,30 Z" fill="#fff" opacity="0.4"/>
                  </svg>
                </div>
              </div>

              <!-- 考核等级文字 -->
              <div style="text-align: center;">
                <div style="font-size: 14px; color: #666; margin-bottom: 8px; font-weight: 500;">{{ assessmentData.label }}</div>
                <div style="font-size: 32px; font-weight: 700; color: #e64340; margin-bottom: 8px; position: relative;">
                  {{ assessmentData.grade }}
                  <!-- 装饰效果 -->
                  <div style="position: absolute; bottom: -4px; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #0066b3, transparent); opacity: 0.5;"></div>
                </div>
                <div style="display: flex; align-items: center; justify-content: center; font-size: 12px; color: #999; background: #f8fafc; padding: 4px 12px; border-radius: 12px; margin-top: 4px;">
                  <svg width="14" height="14" viewBox="0 0 1024 1024" style="margin-right: 6px; color: #0066b3;">
                    <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292a31.8 31.8 0 0 1-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 12.9L512 599.6l94.3-128.8c6-8 15.6-12.9 25.9-12.9H699c6.5 0 10.3 7.4 6.5 12.7z" fill="#0066b3" />
                  </svg>
                  <span>{{ assessmentData.status }}</span>
                </div>
              </div>
            </div>

            <!-- 右侧：考核指标 -->
            <div style="flex: 1.5; padding-left: 20px; display: flex; flex-direction: column; justify-content: center;">
              <div style="font-size: 16px; font-weight: 600; color: #333; margin-bottom: 15px; display: flex; align-items: center;">
                <!-- 更精致的文档图标 -->
                <svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 8px; color: #0066b3;">
                  <path d="M14,2H6C4.9,2,4,2.9,4,4v16c0,1.1,0.9,2,2,2h12c1.1,0,2-0.9,2-2V8L14,2z" fill="#0066b3" opacity="0.9"/>
                  <path d="M14,2v6h6" fill="#0066b3" opacity="0.7"/>
                  <rect x="8" y="12" width="8" height="2" fill="#fff"/>
                  <rect x="8" y="16" width="8" height="2" fill="#fff"/>
                  <rect x="8" y="20" width="8" height="2" fill="#fff"/>
                </svg>
                {{ assessmentData.title }}
              </div>
              <ul style="padding-left: 20px; margin: 0; color: #666; font-size: 14px; line-height: 1.8;">
                <li v-for="(item, index) in assessmentData.indicators" :key="index" style="margin-bottom: 10px; position: relative; padding-left: 8px;">
                  <!-- 更漂亮的列表项图标 -->
                  <svg width="12" height="12" viewBox="0 0 12 12" style="position: absolute; left: -14px; top: 5px;">
                    <!-- 渐变圆形背景 -->
                    <circle cx="6" cy="6" r="6" fill="url(#gradient)"/>
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#0066b3" stop-opacity="0.9"/>
                        <stop offset="100%" stop-color="#0088cc" stop-opacity="0.9"/>
                      </linearGradient>
                    </defs>
                    <!-- 对勾图标 -->
                    <path d="M3,6 L5,8 L9,4" stroke="#fff" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 无考核数据时显示统计卡 -->
        <div v-else class="stats-card">
          <div style="display: flex; flex-wrap: wrap; margin: -5px -5px; height: 100%;">
            <!-- 参与项目总数 -->
            <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
              <div class="stat-item">
                <div style="display: flex; align-items: center; height: 100%;">
                  <div class="icon" style="margin-right: 8px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="#0066b3"/>
                    </svg>
                  </div>
                  <div style="flex: 1;">
                    <div class="label">参与项目总数</div>
                    <div class="value">{{ stats.participationCount }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 里程碑完成总数 -->
            <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
              <div class="stat-item">
                <div style="display: flex; align-items: center; height: 100%;">
                  <div class="icon" style="margin-right: 8px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M14 6L10.25 11L13 10.25V18H11V10.25L7.75 11L4 6L8 5L10 2L12 5L14 6ZM19 18H15V20H19V22H15V24H21V18H19ZM15 12H17V14H15V12ZM19 12H21V14H19V12ZM15 16H17V18H15V16ZM19 16H21V18H19V16Z" fill="#0066b3"/>
                    </svg>
                  </div>
                  <div style="flex: 1;">
                    <div class="label">里程碑完成总数</div>
                    <div class="value">{{ stats.milestoneCount }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 负责项目总数 -->
            <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
              <div class="stat-item">
                <div style="display: flex; align-items: center; height: 100%;">
                  <div class="icon" style="margin-right: 8px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20 6H12L10 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6ZM20 18H4V8H20V18Z" fill="#0066b3"/>
                    </svg>
                  </div>
                  <div style="flex: 1;">
                    <div class="label">负责项目总数</div>
                    <div class="value">{{ stats.responsibleCount }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 项目绩效平均分 -->
            <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
              <div class="stat-item">
                <div style="display: flex; align-items: center; height: 100%;">
                  <div class="icon" style="margin-right: 8px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z" fill="#0066b3"/>
                    </svg>
                  </div>
                  <div style="flex: 1;">
                    <div class="label">项目绩效平均分</div>
                    <div class="value">{{ stats.averageScore }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 第二行：人才画像 + 右侧垂直卡片流 -->
    <div class="row" style="display: flex; flex-wrap: wrap; margin: -20px -20px 10px;">
      <!-- 左侧人才画像 -->
      <div class="col" style="width: 66.6667%; padding: 10px;">
        <div class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 20px; height: 100%;">
          <div style="font-size: 16px; font-weight: 600; color: #333; margin-bottom: 20px; display: flex; align-items: center;">
            <svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 8px; color: #0066b3;">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="#0066b3"/>
            </svg>
            人才画像
            <div style="margin-left: 10px; font-size: 12px; color: #999; font-weight: normal;">基于综合评估的人才发展蓝图</div>
          </div>

          <!-- 人才画像核心信息 -->
          <div style="display: flex; justify-content: center; align-items: stretch; margin-bottom: 25px;">
            <!-- 左侧：基本标签 -->
            <div style="width: 40%; padding-right: 20px; border-right: 1px solid #e6f0ff;">
              <div class="profile-section">
                <div class="section-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" style="margin-right: 6px;">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="#0066b3"/>
                  </svg>
                  基础画像
                </div>
                <div class="tag-container">
                  <div class="tag-item" v-for="(tag, index) in talentProfile.basicTags" :key="index">
                    <!--                    <div class="tag-icon">{{ tag.icon }}</div>-->
                    <div>
                      <div class="tag-label">{{ tag.label }}</div>
                      <div class="tag-value">{{ tag.value }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 中间：人才定位图标 -->
            <div style="width: 20%; padding: 0 20px; display: flex; align-items: center; justify-content: center;">
              <div class="talent-positioning">
                <div class="positioning-ring">
                  <div class="ring-inner">
                    <div class="talent-score">{{ talentProfile.talentScore }}</div>
                    <div class="score-label">人才指数</div>
                  </div>
                </div>
                <div class="positioning-label">高潜人才</div>
              </div>
            </div>

            <!-- 右侧：能力标签 -->
            <div style="width: 40%; padding-left: 20px; border-left: 1px solid #e6f0ff;">
              <div class="profile-section">
                <div class="section-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" style="margin-right: 6px;">
                    <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm0 15l-5-5h3V9h4v4h3l-5 5z" fill="#0066b3"/>
                  </svg>
                  能力标签
                </div>
                <div class="tag-container">
                  <div class="tag-item" v-for="(tag, index) in talentProfile.skillTags" :key="index">
                    <!--                    <div class="tag-icon">{{ tag.icon }}</div>-->
                    <div>
                      <div class="tag-label">{{ tag.label }}</div>
                      <div class="tag-value">{{ tag.value }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 人才发展评估 -->
          <div class="development-assessment">
            <div class="assessment-title">
              <svg width="18" height="18" viewBox="0 0 24 24" style="margin-right: 8px;">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#0066b3"/>
              </svg>
              人才发展评估与规划
            </div>

            <div class="assessment-grid">
              <!-- 个人潜力评估 -->
              <div class="assessment-card potential-card">
                <div class="card-header">
                  <div class="card-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 6px;">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" fill="#0066b3"/>
                    </svg>
                    个人潜力评估
                  </div>
                  <div class="card-badge" :style="talentProfile.potential.style">
                    {{ talentProfile.potential.level }}
                  </div>
                </div>
                <div class="card-content">
                  <div class="potential-indicators">
                    <div class="indicator" v-for="(indicator, index) in talentProfile.potential.indicators" :key="index">
                      <div class="indicator-label">{{ indicator.label }}</div>
                      <div class="progress-bar">
                        <div class="progress-fill" :style="{ width: indicator.value + '%' }"></div>
                      </div>
                      <div class="indicator-value">{{ indicator.value }}%</div>
                    </div>
                  </div>
                  <div class="assessment-summary">
                    <div class="summary-title">评估要点</div>
                    <div class="summary-text">{{ talentProfile.potential.summary }}</div>
                  </div>
                </div>
              </div>

              <!-- 发展方向规划 -->
              <div class="assessment-card direction-card">
                <div class="card-header">
                  <div class="card-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 6px;">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" fill="#0066b3"/>
                    </svg>
                    发展方向规划
                  </div>
                  <div class="card-badge" style="background: #e6f0ff; color: #0066b3; border: 1px solid #b3d1ff;">
                    3个方向
                  </div>
                </div>
                <div class="card-content">
                  <div class="direction-list">
                    <div class="direction-item" v-for="(direction, index) in talentProfile.developmentDirections" :key="index">
                      <!--                      <div class="direction-icon">{{ direction.icon }}</div>-->
                      <div>
                        <div class="direction-name">{{ direction.name }}</div>
                        <div class="direction-timeline">
                          <span class="timeline-label">建议时间：</span>
                          <span class="timeline-value">{{ direction.timeline }}</span>
                        </div>
                      </div>
                      <div class="direction-priority" :class="'priority-' + direction.priority">
                        {{ direction.priorityLabel }}
                      </div>
                    </div>
                  </div>
                  <div class="recommendation">
                    <div class="recommendation-title">专家建议</div>
                    <div class="recommendation-text">{{ talentProfile.developmentRecommendation }}</div>
                  </div>
                </div>
              </div>

              <!-- 继任发展计划 -->
              <div class="assessment-card succession-card">
                <div class="card-header">
                  <div class="card-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 6px;">
                      <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="#0066b3"/>
                    </svg>
                    继任发展计划
                  </div>
                  <div class="card-badge" style="background: #e6f0ff; color: #0066b3; border: 1px solid #b3d1ff;">
                    预备人选
                  </div>
                </div>
                <div class="card-content">
                  <div class="succession-info">
                    <div class="succession-item">
                      <div class="succession-label">目标岗位</div>
                      <div class="succession-value">{{ talentProfile.successionPlan.targetPosition }}</div>
                    </div>
                    <div class="succession-item">
                      <div class="succession-label">准备度</div>
                      <div class="readiness-indicator">
                        <div class="readiness-bar">
                          <div class="readiness-fill" :style="{ width: talentProfile.successionPlan.readiness + '%' }"></div>
                        </div>
                        <div class="readiness-value">{{ talentProfile.successionPlan.readiness }}%</div>
                      </div>
                    </div>
                    <div class="succession-item">
                      <div class="succession-label">预计时间</div>
                      <div class="succession-value">{{ talentProfile.successionPlan.estimatedTime }}</div>
                    </div>
                  </div>
                  <div class="development-actions">
                    <div class="actions-title">发展行动项</div>
                    <ul class="actions-list">
                      <li v-for="(action, index) in talentProfile.successionPlan.actions" :key="index">
                        {{ action }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：统计卡片 + 项目经历 + 奖惩情况 -->
      <div class="col" style="width: 33.3333%; padding: 10px;">
        <div style="display: flex; flex-direction: column; gap: 10px; height: 100%;">
          <!-- 统计卡片 - 调整高度 -->
          <div class="stats-card" style="flex: 1;">
            <div style="display: flex; flex-wrap: wrap; margin: -5px -5px; height: 100%;">
              <!-- 参与项目总数 -->
              <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
                <div class="stat-item" style="height: 80px;">
                  <div style="display: flex; align-items: center; height: 100%;">
                    <div class="icon" style="margin-right: 8px;">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="#0066b3"/>
                      </svg>
                    </div>
                    <div style="flex: 1;">
                      <div class="label">参与项目总数</div>
                      <div class="value">{{ stats.participationCount }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 里程碑完成总数 -->
              <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
                <div class="stat-item" style="height: 80px;">
                  <div style="display: flex; align-items: center; height: 100%;">
                    <div class="icon" style="margin-right: 8px;">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 6L10.25 11L13 10.25V18H11V10.25L7.75 11L4 6L8 5L10 2L12 5L14 6ZM19 18H15V20H19V22H15V24H21V18H19ZM15 12H17V14H15V12ZM19 12H21V14H19V12ZM15 16H17V18H15V16ZM19 16H21V18H19V16Z" fill="#0066b3"/>
                      </svg>
                    </div>
                    <div style="flex: 1;">
                      <div class="label">里程碑完成总数</div>
                      <div class="value">{{ stats.milestoneCount }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 负责项目总数 -->
              <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
                <div class="stat-item" style="height: 80px;">
                  <div style="display: flex; align-items: center; height: 100%;">
                    <div class="icon" style="margin-right: 8px;">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6H12L10 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6ZM20 18H4V8H20V18Z" fill="#0066b3"/>
                      </svg>
                    </div>
                    <div style="flex: 1;">
                      <div class="label">负责项目总数</div>
                      <div class="value">{{ stats.responsibleCount }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 项目绩效平均分 -->
              <div style="width: 50%; padding: 5px; display: flex; flex-direction: column;">
                <div class="stat-item" style="height: 80px;">
                  <div style="display: flex; align-items: center; height: 100%;">
                    <div class="icon" style="margin-right: 8px;">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z" fill="#0066b3"/>
                      </svg>
                    </div>
                    <div style="flex: 1;">
                      <div class="label">项目绩效平均分</div>
                      <div class="value">{{ stats.averageScore }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 项目经历 -->
          <div class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 20px; flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
              <div style="font-size: 16px; font-weight: 600; color: #333;">项目经历</div>
              <a style="font-size: 14px; color: #0066b3; text-decoration: none;">更多</a>
            </div>
            <div class="timeline-container">
              <div class="timeline-item" v-for="(item, index) in projectList" :key="index">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                  <!-- 第一行：时间 -->
                  <div style="font-size: 14px; color: #666; margin-bottom: 4px; line-height: 1.4;">
                    {{ item.date }}
                  </div>
                  <!-- 第二行：项目名称和评分 -->
                  <div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px; line-height: 1.4; margin-bottom: 4px;">
                    <span style="color: #333; font-weight: 600; flex: 1; margin-right: 8px;">{{ item.name }}</span>
                    <span style="color: #0066b3; font-weight: 600; min-width: 40px; text-align: right;">{{ item.score }}</span>
                  </div>
                  <!-- 第三行：项目角色 -->
                  <div style="font-size: 14px; line-height: 1.4;">
                    <span style="color: #666; margin-right: 6px;">项目角色：</span>
                    <span style="color: #333; font-weight: 600;">{{ item.role }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 奖惩情况 -->
          <div class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 20px; flex: 1;">
            <div style="font-size: 16px; font-weight: 600; color: #333; margin-bottom: 20px;">奖惩情况</div>
            <div style="display: flex; flex-wrap: wrap; margin: -5px -5px; height: calc(100% - 40px);">
              <div style="width: 50%; padding: 5px; height: 50%;" v-for="(item, index) in awardList" :key="index">
                <div class="award-card" style="height: 100%;">
                  <div style="font-size: 28px; margin-bottom: 5px;">{{ item.icon }}</div>
                  <div style="font-size: 12px; color: #666; margin-bottom: 3px;">{{ item.name }}</div>
                  <div style="font-size: 12px; color: #999;">{{ item.date }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 第三行：人才评分 + 培训经历 -->
    <div class="row" style="display: flex; flex-wrap: wrap; margin: -20px -20px 20px;">
      <!-- 左侧人才评分 -->
      <div class="col" style="width: 66.6667%; padding: 10px;">
        <div class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 15px; height: 100%;">
          <div style="font-size: 16px; font-weight: 600; color: #333; margin-bottom: 15px;">人才评分</div>
          <div style="display: flex; flex-wrap: wrap; margin: -4px -4px;">
            <!-- 个人能力自评 -->
            <div style="width: 25%; padding: 4px;">
              <div class="score-module" style="border: 1px solid #e6f0ff; border-radius: 6px; padding: 12px; height: 100%; background: #fff; box-shadow: 0 1px 4px rgba(0, 102, 179, 0.05);">
                <!-- 模块标题行 -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f5ff;">
                  <div style="font-size: 13px; color: #333; font-weight: 600; line-height: 1.2;">个人能力自评</div>
                  <div style="font-size: 13px; color: #ff4d4f; font-weight: 600;">{{ ratings.personal }}</div>
                </div>
                <!-- 雷达图 -->
                <div id="radar1" style="width: 100%; height: 190px;"></div>
              </div>
            </div>

            <!-- 岗位胜任力 -->
            <div style="width: 25%; padding: 4px;">
              <div class="score-module" style="border: 1px solid #e6f0ff; border-radius: 6px; padding: 12px; height: 100%; background: #fff; box-shadow: 0 1px 4px rgba(0, 102, 179, 0.05);">
                <!-- 模块标题行 -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f5ff;">
                  <div style="font-size: 13px; color: #333; font-weight: 600; line-height: 1.2;">岗位胜任力</div>
                  <div style="font-size: 13px; color: #ff4d4f; font-weight: 600;">{{ ratings.position }}</div>
                </div>
                <!-- 雷达图 -->
                <div id="radar2" style="width: 100%; height: 190px;"></div>
              </div>
            </div>

            <!-- 板凳数据 -->
            <div style="width: 25%; padding: 4px;">
              <div class="score-module" style="border: 1px solid #e6f0ff; border-radius: 6px; padding: 12px; height: 100%; background: #fff; box-shadow: 0 1px 4px rgba(0, 102, 179, 0.05);">
                <!-- 模块标题行 -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f5ff;">
                  <div style="font-size: 13px; color: #333; font-weight: 600; line-height: 1.2;">板凳数据</div>
                  <div style="font-size: 13px; color: #ff4d4f; font-weight: 600;">{{ ratings.bench }}</div>
                </div>
                <!-- 雷达图 -->
                <div id="radar3" style="width: 100%; height: 190px;"></div>
              </div>
            </div>

            <!-- 员工关系图谱 -->
            <div style="width: 25%; padding: 4px;">
              <div class="score-module" style="border: 1px solid #e6f0ff; border-radius: 6px; padding: 12px; height: 100%; background: #fff; box-shadow: 0 1px 4px rgba(0, 102, 179, 0.05);">
                <!-- 模块标题行 -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f5ff;">
                  <div style="font-size: 13px; color: #333; font-weight: 600; line-height: 1.2;">员工关系图谱</div>
                  <div style="font-size: 13px; color: #0066b3; font-weight: 600;">网络关系</div>
                </div>
                <!-- 关系图 -->
                <div id="network" style="width: 100%; height: 190px;"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：培训经历 -->
      <div class="col" style="width: 33.3333%; padding: 10px;">
        <div class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 20px; height: 100%;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div style="font-size: 16px; font-weight: 600; color: #333;">培训经历</div>
            <a style="font-size: 14px; color: #0066b3; text-decoration: none;">更多</a>
          </div>
          <div class="timeline-container" style="height: calc(100% - 40px);">
            <div class="timeline-item" v-for="(item, index) in trainingList" :key="index">
              <div class="timeline-dot" :style="{background: item.status === '已通过' ? '#1890ff' : item.status === '进行中' ? '#52c41a' : '#faad14'}"></div>
              <div class="timeline-content">
                <!-- 第一行：时间 -->
                <div style="font-size: 14px; color: #666; margin-bottom: 4px; line-height: 1.4;">
                  {{ item.date }}
                </div>
                <!-- 第二行：培训名称和状态 -->
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px; line-height: 1.4; margin-bottom: 4px;">
                  <span style="color: #333; font-weight: 600; flex: 1; margin-right: 8px;">{{ item.name }}</span>
                  <span :style="{
              background: item.status === '已通过' ? '#f6ffed' :
                         item.status === '进行中' ? '#e6f7ff' : '#fff7e6',
              color: item.status === '已通过' ? '#1890ff' :
                     item.status === '进行中' ? '#52c41a' : '#faad14',
              border: item.status === '已通过' ? '1px solid #b7eb8f' :
                      item.status === '进行中' ? '1px solid #91d5ff' : '1px solid #ffd591',
              borderRadius: '4px',
              padding: '2px 8px',
              fontSize: '12px',
              fontWeight: '600'
            }">{{ item.status }}</span>
                </div>
                <!-- 第三行：培训时长（如有数据） -->
<!--                <div style="font-size: 14px; line-height: 1.4;">
                  <span style="color: #666; margin-right: 6px;">培训时长：</span>
                  <span style="color: #333; font-weight: 600;">{{ item.duration || '16课时' }}</span>
                </div>-->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 第四行：考勤数据 + 其他信息 -->
    <div class="row" style="display: flex; flex-wrap: wrap; margin: -20px -20px;">
      <!-- 考勤数据 -->
      <div class="col" style="width: 66.6667%; padding: 10px;">
        <div class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 20px; height: 100%;">
          <div style="font-size: 16px; font-weight: 600; color: #333; margin-bottom: 10px;">个人考勤数据</div>
          <div style="font-size: 14px; color: #0066b3; display: flex; align-items: center; margin-bottom: 15px;">
            <svg width="16" height="16" viewBox="0 0 1024 1024" style="margin-right: 6px;">
              <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292a31.8 31.8 0 0 1-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 12.9L512 599.6l94.3-128.8c6-8 15.6-12.9 25.9-12.9H699c6.5 0 10.3 7.4 6.5 12.7z" fill="#0066b3" />
            </svg>
            {{ attendance.average }}
          </div>
          <div id="attendance-line" style="width: 100%; height: 190px;"></div>
        </div>
      </div>

      <!-- 其他信息 -->
      <div class="col" style="width: 33.3333%; padding: 10px;">
        <div class="card-container" style="background: #fff; border-radius: 8px; border: 1px solid #e6f0ff; padding: 20px; height: 100%;">
          <div style="font-size: 16px; font-weight: 600; color: #333; margin-bottom: 20px;">其他信息</div>
          <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
            <div class="info-row">
              <div style="font-size: 14px; color: #666; margin-bottom: 4px;">当前状态</div>
              <div style="font-size: 14px; color: #0066b3; font-weight: 600;">在岗</div>
            </div>
            <div class="info-row">
              <div style="font-size: 14px; color: #666; margin-bottom: 4px;">上次评估时间</div>
              <div style="font-size: 14px; color: #333; font-weight: 600;">2023.06.15</div>
            </div>
            <div class="info-row">
              <div style="font-size: 14px; color: #666; margin-bottom: 4px;">下次评估时间</div>
              <div style="font-size: 14px; color: #333; font-weight: 600;">2023.12.15</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import * as echarts from 'echarts'

// 用户基本信息
const user = {
  avatar: 'https://avatars.githubusercontent.com/u/100',
  name: '倪丽',
  department: '置信项目组/人力资源部',
  gender: '女',
  age: 28,
  origin: '上海市',
  nation: '汉族',
  entryTime: '2018.04',
  positionType: '人事专员',
  politicalStatus: '中共党员',
  university: '上海交通大学',
  phone: '139-1777-9998',
  email: 'wangqi@shdc.com',
  tags: [
    { text: '专业人才库', style: 'background: #0066b3; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px;' },
    { text: '青年骨干库', style: 'background: #0088cc; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;' }
  ]
}

// 统计卡片数据
const stats = {
  participationCount: '16个',
  milestoneCount: '200个',
  responsibleCount: '5个',
  averageScore: '4.7分'
}

// 考核数据 - 可以设置为null或空对象来测试无考核数据的情况
const assessmentData = {
  label: '上半年考核等级',
  grade: '称职',
  status: '考核通过',
  title: '本年度重点考核指标',
  indicators: [
    '模块快速调研开发',
    '人才盘点建库',
    '优化现有流程'
  ]
}

// 计算是否有考核数据
const hasAssessment = computed(() => {
  return assessmentData && Object.keys(assessmentData).length > 0
})

// 人才画像数据
const talentProfile = {
  talentScore: 82,

  basicTags: [
    { icon: '🎯', label: '岗龄', value: '5年' },
    { icon: '🏷️', label: '职称', value: '人事中级专员' },
    { icon: '📍', label: '挂职经历', value: '借调地产人力资源部' },
    { icon: '🎓', label: '专业资质', value: '企业人力资源管理师' },
    { icon: '🌍', label: '熟悉区域', value: '上海、华东' },
    { icon: '📊', label: '绩效等级', value: '持续高绩效' }
  ],

  skillTags: [
    { icon: '💬', label: '沟通协调', value: '优秀' },
    { icon: '📈', label: '项目管理', value: '良好' },
    { icon: '🔍', label: '问题分析', value: '优秀' },
    { icon: '🤝', label: '团队协作', value: '良好' },
    { icon: '💡', label: '创新思维', value: '中等' },
    { icon: '📚', label: '学习能力', value: '优秀' }
  ],

  potential: {
    level: '高潜',
    style: 'background: #e6f0ff; color: #0066b3; border: 1px solid #b3d1ff;',
    indicators: [
      { label: '成长敏捷性', value: 85 },
      { label: '业务洞察力', value: 78 },
      { label: '领导潜质', value: 72 },
      { label: '变革适应性', value: 80 }
    ],
    summary: '具备较强的学习能力和业务理解力，在复杂环境中表现出良好的适应性和问题解决能力，建议加强战略思维和跨部门影响力。'
  },

  developmentDirections: [
    {
      icon: '📊',
      name: '人力资源高级专员',
      timeline: '6-12个月',
      priority: 1,
      priorityLabel: '优先'
    },
    {
      icon: '👥',
      name: '团队管理方向',
      timeline: '12-18个月',
      priority: 2,
      priorityLabel: '中期'
    },
    {
      icon: '🏢',
      name: '人力资源业务伙伴(HRBP)',
      timeline: '18-24个月',
      priority: 3,
      priorityLabel: '长期'
    }
  ],

  developmentRecommendation: '建议优先在现有人力资源专业领域深化，同时参与跨部门项目以拓宽业务视野，可考虑担任小型项目负责人锻炼领导能力。',

  successionPlan: {
    targetPosition: '人力资源部门副经理',
    readiness: 65,
    estimatedTime: '18-24个月',
    actions: [
      '完成高级人力资源管理师认证',
      '主导至少2个跨部门协作项目',
      '参与公司战略规划相关培训',
      '完成团队管理基础课程学习',
      '轮岗至业务部门了解一线需求'
    ]
  }
}

// 项目经历数据
const projectList = [
  { date: '2021.07-2021.09', name: '瑞虹土地资产处置工作专班', role: '项目助理', score: 4.89 },
  { date: '2020.02-2020.05', name: '瑞虹土地资产处置工作专班', role: '项目助理', score: 4.8 },
  { date: '2019.03-2019.05', name: '瑞虹土地资产处置工作专班', role: '项目助理', score: 4.89 }
]

// 人才评分数据
const ratings = {
  personal: '优秀',
  position: '良好',
  bench: '称职'
}

// 考勤数据
const attendance = {
  average: '平均每天考勤9h',
  data: [6, 8, 9, 10, 9],
  dates: ['08.20', '08.21', '08.22', '08.23', '08.24']
}

// 奖惩情况数据
const awardList = [
  { icon: '🏆', name: 'XXXXXX奖', date: '2021.01.12' },
  { icon: '🏆', name: 'XXXXXX奖', date: '2020.12.04' },
  { icon: '🏅', name: 'XXXXXX奖', date: '2021.11.25' },
  { icon: '🏆', name: 'XXXXXX奖', date: '2021.10.22' }
]

// 培训经历数据
// 培训经历数据
const trainingList = [
  {
    name: '人力资源管理高级研修班',
    date: '2023.05.21',
    status: '已通过',
    duration: '24课时'
  },
  {
    name: '项目管理实战培训',
    date: '2023.04.18',
    status: '已通过',
    duration: '32课时'
  },
  {
    name: '领导力发展训练营',
    date: '2023.03.25',
    status: '进行中',
    duration: '40课时'
  },
  {
    name: '数据分析与决策支持',
    date: '2023.02.10',
    status: '已通过',
    duration: '20课时'
  }
]

// 雷达图数据
// 在<script setup>中修改雷达图数据
const radarData = {
  personal: [8, 9, 7, 8, 7],  // 5个值
  position: [7, 8, 6, 7, 6],   // 5个值
  bench: [6, 5, 7, 6, 5],      // 5个值
  indicators: [
    { name: '专业能力', max: 10 },
    { name: '沟通协调', max: 10 },
    { name: '团队协作', max: 10 },
    { name: '学习能力', max: 10 },
    { name: '创新能力', max: 10 }
  ]
}

// 初始化图表
// 在onMounted()中修改雷达图配置
onMounted(() => {
  // 处理雷达图指标名称 - 确保文字显示完整
  const radarIndicatorsWithLineBreak = radarData.indicators.map(item => {
    const name = item.name;
    // 对于2-3个字的指标，不换行
    if (name.length <= 3) {
      return item;
    }
    // 对于4个字的指标，2个字换行一次
    if (name.length === 4) {
      return {
        ...item,
        name: name.substring(0, 2) + '\n' + name.substring(2)
      };
    }
    return item;
  });

  // 通用雷达图配置
  const radarOption = {
    backgroundColor: '#fff',
    radar: {
      indicator: radarIndicatorsWithLineBreak,
      radius: '65%', // 减小半径，为标签留出空间
      center: ['50%', '55%'], // 稍微下移中心点
      splitNumber: 4,
      shape: 'polygon',
      name: {
        textStyle: {
          color: '#333',
          fontSize: 9, // 减小字体大小
          fontWeight: 'normal',
          backgroundColor: 'rgba(255, 255, 255, 0.9)', // 半透明白色背景
          borderRadius: 3,
          padding: [2, 3], // 减小内边距
          lineHeight: 12
        }
      },
      axisLine: {
        lineStyle: {
          color: '#e6f0ff',
          width: 0.5 // 减小线条宽度
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e6f0ff',
          width: 0.5
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(0,102,179,0.03)', 'rgba(0,102,179,0.01)']
        }
      }
    },
    grid: {
      top: '5%', // 减小顶部边距
      bottom: '5%', // 减小底部边距
      left: '5%', // 减小左边距
      right: '5%', // 减小右边距
      containLabel: true
    },
    series: [{
      type: 'radar',
      data: [{
        value: [],
        name: '能力',
        itemStyle: {
          color: '#0066b3'
        },
        lineStyle: {
          color: '#0066b3',
          width: 1.5 // 减小线条宽度
        },
        areaStyle: {
          color: 'rgba(0, 102, 179, 0.15)'
        }
      }],
      symbolSize: 4, // 减小符号大小
      symbol: 'circle',
      label: {
        show: true,
        formatter: function(params) {
          return params.value;
        },
        fontSize: 8, // 减小数值标签字体
        color: '#0066b3',
        position: 'top'
      }
    }],
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e6f0ff',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      }
    }
  };

  // 雷达图1 - 个人能力自评
  const radar1 = echarts.init(document.getElementById('radar1'))
  const radar1Option = JSON.parse(JSON.stringify(radarOption))
  radar1Option.series[0].data[0].value = radarData.personal
  radar1Option.series[0].data[0].areaStyle.color = 'rgba(0, 102, 179, 0.2)'
  radar1.setOption(radar1Option)

  // 雷达图2 - 岗位胜任力
  const radar2 = echarts.init(document.getElementById('radar2'))
  const radar2Option = JSON.parse(JSON.stringify(radarOption))
  radar2Option.series[0].data[0].value = radarData.position
  radar2Option.series[0].data[0].areaStyle.color = 'rgba(0, 102, 179, 0.15)'
  radar2.setOption(radar2Option)

  // 雷达图3 - 板凳数据
  const radar3 = echarts.init(document.getElementById('radar3'))
  const radar3Option = JSON.parse(JSON.stringify(radarOption))
  radar3Option.series[0].data[0].value = radarData.bench
  radar3Option.series[0].data[0].areaStyle.color = 'rgba(0, 102, 179, 0.1)'
  radar3.setOption(radar3Option)

  // 关系图 - 调整为更紧凑的布局
  const network = echarts.init(document.getElementById('network'))
  network.setOption({
    backgroundColor: '#fff',
    series: [{
      type: 'graph',
      layout: 'force',
      force: {
        repulsion: 60, // 减小斥力
        gravity: 0.15, // 减小重力
        edgeLength: [20, 35] // 减小边长度
      },
      roam: false, // 禁止缩放
      focusNodeAdjacency: true,
      edgeSymbol: ['circle', 'arrow'],
      edgeSymbolSize: [2, 6],
      data: [
        { name: '我', symbolSize: 16, itemStyle: { color: '#0066b3' } },
        { name: '同楼层', symbolSize: 10, itemStyle: { color: '#0066b3', opacity: 0.7 } },
        { name: '同出图', symbolSize: 10, itemStyle: { color: '#0066b3', opacity: 0.7 } },
        { name: '同亲属', symbolSize: 10, itemStyle: { color: '#0066b3', opacity: 0.7 } },
        { name: '同校', symbolSize: 10, itemStyle: { color: '#0066b3', opacity: 0.7 } },
        { name: '同事', symbolSize: 10, itemStyle: { color: '#0066b3', opacity: 0.7 } }
      ],
      links: [
        { source: '我', target: '同楼层' },
        { source: '我', target: '同出图' },
        { source: '我', target: '同亲属' },
        { source: '我', target: '同校' },
        { source: '我', target: '同事' }
      ],
      label: {
        show: true,
        formatter: '{b}',
        fontSize: 8, // 减小字体
        position: 'right',
        offset: [2, 0]
      },
      lineStyle: {
        opacity: 0.3,
        color: '#0066b3',
        width: 0.8
      },
      emphasis: {
        scale: false,
        focus: 'adjacency',
        lineStyle: {
          width: 1.5,
          opacity: 0.8
        }
      }
    }]
  })

  // 考勤折线图
  const attendanceLine = echarts.init(document.getElementById('attendance-line'))
  attendanceLine.setOption({
    backgroundColor: '#fff',
    grid: { top: 15, bottom: 25, left: 25, right: 10 },
    xAxis: {
      type: 'category',
      data: attendance.dates,
      axisLine: { lineStyle: { color: '#e6f0ff' } },
      axisLabel: { fontSize: 11, color: '#999' },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      max: 12,
      show: true,
      axisLine: { lineStyle: { color: '#e6f0ff' } },
      axisLabel: { fontSize: 11, color: '#999' },
      splitLine: { lineStyle: { color: '#f0f5ff' } }
    },
    series: [{
      type: 'line',
      data: attendance.data,
      areaStyle: { color: 'rgba(0, 102, 179, 0.1)' },
      lineStyle: { color: '#0066b3', width: 1.5 },
      itemStyle: { color: '#0066b3', borderColor: '#fff', borderWidth: 1.5 },
      symbol: 'circle',
      symbolSize: 5,
      smooth: true
    }],
    tooltip: { trigger: 'axis', textStyle: { fontSize: 11 } }
  })
})
</script>

<style scoped>
/* 头部卡片样式 */
.header-card {
  display: flex;
  gap: 30px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 102, 179, 0.05);
  border: 1px solid #e6f0ff;
  height: auto;
  min-height: 220px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  width: auto;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  object-fit: cover;
}


/* 头部信息网格样式 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  font-size: 14px;
  flex: 1;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: relative;
}

.info-label {
  color: #333;
  font-weight: 600;
  font-size: 13px;
}

.info-separator {
  width: 100%;
  height: 1px;
  background: #f0f5ff;
  margin: 4px 0;
}

.info-value {
  color: #666;
  font-weight: 600;
  font-size: 14px;
}

.phone, .email {
  color: #0066b3;
  font-weight: 600;
}

/* 统计卡片样式 */
.stats-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 102, 179, 0.05);
  border: 1px solid #e6f0ff;
  height: 100%;
}

.stat-item {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e6f0ff;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 102, 179, 0.1);
}

.stat-item .icon {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-item .icon svg {
  width: 24px;
  height: 24px;
}

.stat-item .label {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-item .value {
  font-size: 18px;
  font-weight: 700;
  color: #0066b3;
}

/* 通用卡片样式 */
.card-container {
  box-shadow: 0 2px 12px rgba(0, 102, 179, 0.05);
  transition: all 0.2s ease;
  border: 1px solid #e6f0ff;
}
.card-container:hover {
  box-shadow: 0 4px 16px rgba(0, 102, 179, 0.1);
}

/* 人才画像部分样式 */
.profile-section {
  margin-bottom: 15px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-item {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 6px;
  padding: 8px 12px;
  width: calc(50% - 5px);
  border: 1px solid #e6f0ff;
  transition: all 0.2s ease;
}

.tag-item:hover {
  background: #f0f5ff;
  transform: translateY(-1px);
}

.tag-icon {
  font-size: 18px;
  margin-right: 8px;
  color: #0066b3;
}

.tag-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 2px;
}

.tag-value {
  font-size: 14px;
  font-weight: 600;
  color: #0066b3;
}

/* 人才定位图标 */
.talent-positioning {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.positioning-ring {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0066b3, #0088cc);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  box-shadow: 0 4px 16px rgba(0, 102, 179, 0.2);
}

.ring-inner {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.talent-score {
  font-size: 24px;
  font-weight: 700;
  color: #0066b3;
}

.score-label {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.positioning-label {
  font-size: 14px;
  font-weight: 600;
  color: #0066b3;
  background: #e6f0ff;
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid #b3d1ff;
}

/* 人才发展评估 */
.development-assessment {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #e6f0ff;
}

.assessment-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.assessment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.assessment-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e6f0ff;
  transition: transform 0.2s, box-shadow 0.2s;
}

.assessment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 102, 179, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f5ff;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
}

.card-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
}

/* 个人潜力评估卡片 */
.potential-card {
  border-top: 3px solid #0066b3;
}

.potential-indicators {
  margin-bottom: 15px;
}

.indicator {
  margin-bottom: 10px;
}

.indicator-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.progress-bar {
  height: 6px;
  background: #f0f5ff;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0066b3, #0088cc);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.indicator-value {
  font-size: 12px;
  color: #0066b3;
  font-weight: 600;
  text-align: right;
}

.assessment-summary {
  background: #f8fafc;
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid #0066b3;
}

.summary-title {
  font-size: 12px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.summary-text {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 发展方向卡片 */
.direction-card {
  border-top: 3px solid #0088cc;
}

.direction-list {
  margin-bottom: 15px;
}

.direction-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed #e6f0ff;
}

.direction-item:last-child {
  border-bottom: none;
}

.direction-icon {
  font-size: 18px;
  margin-right: 10px;
  color: #0066b3;
}

.direction-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.direction-timeline {
  font-size: 12px;
  color: #666;
}

.timeline-label {
  color: #999;
}

.timeline-value {
  color: #0066b3;
  font-weight: 500;
}

.direction-priority {
  margin-left: auto;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 8px;
}

.priority-1 {
  background: #e6f0ff;
  color: #0066b3;
  border: 1px solid #b3d1ff;
}

.priority-2 {
  background: #e6f7ff;
  color: #0088cc;
  border: 1px solid #91d5ff;
}

.priority-3 {
  background: #f0f5ff;
  color: #666;
  border: 1px solid #d9e6ff;
}

.recommendation {
  background: #f0f5ff;
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid #0088cc;
}

.recommendation-title {
  font-size: 12px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.recommendation-text {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 继任计划卡片 */
.succession-card {
  border-top: 3px solid #0066b3;
}

.succession-info {
  margin-bottom: 15px;
}

.succession-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.succession-label {
  font-size: 12px;
  color: #666;
}

.succession-value {
  font-size: 14px;
  font-weight: 600;
  color: #0066b3;
}

.readiness-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.readiness-bar {
  width: 80px;
  height: 6px;
  background: #f0f5ff;
  border-radius: 3px;
  overflow: hidden;
}

.readiness-fill {
  height: 100%;
  background: linear-gradient(90deg, #0066b3, #0088cc);
  border-radius: 3px;
}

.readiness-value {
  font-size: 14px;
  font-weight: 600;
  color: #0066b3;
  min-width: 40px;
}

.development-actions {
  background: #f0f5ff;
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid #0066b3;
}

.actions-title {
  font-size: 12px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.actions-list {
  margin: 0;
  padding-left: 18px;
}

.actions-list li {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  line-height: 1.4;
}

/* 时间线样式优化 */
.timeline-container {
  position: relative;
  padding-left: 20px;
}
.timeline-container::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: #e6f0ff;
}
.timeline-item {
  position: relative;
  margin-bottom: 20px;
  padding-left: 10px;
}
.timeline-item:last-child {
  margin-bottom: 0;
}
.timeline-dot {
  position: absolute;
  left: -16px;
  top: 4px; /* 调整位置以对齐时间行 */
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #0066b3;
  z-index: 1;
}
.timeline-content {
  padding-bottom: 10px;
}

/* 奖惩卡片 */
.award-card {
  background: #f8fafc;
  border-radius: 8px;
  padding: 15px 10px;
  text-align: center;
  border: 1px solid #e6f0ff;
  transition: transform 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.award-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 102, 179, 0.1);
}

/* 培训经历 */
.training-list {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.training-item {
  padding-bottom: 15px;
  margin-bottom: 15px;
  border-bottom: 1px dashed #e6f0ff;
}
.training-item:last-child {
  padding-bottom: 0;
  margin-bottom: 0;
  border-bottom: none;
}

/* 信息行 */
.info-row {
  padding-bottom: 10px;
  margin-bottom: 10px;
  border-bottom: 1px solid #f0f5ff;
}
.info-row:last-child {
  padding-bottom: 0;
  margin-bottom: 0;
  border-bottom: none;
}

/* 响应式 */
@media (max-width: 1200px) {
  .row {
    flex-direction: column;
  }

  .col {
    width: 100% !important;
  }

  .header-card {
    flex-direction: column;
    gap: 20px;
    min-height: auto;
  }

  .avatar-section {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-card {
    min-height: auto;
  }

  .assessment-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .tag-item {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .talent-positioning {
    margin: 20px 0;
  }

  .positioning-ring {
    width: 80px;
    height: 80px;
  }

  .ring-inner {
    width: 60px;
    height: 60px;
  }

  .talent-score {
    font-size: 20px;
  }

  .profile-section {
    border: none !important;
    padding: 0 !important;
  }
}

/* 动画效果 */
@keyframes subtlePulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.9; }
}

.card-container > div > div:first-child svg {
  animation: subtlePulse 3s infinite ease-in-out;
  filter: drop-shadow(0 2px 4px rgba(0, 102, 179, 0.2));
}

/* 主题蓝色渐变效果 */
.theme-gradient {
  background: linear-gradient(135deg, #0066b3, #0088cc);
}

.theme-gradient-light {
  background: linear-gradient(135deg, #e6f0ff, #f0f5ff);
}

/* 在<style scoped>中添加或修改 */
@media (max-width: 1200px) {
  /* 人才评分模块在小屏幕上的调整 */
  .score-module {
    padding: 10px !important;
  }

  #radar1, #radar2, #radar3, #network {
    height: 170px !important;
  }

  .score-module > div:first-child {
    margin-bottom: 10px !important;
    padding-bottom: 6px !important;
  }

  .score-module > div:first-child > div:first-child,
  .score-module > div:first-child > div:last-child {
    font-size: 12px !important;
  }
}

/* 确保图表容器有最小宽度 */
.score-module {
  min-width: 140px;
}
</style>