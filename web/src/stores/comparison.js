import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useComparisonStore = defineStore('comparison', () => {
    const comparisonList = ref([])
    const comparisonHistory = ref([])

    const addToComparison = (talent) => {
        if (comparisonList.value.length >= 5) {
            throw new Error('对比列表最多支持5位人才')
        }

        if (!comparisonList.value.find(item => item.id === talent.id)) {
            comparisonList.value.push({
                ...talent,
                addedAt: new Date().toISOString()
            })

            // 保存到本地存储
            saveToLocalStorage()
        }
    }

    const removeFromComparison = (talentId) => {
        const index = comparisonList.value.findIndex(item => item.id === talentId)
        if (index !== -1) {
            comparisonList.value.splice(index, 1)
            saveToLocalStorage()
        }
    }

    const clearComparison = () => {
        comparisonList.value = []
        saveToLocalStorage()
    }

    const saveToHistory = (name = '未命名对比') => {
        if (comparisonList.value.length === 0) return

        const historyItem = {
            id: Date.now().toString(),
            name,
            participants: [...comparisonList.value],
            createdAt: new Date().toISOString()
        }

        comparisonHistory.value.unshift(historyItem)

        // 限制历史记录数量
        if (comparisonHistory.value.length > 10) {
            comparisonHistory.value = comparisonHistory.value.slice(0, 10)
        }

        saveHistoryToLocalStorage()
    }

    const loadFromHistory = (historyId) => {
        const historyItem = comparisonHistory.value.find(item => item.id === historyId)
        if (historyItem) {
            comparisonList.value = [...historyItem.participants]
            saveToLocalStorage()
        }
    }

    const saveToLocalStorage = () => {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('talent_comparison', JSON.stringify(comparisonList.value))
        }
    }

    const loadFromLocalStorage = () => {
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('talent_comparison')
            if (saved) {
                try {
                    comparisonList.value = JSON.parse(saved)
                } catch (error) {
                    console.error('加载对比列表失败:', error)
                }
            }
        }
    }

    const saveHistoryToLocalStorage = () => {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('talent_comparison_history', JSON.stringify(comparisonHistory.value))
        }
    }

    const loadHistoryFromLocalStorage = () => {
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('talent_comparison_history')
            if (saved) {
                try {
                    comparisonHistory.value = JSON.parse(saved)
                } catch (error) {
                    console.error('加载对比历史失败:', error)
                }
            }
        }
    }

    // 初始化时加载本地存储
    if (typeof localStorage !== 'undefined') {
        loadFromLocalStorage()
        loadHistoryFromLocalStorage()
    }

    return {
        comparisonList,
        comparisonHistory,
        addToComparison,
        removeFromComparison,
        clearComparison,
        saveToHistory,
        loadFromHistory
    }
})