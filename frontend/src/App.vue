<template>
  <n-config-provider :theme="theme">
    <n-message-provider :placement="placement" max="5">
      <RouterView/>
    </n-message-provider>
    <n-global-style/>
  </n-config-provider>
</template>

<script>
import {defineComponent, ref} from "vue";

export default defineComponent({
  setup() {
    const placementRef = ref("bottom")
    window.changePlacement = (value) => {
      placementRef.value = value;
    }
    return {
      placement: placementRef,
      theme: ref(null),
    };
  }
});
</script>