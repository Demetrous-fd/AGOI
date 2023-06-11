<template>
  <div class="container">

    <n-grid :x-gap="12" :y-gap="12" cols="1 s:3" responsive="screen">
      <n-grid-item>
        <QrScanner ref="qrScanner" v-on:handleQrScan="handleQrScan"/>
      </n-grid-item>
      <n-grid-item span="2" class="mainMenu">
        <n-card :bordered="false">
          <n-h1>Привет <n-text @click="next">{{ hi }}</n-text></n-h1>
          <n-button-group vertical style="width: 100%">
            <router-link v-slot="{ navigate }" :to="{ name: 'inventoryPrepare' }" custom>
              <n-button size="large" @click="navigate">Начать инвентаризацию 📝</n-button>
            </router-link>
            <router-link v-slot="{ navigate }" :to="{ name: 'reportHistory' }" custom>
              <n-button size="large" @click="navigate">Отчёты по инвентаризации</n-button>
            </router-link>
            <n-button size="large" @click="goToAdmin">Перейти в панель управления</n-button>
            <router-link v-slot="{ navigate }" :to="{ name: 'logout' }" custom>
              <n-button size="large" @click="navigate">Выход</n-button>
            </router-link>
          </n-button-group>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
  <InstanceInfo ref="modalInfo"/>
</template>

<script setup>
import InstanceInfo from "@/components/InstanceInfo.vue";
import QrScanner from '@/components/QrScanner.vue'
import {RouterLink} from 'vue-router'
</script>

<script>
import {useMessage} from "naive-ui";

export default {
  data() {
    return {
      message: useMessage(),
      hiList: ['🖐', '👊', '✊', '👊', '🖐', '👏'],
      hi: '🖐',
      hiIndex: 0
    }
  },
  methods: {
    goToAdmin() {
      location.href = `${import.meta.env.VITE_API_URL}/admin/`
    },
    handleQrScan(result) {
      const uuidRegex = /[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}/i
      const uuid = result.data.match(uuidRegex)
      if (uuid) {
        if (!navigator.onLine) {
          this.message.error('Нет доступа в интернет')
          return
        }
        if (!this.$refs.modalInfo.showModal) {
          if (this.$refs.modalInfo.instanceId === uuid[0])
            this.$refs.modalInfo.showModal = true
          else
            this.$refs.modalInfo.instanceId = uuid[0]
        }
        this.$refs.qrScanner.stopQrScan()
      }
    },
    next(){
      this.hi = this.hiList[++this.hiIndex]
      if (!this.hi)
        this.hi = '🌚'
    }
  }
}
</script>

<style scoped>
.mainMenu {
  height: 100%;
  display: flex;
  align-items: center;
  text-align: center;
  justify-content: center;
}

.mainMenu button {
  width: 100%;
  white-space: pre-line;
}
</style>
