<template>
  <div class="settings-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">配置</h1>
        </div>
        <div class="header-actions">
          <button 
            class="btn btn-primary btn-lg"
            @click="saveConfig" 
            :disabled="loading"
          >
            保存所有设置
          </button>
          <div v-if="saveResult" class="save-result" :class="saveResult.type">
            {{ saveResult.message }}
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Navigation -->
    <div class="settings-nav">
      <button 
        class="nav-tab"
        :class="{ 'active': activeTab === 'mappings' }"
        @click="activeTab = 'mappings'"
      >
        路径映射
      </button>
      <button 
        class="nav-tab"
        :class="{ 'active': activeTab === 'system' }"
        @click="activeTab = 'system'"
      >
        系统设置
      </button>
    </div>

    <!-- Path Mappings Tab -->
    <div v-if="activeTab === 'mappings'" class="tab-content">
      <div class="section-card">

        <!-- Add New Mapping -->
        <div class="mapping-form">
          <div class="form-title-container">
            <div class="form-title">{{ editingIndex !== -1 ? '编辑映射' : '添加新映射' }}</div>
            <router-link to="/help" class="help-link">
              <span class="help-icon">?</span>
              查看映射说明
            </router-link>
          </div>
          <div class="form-container">
            <div class="form-inputs">
              <div class="form-group">
                <label class="form-label">源路径</label>
                <input 
                  type="text" 
                  v-model="newMapping.source" 
                  placeholder="例如: /mnt/nfs/192.168.1.50#myShare/movie" 
                  class="form-input"
                >
                <small class="form-help">芝杜播放器中的路径（详见帮助）</small>
              </div>
              <div class="form-group">
                <label class="form-label">目标路径</label>
                <input 
                  type="text" 
                  v-model="newMapping.target" 
                  placeholder="例如：myNAS/myShare/movie" 
                  class="form-input"
                >
                <small class="form-help">蓝光机可识别路径，或者BlurayPoster中的Media路径</small>
              </div>
              <div class="form-group">
                <label class="form-label">STRM路径</label>
                <input 
                  type="text" 
                  v-model="newMapping.strm" 
                  placeholder="例如: /actual/path/to/strm/files (可选)" 
                  class="form-input"
                >
                <small class="form-help">用于读取STRM文件的实际文件系统路径（可选，用于STRM文件处理）</small>
              </div>
            </div>
            <div class="form-actions">
              <button 
                class="btn btn-primary"
                @click="editingIndex !== -1 ? updateMapping() : addMapping()" 
                :disabled="loading || !canAddMapping"
              >
                {{ editingIndex !== -1 ? '更新映射' : '添加映射' }}
              </button>
              <button 
                v-if="editingIndex !== -1"
                class="btn btn-outline"
                @click="cancelEdit"
              >
                取消
              </button>
            </div>
          </div>
        </div>

        <!-- Mappings List -->
        <div class="mappings-section">
          <div class="mappings-header">
            <h3>路径映射列表 ({{ pathMappings.length }})</h3>
          </div>

          <div class="mappings-table">
            <div class="table-header">
              <div class="table-col source-col">源路径</div>
              <div class="table-col target-col">目标路径</div>
              <div class="table-col strm-col">STRM路径</div>
              <div class="table-col actions-col">操作</div>
            </div>
            
            <div class="table-body">
              <div v-for="(mapping, index) in pathMappings" :key="index" class="table-row">
                <div class="table-cell source-cell">
                  <div class="cell-label">源路径</div>
                  <code>{{ mapping.source }}</code>
                </div>
                <div class="table-cell target-cell">
                  <div class="cell-label">目标路径</div>
                  <code>{{ mapping.target }}</code>
                </div>
                <div class="table-cell strm-cell">
                  <div class="cell-label">STRM路径</div>
                  <code>{{ mapping.strm || '-' }}</code>
                </div>
                <div class="table-cell actions-cell">
                  <div class="cell-label">操作</div>
                  <div class="action-buttons">
                    <button 
                      class="btn btn-sm btn-outline"
                      @click="editMapping(index)"
                      :disabled="loading"
                    >
                      编辑
                    </button>
                    <button 
                      class="btn btn-danger btn-sm" 
                      @click="removeMapping(mapping.source, mapping.target)" 
                      :disabled="loading"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="pathMappings.length === 0" class="empty-table">
              <div class="empty-text">暂无路径映射</div>
              <div class="empty-subtitle">添加第一个路径映射以开始使用</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Settings Tab -->
    <div v-if="activeTab === 'system'" class="tab-content">
      <div class="section-card">

        <div class="settings-form">
                    <!-- System Settings Grid -->
          <div class="settings-grid">
            <!-- 第一列 -->
            <div class="form-group">
              <label class="form-label">芝杜IP地址</label>
              <input 
                type="text" 
                v-model="zidooIp" 
                placeholder="192.168.1.99"
                class="form-input"
                pattern="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
              >
              <small class="form-help">Zidoo设备的IP地址</small>
            </div>
            
            <div class="form-group">
              <label class="form-label">心跳频率</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model="heartRate" 
                  min="200" 
                  max="2000"
                  step="100"
                  class="form-input"
                >
                <span class="input-suffix">ms</span>
              </div>
              <small class="form-help">检查Zidoo状态的频率，最小200ms，最大2000ms</small>
            </div>
            
            <!-- 第二行 -->
            <div class="form-group">
              <label class="form-label">通知IP地址</label>
              <input 
                type="text" 
                v-model="notificationIp" 
                placeholder="192.168.1.50"
                class="form-input"
              >
              <small class="form-help">BlurayPoster的IP地址</small>
            </div>
            
            <div class="form-group">
              <label class="form-label">超时时间</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model="notificationTimeout" 
                  min="1" 
                  max="60"
                  class="form-input"
                >
                <span class="input-suffix">秒</span>
              </div>
              <small class="form-help">通知超时时间</small>
            </div>
            
            <!-- 第三行 -->
            <div class="form-group">
              <label class="form-label">日志级别</label>
              <select v-model="logLevel" class="form-select">
                <option value="DEBUG">DEBUG - 详细调试信息</option>
                <option value="INFO">INFO - 一般信息</option>
                <option value="WARNING">WARNING - 警告信息</option>
                <option value="ERROR">ERROR - 错误信息</option>
                <option value="CRITICAL">CRITICAL - 严重错误</option>
              </select>
              <small class="form-help">控制日志输出的详细程度</small>
            </div>
            
            <!-- 第四行 -->
            <div class="form-group">
              <label class="form-label">自动启动监控</label>
              <div class="setting-toggle">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    id="autoStart"
                    v-model="autoStart"
                  >
                  <span class="switch-slider"></span>
                </label>
              </div>
              <small class="form-help">启用后，应用启动时会自动启动监控服务，无需手动启动</small>
            </div>
            
            <!-- 第五行 -->
            <div class="form-group">
              <label class="form-label">CloudDrive挂载路径</label>
              <input 
                type="text" 
                v-model="clouddriveMountPath" 
                placeholder="/mnt/smb/192.168.1.50#cloud/CloudDrive/115"
                class="form-input"
              >
              <small class="form-help">用于拼接STRM文件中的相对路径，获得实际播放地址</small>
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
import { ref, computed, onMounted } from 'vue'
import { useWatcherStore } from '../stores/watcher'

