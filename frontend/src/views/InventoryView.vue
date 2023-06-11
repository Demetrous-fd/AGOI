<template>
  <!--  Прогресс инвентаризации + popup по завершению XD-->
  <!--  <n-progress type="circle" status="success" :percentage="percentage" />-->
  <n-grid :x-gap="12" :y-gap="12" cols="1 s:3" responsive="screen">
    <n-grid-item>
      <QrScanner v-on:handleQrScan="handleQrScan"/>
      <n-button @click="showModal = true" size="large" type="error" class="modalButton">
        Завершить инвентаризацию
      </n-button>
      <n-collapse style="padding-top: 16px">
        <n-collapse-item title="Просканированные вещи">
          <n-collapse>
            <n-collapse-item v-for="(instance, object_name) in instances" :title="object_name">
              <n-space vertical>
                <n-button
                    v-for="object in instance.ids"
                    size="medium"
                    :type="scannedInstances.includes(object.id) ? 'success' : 'error'"
                    style="width: 100%"
                    @click="() => {
                      if (this.offline){
                          this.message.error('Нет доступа в интернет')
                          return
                      }
                      if ($refs.modalInfo.instanceId === object.id)
                        $refs.modalInfo.showModal = true
                      else
                        $refs.modalInfo.instanceId = object.id
                    }"
                >
                  {{ object.number }}
                </n-button>
              </n-space>
            </n-collapse-item>
          </n-collapse>
        </n-collapse-item>
      </n-collapse>
    </n-grid-item>
    <n-grid-item span="2" class="mainMenu" style="text-align: center">
      <n-card title="Наименования" embedded>
        <n-grid :x-gap="12" :y-gap="12" cols="2 m:3 xl:4" responsive="screen">
          <n-grid-item v-for="(value, name) in instances">
            <n-statistic :label="name">
              <template #prefix>
                <n-text strong v-if="name === 'Не соответствующее месту нахождения'" style="color: red">
                  {{ value.currentCount }}
                </n-text>
                <n-text v-else>{{ value.currentCount }}</n-text>
              </template>
              <template #suffix v-if="value.count > 0">
                / {{ value.count }}
              </template>
            </n-statistic>
          </n-grid-item>
        </n-grid>
      </n-card>
    </n-grid-item>
  </n-grid>
  <n-modal
      v-model:show="showModal"
      preset="dialog"
      title="Уведомление"
      content="Вы уверены что хотите завершить инвентаризацию ?"
      positive-text="Завершить"
      negative-text="Продолжить позже"
      @positive-click="finishHandler"
      @negative-click="this.$router.push({name: 'home'})"
      :positive-button-props="{disabled: offline}"
  />
  <InstanceInfo ref="modalInfo"/>
</template>

<script>
import InstanceInfo from "@/components/InstanceInfo.vue";
import QrScanner from '@/components/QrScanner.vue'
import {defineComponent, ref} from "vue";
import {
  createReportItem,
  getScannedInstancesId,
  getCountInstances,
  getCountScannedInstances,
  getReport,
  finishReport,
  listenReportEvent
} from "@/services/report";
import {delay} from "@/helpers/retry";
import {useMessage} from "naive-ui";
import {removeReportFromLocalStorage} from "../services/report";

