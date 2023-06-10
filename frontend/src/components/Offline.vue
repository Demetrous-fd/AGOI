<template>
  <n-result
      title="Нет доступа в интернет"
      style="display: block; max-width: 50vh; margin: 0 auto 0 auto"
  >
    <template #icon>
      <OfflineIcon />
    </template>
  </n-result>
</template>

<script>
import OfflineIcon from "@/components/icons/IconOffline.vue";
export default {
  name: "Offline",
  components: {OfflineIcon}
}
</script>