const store = useWatcherStore()

// Reactive data
const activeTab = ref('mappings')
const editingIndex = ref(-1)
const newMapping = ref({
  source: '',
  target: '',
  strm: ''
})

const saveResult = ref(null)

// Computed properties
const pathMappings = computed(() => store.pathMappings || [])
const config = computed(() => store.config || {})
const loading = computed(() => store.loading || false)
const error = computed(() => store.error || null)



const canAddMapping = computed(() => {
  return newMapping.value.source.trim() && newMapping.value.target.trim()
})

// Form data computed properties
const heartRate = computed({
  get: () => config.value?.general?.heart_rate || 500,
  set: (value) => {
    if (!store.config) store.config = {}
    if (!store.config.general) store.config.general = {}
    store.config.general.heart_rate = parseInt(value)
  }
})

const logLevel = computed({
  get: () => config.value?.general?.log_level || 'INFO',
  set: (value) => {
    if (!store.config) store.config = {}
    if (!store.config.general) store.config.general = {}
    store.config.general.log_level = value
  }
})

const autoStart = computed({
  get: () => config.value?.general?.auto_start || false,
  set: (value) => {
    if (!store.config) store.config = {}
    if (!store.config.general) store.config.general = {}
    store.config.general.auto_start = value
  }
})

const zidooIp = computed({
  get: () => config.value?.zidoo?.ip || '192.168.1.99',
  set: (value) => {
    if (!store.config) store.config = {}
    if (!store.config.zidoo) store.config.zidoo = {}
    store.config.zidoo.ip = value
  }
})

// 端口固定为9529，不需要用户配置

