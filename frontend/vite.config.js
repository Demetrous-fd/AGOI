import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'

import vue from '@vitejs/plugin-vue'
import {VitePWA} from 'vite-plugin-pwa'
import legacy from '@vitejs/plugin-legacy'
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        cssInjectedByJsPlugin(),
        legacy({
            targets: ['defaults', 'safari >= 11', 'not IE 11'],
        }),
        VitePWA({
            registerType: 'autoUpdate',
            devOptions: {
                enabled: true,
            },
            manifest: {
                name: 'AGO QrScanner',
                short_name: 'AGO',
                description: 'None',
                theme_color: '#ffffff',
                icons: [
                    {
                        src: 'assets/images/android-chrome-192x192.png',
                        sizes: '192x192',
                        type: 'image/png'
                    },
                    {
                        src: 'assets/images/android-chrome-512x512.png',
                        sizes: '512x512',
                        type: 'image/png'
                    }
                ]
            }
        })
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    base: '/',
    define: {
        'import.meta.env.ENV_VARIABLE': JSON.stringify(process.env.ENV_VARIABLE)
    },
    build: {
        rollupOptions: {
            output: {
                manualChunks: undefined,
            },
        },
    },
})
