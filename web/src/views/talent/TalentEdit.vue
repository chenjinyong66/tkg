<template>
  <div class="talent-edit">
    <!-- 页面标题 -->
    <div class="edit-header">
      <a-button type="text" @click="goBack" class="back-button">
        <ArrowLeftOutlined />
        返回
      </a-button>
      <h2>编辑人才信息</h2>
      <div class="header-actions">
        <a-button @click="handleReset">
          <RedoOutlined />
          重置
        </a-button>
        <a-button type="primary" @click="handleSave" :loading="saving">
          <SaveOutlined />
          保存更改
        </a-button>
      </div>
    </div>

    <!-- 编辑表单 -->
    <a-form
        ref="formRef"
        :model="formState"
        :rules="formRules"
        layout="vertical"
        class="edit-form"
        @finish="handleSave"
    >
      <a-card title="基本信息" class="form-section">
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="姓名" name="name" required>
              <a-input
                  v-model:value="formState.name"
                  placeholder="请输入人才姓名"
                  size="large"
                  :maxlength="20"
                  show-count
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="员工编号" name="employeeId" required>
              <a-input
                  v-model:value="formState.employeeId"
                  placeholder="请输入员工编号"
                  size="large"
                  :maxlength="20"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="部门" name="department">
              <a-cascader
                  v-model:value="formState.department"
                  :options="departmentOptions"
                  placeholder="请选择部门"
                  size="large"
                  allow-clear
                  show-search
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="职位" name="position">
              <a-input
                  v-model:value="formState.position"
                  placeholder="请输入职位"
                  size="large"
                  :maxlength="50"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="联系方式" name="contact">
              <a-input
                  v-model:value="formState.contact"
                  placeholder="请输入手机号"
                  size="large"
                  :maxlength="15"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="电子邮箱" name="email">
              <a-input
                  v-model:value="formState.email"
                  placeholder="请输入邮箱地址"
                  size="large"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="工作地点" name="location">
              <a-input
                  v-model:value="formState.location"
                  placeholder="请输入工作地点"
                  size="large"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="入职时间" name="joinDate">
              <a-date-picker
                  v-model:value="formState.joinDate"
                  placeholder="请选择入职时间"
                  size="large"
                  style="width: 100%"
                  :disabled-date="disabledFutureDate"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-card>

      <!-- 能力信息 -->
      <a-card title="能力信息" class="form-section">
        <a-form-item label="人才级别" name="level">
          <a-radio-group v-model:value="formState.level" button-style="solid" size="large">
            <a-radio-button value="junior">初级</a-radio-button>
            <a-radio-button value="intermediate">中级</a-radio-button>
            <a-radio-button value="senior">高级</a-radio-button>
            <a-radio-button value="expert">专家</a-radio-button>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="人才状态" name="status">
          <a-select
              v-model:value="formState.status"
              placeholder="请选择人才状态"
              size="large"
          >
            <a-select-option value="active">在职</a-select-option>
            <a-select-option value="probation">试用期</a-select-option>
            <a-select-option value="leave">休假</a-select-option>
            <a-select-option value="inactive">离职</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="专业领域" name="expertise">
          <a-select
              v-model:value="formState.expertise"
              mode="multiple"
              placeholder="请选择专业领域"
              size="large"
              :options="expertiseOptions"
              :max-tag-count="3"
              allow-clear
          />
        </a-form-item>

        <a-form-item label="技能标签" name="skills">
          <div class="skills-input-container">
            <a-select
                v-model:value="formState.skills"
                mode="tags"
                placeholder="输入技能后按回车添加，支持逗号分隔"
                size="large"
                :token-separators="[',']"
                :max-tag-count="5"
                allow-clear
            >
              <a-select-option v-for="skill in commonSkills" :key="skill" :value="skill">
                {{ skill }}
              </a-select-option>
            </a-select>
            <div class="skills-preview" v-if="formState.skills?.length > 0">
              <span class="preview-label">当前技能：</span>
              <div class="skills-tags">
                <a-tag
                    v-for="skill in formState.skills"
                    :key="skill"
                    :color="getSkillColor(skill)"
                    closable
                    @close="removeSkill(skill)"
                >
                  {{ skill }}
                </a-tag>
              </div>
            </div>
          </div>
        </a-form-item>

        <a-form-item label="综合评分" name="rating">
          <div class="rating-input">
            <a-slider
                v-model:value="formState.rating"
                :min="0"
                :max="10"
                :step="0.1"
                :marks="ratingMarks"
                style="flex: 1;"
            />
            <div class="rating-value">
              <a-input-number
                  v-model:value="formState.rating"
                  :min="0"
                  :max="10"
                  :step="0.1"
                  size="large"
                  style="width: 100px; margin-left: 16px;"
              />
            </div>
          </div>
        </a-form-item>
      </a-card>

      <!-- 附加信息 -->
      <a-card title="附加信息" class="form-section">
        <a-form-item label="备注信息" name="remarks">
          <a-textarea
              v-model:value="formState.remarks"
              placeholder="请输入备注信息"
              :rows="4"
              show-count
              :maxlength="500"
          />
        </a-form-item>

        <a-form-item label="教育背景" name="education">
          <a-textarea
              v-model:value="formState.education"
              placeholder="请输入教育背景"
              :rows="2"
              show-count
              :maxlength="200"
          />
        </a-form-item>

        <a-form-item label="工作经历" name="experience">
          <a-textarea
              v-model:value="formState.experience"
              placeholder="请输入工作经历"
              :rows="3"
              show-count
              :maxlength="300"
          />
        </a-form-item>

        <a-form-item label="证书资质" name="certificates">
          <a-textarea
              v-model:value="formState.certificates"
              placeholder="请输入证书资质"
              :rows="2"
              show-count
              :maxlength="200"
          />
        </a-form-item>
      </a-card>

      <!-- 系统信息 -->
      <a-card title="系统信息" class="form-section">
        <a-row :gutter="24">
          <a-col :span="8">
            <div class="system-info-item">
              <span class="label">创建时间：</span>
              <span class="value">{{ formatDateTime(formState.createTime) }}</span>
            </div>
          </a-col>
          <a-col :span="8">
            <div class="system-info-item">
              <span class="label">更新时间：</span>
              <span class="value">{{ formatDateTime(formState.updateTime) }}</span>
            </div>
          </a-col>
          <a-col :span="8">
            <div class="system-info-item">
              <span class="label">创建人：</span>
              <span class="value">{{ formState.creator || '系统' }}</span>
            </div>
          </a-col>
        </a-row>
      </a-card>

      <!-- 表单操作 -->
      <div class="form-actions">
        <a-space>
          <a-button @click="goBack">
            取消
          </a-button>
          <a-button @click="handleReset">
            重置
          </a-button>
          <a-button type="primary" html-type="submit" :loading="saving">
            保存更改
          </a-button>
        </a-space>
      </div>
    </a-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  ArrowLeftOutlined, SaveOutlined, RedoOutlined
} from '@ant-design/icons-vue'
import { talentApi } from '@/apis/talent_api'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const talentId = route.params.id

