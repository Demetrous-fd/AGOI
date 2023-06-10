<template>
  <BackButton @click="this.$router.push({name: 'home'})"/>
  <div class="container">
    <Offline v-if="offline"/>
    <n-card header-style="text-align: center" size="huge" v-if="!offline">
      <n-h1 align="center">Подготовка к инвентаризации</n-h1>
      <n-h4>Адрес:</n-h4>
      <n-select
          placeholder="Выбирете адрес"
          v-model:value="targetAddress"
          :options="addresses"
          @update:value="loadLocations"
      />

      <n-h4>Помещение:</n-h4>
      <n-select
          placeholder="Выбирете помещение"
          v-model:value="targetLocation"
          :options="locations"
      />
      <template #action>
        <n-button
            type="success"
            :disabled="disabled"
            style="width: 100%"
            @click="startInventory"
        >
          Начать
        </n-button>
      </template>
    </n-card>
  </div>
</template>
<script>
import BackButton from '@/components/BackButton.vue'
import Offline from '@/components/Offline.vue'

import {saveReportToLocalStorage} from "@/services/report";
import {createReport, getReport} from "@/services/report";
import {getAddresses} from "@/services/address";
import {getLocations} from "@/services/location";
import {useAuthStore} from "@/stores";

import {ref} from "vue";

export default {
  name: "SetupInventoryView",
  components: {BackButton, Offline},
  setup() {
    return {
      disabled: ref(true),
      targetAddress: ref(null),
      targetLocation: ref(null),
      authStore: useAuthStore()
    }
  },
  data() {
    return {
      addresses: [],
      locations: [],
      offline: ref(false)
    }
  },
  mounted() {
    getAddresses().then(
        response => {
          this.addresses = response.data.map((address) => {
            return {label: address.name, value: address.id}
          })
        }
    )
    this.offline = !navigator.onLine
  },
  methods: {
    loadLocations(id) {
      this.targetLocation = null
      getLocations(id).then(
          response => this.locations = response.data.map((location) => {
            return {label: location.name, value: location.id}
          }))
    },
    startInventory() {
      this.authStore.username.then(
          user => createReport(this.targetLocation, user.id).then(
              response => {
                getReport(response.data.id).then(
                    response => {
                      const report = response.data
                      report.location = `${report.location.address} : ${report.location.name}`
                      report.username = report.user.username
                      report.full_name = report.user.full_name
                      delete report.user
                      saveReportToLocalStorage(report)
                      this.$router.push(
                          {
                            name: "inventory",
                            params: {reportId: response.data.id}
                          }
                      )
                    }
                )
              }
          )
      )

    }
  },
  watch: {
    targetLocation(id) {
      this.disabled = id === null;
    }
  }
}
</script>

<style scoped>
.n-h4 {
  margin-bottom: 0;
}

.router-link button {
  white-space: pre-line;
  height: auto;
  min-height: 40px;
  width: 100%;
  max-width: 512px;
  min-width: 256px;
  padding: 8px 16px;
}
</style>