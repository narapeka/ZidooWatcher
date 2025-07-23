<template>
  <div class="logs-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">日志</h1>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary btn-lg" @click="clearLogs">
            清空日志
          </button>
        </div>
      </div>
    </div>

        <!-- Log Controls -->
    <div class="log-controls">
      <div class="control-group">
        <div class="filter-group">
          <label class="filter-label">日志级别:</label>
          <select v-model="selectedLevel" class="filter-select">
            <option value="">全部</option>
            <option value="DEBUG">DEBUG - 详细调试信息</option>
            <option value="INFO">INFO - 一般信息</option>
            <option value="WARNING">WARNING - 警告信息</option>
            <option value="ERROR">ERROR - 错误信息</option>
            <option value="CRITICAL">CRITICAL - 严重错误</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">自动滚动:</label>
          <label class="toggle-switch">
            <input type="checkbox" v-model="autoScroll">
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>

      <div class="action-group">
        <button 
          v-if="connectionStatus === 'disconnected' || connectionStatus === 'error'"
          class="btn btn-primary btn-sm"
          @click="manualReconnect"
        >
          重新连接
        </button>
      </div>
    </div>

    <!-- Log Container -->
    <div class="log-container">
      <div class="log-header">
        <div class="log-col-time">时间</div>
        <div class="log-col-level">级别</div>
        <div class="log-col-message">消息</div>
      </div>
      
      <div class="log-content" ref="logContainer">
        <div 
          v-for="(log, index) in displayedLogs" 
          :key="`${log.timestamp}-${index}`"
          class="log-entry"
          :class="`log-${log.level?.toLowerCase()}`"
        >
          <div class="log-meta">
            <div class="log-time">{{ formatLogTime(log.timestamp) }}</div>
            <div class="log-level">
              <span class="level-badge" :class="`level-${log.level?.toLowerCase()}`">
                {{ log.level }}
              </span>
            </div>
          </div>
          <div class="log-message">{{ log.message }}</div>
        </div>
        
        <div v-if="displayedLogs.length === 0" class="empty-state">
          <div class="empty-text">暂无日志数据</div>
          <div class="empty-subtitle">系统运行时的日志将在这里显示</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useWatcherStore } from '../stores/watcher'

const store = useWatcherStore()

// Reactive data
const selectedLevel = ref('')
const autoScroll = ref(true)
const maxLogs = ref(1000)
const isPaused = ref(false)
const connectionStatus = ref('disconnected')
const lastUpdate = ref(null)

// Refs
const logContainer = ref(null)

// Connection state (for polling)

// Computed properties
const logs = computed(() => store.logs || [])
const totalLogs = computed(() => logs.value.length)

const filteredLogs = computed(() => {
  let filtered = logs.value
  
  if (selectedLevel.value) {
    filtered = filtered.filter(log => log.level === selectedLevel.value)
  }
  
  return filtered.slice(0, maxLogs.value)
})

const displayedLogs = computed(() => {
  return filteredLogs.value.slice().reverse()
})

const connectionText = computed(() => {
  switch (connectionStatus.value) {
    case 'connected': return '已连接'
    case 'connecting': return '连接中'
    case 'disconnected': return '已断开'
    case 'error': return '连接错误'
    default: return '未知状态'
  }
})

// Methods
const getLogCount = (level) => {
  return logs.value.filter(log => log.level === level).length
}

const clearLogs = () => {
  store.clearLogs()
}

const pauseResume = () => {
  isPaused.value = !isPaused.value
}

