import {defineStore} from 'pinia'
import {retryGetRequest} from "../helpers/retry";

export const useAuthStore = defineStore('auth', {
    state: () => ({
        access: '',
        refresh: '',
        lastVerify: {
            time: null,
            next: null,
            result: false
        },
        user: {}
    }),
    getters: {
        async username(){
            if (!this.user.id) {
                const response = await retryGetRequest("/api/v1/users/me/")
                if (response.status === 200)
                    this.user = response.data
            }
            return this.user
        }
    },
    persist: {
        paths: ['access', 'refresh', 'lastVerify']
    }
})