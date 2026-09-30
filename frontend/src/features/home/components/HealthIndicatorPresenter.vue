<script setup lang="ts">
import AsyncState from "@/shared/foundation/ui/AsyncState.vue";

type HealthIndicatorStatus = "loading" | "error" | "success";

defineProps<{
  status: HealthIndicatorStatus;
}>();

defineEmits<{
  retry: [];
}>();
</script>

<template>
  <section class="health-indicator" aria-labelledby="health-indicator-heading">
    <div>
      <p class="health-indicator__eyebrow">{{ $t("ui.health.eyebrow") }}</p>
      <h2 id="health-indicator-heading">{{ $t("ui.health.title") }}</h2>
    </div>
    <AsyncState
      :status="status"
      :loading-label="$t('ui.health.loading')"
      :error-label="$t('ui.health.error')"
      :success-label="$t('ui.health.ok')"
      @retry="$emit('retry')"
    >
      <template #retry-label>{{ $t("ui.health.retry") }}</template>
    </AsyncState>
  </section>
</template>

<style scoped>
.health-indicator {
  display: flex;
  width: min(100%, 42rem);
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid #dce4dc;
  border-radius: 1.25rem;
  background: rgb(255 255 255 / 72%);
  box-shadow: 0 1rem 3rem rgb(23 42 38 / 6%);
  text-align: left;
}

.health-indicator__eyebrow {
  margin: 0 0 0.35rem;
  color: #648277;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  color: #244238;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.4rem;
  font-weight: 500;
}

@media (max-width: 34rem) {
  .health-indicator {
    align-items: flex-start;
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
