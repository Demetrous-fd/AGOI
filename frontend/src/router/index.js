import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from "@/stores";


const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            meta: {requiresAuth: true},
            component: () => import('../views/HomeView.vue')
        },
        {
            path: '/report',
            name: 'reportHistory',
            component: () => import('../views/ReportHistoryView.vue')
        },
        {
            path: '/report/:reportId',
            name: 'report',
            props: true,
            component: () => import('../views/InventoryReportView.vue')
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/LoginView.vue')
        },
        {
            path: '/logout',
            name: 'logout'
        },
        {
            path: '/inventory/:reportId',
            name: 'inventory',
            props: true,
            meta: {requiresAuth: true},
            component: () => import('../views/InventoryView.vue')
        },
        {
            path: '/inventory',
            name: 'inventoryPrepare',
            meta: {requiresAuth: true},
            component: () => import('../views/inventoryPrepareView.vue')
        }
    ]
})

router.beforeEach(async (to) => {
    if (to.meta.requiresAuth) {
        const isLoggedIn = await (await import("@/helpers")).isLoggedIn()

        if (to.meta.requiresAuth && !isLoggedIn) return '/login'
        if (to.name === 'login' && isLoggedIn) return '/'
    }

    if (to.name === 'logout') {
        (await import("@/helpers")).logout()
        return '/login'
    }
})

export default router
