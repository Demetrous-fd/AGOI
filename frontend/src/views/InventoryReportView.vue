<template>
  <BackButton @click="this.$router.push({name: 'reportHistory'})" style="z-index: 1"/>
  <div class="container">
    <n-card
        :bordered="false"
        header-style="text-align: center"
        content-style="padding: 0"
        size="huge"
        v-if="Object.keys(report).length !== 0"
    >
      <n-h1 align="center">Отчёт</n-h1>

      <n-h3>Дата начала: {{ (new Date(report.created_at)).toLocaleString() }}</n-h3>
      <n-h3>Дата окончания: {{ (new Date(report.updated_at)).toLocaleString() }}</n-h3>
      <n-h3>Адрес: {{ report.location.address }}</n-h3>
      <n-h3>Помещение: {{ report.location.name }}</n-h3>

      <n-table style="margin-top: 16px;">
        <thead>
        <tr>
          <th>Наименование</th>
          <th>Отсканировано</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(instance, name) in instances">
          <td>{{ name }}</td>
          <td>{{ instance.currentCount }} / {{ instance.count }}</td>
        </tr>
        </tbody>
      </n-table>

      <n-collapse style="padding-top: 16px; padding-bottom: 16px">
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
      <template #action>
        <div style="display: flex; justify-content: center">
          <n-button>
            <a :href="downloadUrl" download style="text-decoration: none">Скачать отчёт</a>
          </n-button>
        </div>
      </template>
    </n-card>
  </div>
  <InstanceInfo ref="modalInfo"/>
</template>

<script>
import {
  getReport,
  getCountInstances,
  getCountScannedInstances,
  getScannedInstancesId
} from "@/services/report";
import BackButton from "@/components/BackButton.vue";
import InstanceInfo from "@/components/InstanceInfo.vue";
import {ref} from "vue";

export default {
  name: "InventoryReport",
  components: {BackButton, InstanceInfo},
  props: {
    reportId: {
      type: String,
      required: true
    }
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
      report: ref({}),
      scannedInstances: [],
      downloadUrl: `${import.meta.env.VITE_API_URL}/api/v1/report/${this.reportId}/download/`
    }
  },
  mounted() {
    if (!this.reportId)
      this.$router.push({name: "reportHistory"})

    getReport(this.reportId).then(
        response => {
          this.report = response.data
        }
    )
    this.test()
  },
  methods: {
    test() {
      getCountInstances(this.reportId).then(
          response => {
            for (const instance of response.data) {
              this.instances[instance.name] = {currentCount: 0, count: instance.count, ids: instance.ids}
            }
          }
      ).then(
          _ => getCountScannedInstances(this.reportId).then(
              response => {
                for (const obj of response.data) {
                  if (obj.name === "unknown") {
                    if (obj.currentCount > 0) {
                      this.instances["Не соответствующее месту нахождения"].currentCount = obj.currentCount
                      this.instances["Не соответствующее месту нахождения"].ids.push(...obj.ids)
                    }
                  } else {
                    this.instances[obj.name].currentCount = obj.currentCount
                  }
                }
              }
          )
      ).then(
          _ => {
            if (this.instances["Не соответствующее месту нахождения"].currentCount === 0)
              delete this.instances["Не соответствующее месту нахождения"]
          }
      )
      getScannedInstancesId(this.reportId).then(
          response => this.scannedInstances = response.data
      )
    }
  }
}
</script>

<style scoped>
.n-h4,
.n-h3 {
  margin: 0;
}

td, th {
  text-align: center;
}


@media (min-width: 320px) or (min-width: 481px) or (min-width: 641px) or (min-width: 961px) {
  .n-card {
    width: 100%;
  }
}

@media (min-width: 1024px) or (min-width: 1281px) {
  .n-card {
    width: 70%;
  }
}
</style>