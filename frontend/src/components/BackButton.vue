<template>
  <div style="position: absolute; top: 36px; left: 12px;">
    <n-button strong secondary circle style="width: 40px; height: 40px; margin-right: 16px">
      <template #icon>
        <n-icon>
          <ArrowIcon style="transform: rotateY(180deg)"/>
        </n-icon>
      </template>
    </n-button>
  </div>
</template>

<script>
import ArrowIcon from '@/components/icons/IconArrow.vue'
export default {
  name: "BackButton",
  components: {ArrowIcon}
}
</script>

<style scoped>

</style>