export default defineComponent({
  components: {QrScanner, InstanceInfo},
  props: {
    reportId: {
      type: String,
      required: true
    }
  },
  setup() {
    return {
      showModal: ref(false),
      offline: ref(false),
      message: useMessage()
    };
  },
  data() {
    return {
      instances: {
        "Не соответствующее месту нахождения": {
          count: 0,
          currentCount: 0,
          ids: []
        }
      },
      scannedInstances: [],
      ignore: {}
    }
  },
  mounted() {
    getReport(this.reportId).then(
        response => {
          if (response.data.status === 'finish')
            this.$router.push({name: 'report', params: {reportId: this.reportId}})
        }
    ).catch(e => e)

    this.prepareReportData()
    this.loadScannedInstances()
    this.uploadOfflineScannedInstances()

    window.addEventListener('online', () => {
      this.message.success(
          "Соединение восстановлено",
          {placement: "bottom", duration: 5000}
      )
      this.uploadOfflineScannedInstances()
      this.offline = false
    })
    window.addEventListener('offline',
        () => {
          this.message.warning(
              "Отсутствует доступ в интернет, но можно работать дальше",
              {placement: "bottom", duration: 10000}
          )
          this.offline = true
        }
    )
    listenReportEvent(this.handleReportEvent)
  },
  methods: {
    prepareReportData() {
      const reportData = JSON.parse(localStorage.getItem(this.reportId))
      if (reportData === null)
        getCountInstances(this.reportId).then(
            response => {
              for (const instance of response.data) {
                this.instances[instance.name] = {currentCount: 0, count: instance.count, ids: instance.ids}
              }
              localStorage.setItem(this.reportId, JSON.stringify(this.instances))
            }
        )
      else
        this.instances = reportData
    },
    loadScannedInstances() {
      getScannedInstancesId(this.reportId).then(
          response => {
            let instancesId = JSON.parse(localStorage.getItem(`instancesId-${this.reportId}`))
            instancesId = instancesId === null ? [] : instancesId

            const newInstancesId = response.data.filter(x => !instancesId.includes(x))

            instancesId.push(...newInstancesId)
            localStorage.setItem(`instancesId-${this.reportId}`, JSON.stringify(instancesId))
            this.scannedInstances = instancesId
          }
      ).catch(
          e => {
            let instancesId = JSON.parse(localStorage.getItem(`instancesId-${this.reportId}`))
            instancesId = instancesId === null ? [] : instancesId
            this.scannedInstances = instancesId
          }
      )

      getCountScannedInstances(this.reportId).then(
          response => {
            for (const obj of response.data) {
              if (obj.name === "unknown") {
                if (obj.currentCount > 0) {
                  this.instances["Не соответствующее месту нахождения"].currentCount = obj.currentCount
                  this.instances["Не соответствующее месту нахождения"].ids.push(...obj.ids)
                }
              } else
                this.instances[obj.name].currentCount = obj.currentCount
            }
          }
      ).catch(
          e => {
            for (const instanceId of this.scannedInstances) {
              let next = false
              for (const key in this.instances) {
                if (key === "Не соответствующее месту нахождения")
                  continue

                if (this.instances[key].ids.includes(instanceId)) {
                  this.instances[key].currentCount++
                  next = true
                  break
                }
              }
              if (next)
                continue

              this.instances["Не соответствующее месту нахождения"].currentCount++
              this.instances["Не соответствующее месту нахождения"].ids.push({id: instanceId, number: "Не указано"})
            }
          }
      )
    },
    uploadOfflineScannedInstances() {
      let instancesId = JSON.parse(localStorage.getItem(`instancesId-${this.reportId}-offline`))
      instancesId = instancesId === null ? {real: [], unknown: []} : instancesId
      const ids = [...instancesId.real, ...instancesId.unknown]

      if (ids.length > 0) {
        for (const instance of ids) {
          this.tryAddReportItem(instance)
        }
        localStorage.setItem(`instancesId-${this.reportId}-offline`, null)
        this.message.info("Загружено оборудование из offline хранилища", {duration: 5000, placement: "bottom"})
      }
    },
    updateScannedInstancesId(id) {
      if (!this.scannedInstances.includes(id))
        this.scannedInstances.push(id)
      localStorage.setItem(`instancesId-${this.reportId}`, JSON.stringify(this.scannedInstances))
    },
    handleQrScan(result) {
      const uuidRegex = /[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}/i
      const uuid = result.data.match(uuidRegex)
      if (!uuid)
        return

      if (this.ignore[uuid[0]])
        return

      this.ignore[uuid[0]] = 1
      setTimeout(() => delete this.ignore[uuid[0]], 2000)
      if (!this.scannedInstances.includes(uuid[0])) {
        this.scannedInstances.push(uuid[0])
        this.tryAddReportItem(uuid[0])
      } else if (uuid) {
        this.message.warning("Оборудование было добавлено ранее.")
      }
    },
    handleReportEvent(event) {
      const data = JSON.parse(event.data).data
      if (this.reportId !== data.report)
        return

      if (data.model === "report" && data.status === "finish") {
        this.clearReportData()
        this.$router.push({name: 'report', params: {reportId: this.reportId}})
        return
      }

      if (data.model !== "report-item")
        return

      if (this.scannedInstances.includes(data.id))
        return

      this.scannedInstances.push(data.id)
      if (data.status !== "error") {
        this.instances[data.name].currentCount++
      } else {
        this.instances["Не соответствующее месту нахождения"].currentCount++
        this.instances["Не соответствующее месту нахождения"]["ids"].push({
          id: data.id,
          number: data.number
        })
      }
    },
    addInstanceToOfflineStorage(instanceId) {
      let instancesId = JSON.parse(localStorage.getItem(`instancesId-${this.reportId}-offline`))
      instancesId = instancesId === null ? {unknown: [], real: []} : instancesId

      for (const key in this.instances) {
        if (key === "Не соответствующее месту нахождения")
          continue
        for (const instance of this.instances[key].ids) {
          if (instance.id === instanceId) {
            instancesId.real.push(instanceId)
            this.instances[key].currentCount++
            localStorage.setItem(`instancesId-${this.reportId}-offline`, JSON.stringify(instancesId))
            return true
          }
        }
      }
      instancesId.unknown.push(instanceId)
      this.instances["Не соответствующее месту нахождения"].currentCount++
      this.instances["Не соответствующее месту нахождения"].ids.push({id: instanceId, number: "Не указано"})
      localStorage.setItem(`instancesId-${this.reportId}-offline`, JSON.stringify(instancesId))
      return false
    },
    tryAddReportItem(instanceId) {
      createReportItem(this.reportId, instanceId).then(
          response => {
            this.scannedInstances.push(instanceId)
            if (response.data.status !== "error") {
              this.instances[response.data.name].currentCount++
              this.message.success("Добавлено", {duration: 1000, placement: "bottom"})
            } else {
              this.instances["Не соответствующее месту нахождения"].currentCount++
              this.instances["Не соответствующее месту нахождения"]["ids"].push({
                id: instanceId,
                number: response.data.number
              })

              this.message.warning("Оборудование отсутствует в списке текущей инвентаризации.", {
                duration: 5000,
                placement: "bottom"
              })
            }
            this.updateScannedInstancesId(instanceId)
          }
      ).catch(
          e => {
            const result = this.addInstanceToOfflineStorage(instanceId)
            if (!result)
              this.message.warning("Оборудование отсутствует в списке текущей инвентаризации.", {
                duration: 3000,
                placement: "bottom"
              })
            else
              this.message.success("Добавлено", {duration: 1000, placement: "bottom"})
          }
      )
    },
    finishHandler() {
      finishReport(this.reportId).then(
          _ => {
            this.clearReportData()
            this.$router.push({name: 'report', params: {reportId: this.reportId}})
          }
      ).catch(
          e => this.$router.push({name: 'home'})
      )
    },
    clearReportData() {
      removeReportFromLocalStorage(this.reportId)
      localStorage.removeItem(this.reportId)
      localStorage.removeItem(`instancesId-${this.reportId}`)
      localStorage.removeItem(`instancesId-${this.reportId}-offline`)
    }
  }
});
</script>

<style scoped>
.mainMenu button {
  width: 100%;
}

.modalButton {
  white-space: pre-line;
  width: 100%;
  margin-top: 16px
}
</style>
