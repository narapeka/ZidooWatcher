<template>
  <div class="settings-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">配置</h1>
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
      <!-- Add Mapping Form -->
      <div v-if="showMappingForm" class="section-card mapping-form-card">
        <div class="form-header">
          <div class="form-header-left">
            <h3 class="section-title">添加新映射</h3>
            <span class="mapping-type-badge" :class="newMapping.mappingType === 'media' ? 'badge-media' : 'badge-strm'">
              {{ newMapping.mappingType === 'media' ? '媒体' : 'STRM' }}
            </span>
          </div>
          <button class="btn-icon" @click="cancelEdit" title="关闭">
            <span>×</span>
          </button>
        </div>
        
        <div class="form-container">
          <div class="form-inputs">
            <div class="form-group">
              <label class="form-label">源路径</label>
              <input 
                type="text" 
                v-model="newMapping.source" 
                :placeholder="newMapping.mappingType === 'media' ? '例如: /mnt/smb/192.168.1.50#myShare/movie' : '例如: /mnt/smb/192.168.1.50#myShare/strm'" 
                class="form-input"
              >
              <small class="form-help">芝杜播放器中的路径（详见帮助）</small>
            </div>
            <div class="form-group">
              <label class="form-label">
                <span v-if="newMapping.mappingType === 'media'">目标路径</span>
                <span v-else>STRM路径</span>
              </label>
              <input 
                type="text" 
                v-model="newMapping.target" 
                :placeholder="newMapping.mappingType === 'media' ? '例如：/myNAS/myShare/movie' : '例如: /myNAS/myShare/strm'" 
                class="form-input"
              >
              <small class="form-help">
                <span v-if="newMapping.mappingType === 'media'">蓝光机可识别路径，或者BlurayPoster中的Media路径</span>
                <span v-else>用于读取STRM文件的实际文件系统路径</span>
              </small>
            </div>
          </div>
          <div class="form-actions">
            <button 
              class="btn btn-primary"
              @click="addMapping()" 
              :disabled="loading || !canAddMapping"
            >
              保存
            </button>
            <button 
              class="btn btn-outline"
              @click="cancelEdit"
            >
              取消
            </button>
          </div>
        </div>
      </div>

      <!-- Mappings List Section -->
      <div class="section-card mappings-list-card">
        <div class="mappings-header">
          <div class="mappings-header-left">
            <h3 class="section-title">路径映射</h3>
          </div>
          <div class="mappings-header-right">
            <router-link to="/help" class="help-link">
              <span class="help-icon">?</span>
              查看映射说明
            </router-link>
            <div v-if="editingIndex === -1" class="menu-button-wrapper">
              <button 
                class="btn btn-primary"
                @click="showMappingMenu = !showMappingMenu"
                :class="{ 'menu-open': showMappingMenu }"
              >
                添加映射
                <span class="menu-arrow">▼</span>
              </button>
              <div v-if="showMappingMenu" class="menu-dropdown" @click.stop>
                <button 
                  class="menu-item"
                  @click="startAddMapping('media')"
                >
                  <span class="menu-item-icon">📁</span>
                  添加媒体路径映射
                </button>
                <button 
                  class="menu-item"
                  @click="startAddMapping('strm')"
                >
                  <span class="menu-item-icon">📄</span>
                  添加STRM文件映射
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="mappings-table">
          <div class="table-header">
            <div class="table-col type-col">类型</div>
            <div class="table-col source-col">源路径</div>
            <div class="table-col target-col">目标路径</div>
            <div class="table-col actions-col">操作</div>
          </div>
          
          <div class="table-body">
            <div 
              v-for="(mapping, index) in pathMappings" 
              :key="index" 
              class="table-row"
              :class="{ 'editing': editingIndex === index }"
            >
              <div class="table-cell type-cell">
                <div class="cell-label">类型</div>
                <span class="mapping-type-badge" :class="(mapping.mapping_type || 'media') === 'media' ? 'badge-media' : 'badge-strm'">
                  {{ (mapping.mapping_type || 'media') === 'media' ? '媒体' : 'STRM' }}
                </span>
              </div>
              <div class="table-cell source-cell">
                <div class="cell-label">源路径</div>
                <code v-if="editingIndex !== index">{{ mapping.source }}</code>
                <input 
                  v-else
                  type="text" 
                  v-model="editingMapping.source" 
                  class="inline-input"
                  @keyup.enter="saveInlineEdit(index)"
                  @keyup.esc="cancelInlineEdit"
                >
              </div>
              <div class="table-cell target-cell">
                <div class="cell-label">
                  <span v-if="(mapping.mapping_type || 'media') === 'media'">目标路径</span>
                  <span v-else>STRM路径</span>
                </div>
                <code v-if="editingIndex !== index">{{ mapping.target || '-' }}</code>
                <input 
                  v-else
                  type="text" 
                  v-model="editingMapping.target" 
                  class="inline-input"
                  @keyup.enter="saveInlineEdit(index)"
                  @keyup.esc="cancelInlineEdit"
                >
              </div>
              <div class="table-cell actions-cell">
                <div class="cell-label">操作</div>
                <div class="action-buttons" v-if="editingIndex !== index">
                  <button 
                    class="btn btn-sm btn-outline"
                    @click="startInlineEdit(index)"
                    :disabled="loading"
                  >
                    编辑
                  </button>
                  <button 
                    class="btn btn-danger btn-sm" 
                    @click="removeMapping(mapping.source, mapping.mapping_type || 'media', mapping.target)" 
                    :disabled="loading"
                  >
                    删除
                  </button>
                </div>
                <div class="action-buttons" v-else>
                  <button 
                    class="btn btn-sm btn-success"
                    @click="saveInlineEdit(index)"
                    :disabled="loading || !canSaveInlineEdit"
                  >
                    保存
                  </button>
                  <button 
                    class="btn btn-sm btn-outline" 
                    @click="cancelInlineEdit"
                    :disabled="loading"
                  >
                    取消
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="pathMappings.length === 0" class="empty-table">
            <div class="empty-icon">📋</div>
            <div class="empty-text">暂无路径映射</div>
            <div class="empty-subtitle">点击"添加映射"按钮创建第一个路径映射</div>
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
          
          <!-- Save Button -->
          <div class="settings-form-actions">
            <button 
              class="btn btn-primary btn-lg"
              @click="saveConfig" 
              :disabled="loading"
            >
              保存系统设置
            </button>
            <div v-if="saveResult" class="save-result" :class="saveResult.type">
              {{ saveResult.message }}
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWatcherStore } from '../stores/watcher'

