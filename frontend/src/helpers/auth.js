import axios from "axios";
import {useAuthStore} from "@/stores/auth";

const authStore = useAuthStore()

export async function login(username, password) {
    try {
        const response = await axios.post('/api/v1/jwt/create', {username: username, password: password})

        if (response.status === 200) {
            authStore.access = response.data.access
            authStore.refresh = response.data.refresh
            authStore.lastVerify.result = true
            axios.defaults.headers.common['Authorization'] = 'Bearer ' + response.data.access
            return Promise.resolve(true)
        }
        return Promise.resolve(false)
    } catch (e) {
        return Promise.resolve(false)
    }
}

export function logout() {
    authStore.access = ''
    authStore.refresh = ''
    authStore.lastVerify.result = false
    axios.defaults.headers.common['Authorization'] = ''
}

export async function isLoggedIn(refreshOnFail = true) {
    if (!authStore.lastVerify.time && !authStore.lastVerify.result
        || (Math.floor(Date.now() / 1000) - authStore.lastVerify.next >= 0)) {
        authStore.lastVerify.time = Math.floor(Date.now() / 1000)
        authStore.lastVerify.next = Math.floor(Date.now() / 1000) + (import.meta.env.VITE_ACCESS_EXPIRE ? import.meta.env.VITE_ACCESS_EXPIRE : 3600)
        try {
            const response = await axios.post("/api/v1/jwt/verify/", {token: authStore.access}, {skipAuthRefresh: true})
            authStore.lastVerify.result = response.status === 200
        } catch (e) {
            if (e.code === "ERR_NETWORK")
                return true
            if (refreshOnFail)
                await refreshToken()
            return await isLoggedIn(false)
        }
    }
    return authStore.lastVerify.result
}

export function refreshToken() {
    return axios.post('/api/v1/jwt/refresh', {refresh: authStore.refresh}).then(
        response => {
            if (response.status === 200) {
                authStore.access = response.data.access
                authStore.refresh = response.data.refresh
                authStore.lastVerify.result = true
                axios.defaults.headers.common['Authorization'] = 'Bearer ' + response.data.access
            }
        }
    ).catch(
        (e) => {
                authStore.access = ''
                authStore.refresh = ''
                authStore.lastVerify.result = false
                axios.defaults.headers.common['Authorization'] = '';
        }
    )
}