const formRef = ref()
const saving = ref(false)
const originalData = ref({})

// 部门选项
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
  '安全生产', '应急处理', '数据分析', '系统规划',
  '设备检修', '故障诊断', '方案设计', '技术培训'
]

// 评分刻度
const ratingMarks = {
  0: '0',
  2: '2',
  4: '4',
  6: '6',
  8: '8',
  10: '10'
}

// 表单状态
const formState = reactive({
  // 基本信息
  name: '',
  employeeId: '',
  department: [],
  position: '',
  contact: '',
  email: '',
  location: '',
  joinDate: null,

  // 能力信息
  level: 'intermediate',
  status: 'active',
  expertise: [],
  skills: [],
  rating: 0,

  // 附加信息
  remarks: '',
  education: '',
  experience: '',
  certificates: '',

  // 系统信息
  createTime: null,
  updateTime: null,
  creator: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度为2-20个字符', trigger: 'blur' }
  ],
  employeeId: [
    { required: true, message: '请输入员工编号', trigger: 'blur' },
    { min: 3, max: 20, message: '员工编号长度为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  rating: [
    { type: 'number', min: 0, max: 10, message: '评分范围为0-10', trigger: 'blur' }
  ]
}

// 工具函数
const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

const disabledFutureDate = (current) => {
  return current && current > dayjs().endOf('day')
}

const getSkillColor = (skill) => {
  const colors = [
    'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'gold', 'lime'
  ]
  const index = skill.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colors[index % colors.length]
}

// 业务函数
const loadTalentInfo = async () => {
  try {
    const response = await talentApi.getTalentDetail(talentId)
    const talent = response.talent

    if (talent) {
      // 保存原始数据
      originalData.value = { ...talent }

      // 填充表单
      Object.assign(formState, {
        name: talent.name || '',
        employeeId: talent.employeeId || '',
        department: talent.department ? (Array.isArray(talent.department) ? talent.department : [talent.department]) : [],
        position: talent.position || '',
        contact: talent.contact || '',
        email: talent.email || '',
        location: talent.location || '',
        joinDate: talent.joinDate ? dayjs(talent.joinDate) : null,
        level: talent.level || 'intermediate',
        status: talent.status || 'active',
        expertise: Array.isArray(talent.expertise) ? talent.expertise : [],
        skills: Array.isArray(talent.skills) ? talent.skills : [],
        rating: talent.rating || 0,
        remarks: talent.remarks || '',
        education: talent.education || '',
        experience: talent.experience || '',
        certificates: talent.certificates || '',
        createTime: talent.createTime,
        updateTime: talent.updateTime,
        creator: talent.creator || ''
      })
    }
  } catch (error) {
    console.error('加载人才信息失败:', error)
    message.error('加载人才信息失败')
  }
}

const goBack = () => {
  router.back()
}

const handleReset = () => {
  if (originalData.value) {
    // 重置为原始数据
    Object.assign(formState, originalData.value)

    // 处理日期字段
    if (formState.joinDate) {
      formState.joinDate = dayjs(formState.joinDate)
    }

    message.success('表单已重置')
  }
}

const removeSkill = (skill) => {
  const index = formState.skills.indexOf(skill)
  if (index !== -1) {
    formState.skills.splice(index, 1)
  }
}

const handleSave = async () => {
  try {
    // 验证表单
    await formRef.value.validate()

    saving.value = true

    // 准备数据
    const talentData = {
      ...formState,
      joinDate: formState.joinDate ? dayjs(formState.joinDate).format('YYYY-MM-DD') : null,
      rating: parseFloat(formState.rating) || 0
    }

    // 保存数据
    await talentApi.updateTalent(talentId, talentData)

    message.success('人才信息更新成功')

    // 返回上一页
    setTimeout(() => {
      router.push(`/talent/${talentId}`)
    }, 1000)

  } catch (error) {
    console.error('保存失败:', error)
    if (error.errorFields) {
      message.error('请检查表单填写是否正确')
    } else {
      message.error(error.message || '保存失败')
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadTalentInfo()
})
</script>

<style lang="less" scoped>
.talent-edit {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.edit-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  .back-button {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  h2 {
    flex: 1;
    margin: 0 24px;
    font-size: 18px;
    font-weight: 600;
    color: #1f1f1f;
  }

  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.edit-form {
  .form-section {
    margin-bottom: 24px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    :deep(.ant-card-head) {
      border-bottom: 1px solid #f0f0f0;
      background: #fafafa;
    }

    .skills-input-container {
      .skills-preview {
        margin-top: 12px;
        padding: 12px;
        background: #fafafa;
        border-radius: 4px;
        border: 1px solid #f0f0f0;

        .preview-label {
          font-size: 14px;
          color: #666;
          margin-right: 8px;
        }

        .skills-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-top: 8px;
        }
      }
    }

    .rating-input {
      display: flex;
      align-items: center;
      gap: 16px;

      .rating-value {
        min-width: 100px;
      }
    }

    .system-info-item {
      padding: 12px;
      background: #fafafa;
      border-radius: 4px;
      border: 1px solid #f0f0f0;

      .label {
        color: #666;
        font-size: 14px;
      }

      .value {
        color: #333;
        font-weight: 500;
        margin-left: 8px;
      }
    }
  }
}

.form-actions {
  padding: 24px;
  text-align: center;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

@media (max-width: 768px) {
  .edit-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;

    h2 {
      margin: 0;
      text-align: center;
    }

    .header-actions {
      justify-content: center;
    }
  }

  .edit-form {
    .ant-col {
      width: 100%;
    }

    .rating-input {
      flex-direction: column;
      align-items: stretch;

      .rating-value {
        margin-left: 0 !important;
        margin-top: 12px;
      }
    }
  }
}
</style>