const notificationIp = computed({
  get: () => {
    const endpoint = config.value?.notification?.endpoint || 'http://192.168.1.50:7507/play'
    // 从完整URL中提取IP地址
    const match = endpoint.match(/http:\/\/([^:]+):\d+\/play/)
    return match ? match[1] : '192.168.1.50'
  },
  set: (value) => {
    if (!store.config) store.config = {}
    if (!store.config.notification) store.config.notification = {}
    // 自动拼接端口和路径
    const cleanIp = value.trim()
    if (cleanIp) {
      store.config.notification.endpoint = `http://${cleanIp}:7507/play`
    } else {
      store.config.notification.endpoint = 'http://192.168.1.50:7507/play'
    }
  }
})

const notificationTimeout = computed({
  get: () => config.value?.notification?.timeout_seconds || 10,
  set: (value) => {
    if (!store.config) store.config = {}
    if (!store.config.notification) store.config.notification = {}
    store.config.notification.timeout_seconds = parseInt(value)
  }
})

const clouddriveMountPath = computed({
  get: () => config.value?.clouddrive?.mount_path || '',
  set: (value) => {
    if (!store.config) store.config = {}
    if (!store.config.clouddrive) store.config.clouddrive = {}
    store.config.clouddrive.mount_path = value
  }
})

// Methods
const addMapping = async () => {
  if (canAddMapping.value) {
    await store.addPathMapping(
      newMapping.value.source.trim(), 
      newMapping.value.target.trim(), 
      true,
      newMapping.value.strm?.trim() || null
    )
    newMapping.value = { source: '', target: '', strm: '' }
  }
}

const editMapping = (index) => {
  const mapping = pathMappings.value[index]
  newMapping.value = { 
    source: mapping.source, 
    target: mapping.target,
    strm: mapping.strm || ''
  }
  editingIndex.value = index
}

const updateMapping = async () => {
  if (canAddMapping.value && editingIndex.value !== -1) {
    const oldMapping = pathMappings.value[editingIndex.value]
    // Remove the old mapping
    await store.removePathMapping(oldMapping.source, oldMapping.target)
    // Add the updated mapping
    await store.addPathMapping(
      newMapping.value.source.trim(), 
      newMapping.value.target.trim(), 
      oldMapping.enable || true,
      newMapping.value.strm?.trim() || null
    )
    cancelEdit()
  }
}

const cancelEdit = () => {
  newMapping.value = { source: '', target: '', strm: '' }
  editingIndex.value = -1
}

const removeMapping = (source, target) => {
  store.removePathMapping(source, target)
}

const saveConfig = async () => {
  try {
    await store.updateConfig(config.value)
    saveResult.value = { type: 'success', message: '配置保存成功！' }
    setTimeout(() => {
      saveResult.value = null
    }, 3000)
  } catch (err) {
    saveResult.value = { type: 'error', message: '配置保存失败: ' + err.message }
    setTimeout(() => {
      saveResult.value = null
    }, 5000)
  }
}



const clearError = () => {
  store.clearError()
}

// Lifecycle
onMounted(async () => {
  await store.fetchConfig()
  await store.fetchPathMappings()
})
</script>

<style scoped>
.settings-page {
  width: 100%;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 1.5rem;
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
  color: #ffffff;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 1rem;
  flex-shrink: 0;
}

.save-result {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  white-space: nowrap;
}

.save-result.success {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.save-result.error {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* Settings Navigation */
.settings-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  padding: 0.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.nav-tab {
  display: block;
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  text-align: center;
  min-width: 0;
}

.nav-tab:hover {
  background: rgba(59, 130, 246, 0.2);
  color: #f1f5f9;
}

.nav-tab.active {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}



/* Tab Content */
.tab-content {
  animation: fadeIn 0.3s ease;
  width: 100%;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Section Card */
.section-card {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.2);
  overflow: hidden;
  width: 100%;
}



/* Forms */
.settings-form,
.mapping-form {
  padding: 2rem;
  max-width: none;
  width: 100%;
}

.section-card > .settings-form:first-child,
.section-card > .mapping-form:first-child {
  padding-top: 2rem;
}

.form-container {
  max-width: none;
  width: 100%;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: repeat(4, auto);
  gap: 2rem;
  width: 100%;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(6, auto);
  }
}

.form-title-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.form-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}

.help-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  color: #93c5fd;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.help-link:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
  border-color: rgba(59, 130, 246, 0.5);
  color: #dbeafe;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.2);
}

.help-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
}



.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-start;
  align-items: center;
  padding-top: 0.5rem;
  flex-wrap: wrap;
}

.form-actions .btn {
  min-width: 120px;
  justify-content: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 120px;
  justify-content: flex-start;
}



.form-label {
  font-size: 0.875rem;
  color: #e2e8f0;
  font-weight: 600;
}

.form-input,
.form-select {
  padding: 0.75rem 1rem;
  border: 2px solid rgba(148, 163, 184, 0.3);
  border-radius: 0.75rem;
  font-size: 0.875rem;
  background: rgba(15, 23, 42, 0.6);
  color: #f1f5f9;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-group {
  position: relative;
  display: flex;
}

