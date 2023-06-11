import './assets/main.css'

import {createApp} from 'vue'
import {createPinia} from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import naive from 'naive-ui'

import createAuthRefreshInterceptor from 'axios-auth-refresh'
import axios from 'axios'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
pinia.use(piniaPluginPersistedstate)

app.use(router)
app.use(naive)

router.isReady().then(() => {
    app.mount('#app')
})

import {useAuthStore} from "./stores";

const authStore = useAuthStore()

axios.defaults.baseURL = import.meta.env.VITE_API_URL
const refreshAuthLogic = (failedRequest) => {
    if (authStore.refresh) {
        axios.post('/api/v1/jwt/refresh', {refresh: authStore.refresh}).then((response) => {
            authStore.access = response.data.access
            authStore.refresh = response.data.refresh
            authStore.lastVerify.result = response.status === 200
            failedRequest.response.config.headers['Authorization'] = 'Bearer ' + authStore.access;
            return Promise.resolve();
        }).catch(function (error) {
            if (navigator.onLine) {
                authStore.$reset()
                location.href = "/login"
                return Promise.resolve()
            }
        })
    }
}

// Instantiate the interceptor
createAuthRefreshInterceptor(axios, refreshAuthLogic)

axios.interceptors.request.use((request) => {
    request.headers['Authorization'] = `Bearer ${authStore.access}`;
    return request;
});