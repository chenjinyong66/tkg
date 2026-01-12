/**
 * 人才搜索工具函数
 * 提供与人才搜索相关的数据处理和格式化功能
 */

/**
 * 格式化搜索结果为表格所需的数据格式
 * @param {Array} results - 原始搜索结果
 * @returns {Array} 格式化后的数据
 */
export const formatTalentSearchResults = (results = []) => {
  if (!Array.isArray(results)) {
    return [];
  }

  return results.map((talent, index) => ({
    id: talent.id || index,
    key: talent.id || `${index}-${Date.now()}`,
    name: talent.name || talent.talent_name || talent.entity_name || '未知',
    position: talent.position || talent.title || talent.role || '-',
    department: talent.department || talent.org || '-',
    skills: Array.isArray(talent.skills) ? talent.skills : 
             typeof talent.skills === 'string' ? talent.skills.split(',') : 
             Array.isArray(talent.skill_list) ? talent.skill_list : 
             [],
    experience: talent.experience || talent.years_of_experience || '-',
    education: talent.education || talent.education_background || '-',
    contact: talent.contact || talent.email || talent.phone || '-',
    status: talent.status || 'active',
    created_at: talent.created_at || talent.created_time || new Date().toISOString(),
    updated_at: talent.updated_at || talent.updated_time || new Date().toISOString()
  }));
};

/**
 * 根据搜索查询解析过滤条件
 * @param {string} query - 搜索查询
 * @returns {Object} 解析出的过滤条件
 */
export const parseSearchQueryFilters = (query = '') => {
  const filters = {};
  
  if (!query) {
    return filters;
  }

  // 示例：解析查询中的特定关键词
  const lowerQuery = query.toLowerCase();
  
  // 按技能搜索
  if (lowerQuery.includes('技能') || lowerQuery.includes('skill')) {
    const skillMatch = query.match(/(?:技能|skill)[：:]\s*([^，,]+)/i);
    if (skillMatch) {
      filters.skill = skillMatch[1].trim();
    }
  }
  
  // 按部门搜索
  if (lowerQuery.includes('部门') || lowerQuery.includes('dept')) {
    const deptMatch = query.match(/(?:部门|dept)[：:]\s*([^，,]+)/i);
    if (deptMatch) {
      filters.department = deptMatch[1].trim();
    }
  }
  
  // 按职位搜索
  if (lowerQuery.includes('职位') || lowerQuery.includes('position')) {
    const positionMatch = query.match(/(?:职位|position)[：:]\s*([^，,]+)/i);
    if (positionMatch) {
      filters.position = positionMatch[1].trim();
    }
  }
  
  // 检查是否包含"高级"、"中级"、"初级"等关键词
  if (lowerQuery.includes('高级')) {
    filters.seniority = 'senior';
  } else if (lowerQuery.includes('中级')) {
    filters.seniority = 'intermediate';
  } else if (lowerQuery.includes('初级')) {
    filters.seniority = 'junior';
  }
  
  return filters;
};

/**
 * 生成搜索建议
 * @param {string} input - 用户输入
 * @returns {Array} 搜索建议列表
 */
export const generateSearchSuggestions = (input = '') => {
  if (!input.trim()) {
    return [
      '搜索具有JavaScript技能的人才',
      '查找技术部门的高级工程师',
      '寻找有5年以上经验的产品经理',
      '查询AI领域的专家'
    ];
  }

  const suggestions = [];
  const lowerInput = input.toLowerCase();

  // 根据输入生成相关建议
  if (lowerInput.includes('技能') || lowerInput.includes('skill')) {
    suggestions.push(
      `${input} 方面的专家`,
      `具备 ${input} 能力的人才`,
      `${input} 相关职位`
    );
  }

  if (lowerInput.includes('部门') || lowerInput.includes('team')) {
    suggestions.push(
      `${input} 优秀人才`,
      `${input} 技能要求`,
      `${input} 团队成员`
    );
  }

  // 默认建议
  if (suggestions.length === 0) {
    suggestions.push(
      `${input} 相关人才`,
      `具备 ${input} 技能的人才`,
      `搜索 ${input}`
    );
  }

  return suggestions.slice(0, 5); // 限制返回5个建议
};

