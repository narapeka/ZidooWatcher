<template>
  <div class="layout">
    <!-- Mobile Menu Overlay -->
    <div v-if="isMobileMenuOpen" class="mobile-overlay" @click="closeMobileMenu"></div>
    
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-mobile-open': isMobileMenuOpen }">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-text">
            <span class="logo-zidoo">Zidoo</span><span class="logo-watcher">Watcher</span>
          </span>
        </div>
        <button class="mobile-close" @click="closeMobileMenu" v-if="isMobile">
          <i class="icon-close">×</i>
        </button>
      </div>
      
                  <nav class="sidebar-nav">
              <router-link to="/" class="nav-item" @click="closeMobileMenu" exact>
                <span class="nav-text">主页</span>
              </router-link>
              <router-link to="/logs" class="nav-item" @click="closeMobileMenu" exact>
                <span class="nav-text">日志</span>
              </router-link>
              <router-link to="/settings" class="nav-item" @click="closeMobileMenu" exact>
                <span class="nav-text">配置</span>
              </router-link>
              <router-link to="/help" class="nav-item" @click="closeMobileMenu" exact>
                <span class="nav-text">帮助</span>
              </router-link>
            </nav>
      
      <div class="sidebar-footer">
        <div class="status-indicator" :class="statusClass">
          <div class="status-dot"></div>
          <span class="status-text">{{ statusText }}</span>
        </div>
      </div>
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
      <!-- Mobile Header -->
      <header class="mobile-header" v-if="isMobile">
        <button class="mobile-menu-btn" @click="openMobileMenu">
          <span class="hamburger"></span>
          <span class="hamburger"></span>
          <span class="hamburger"></span>
        </button>
        <div class="mobile-title">
          <span class="mobile-logo">
            <span class="logo-zidoo">Zidoo</span><span class="logo-watcher">Watcher</span>
          </span>
        </div>
      </header>
      
      <!-- Page Content -->
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useWatcherStore } from '../stores/watcher'

const route = useRoute()
const store = useWatcherStore()

// Reactive data
const isMobile = ref(false)
const isMobileMenuOpen = ref(false)

// Computed properties
const statusClass = computed(() => {
  return store.isRunning ? 'status-running' : 'status-stopped'
})

const statusText = computed(() => {
  return store.isRunning ? '运行中' : '已停止'
})

const currentPageTitle = computed(() => {
  switch (route.name) {
    case 'Dashboard':
      return '主页'
    case 'Logs':
      return '日志'
    case 'Settings':
      return '配置'
    default:
      return 'ZidooWatcher'
  }
})

// Methods
const checkIsMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    isMobileMenuOpen.value = false
  }
}

const openMobileMenu = () => {
  isMobileMenuOpen.value = true
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

// Lifecycle
onMounted(() => {
  checkIsMobile()
  window.addEventListener('resize', checkIsMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkIsMobile)
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: #e2e8f0;
}

/* Sidebar Styles */
.sidebar {
  width: 280px;
  background: rgba(45, 55, 72, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 100;
  transition: transform 0.3s ease;
}

.sidebar-header {
  padding: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 1.5rem;
  font-style: italic;
  color: white;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-zidoo {
  font-weight: 800;
}

.logo-watcher {
  font-weight: 400;
}

.mobile-close {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.mobile-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: block;
  padding: 1rem 2rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  font-weight: 500;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-left-color: #3b82f6;
}

.nav-item.router-link-exact-active {
  background: rgba(59, 130, 246, 0.2);
  color: white;
  border-left-color: #3b82f6;
}

.nav-text {
  font-size: 0.95rem;
}

.sidebar-footer {
  padding: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.status-running {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-stopped {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.mobile-header {
  display: none;
  background: rgba(45, 55, 72, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem;
  align-items: center;
  gap: 1rem;
}

.mobile-menu-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 2rem;
  height: 2rem;
  justify-content: center;
}

.hamburger {
  width: 100%;
  height: 2px;
  background: white;
  border-radius: 1px;
  transition: all 0.3s ease;
}

.mobile-title {
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.mobile-logo {
  font-style: italic;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: rgba(48, 58, 74, 0.922);
  backdrop-filter: blur(10px);
}

/* Mobile Styles */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    transform: translateX(-100%);
    z-index: 200;
  }

  .sidebar-mobile-open {
    transform: translateX(0);
  }

  .mobile-close {
    display: block;
  }

  .mobile-header {
    display: flex;
  }

  .main-content {
    width: 100%;
  }

  .content-wrapper {
    padding: 1rem;
  }

  .mobile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 150;
  }
}

@media (max-width: 480px) {
  .content-wrapper {
    padding: 0.5rem;
  }

  .sidebar {
    width: 100%;
  }
}
</style> 