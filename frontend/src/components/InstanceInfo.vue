<template>
  <n-modal
      v-model:show="showModal"
      preset="card"
      title="Информация о оборудовании"
  >
    <n-card embedded :bordered="false">
      <n-h3>
        Наименование оборудования
        <n-h4>
          Полное: {{ instance.object.name }}<br>
          Короткое: {{ instance.object.short_name }}<br>
          Тип оборудования: {{ instance.object.equipment_type }}<br>
          <n-h4 v-if="instance.object.description">
            Описание:
            <n-text>{{ instance.object.description }}</n-text>
          </n-h4>
        </n-h4>
      </n-h3>
      <n-h3>Инвентарный номер: {{ instance.inventory_number }}</n-h3>
      <n-h3>Номер контракта: {{ instance.contract_number.number }}</n-h3>
      <n-h3>МОЛ: {{ instance.owner }}</n-h3>
      <n-h3>
        Расположение:
        <n-h4>
          Адрес:{{ instance.location.address }}<br>
          Помещение:{{ instance.location.name }}
        </n-h4>
      </n-h3>
      <n-h3>Состояние: {{ instance.state }}</n-h3>
      <n-h3>Добавлен: {{ (new Date(instance.created_at)).toLocaleString() }}</n-h3>
    </n-card>
    <template #action>
      <n-button-group>
        <n-button
            type="info"
            ghost
            @click="goToAdmin(`inventory/instance/${instanceId}/history/`)"
        >
          История изменений
        </n-button>
        <n-button
            type="info"
            ghost
            @click="goToAdmin(`inventory/instance/${instanceId}/change/`)"
        >
          Изменить данные
        </n-button>
      </n-button-group>
    </template>
  </n-modal>
</template>

<script>
import {ref} from "vue";
import {getInstance} from "@/services/instance";

export default {
  name: "InstanceInfo",
  props: {
    instanceId: {
      type: String,
      required: true
    }
  },
  setup() {
    return {
      showModal: ref(false),
      instanceId: ref(null),
    }
  },
  data() {
    return {
      instance: {}
    }
  },
  watch: {
    instanceId(newId) {
      getInstance(newId).then(
          response => {
            this.instance = response.data
            this.showModal = true
          }
      )
    }
  },
  methods: {
    goToAdmin(url = ''){
      location.href = `${import.meta.env.VITE_API_URL}/admin/${url}`
    }
  }
}
</script>

<style scoped>

</style>