/**
 * 验证搜索参数
 * @param {Object} params - 搜索参数
 * @returns {Object} { valid: boolean, errors: Array }
 */
export const validateSearchParams = (params = {}) => {
  const errors = [];

  // 验证查询字段
  if (!params.query || typeof params.query !== 'string' || params.query.trim().length === 0) {
    errors.push('搜索查询不能为空');
  }

  // 验证分页参数
  if (params.page && (typeof params.page !== 'number' || params.page < 1)) {
    errors.push('页码必须是大于0的数字');
  }

  if (params.limit && (typeof params.limit !== 'number' || params.limit < 1 || params.limit > 100)) {
    errors.push('每页数量必须是1-100之间的数字');
  }

  // 验证过滤条件
  if (params.filters) {
    if (params.filters.skill && typeof params.filters.skill !== 'string') {
      errors.push('技能过滤条件必须是字符串');
    }
    if (params.filters.department && typeof params.filters.department !== 'string') {
      errors.push('部门过滤条件必须是字符串');
    }
    if (params.filters.position && typeof params.filters.position !== 'string') {
      errors.push('职位过滤条件必须是字符串');
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
};

/**
 * 处理搜索结果统计
 * @param {Array} results - 搜索结果
 * @returns {Object} 统计信息
 */
export const getSearchResultsStats = (results = []) => {
  if (!Array.isArray(results)) {
    return {
      total: 0,
      departments: {},
      positions: {},
      skills: {},
      seniorityDistribution: {}
    };
  }

  const stats = {
    total: results.length,
    departments: {},
    positions: {},
    skills: {},
    seniorityDistribution: {}
  };

  results.forEach(talent => {
    // 统计部门分布
    const dept = talent.department || '未知';
    stats.departments[dept] = (stats.departments[dept] || 0) + 1;

    // 统计职位分布
    const position = talent.position || '未知';
    stats.positions[position] = (stats.positions[position] || 0) + 1;

    // 统计技能分布
    const skills = Array.isArray(talent.skills) ? talent.skills : 
                   typeof talent.skills === 'string' ? talent.skills.split(',') : [];
    
    skills.forEach(skill => {
      const skillName = skill.trim();
      if (skillName) {
        stats.skills[skillName] = (stats.skills[skillName] || 0) + 1;
      }
    });

    // 统计经验分布（如果提供经验信息）
    if (talent.experience) {
      let expRange = '未知';
      const exp = parseInt(talent.experience);
      if (!isNaN(exp)) {
        if (exp < 2) expRange = '0-2年';
        else if (exp < 5) expRange = '2-5年';
        else if (exp < 10) expRange = '5-10年';
        else expRange = '10年以上';
      }
      stats.seniorityDistribution[expRange] = (stats.seniorityDistribution[expRange] || 0) + 1;
    }
  });

  return stats;
};

/**
 * 导出搜索结果为CSV格式
 * @param {Array} results - 搜索结果
 * @param {Array} columns - 列定义
 * @returns {string} CSV格式字符串
 */
export const exportResultsToCSV = (results = [], columns = []) => {
  if (!Array.isArray(results) || results.length === 0) {
    return '';
  }

  // 生成CSV头部
  const headers = columns.map(col => `"${col.title}"`).join(',');
  
  // 生成CSV数据行
  const rows = results.map(item => {
    return columns.map(col => {
      let value = item[col.dataIndex] || '';
      if (Array.isArray(value)) {
        value = value.join(';');
      }
      // 转义CSV中的特殊字符
      value = String(value).replace(/"/g, '""');
      return `"${value}"`;
    }).join(',');
  });

  return [headers, ...rows].join('\n');
};