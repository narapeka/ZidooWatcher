import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useWatcherStore = defineStore('watcher', () => {
  // State
  const serviceStatus = ref({
    is_running: false,
    is_paused: false,
    last_status: null,
    last_notified_path: null
  })
  
  const currentStatus = ref({
    status: 'stopped',
    video_path: null,
    zidoo_status: null,
    title: null,
    position: 0,
    duration: 0,
    timestamp: null,
    connectivity: 'unknown'
  })
  
  const logs = ref([])
  const config = ref({
    general: {
      enable_watcher: true,
      heart_rate: 500,
      log_level: 'INFO'
    },
    zidoo: {
      ip: '192.168.1.99',
      api_path: '/ZidooVideoPlay/getPlayStatus'
    },
    notification: {
      endpoint: 'http://192.168.1.50:7507/play',
      timeout_seconds: 10
    },
    extension_monitoring: {
      bdmv: true,
      iso: true,
      mkv: false,
      mp4: false
    }
  })
  
  const pathMappings = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Polling state
  const polling = ref({
    logs: false,
    status: false,
    intervals: {
      logs: null,
      status: null
    },
    lastLogId: 0,
    retryCount: 0,
    maxRetries: 5
  })
  

  
  // Computed
  const isRunning = computed(() => serviceStatus.value.is_running)
  
  // Polling methods
  const startLogPolling = (intervalMs = 2000) => {
    if (polling.value.logs) return // Already polling
    
    polling.value.logs = true
    polling.value.retryCount = 0
    
    const pollLogs = async () => {
      try {
        const response = await axios.get('/api/logs/recent', {
          params: { since_id: polling.value.lastLogId }
        })
        
        if (response.data.success && response.data.logs.length > 0) {
          // Add new logs
          response.data.logs.forEach(log => {
            addLog(log)
          })
          
          // Update last log ID
          polling.value.lastLogId = response.data.latest_id
        }
        
        // Reset retry count on success
        polling.value.retryCount = 0
        
      } catch (err) {
        console.error('Log polling error:', err)
        polling.value.retryCount++
        
        // Exponential backoff
        if (polling.value.retryCount <= polling.value.maxRetries) {
          const delay = Math.min(intervalMs * Math.pow(2, polling.value.retryCount - 1), 30000)
          setTimeout(() => {
            if (polling.value.logs) {
              pollLogs()
            }
          }, delay)
          return
        } else {
          console.error('Max retries reached for log polling')
          stopLogPolling()
        }
      }
      
      // Schedule next poll
      if (polling.value.logs) {
        polling.value.intervals.logs = setTimeout(pollLogs, intervalMs)
      }
    }
    
    // Start polling immediately
    pollLogs()
  }
  
  const stopLogPolling = () => {
    polling.value.logs = false
    if (polling.value.intervals.logs) {
      clearTimeout(polling.value.intervals.logs)
      polling.value.intervals.logs = null
    }
  }
  
  const startStatusPolling = (intervalMs = 3000) => {
    if (polling.value.status) return // Already polling
    
    polling.value.status = true
    polling.value.retryCount = 0
    
    const pollStatus = async () => {
      try {
        const response = await axios.get('/api/status/current')
        
        if (response.data.success) {
          // Update service status
          if (response.data.service_status) {
            serviceStatus.value = response.data.service_status
          }
          
          // Update current status
          if (response.data.current_status) {
            updateCurrentStatus(response.data.current_status)
          }
        }
        
        // Reset retry count on success
        polling.value.retryCount = 0
        
      } catch (err) {
        console.error('Status polling error:', err)
        polling.value.retryCount++
        
        // Exponential backoff
        if (polling.value.retryCount <= polling.value.maxRetries) {
          const delay = Math.min(intervalMs * Math.pow(2, polling.value.retryCount - 1), 30000)
          setTimeout(() => {
            if (polling.value.status) {
              pollStatus()
            }
          }, delay)
          return
        } else {
          console.error('Max retries reached for status polling')
          stopStatusPolling()
        }
      }
      
      // Schedule next poll
      if (polling.value.status) {
        polling.value.intervals.status = setTimeout(pollStatus, intervalMs)
      }
    }
    
    // Start polling immediately
    pollStatus()
  }
  
  const stopStatusPolling = () => {
    polling.value.status = false
    if (polling.value.intervals.status) {
      clearTimeout(polling.value.intervals.status)
      polling.value.intervals.status = null
    }
  }
  
  const startPolling = () => {
    startLogPolling(2000)    // Poll logs every 2 seconds
    startStatusPolling(3000) // Poll status every 3 seconds
  }
  
  const stopPolling = () => {
    stopLogPolling()
    stopStatusPolling()
  }
  
  // Actions
  const fetchServiceStatus = async () => {
    try {
      loading.value = true
      const response = await axios.get('/api/service/status')
      serviceStatus.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching service status:', err)
    } finally {
      loading.value = false
    }
  }
  
  const startService = async () => {
    try {
      loading.value = true
      await axios.post('/api/service/start')
      await fetchServiceStatus()
    } catch (err) {
      error.value = err.message
      console.error('Error starting service:', err)
    } finally {
      loading.value = false
    }
  }
  
  const stopService = async () => {
    try {
      loading.value = true
      await axios.post('/api/service/stop')
      await fetchServiceStatus()
    } catch (err) {
      error.value = err.message
      console.error('Error stopping service:', err)
    } finally {
      loading.value = false
    }
  }
  
  const fetchConfig = async () => {
    try {
      const response = await axios.get('/api/config')
      config.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching config:', err)
    }
  }
  
  const updateConfig = async (newConfig) => {
    try {
      loading.value = true
      await axios.post('/api/config', newConfig)
      await fetchConfig()
    } catch (err) {
      error.value = err.message
      console.error('Error updating config:', err)
    } finally {
      loading.value = false
    }
  }

  const updateExtensionMonitoring = async (extensionData) => {
    try {
      loading.value = true
      await axios.put('/api/extension-monitoring', extensionData)
      await fetchConfig()
    } catch (err) {
      error.value = err.message
      console.error('Error updating extension monitoring:', err)
    } finally {
      loading.value = false
    }
  }

  const toggleExtensionMonitoring = async (extension, enable) => {
    try {
      loading.value = true
      const extensionData = { [extension]: enable }
      await axios.put('/api/extension-monitoring', extensionData)
      await fetchConfig()
    } catch (err) {
      error.value = err.message
      console.error('Error toggling extension monitoring:', err)
    } finally {
      loading.value = false
    }
  }
  
  const fetchPathMappings = async () => {
    try {
      const response = await axios.get('/api/mappings')
      pathMappings.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching path mappings:', err)
    }
  }
  
    const addPathMapping = async (source, target, enable = true) => {
    try {
      loading.value = true
      await axios.post('/api/mappings', { 
        source, 
        target, 
        enable 
      })
      await fetchPathMappings()
    } catch (err) {
      error.value = err.message
      console.error('Error adding path mapping:', err)
    } finally {
      loading.value = false
    }
  }

  const removePathMapping = async (source, target) => {
    try {
      loading.value = true
      await axios.delete('/api/mappings', { 
        data: { 
          source, 
          target 
        } 
      })
      await fetchPathMappings()
    } catch (err) {
      error.value = err.message
      console.error('Error removing path mapping:', err)
    } finally {
      loading.value = false
    }
  }

  const togglePathMapping = async (source, target, enable) => {
    try {
      loading.value = true
      await axios.put('/api/mappings/toggle', { 
        source, 
        target, 
        enable 
      })
      await fetchPathMappings()
    } catch (err) {
      error.value = err.message
      console.error('Error toggling path mapping:', err)
    } finally {
      loading.value = false
    }
  }
  
  const addLog = (logData) => {
    // Handle both old WebSocket format and new polling format
    const log = {
      id: logData.id || Date.now(),
      type: logData.type || 'log',
      level: logData.level || 'INFO',
      message: logData.message,
      timestamp: logData.timestamp || new Date().toISOString()
    }
    
    logs.value.push(log)
    
    // Keep only last 1000 logs to prevent memory issues
    if (logs.value.length > 1000) {
      logs.value.splice(0, logs.value.length - 1000)
    }
  }

  const clearLogs = async () => {
    try {
      await axios.post('/api/logs/clear')
      logs.value = []
      polling.value.lastLogId = 0
    } catch (err) {
      error.value = err.message
      console.error('Error clearing logs:', err)
    }
  }
  
  const updateCurrentStatus = (status) => {
    currentStatus.value = { ...currentStatus.value, ...status }
  }
  
  const clearError = () => {
    error.value = null
  }
  
  return {
    // State
    serviceStatus,
    currentStatus,
    logs,
    config,
    pathMappings,
    loading,
    error,
    
    // Computed
    isRunning,
    
    // Polling
    polling,
    startPolling,
    stopPolling,
    
    // Actions
    fetchServiceStatus,
    startService,
    stopService,
    fetchConfig,
    updateConfig,
    updateExtensionMonitoring,
    toggleExtensionMonitoring,
    fetchPathMappings,
    addPathMapping,
    removePathMapping,
    togglePathMapping,
    addLog,
    clearLogs,
    updateCurrentStatus,
    clearError
  }
}) 