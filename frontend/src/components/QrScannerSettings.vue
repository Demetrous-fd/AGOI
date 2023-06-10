<template>
  <n-button @click="showModal = true" text>
    <template #icon>
      <n-icon size="48px">
        <SettingsIcon/>
      </n-icon>
    </template>
  </n-button>
  <n-button v-if="hasFlash && camera._active" @click="switchFlash" text>
    <template #icon>
      <n-icon v-if="useFlash" size="36px">
        <StrokeFlashIcon/>
      </n-icon>
      <n-icon v-else size="36px">
        <FlashIcon/>
      </n-icon>
    </template>
  </n-button>
  <n-modal
      v-model:show="showModal"
      class="custom-card"
      preset="card"
      :style="bodyStyle"
      title="Изменение настроек QR сканера"
      :bordered="false"
      size="huge"
      :segmented="segmented"
  >
    <n-card :bordered="false" title="Камера" size="small">
      <n-space vertical>
        <n-select
            v-model:value="useCamera"
            :options="camerasList"
            @update:value="changeCamera"
        />
      </n-space>
    </n-card>
  </n-modal>
</template>

<script>
import {defineComponent, ref} from "vue";

import SettingsIcon from '@/components/icons/IconSettings.vue'
import FlashIcon from '@/components/icons/IconFlash.vue'
import StrokeFlashIcon from '@/components/icons/IconStrokeFlash.vue'

import QrScanner from 'qr-scanner'

export default defineComponent({
  name: 'QrScannerSettings',
  components: {SettingsIcon, FlashIcon, StrokeFlashIcon},
  emits: ['changeCamera', 'switchFlash'],
  props: {
    camera: Object,
    hasFlash: Boolean
  },
  data: () => ({
    camerasList: [{label: "По умолчанию", value: "environment"}],
  }),
  setup() {
    return {
      bodyStyle: {
        width: "600px"
      },
      segmented: {
        content: "soft",
        footer: "soft"
      },
      showModal: ref(false),
      useFlash: ref(false),
      useCamera: ref(localStorage.useCamera ? localStorage.useCamera : "environment")
    };
  },
  async mounted() {
    const data = await QrScanner.listCameras(true)
    for (const camera of data) {
      this.camerasList.push({label: camera.label, value: camera.id})
    }

    if (localStorage.useCamera in this.camerasList) {
      this.useCamera = localStorage.useCamera
    }
  },
  methods: {
    switchFlash() {
      this.useFlash = !this.useFlash
      this.$emit("switchFlash")
    },
    changeCamera(cameraId, proxy) {
      this.$emit('changeCamera', this.useCamera)
      if (this.useFlash)
        this.switchFlash()
    }
  },
  watch: {
    useCamera(value, option) {
      localStorage.useCamera = value
    }
  }
});
</script>


<style scoped>
button {
  padding-right: 24px;
}
</style>