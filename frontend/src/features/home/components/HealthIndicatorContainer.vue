<script setup lang="ts">
import { computed } from "vue";
import HealthIndicatorPresenter from "./HealthIndicatorPresenter.vue";
import { useHealthQuery } from "../composables/useHealthQuery";

const healthQuery = useHealthQuery();
const status = computed(() => {
  if (healthQuery.isPending.value) return "loading";
  if (healthQuery.isError.value || healthQuery.data.value?.status !== "ok") {
    return "error";
  }
  return "success";
});
</script>

<template>
  <HealthIndicatorPresenter :status="status" @retry="healthQuery.refetch" />
</template>
