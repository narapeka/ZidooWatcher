import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import DashboardPage from '../views/DashboardPage.vue'
import LogsPage from '../views/LogsPage.vue'
import SettingsPage from '../views/SettingsPage.vue'
import HelpPage from '../views/HelpPage.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardPage,
        meta: { title: '主页' }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: LogsPage,
        meta: { title: '日志' }
      },
                        {
                    path: 'settings',
                    name: 'Settings',
                    component: SettingsPage,
                    meta: { title: '配置' }
                  },
                  {
                    path: 'help',
                    name: 'Help',
                    component: HelpPage,
                    meta: { title: '帮助' }
                  }
    ]
  },
  // 重定向 /config 到 /settings (向后兼容)
  {
    path: '/config',
    redirect: '/settings'
  },
  // 捕获所有未匹配的路由，重定向到首页
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Add title meta
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - ZidooWatcher`
  } else {
    document.title = 'ZidooWatcher'
  }
  next()
})

export default router 