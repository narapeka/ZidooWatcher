<template>
  <div class="dashboard-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">主页</h1>
    </div>

        <!-- Service Control Panel -->
    <div class="card service-control-card">
      <div class="card-header">
        <h3>服务控制</h3>
        <div class="status-badge" :class="statusClass">
          {{ statusText }}
        </div>
      </div>
      <div class="card-content">
        <div class="control-actions">
          <button
            class="btn btn-primary"
            @click="startService"
            :disabled="loading || store.isRunning"
          >
            启动服务
          </button>

          <button
            class="btn btn-danger"
            @click="stopService"
            :disabled="loading || !store.isRunning"
          >
            停止服务
          </button>
        </div>
        
        <!-- 设备连接状态 -->
        <div class="status-footer">
          <div class="footer-item">
            <span class="footer-label">设备连接:</span>
            <span class="footer-value" :class="getConnectivityClass(currentStatus?.connectivity)">
              {{ currentStatus?.connectivity ? getConnectivityText(currentStatus.connectivity) : '未知' }}
            </span>
          </div>
          <div class="footer-item">
            <span class="footer-label">最后更新:</span>
            <span class="footer-value">
              {{ currentStatus?.timestamp ? formatTimestamp(currentStatus.timestamp) : '无数据' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboard Grid -->
    <div class="dashboard-grid">
      <!-- Path Mappings Quick Control -->
      <div class="card mappings-card">
        <div class="card-header">
          <h3>监控目录</h3>
        </div>
        
        <div class="card-content">
          <div class="mappings-list" v-if="sortedPathMappings.length > 0">
            <div class="mapping-list-container">
              <div v-for="(mapping, index) in sortedPathMappings" :key="index" class="mapping-item">
                <div class="mapping-info">
                  <span class="mapping-type-badge" :class="(mapping.mapping_type || 'media') === 'media' ? 'badge-media' : 'badge-strm'">
                    {{ (mapping.mapping_type || 'media') === 'media' ? '媒体' : 'STRM' }}
                  </span>
                  <div class="mapping-source">{{ mapping.source }}</div>
                  <div class="mapping-arrow">→</div>
                  <div class="mapping-target">{{ mapping.target }}</div>
                </div>
                <div class="mapping-toggle">
                  <label class="switch">
                    <input 
                      type="checkbox" 
                      :checked="mapping.enable"
                      @change="toggleMapping(mapping.source, mapping.mapping_type || 'media', mapping.target, $event.target.checked)"
                      :disabled="loading"
                    >
                    <span class="switch-slider"></span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <div class="empty-text">暂无路径映射</div>
            <router-link to="/settings" class="btn btn-primary btn-sm">
              去设置
            </router-link>
          </div>
        </div>
      </div>

      <!-- Extension Monitoring Card -->
      <div class="card extension-monitoring-card">
        <div class="card-header">
          <h3>监控扩展名</h3>
        </div>
        
        <div class="card-content">
          <div class="extension-list">
            <div class="extension-item">
              <div class="extension-info">
                <div class="extension-name">BDMV</div>
                <div class="extension-desc">蓝光文件夹</div>
              </div>
              <div class="extension-toggle">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    :checked="config.extension_monitoring?.bdmv"
                    @change="toggleExtension('bdmv', $event.target.checked)"
                    :disabled="loading"
                  >
                  <span class="switch-slider"></span>
                </label>
              </div>
            </div>
            
            <div class="extension-item">
              <div class="extension-info">
                <div class="extension-name">ISO</div>
                <div class="extension-desc">光盘镜像</div>
              </div>
              <div class="extension-toggle">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    :checked="config.extension_monitoring?.iso"
                    @change="toggleExtension('iso', $event.target.checked)"
                    :disabled="loading"
                  >
                  <span class="switch-slider"></span>
                </label>
              </div>
            </div>
            
            <div class="extension-item">
              <div class="extension-info">
                <div class="extension-name">MKV</div>
                <div class="extension-desc">Matroska视频</div>
              </div>
              <div class="extension-toggle">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    :checked="config.extension_monitoring?.mkv"
                    @change="toggleExtension('mkv', $event.target.checked)"
                    :disabled="loading"
                  >
                  <span class="switch-slider"></span>
                </label>
              </div>
            </div>
            
            <div class="extension-item">
              <div class="extension-info">
                <div class="extension-name">MP4</div>
                <div class="extension-desc">MPEG-4视频</div>
              </div>
              <div class="extension-toggle">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    :checked="config.extension_monitoring?.mp4"
                    @change="toggleExtension('mp4', $event.target.checked)"
                    :disabled="loading"
                  >
                  <span class="switch-slider"></span>
                </label>
              </div>
            </div>
            
            <div class="extension-item">
              <div class="extension-info">
                <div class="extension-name">M2TS</div>
                <div class="extension-desc">蓝光视频流</div>
              </div>
              <div class="extension-toggle">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    :checked="config.extension_monitoring?.m2ts"
                    @change="toggleExtension('m2ts', $event.target.checked)"
                    :disabled="loading"
                  >
                  <span class="switch-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Modal -->
    <div v-if="error" class="error-modal" @click="clearError">
      <div class="error-content" @click.stop>
        <div class="error-header">
          <h3>错误信息</h3>
          <button class="error-close" @click="clearError">×</button>
        </div>
        <div class="error-message">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useWatcherStore } from '../stores/watcher'

const store = useWatcherStore()

// Computed properties
const statusClass = computed(() => {
  return store.isRunning ? 'status-running' : 'status-stopped'
})

const statusText = computed(() => {
  return store.isRunning ? '运行中' : '已停止'
})

const currentStatus = computed(() => store.currentStatus || {})
const pathMappings = computed(() => store.pathMappings || [])
const sortedPathMappings = computed(() => {
  const mappings = [...pathMappings.value]
  return mappings.sort((a, b) => {
    const aType = a.mapping_type || 'media'
    const bType = b.mapping_type || 'media'
    // Media type comes first
    if (aType === 'media' && bType === 'strm') return -1
    if (aType === 'strm' && bType === 'media') return 1
    return 0
  })
})
const config = computed(() => store.config || {})
const loading = computed(() => store.loading || false)
const error = computed(() => store.error || null)

// Methods
const startService = () => store.startService()
const stopService = () => store.stopService()

const toggleMapping = (source, mappingType, target, enable) => {
  store.togglePathMapping(source, mappingType || 'media', target, enable)
}

const toggleExtension = (extension, enable) => {
  store.toggleExtensionMonitoring(extension, enable)
}

const clearError = () => {
  store.clearError()
}

const getConnectivityClass = (connectivity) => {
  if (!connectivity) return 'status-unknown'
  switch (connectivity) {
    case 'online': return 'status-online'
    case 'offline': return 'status-offline'
    case 'error': return 'status-error'
    default: return 'status-unknown'
  }
}

const getConnectivityText = (connectivity) => {
  if (!connectivity) return '未知'
  switch (connectivity) {
    case 'online': return '在线'
    case 'offline': return '离线'
    case 'error': return '错误'
    default: return '未知'
  }
}

const formatTimestamp = (timestamp) => {
  try {
    // 直接使用浏览器本地时区
    const date = new Date(timestamp * 1000)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMins < 1) {
      return '刚刚'
    } else if (diffMins < 60) {
      return `${diffMins}分钟前`
    } else if (diffHours < 24) {
      return `${diffHours}小时前`
    } else if (diffDays < 7) {
      return `${diffDays}天前`
    } else {
      // 超过7天显示具体日期（使用浏览器本地时区）
      return date.toLocaleDateString('zh-CN', {
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  } catch (error) {
    console.error('时间格式化错误:', error)
    return '时间错误'
  }
}

// Lifecycle
onMounted(async () => {
  await store.fetchServiceStatus()
  await store.fetchConfig()
  await store.fetchPathMappings()
  store.startPolling()
})

onUnmounted(() => {
  store.stopPolling()
})
</script>

<style scoped>
.dashboard-page {
  width: 100%;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* Service Control */
.service-control-card {
  margin-bottom: 1.5rem;
}

.control-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

/* Cards */
.card {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.2);
  overflow: hidden;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.card-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 有status-badge的卡片头部减少padding以保持一致高度 */
.service-control-card .card-header,
.status-card .card-header {
  padding: 0.75rem 1.5rem;
}

.card-header h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
}

.status-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}



.card-content {
  padding: 1.5rem;
}

/* Status Card */
.playing-status {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.idle-status {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 1rem;
}

.idle-message {
  text-align: center;
  color: #64748b;
}

.idle-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 0.5rem;
}

.idle-subtitle {
  font-size: 0.875rem;
  color: #64748b;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.status-label {
  font-size: 0.875rem;
  color: #cbd5e1;
  font-weight: 500;
}

.status-value {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
}

.title-value {
  color: #3b82f6;
  font-weight: 500;
}

.status-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  gap: 1rem;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.footer-label {
  color: #94a3b8;
  font-weight: 500;
}

.footer-value {
  color: #e2e8f0;
  font-weight: 600;
}

.path-value code {
  background: rgba(59, 130, 246, 0.1);
  color: #f1f5f9;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  word-break: break-all;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  color: #cbd5e1;
}

/* Mappings Card */



.mapping-list-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mapping-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.5rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.mapping-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.mapping-source,
.mapping-target {
  font-size: 0.875rem;
  color: #e2e8f0;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 
    'Menlo', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  word-break: break-all;
  flex: 1;
}

.mapping-arrow {
  color: #3b82f6;
  font-weight: bold;
}

.mapping-type-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem 0.875rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 60px;
  width: 60px;
}

.badge-media {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.15));
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
}

