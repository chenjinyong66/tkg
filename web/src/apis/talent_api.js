import {apiGet, apiPost, apiDelete, apiPut} from './base'

/**
 * 人才员工考核文件管理API模块
 * 包含考核文件管理、员工信息、知识图谱等功能
 * 权限要求: 任何已登录用户（普通用户、管理员、超级管理员）
 */

export const talentApi = {
    /**
     * 获取人才列表
     * @returns {Promise} - 人才列表
     */
    getTalents: () => apiGet('/api/talent/talents'),

    /**
     * 获取人才详情
     * @param {string} talentId - 人才ID
     * @returns {Promise} - 人才详情
     */
    getTalentDetail: (talentId) => apiGet(`/api/talent/talents/${talentId}`),

    /**
     * 创建人才
     * @param {Object} data - 人才信息
     * @returns {Promise} - 创建结果
     */
    createTalent: (data) => apiPost('/api/talent/talents', data),

    /**
     * 更新人才信息
     * @param {string} talentId - 人才ID
     * @param {Object} data - 更新数据
     * @returns {Promise} - 更新结果
     */
    updateTalent: (talentId, data) => apiPut(`/api/talent/talents/${talentId}`, data),

    /**
     * 删除人才
     * @param {string} talentId - 人才ID
     * @returns {Promise} - 删除结果
     */
    deleteTalent: (talentId) => apiDelete(`/api/talent/talents/${talentId}`),

    /**
     * 获取考核文件列表
     * @returns {Promise} - 考核文件列表
     */
    getTalentFiles: () => apiGet('/api/talent/files'),

    /**
     * 获取特定人才的考核文件列表
     * @param {string} talentId - 人才ID
     * @returns {Promise} - 考核文件列表
     */
    getTalentFilesByTalent: (talentId) => apiGet(`/api/talent/talents/${talentId}/files`),

    /**
     * 上传考核文件
     * @param {FormData} formData - 包含文件和员工信息的表单数据
     * @returns {Promise} - 上传结果
     */
    uploadTalentFile: (formData) => {
        return apiPost('/api/talent/upload', formData)
    },

    /**
     * 删除考核文件
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 删除结果
     */
    deleteTalentFile: (fileId) => apiDelete(`/api/talent/files/${fileId}`),

    /**
     * 获取考核文件详情
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 文件详情
     */
    getTalentFileDetail: (fileId) => apiGet(`/api/talent/files/${fileId}`),

    /**
     * 获取员工考核信息
     * @param {string} employeeId - 员工ID
     * @returns {Promise} - 员工考核信息
     */
    getEmployeeReview: (employeeId) => apiGet(`/api/talent/employee/${employeeId}/review`),

    /**
     * 更新员工考核信息
     * @param {string} employeeId - 员工ID
     * @param {Object} data - 更新数据
     * @returns {Promise} - 更新结果
     */
    updateEmployeeReview: (employeeId, data) => apiPut(`/api/talent/employee/${employeeId}/review`, data),

    /**
     * 解析考核文件为Markdown
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 解析结果
     */
    parseFileToMarkdown: (fileId) => apiPost(`/api/talent/files/${fileId}/parse`),

    /**
     * 获取解析后的Markdown内容
     * @param {string} fileId - 文件ID
     * @returns {Promise} - Markdown内容
     */
    getMarkdownContent: (fileId) => apiGet(`/api/talent/files/${fileId}/markdown`),

    /**
     * 直接获取文件内容（适用于文本文件）
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 文件内容
     */
    getFileContent: (fileId) => apiGet(`/api/talent/files/${fileId}/content`),

    /**
     * 更新Markdown内容
     * @param {string} fileId - 文件ID
     * @param {string} content - Markdown内容
     * @returns {Promise} - 更新结果
     */
    updateMarkdownContent: (fileId, content) => apiPut(`/api/talent/files/${fileId}/markdown`, {content}),

    /**
     * 从Markdown内容抽取知识图谱
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 图谱抽取结果
     */
    extractKnowledgeGraph: (fileId) => apiPost(`/api/talent/files/${fileId}/extract-graph`),

    /**
     * 获取知识图谱数据
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 图谱数据
     */
    getKnowledgeGraph: (fileId) => apiGet(`/api/talent/files/${fileId}/graph`),

    /**
     * 获取员工考核历史
     * @param {string} employeeId - 员工ID
     * @returns {Promise} - 考核历史
     */
    getEmployeeReviewHistory: (employeeId) => apiGet(`/api/talent/employee/${employeeId}/history`),

    /**
     * 获取部门考核统计
     * @param {string} department - 部门名称
     * @returns {Promise} - 统计结果
     */
    getDepartmentReviewStats: (department) => apiGet(`/api/talent/department/${department}/stats`),

    /**
     * 导出考核报告
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 导出结果
     */
    exportReviewReport: (fileId) => apiGet(`/api/talent/files/${fileId}/export`, {}, true, 'blob'),

    /**
     * 获取统计信息
     * @returns {Promise} - 统计信息
     */
    getStats: () => apiGet('/api/talent/stats'),

    /**
     * 批量删除人才
     * @param {Array} ids - 人才ID列表
     * @returns {Promise} - 批量删除结果
     */
    batchDeleteTalents: (ids) => apiPost('/api/talents/batch-delete', {ids}),

    /**
     * 获取人才统计
     * @param {string} id - 人才ID
     * @returns {Promise} - 统计信息
     */
    getTalentStats: (id) => apiGet(`/api/talents/${id}/stats`),

    /**
     * 获取人才雷达图数据
     * @param {string} id - 人才ID
     * @returns {Promise} - 雷达图数据
     */
    getTalentRadar: (id) => apiGet(`/api/talents/${id}/radar`),

    /**
     * 更新人才技能
     * @param {string} id - 人才ID
     * @param {Array} skills - 技能列表
     * @returns {Promise} - 更新结果
     */
    updateTalentSkills: (id, skills) => apiPut(`/api/talents/${id}/skills`, {skills}),

    /**
     * 添加人才备注
     * @param {string} id - 人才ID
     * @param {Object} note - 备注内容
     * @returns {Promise} - 添加结果
     */
    addTalentNote: (id, note) => apiPost(`/api/talents/${id}/notes`, {note}),

    /**
     * 归档人才
     * @param {string} id - 人才ID
     * @returns {Promise} - 归档结果
     */
    archiveTalent: (id) => apiPost(`/api/talents/${id}/archive`),

    /**
     * 导出人才报告
     * @param {string} id - 人才ID
     * @returns {Promise} - 导出结果
     */
    exportTalentReport: (id) => apiGet(`/api/talents/${id}/report`, {}, true, 'blob'),

    /**
     * 下载人才文件
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 下载结果
     */
    downloadTalentFile: (fileId) => apiGet(`/api/files/${fileId}/download`, {}, true, 'blob'),

    /**
     * 重命名人才文件
     * @param {string} fileId - 文件ID
     * @param {string} newName - 新文件名
     * @returns {Promise} - 重命名结果
     */
    renameTalentFile: (fileId, newName) => apiPut(`/api/files/${fileId}/rename`, {filename: newName}),

    /**
     * 批量删除文件
     * @param {Array} fileIds - 文件ID列表
     * @returns {Promise} - 批量删除结果
     */
    batchDeleteFiles: (fileIds) => apiPost('/api/files/batch-delete', {fileIds}),

    /**
     * 获取内容分析统计
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 分析统计
     */
    getContentStats: (fileId) => apiGet(`/api/files/${fileId}/analysis`),

    /**
     * 批量解析文件
     * @param {Array} fileIds - 文件ID列表
     * @returns {Promise} - 批量解析结果
     */
    batchParseFiles: (fileIds) => apiPost('/api/files/batch-parse', {fileIds}),

    /**
     * 导出人才列表
     * @param {Array} ids - 人才ID列表
     * @returns {Promise} - 导出结果
     */
    exportTalents: (ids) => apiGet('/api/talents/export', {params: {ids: ids.join(',')}}, true, 'blob'),

    /**
     * 导出图谱数据
     * @param {string} fileId - 文件ID
     * @returns {Promise} - 导出结果
     */
    exportGraphData: (fileId) => apiGet(`/api/files/${fileId}/export-graph`, {}, true, 'blob'),

    /**
     * 获取人才综合评分
     * @param {string} id - 人才ID
     * @returns {Promise} - 综合评分信息
     */
    getTalentOverallRating: (id) => apiGet(`/api/talents/${id}/overall-rating`),

    /**
     * 获取团队对比数据
     * @param {string} id - 人才ID
     * @param {string} timeRange - 时间范围
     * @returns {Promise} - 团队对比数据
     */
    getTeamComparison: (id, timeRange) => apiGet(`/api/talents/${id}/team-comparison`, { params: { timeRange } }),

    /**
     * 获取人才趋势数据
     * @param {string} id - 人才ID
     * @param {Object} params - 查询参数
     * @returns {Promise} - 趋势数据
     */
    getTalentTrend: (id, params) => apiGet(`/api/talents/${id}/trend`, { params }),

    /**
     * 获取人才详细分析
     * @param {string} id - 人才ID
     * @param {string} timeRange - 时间范围
     * @returns {Promise} - 详细分析数据
     */
    getTalentAnalysis: (id, timeRange) => apiGet(`/api/talents/${id}/analysis`, { params: { timeRange } }),

    /**
     * 获取人才改进建议
     * @param {string} id - 人才ID
     * @returns {Promise} - 改进建议
     */
    getTalentSuggestions: (id) => apiGet(`/api/talents/${id}/suggestions`),

    /**
     * 导出人才分析报告
     * @param {string} id - 人才ID
     * @param {Object} params - 报告参数
     * @returns {Promise} - 报告文件
     */
    exportTalentAnalysisReport: (id, params) => apiGet(`/api/talents/${id}/analysis/report`, { params }, true, 'blob'),

    /**
     * 提交人才评估
     * @param {string} id - 人才ID
     * @param {Object} data - 评估数据
     * @returns {Promise} - 提交结果
     */
    submitTalentAssessment: (id, data) => apiPost(`/api/talents/${id}/assessment`, data),

    /**
     * 删除评估
     * @param {string} assessmentId - 评估ID
     * @returns {Promise} - 删除结果
     */
    deleteAssessment: (assessmentId) => apiDelete(`/api/assessments/${assessmentId}`),

    /**
     * 更新评估
     * @param {string} assessmentId - 评估ID
     * @param {Object} data - 更新数据
     * @returns {Promise} - 更新结果
     */
    updateAssessment: (assessmentId, data) => apiPut(`/api/assessments/${assessmentId}`, data),

    /**
     * 添加评估
     * @param {string} talentId - 人才ID
     * @param {Object} data - 评估数据
     * @returns {Promise} - 添加结果
     */
    addAssessment: (talentId, data) => apiPost(`/api/talents/${talentId}/assessments`, data),

    /**
     * 标记建议为完成
     * @param {string} suggestionId - 建议ID
     * @returns {Promise} - 操作结果
     */
    markSuggestionDone: (suggestionId) => apiPost(`/api/suggestions/${suggestionId}/done`)

}