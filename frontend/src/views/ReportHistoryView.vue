<template>
  <BackButton @click="this.$router.push({name: 'home'})"/>
  <n-h1 align="center">Отчёты</n-h1>
  <Offline v-if="offline" />
  <n-result
      status="404"
      title="В данный момент нет отчётов"
      v-if="reports === null && !offline"
  >
    <template #footer>
      <n-button @click="this.$router.push({name: 'home'})" size="large">На главную страницу</n-button>
    </template>
  </n-result>
  <n-h1 align="center" v-if="offline && reports.length !== 0">
    Сохраненные отчёты
  </n-h1>
  <n-grid cols="1 s:3" responsive="screen" style="justify-items: center" v-if="!offline || reports.length !== 0">
    <n-grid-item v-for="report in reports" :key="report.id">
      <n-card embedded :title="`Отчёт за ${formatDateString(report.created_at)}`"
              style="margin-top: 16px; min-width: 320px; max-width: 320px"
              content-style="display: flex; flex-direction: column; align-items: center;"
              header-style="text-align: center;"
      >
        <n-h5 style="text-align: initial; width: 100%;">
          Статус: {{ statuses[report.status] }}<br>
          Помещение: {{ report.location }}<br>
          Инициатор: {{ report.username }} {{ report.full_name ? `-> ${report.full_name}` : '' }}
        </n-h5>
        <div class="inline_container">
          <n-button @click="showModal = true; targetReport = report" type="error" circle>
            <template #icon>
              <n-icon>
                <CrossIcon/>
              </n-icon>
            </template>
          </n-button>

          <n-button @click="handleReport(report)" size="large"
                    icon-placement="right" style="width: 100%">
            <n-text v-if="report.status === 'finish'">Перейти</n-text>
            <n-text v-else>Продолжить</n-text>
            <template #icon>
              <n-icon>
                <ArrowIcon/>
              </n-icon>
            </template>
          </n-button>
        </div>
      </n-card>
    </n-grid-item>
  </n-grid>
  <n-modal
      v-model:show="showModal"
      preset="dialog"
      title="Уведомление"
      content="Вы уверены что хотите удалить отчёт ?"
      positive-text="Удалить"
      negative-text="Отмена"
      @positive-click="removeReport"
  />
</template>

<script>
import ArrowIcon from '@/components/icons/IconArrow.vue'
import CrossIcon from '@/components/icons/IconCross.vue'
import BackButton from '@/components/BackButton.vue'
import Offline from '@/components/Offline.vue'

import {getReportsFromLocalStorage, saveReportToLocalStorage} from "@/services/report";
import {deleteReport, getReports} from "@/services/report";

import {ref} from "vue";

export default {
  name: "ReportHistoryView",
  components: {Offline, ArrowIcon, CrossIcon, BackButton},
  data() {
    return {
      reports: [],
      statuses: {
        finish: "🟢 Завершено",
        in_progress: "🟡 В процессе",
      },
      showModal: false,
      targetReport: null,
      offline: ref(false),
    }
  },
  mounted() {
    this.offline = !navigator.onLine
    if (!this.offline)
      getReports().then(
          response => {
            this.reports = response.data.length !== 0 ? response.data : null
          }
      )
    else {
      this.reports = getReportsFromLocalStorage()
    }
  },
  methods: {
    formatDateString(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString("ru-RU").slice(0, -3)
    },
    removeReport() {
      deleteReport(this.targetReport.id).then(
          response => {
            if (response.status === 204) {
              const index = this.reports.findIndex(value => value.id === this.targetReport.id);
              if (index >= 0) {
                this.reports.splice(index, 1);
              }
            }
          }
      )
    },
    handleReport(report){
      if (report.status !== "in_progress")
        this.$router.push({name: 'report', params: {reportId: report.id}})
      else {
        saveReportToLocalStorage(report)
        this.$router.push({name: 'inventory', params: {reportId: report.id}})
      }
    }
  }
}
</script>

<style scoped>
.inline_container {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
}

.inline_container button {
  margin-left: 8px;
}
</style>