.badge-strm {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.15));
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.4);
  box-shadow: 0 2px 4px rgba(139, 92, 246, 0.1);
}

.mapping-toggle {
  display: flex;
  align-items: center;
}

/* Extension Monitoring Card */
.extension-list {
  display: flex;
  flex-direction: row;
  gap: 1rem;
  justify-content: space-between;
}

.extension-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.5rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  flex: 1;
  min-width: 0;
}

.extension-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.extension-name {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
}

.extension-desc {
  font-size: 0.75rem;
  color: #94a3b8;
}

.extension-toggle {
  display: flex;
  align-items: center;
}

/* Switch 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #e5e7eb;
  transition: all 0.3s ease;
  border-radius: 24px;
  border: 1px solid #d1d5db;
}

.switch-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background: white;
  transition: all 0.3s ease;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

input:checked + .switch-slider {
  background: #3b82f6;
  border-color: #1d4ed8;
}

input:checked + .switch-slider:before {
  transform: translateX(24px);
}

input:disabled + .switch-slider {
  opacity: 0.5;
  cursor: not-allowed;
}

.switch-slider:hover {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Status Colors */
.status-running {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.status-playing {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.status-stopped {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.status-offline {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.status-error {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.status-paused {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.status-unknown {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.status-online {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

.btn-outline {
  background: rgba(59, 130, 246, 0.2);
  color: #f1f5f9;
  border: 1px solid rgba(59, 130, 246, 0.5);
}

.btn-outline:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.3);
  color: #ffffff;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #6b7280;
  text-align: center;
}



.empty-text {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

/* Error Modal */
.error-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.error-content {
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 1rem;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.error-header h3 {
  margin: 0;
  color: #f1f5f9;
}

.error-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #cbd5e1;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.error-close:hover {
  background: rgba(148, 163, 184, 0.2);
  color: #f1f5f9;
}

.error-message {
  padding: 1.5rem;
  color: #e2e8f0;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .mapping-item {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 0;
    padding: 1.5rem;
    padding-top: 4rem; /* Space for badge and toggle row */
  }
  
  .mapping-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    align-items: flex-start !important;
    margin-top: 0.5rem; /* Additional spacing after badge/toggle row */
    width: 100%;
  }
  
  .mapping-source,
  .mapping-target {
    text-align: left !important;
    align-self: flex-start !important;
    width: 100%;
    flex: none;
  }
  
  .mapping-arrow {
    text-align: left !important;
    align-self: flex-start !important;
    margin: 0.125rem 0;
  }
  
  /* Position badge and toggle on same line at top */
  .mapping-info .mapping-type-badge {
    position: absolute;
    top: 1.5rem;
    left: 1.5rem;
    margin: 0;
  }
  
  .mapping-toggle {
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
    justify-content: flex-end;
    margin: 0;
  }
  
  .extension-list {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .extension-item {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }
  
  .extension-info {
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
  }
  
  .extension-toggle {
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .page-header {
    text-align: center;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  

  
  .control-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.125rem;
  }
  
  .card-header {
    padding: 0.75rem 1rem;
  }
  
  /* 移动端有status-badge的卡片头部进一步减少padding */
  .service-control-card .card-header,
  .status-card .card-header {
    padding: 0.5rem 1rem;
  }
  
  .control-actions {
    flex-direction: column;
  }
  
  .btn {
    justify-content: center;
  }
  
  .status-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .footer-item {
    justify-content: space-between;
    padding: 0.5rem 0;
  }
  
  .idle-status {
    padding: 1.5rem 1rem;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style> 