const downloadLogs = () => {
  const logData = filteredLogs.value.map(log => {
    return `${formatLogTime(log.timestamp)} [${log.level}] ${log.message}`
  }).join('\n')
  
  const blob = new Blob([logData], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `zidoo-watcher-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const formatLogTime = (timestamp) => {
  try {
    if (typeof timestamp === 'string') {
      return new Date(timestamp).toLocaleTimeString()
    }
    return new Date(timestamp).toLocaleTimeString()
  } catch (error) {
    return '时间格式错误'
  }
}

const scrollToBottom = () => {
  if (autoScroll.value && logContainer.value) {
    nextTick(() => {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    })
  }
}

// WebSocket connection
const setupPolling = () => {
  connectionStatus.value = 'connecting'
  
  // Start polling
  store.startPolling()
  
  // Monitor polling status
  watch(() => store.polling.logs, (isPolling) => {
    if (isPolling) {
    connectionStatus.value = 'connected'
    lastUpdate.value = new Date().toISOString()
    } else {
      connectionStatus.value = 'disconnected'
    }
  }, { immediate: true })
  
  // Update lastUpdate when new logs arrive
  watch(() => store.logs.length, () => {
      if (!isPaused.value) {
          lastUpdate.value = new Date().toISOString()
          scrollToBottom()
    }
  })
}

// Watch for changes that should trigger scroll
watch([displayedLogs, autoScroll], () => {
  scrollToBottom()
}, { deep: true })

// Lifecycle
onMounted(() => {
  setupPolling()
})

onUnmounted(() => {
  store.stopPolling()
})
</script>

<style scoped>
.logs-page {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 4rem);
}

/* Page Header */
.page-header {
  margin-bottom: 1.5rem;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.header-text {
  flex: 1;
  min-width: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
  background: linear-gradient(135deg, #fff, #e2e8f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

/* Log Controls */
.log-controls {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.2);
  flex-shrink: 0;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
  flex: 1;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group:last-child {
  margin-left: auto;
}

.filter-label {
  font-size: 0.875rem;
  color: #e2e8f0;
  font-weight: 500;
  white-space: nowrap;
}

.filter-select {
  padding: 0.25rem 0.75rem;
  border: 2px solid rgba(148, 163, 184, 0.3);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: rgba(15, 23, 42, 0.6);
  color: #f1f5f9;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #e5e7eb;
  border-radius: 24px;
  transition: 0.3s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .toggle-slider {
  background: #3b82f6;
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}



.action-group {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  white-space: nowrap;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.btn-warning:hover:not(:disabled) {
  background: linear-gradient(135deg, #d97706, #b45309);
}

.btn-lg {
  padding: 0.4375rem 1.25rem;
  font-size: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
}

/* Log Container */
.log-container {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.log-header {
  display: grid;
  grid-template-columns: 150px 100px 1fr;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: rgba(15, 23, 42, 0.6);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  font-weight: 600;
  color: #e2e8f0;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.log-entry {
  display: grid;
  grid-template-columns: 150px 100px 1fr;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  font-size: 0.875rem;
  align-items: center;
  transition: background-color 0.2s ease;
}

.log-entry:hover {
  background: rgba(148, 163, 184, 0.1);
}

.log-entry:last-child {
  border-bottom: none;
}

.log-meta {
  display: contents;
}

.log-time {
  color: #cbd5e1;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 
    'Menlo', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
  font-size: 0.8rem;
  white-space: nowrap;
}

.log-level {
  display: flex;
  justify-content: flex-start;
}

.level-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
  min-width: 60px;
}

.level-debug {
  background: rgba(107, 114, 128, 0.1);
  color: #4b5563;
  border: 1px solid rgba(107, 114, 128, 0.2);
}

.level-info {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.level-warning {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.level-error,
.level-critical {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.log-message {
  color: #f1f5f9;
  word-break: break-word;
  line-height: 1.4;
}

/* Log Level Row Styling */
.log-debug {
  background: rgba(107, 114, 128, 0.02);
}

.log-info {
  background: rgba(59, 130, 246, 0.02);
}

.log-warning {
  background: rgba(245, 158, 11, 0.02);
}

.log-error,
.log-critical {
  background: rgba(239, 68, 68, 0.02);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #6b7280;
  text-align: center;
}



.empty-text {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #f1f5f9;
}

.empty-subtitle {
  font-size: 1rem;
  color: #cbd5e1;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .log-header,
  .log-entry {
    grid-template-columns: 120px 80px 1fr;
  }
}

@media (max-width: 768px) and (min-width: 481px) {
  .logs-page {
    height: calc(100vh - 6rem);
  }
  
  .page-header {
    text-align: center;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1.5rem;
  }
  
  .header-actions {
    align-items: stretch;
  }
  
  .header-actions .btn {
    justify-content: center;
  }
  
  .log-controls {
    padding: 1rem;
    gap: 1rem;
  }
  
  .control-group {
    gap: 1.5rem;
    flex: 1;
  }
  
  .filter-group {
    gap: 0.75rem;
  }
  
  .filter-group:last-child {
    margin-left: 0;  /* 移动端取消右对齐 */
  }
  
  .filter-label {
    font-size: 0.8rem;
    min-width: 60px;
  }
  
  .action-group {
    gap: 0.5rem;
  }
  
  .log-header {
    display: none;
  }
  
  .log-entry {
    display: block;
    padding: 1rem;
    background: rgba(15, 23, 42, 0.4);
    margin-bottom: 0.5rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(148, 163, 184, 0.1);
  }
  
  .log-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  
  .log-time {
    font-size: 0.75rem;
  }
  
  .log-level {
    justify-content: flex-start;
  }
  
  .level-badge {
    font-size: 0.65rem;
  }
  
  .log-message {
    font-size: 0.875rem;
    line-height: 1.5;
  }
}

@media (max-width: 480px) {
  .logs-page {
    height: calc(100vh - 6rem);
  }
  
  .page-header {
    text-align: center;
  }
  
  .page-title {
    font-size: 1.125rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1.5rem;
  }
  
  .header-actions {
    align-items: stretch;
  }
  
  .header-actions .btn {
    justify-content: center;
  }
  
  .log-controls {
    padding: 0.75rem;
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .control-group {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .filter-group {
    justify-content: space-between;
    padding: 0.5rem 0;
  }
  
  .filter-group:last-child {
    margin-left: 0;  /* 小屏移动端也取消右对齐 */
  }
  
  .action-group {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .log-header {
    display: none;
  }
  
  .log-entry {
    display: block;
    padding: 0.875rem;
    background: rgba(15, 23, 42, 0.4);
    margin-bottom: 0.5rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(148, 163, 184, 0.1);
  }
  
  .log-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.625rem;
  }
  
  .log-time {
    font-size: 0.7rem;
  }
  
  .log-level {
    justify-content: flex-start;
  }
  
  .level-badge {
    font-size: 0.6rem;
    padding: 0.125rem 0.375rem;
  }
  
  .log-message {
    font-size: 0.8rem;
    line-height: 1.4;
  }
  
  .filter-label {
    font-size: 0.875rem;
    min-width: auto;
  }
  
  .action-group {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .btn:not(.btn-lg) {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
  }
}



/* Custom Scrollbar */
.log-content::-webkit-scrollbar {
  width: 8px;
}

.log-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
}
</style> 