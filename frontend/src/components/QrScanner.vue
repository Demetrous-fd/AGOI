<template>
  <div class="">
    <div class="qrscanner__container">
      <video ref="videoObject" @click="switchQrScan"></video>
      <div class="hint">
        <ClickIcon v-if="!qrScanner._active" style="transform: scale(0.25)"/>
      </div>
      <div class="settings__container">
        <QrScannerSettings :hasFlash="hasFlash" :camera="qrScanner" v-on:switchFlash="switchCameraFlash"
                           v-on:changeCamera="changeCamera"/>
      </div>
    </div>
  </div>
</template>

<script>
import CameraIcon from '@/components/icons/IconCamera.vue'
import StrokeCameraIcon from '@/components/icons/IconStrokeCamera.vue'
import SettingsIcon from '@/components/icons/IconSettings.vue'
import ClickIcon from '@/components/icons/IconClick.vue'

import QrScannerSettings from '@/components/QrScannerSettings.vue'

import QrScanner from 'qr-scanner'
import {useMessage} from "naive-ui";

export default {
  name: "QrScanner",
  components: {CameraIcon, StrokeCameraIcon, SettingsIcon, ClickIcon, QrScannerSettings},
  data: () => ({
    qrCodeContent: "",
    qrScanner: {_active: false},
    hasFlash: false
  }),
  emits: ["handleQrScan"],
  methods: {
    handleQrScan(result) {
      this.$emit("handleQrScan", result)
    },
    startQrScan() {
      this.qrScanner.start().catch(
          e => this.message.error("Дайте разрешение на использование камеры")
      )
    },
    stopQrScan() {
      this.qrScanner.stop()
    },
    restartQrScan() {
      if (this.qrScanner._active)
        this.stopQrScan()
      this.startQrScan()
    },
    switchQrScan() {
      if (this.qrScanner._active)
        this.stopQrScan()
      else
        this.startQrScan()
    },
    switchCameraFlash() {
      this.qrScanner.toggleFlash()
    },
    changeCamera(value) {
      QrScanner.listCameras().then(
          listCameras => {
            const camera = listCameras.filter((camera) => camera.id === value)
            if (camera.length > 0 || value === "environment") {
              this.qrScanner.setCamera(value)
              this.qrScanner.hasFlash().then(
                  hasFlash => {
                    this.hasFlash = hasFlash
                  }
              )
            }
          }
      )
    }
  },
  mounted() {
    this.qrScanner = new QrScanner(this.$refs.videoObject, this.handleQrScan, {
      onDecodeError: (error) => {
        if (error === "No QR code found") return;
        console.log(error);
      },
      highlightScanRegion: true,
      highlightCodeOutline: true,
    });
    this.qrScanner.setInversionMode('both');
    this.qrScanner.setCamera(localStorage.useCamera ? localStorage.useCamera : "environment")
    this.qrScanner.hasFlash().then(hasFlash => {
      this.hasFlash = hasFlash
    })

    window.addEventListener("orientationchange", (event) => {
      if (this.qrScanner._active) {
        this.restartQrScan()
      }
    });

  },
  setup() {
    const message = useMessage()
    return {
      message
    }
  }
};
</script>

<style lang="scss" scoped>

@mixin aspect-ratio($width, $height) {
  aspect-ratio: calc($width / $height);
  // Fallback (current, using padding hack)
  @supports not (aspect-ratio: 1 / 1) {
    &::before {
      float: left;
      padding-top: calc(100% * #{$height} / #{$width});
      content: "";
    }
    &::after {
      display: block;
      content: "";
      clear: both;
    }
  }
}

//.container {
//  display: flex;
//  flex-direction: column;
//}

.qrscanner__container {
  display: flex;
  flex-direction: column;
  position: relative;
}

.qrscanner__container video {
  @include aspect-ratio(1, 1);
  max-width: 100%;
  border: solid;
  border-radius: 16px;
  object-fit: cover;
  cursor: pointer;
}

.settings__container {
  position: absolute;
  top: 0;
  margin: 20px;
  margin-left: 24px;
}

.hint {
  position: absolute;
  pointer-events: none;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  overflow: hidden;
}
</style>