.input-group .form-input {
  border-radius: 0.75rem 0 0 0.75rem;
  border-right: none;
}

.input-suffix {
  background: #f9fafb;
  border: 2px solid rgba(148, 163, 184, 0.3);
  border-left: none;
  border-radius: 0 0.75rem 0.75rem 0;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #cbd5e1;
  font-weight: 500;
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.4);
}

.form-help {
  font-size: 0.75rem;
  color: #cbd5e1;
  margin-top: 0.25rem;
}





/* Mappings */
.mappings-section {
  padding: 2rem;
}

.mappings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.mappings-header h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
}

/* Mappings Table */
.mappings-table {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.75rem;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.6);
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.table-col {
  padding: 1rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #e2e8f0;
  text-align: left;
}

.source-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.target-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.strm-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.actions-col {
  text-align: center;
}

.table-body {
  /* Empty styles for now */
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s ease;
}

.table-row:hover {
  background: rgba(139, 92, 246, 0.02);
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
}

.cell-label {
  display: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.source-cell {
  border-right: 1px solid #f3f4f6;
}

.target-cell {
  border-right: 1px solid #f3f4f6;
}

.strm-cell {
  border-right: 1px solid #f3f4f6;
}

.actions-cell {
  justify-content: center;
}

.table-cell code {
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 
    'Menlo', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
  font-size: 0.875rem;
  background: rgba(59, 130, 246, 0.1);
  color: #f1f5f9;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  word-break: break-all;
}

/* Empty States */
.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #6b7280;
  text-align: center;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
}



.empty-text {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #e2e8f0;
}

.empty-subtitle {
  font-size: 1rem;
  color: #94a3b8;
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

.btn-success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

.btn-warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.btn-warning:hover:not(:disabled) {
  background: linear-gradient(135deg, #d97706, #b45309);
}

.btn-outline {
  background: rgba(59, 130, 246, 0.1);
  color: #f1f5f9;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.btn-outline:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.2);
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
  background: white;
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
  color: #1f2937;
}

.error-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
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
  background: #f3f4f6;
  color: #1f2937;
}

.error-message {
  padding: 1.5rem;
  color: #1f2937;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .mappings-table {
    border: none;
    background: transparent;
  }
  
  .table-header {
    display: none;
  }
  
  .table-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .table-row {
    display: flex;
    flex-direction: column;
    gap: 0;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 0.75rem;
    background: rgba(15, 23, 42, 0.6);
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .table-cell {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    border-right: none;
    border-bottom: 1px solid rgba(148, 163, 184, 0.15);
    padding: 1.25rem;
  }
  
  .table-cell:last-child {
    border-bottom: none;
  }
  
  .cell-label {
    display: block;
    margin-bottom: 0.75rem;
  }
  
  .actions-cell {
    justify-content: flex-start;
    background: rgba(15, 23, 42, 0.3);
  }
  
  .action-buttons {
    width: 100%;
    justify-content: flex-start;
  }
}

/* Switch 开关样式 */
.setting-toggle {
  display: flex;
  align-items: center;
}

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

@media (max-width: 768px) {
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
  
  .table-cell code {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
  
  .table-body {
    gap: 0.5rem;
  }
  
  .table-row {
    border-radius: 0.5rem;
  }
  
  .table-cell {
    padding: 0.75rem;
  }
  
  .cell-label {
    margin-bottom: 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .action-buttons .btn {
    width: 100%;
    justify-content: center;
  }
  
  .settings-nav {
    padding: 0.25rem;
  }
  
  .nav-tab {
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
  }
  
  .form-inputs {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .mappings-table {
    border-radius: 0.5rem;
  }
  
  .table-body {
    gap: 0.75rem;
  }
  
  .table-row {
    border-radius: 0.5rem;
  }
  
  .table-cell {
    padding: 1rem;
  }
  
  .table-cell code {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
    word-break: break-word;
  }
}

@media (max-width: 480px) {
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
  
  .section-header,
  .settings-form,
  .mapping-form,
  .mappings-section {
    padding: 1rem;
  }
  
  .settings-nav {
    padding: 0.25rem;
    gap: 0.25rem;
  }
  
  .nav-tab {
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
  }
  
  .actions-cell {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn {
    justify-content: center;
  }
  
  .form-title-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .help-link {
    align-self: flex-start;
    font-size: 0.8rem;
    padding: 0.375rem 0.5rem;
  }
  
  .help-icon {
    width: 1rem;
    height: 1rem;
    font-size: 0.7rem;
  }
}
</style> 