const store = useWatcherStore()

// Reactive data
const activeTab = ref('mappings')
const editingIndex = ref(-1)
const showMappingMenu = ref(false)
const showMappingForm = ref(false)
const newMapping = ref({
  mappingType: 'media',
  source: '',
  target: ''
})
const editingMapping = ref({
  source: '',
  target: '',
  mapping_type: 'media'
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

const canSaveInlineEdit = computed(() => {
  return editingMapping.value.source.trim() && editingMapping.value.target.trim()
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
const startAddMapping = (mappingType) => {
  newMapping.value = { mappingType, source: '', target: '' }
  showMappingMenu.value = false
  showMappingForm.value = true
}

const addMapping = async () => {
  if (canAddMapping.value) {
    await store.addPathMapping(
      newMapping.value.source.trim(),
      newMapping.value.mappingType,
      newMapping.value.target.trim(),
      true
    )
    cancelEdit()
  }
}

const startInlineEdit = (index) => {
  const mapping = pathMappings.value[index]
  editingMapping.value = {
    source: mapping.source,
    target: mapping.target || '',
    mapping_type: mapping.mapping_type || 'media'
  }
  editingIndex.value = index
}

const saveInlineEdit = async (index) => {
  if (!canSaveInlineEdit.value) return
  
  const oldMapping = pathMappings.value[index]
  const mappingType = editingMapping.value.mapping_type
  
  // Update the mapping in place (preserves order)
  await store.updatePathMapping(
    oldMapping.source,
    mappingType,
    oldMapping.target,
    editingMapping.value.source.trim(),
    editingMapping.value.target.trim()
  )
  
  cancelInlineEdit()
}

const cancelInlineEdit = () => {
  editingIndex.value = -1
  editingMapping.value = {
    source: '',
    target: '',
    mapping_type: 'media'
  }
}

const cancelEdit = () => {
  newMapping.value = { mappingType: 'media', source: '', target: '' }
  editingIndex.value = -1
  showMappingForm.value = false
  showMappingMenu.value = false
  cancelInlineEdit()
}

const removeMapping = (source, mappingType, target) => {
  store.removePathMapping(source, mappingType, target)
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

// Close menu when clicking outside
const handleClickOutside = (event) => {
  if (showMappingMenu.value && !event.target.closest('.menu-button-wrapper')) {
    showMappingMenu.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await store.fetchConfig()
  await store.fetchPathMappings()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
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
.settings-form {
  padding: 2rem;
  max-width: none;
  width: 100%;
}

.mapping-form-card {
  margin-bottom: 1.5rem;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  margin-bottom: 2rem;
}

.settings-form-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  margin-top: 1rem;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(6, auto);
  }
  
  .settings-form-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .settings-form-actions .btn {
    width: 100%;
    justify-content: center;
  }
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.form-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.form-header .mapping-type-badge {
  font-size: 0.875rem;
  padding: 0.375rem 0.875rem;
}

.btn-icon {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: rgba(148, 163, 184, 0.1);
  color: #f1f5f9;
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
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.mapping-form-card .form-container {
  padding: 0;
}

.mapping-form-card {
  padding: 2rem;
}

/* Menu Button Styles */
.menu-button-wrapper {
  position: relative;
}

.menu-arrow {
  margin-left: 0.5rem;
  font-size: 0.75rem;
  transition: transform 0.3s ease;
}

.btn.menu-open .menu-arrow {
  transform: rotate(180deg);
}

.menu-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 0.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  min-width: 200px;
  z-index: 100;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: #e2e8f0;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.menu-item:hover {
  background: rgba(59, 130, 246, 0.2);
  color: #f1f5f9;
}

.menu-item-icon {
  font-size: 1rem;
  opacity: 0.8;
}

.menu-item:first-child {
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
}

.menu-item:last-child {
  border-bottom-left-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

.mapping-type-display {
  padding: 0.5rem 0;
}

.mapping-type-display .mapping-type-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
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
.mappings-list-card {
  padding: 2rem;
}

.mappings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.mappings-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.section-title {
  margin: 0;
  color: #f1f5f9;
  font-size: 1.5rem;
  font-weight: 700;
}

.mappings-count {
  color: #94a3b8;
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 0.375rem;
}

.mappings-header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Mappings Table */
.mappings-table {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.75rem;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.4);
}

.table-header {
  display: grid;
  grid-template-columns: 100px 1fr 1fr 150px;
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 2px solid rgba(148, 163, 184, 0.3);
}

.table-col {
  padding: 1rem 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #cbd5e1;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
}

.type-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
  min-width: 80px;
}

.source-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.target-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}


.actions-col {
  text-align: center;
}


.table-row {
  display: grid;
  grid-template-columns: 100px 1fr 1fr 150px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  transition: all 0.2s ease;
  background: rgba(15, 23, 42, 0.3);
}

.table-row:hover:not(.editing) {
  background: rgba(59, 130, 246, 0.08);
  transform: translateX(2px);
}

.table-row.editing {
  background: rgba(59, 130, 246, 0.15);
  border: 2px solid rgba(59, 130, 246, 0.4);
  border-radius: 0.5rem;
  margin: 0.25rem 0;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  min-width: 0;
}

.table-cell > * {
  width: 100%;
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

.type-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
  min-width: 100px;
  max-width: 120px;
}

.type-cell {
  border-right: 1px solid rgba(148, 163, 184, 0.15);
  min-width: 100px;
  max-width: 120px;
  justify-content: flex-start;
}

.source-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.source-cell {
  border-right: 1px solid rgba(148, 163, 184, 0.15);
  justify-content: flex-start;
}

.target-col {
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.target-cell {
  border-right: 1px solid rgba(148, 163, 184, 0.15);
  justify-content: flex-start;
}

.actions-col {
  min-width: 150px;
  max-width: 180px;
}

.actions-cell {
  justify-content: center;
  min-width: 150px;
  max-width: 180px;
}


.actions-cell {
  justify-content: center;
}

.table-cell code {
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 
    'Menlo', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
  font-size: 0.875rem;
  background: rgba(59, 130, 246, 0.12);
  color: #e2e8f0;
  padding: 0.5rem 0.875rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(59, 130, 246, 0.25);
  word-break: break-all;
  display: block;
  width: 100%;
  line-height: 1.5;
  box-sizing: border-box;
}

.table-cell code.text-muted {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  border-color: rgba(148, 163, 184, 0.2);
}

.inline-input {
  width: 100%;
  padding: 0.5rem 0.875rem;
  border: 2px solid rgba(59, 130, 246, 0.5);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: rgba(15, 23, 42, 0.8);
  color: #f1f5f9;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 
    'Menlo', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.inline-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  background: rgba(15, 23, 42, 0.95);
}

.btn-success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
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

/* Empty States */
.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: rgba(15, 23, 42, 0.2);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-text {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #e2e8f0;
}

.empty-subtitle {
  font-size: 0.875rem;
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
  
  .table-header {
    display: none;
  }
  
  .table-header {
    grid-template-columns: 1fr;
    display: none;
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
    flex-direction: row;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .action-buttons .btn {
    flex: 1;
    min-width: 0;
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
  
  .mappings-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .mappings-header-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .section-title {
    font-size: 1.25rem;
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
  
  .action-buttons {
    flex-direction: row;
    gap: 0.5rem;
  }
  
  .action-buttons .btn {
    flex: 1;
    min-width: 0;
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