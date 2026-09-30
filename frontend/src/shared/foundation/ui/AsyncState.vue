<script setup lang="ts">
const AsyncStateState = {
  Loading: "loading",
  Error: "error",
  Success: "success",
} as const;

type AsyncStateStatus = (typeof AsyncStateState)[keyof typeof AsyncStateState];

defineProps<{
  status: AsyncStateStatus;
  loadingLabel: string;
  errorLabel: string;
  successLabel: string;
}>();

defineEmits<{
  retry: [];
}>();
</script>

<template>
  <section
    class="async-state"
    :aria-busy="status === AsyncStateState.Loading"
    :aria-live="status === AsyncStateState.Error ? 'assertive' : 'polite'"
    :role="status === AsyncStateState.Error ? 'alert' : 'status'"
  >
    <template v-if="status === AsyncStateState.Loading">
      <span
        class="async-state__indicator async-state__indicator--loading"
        aria-hidden="true"
      />
      <span>{{ loadingLabel }}</span>
    </template>
    <template v-else-if="status === AsyncStateState.Error">
      <span
        class="async-state__indicator async-state__indicator--error"
        aria-hidden="true"
        >!</span
      >
      <span>{{ errorLabel }}</span>
      <button class="async-state__retry" type="button" @click="$emit('retry')">
        <slot name="retry-label" />
      </button>
    </template>
    <template v-else>
      <span
        class="async-state__indicator async-state__indicator--success"
        aria-hidden="true"
        >✓</span
      >
      <span>{{ successLabel }}</span>
    </template>
  </section>
</template>

<style scoped>
.async-state {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  color: #38564e;
  font-size: 0.95rem;
}

.async-state__indicator {
  display: inline-grid;
  width: 1.5rem;
  height: 1.5rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 700;
}

.async-state__indicator--loading {
  width: 1rem;
  height: 1rem;
  border: 2px solid #d4e0d9;
  border-top-color: #47766a;
  animation: async-state-spin 800ms linear infinite;
}

.async-state__indicator--success {
  background: #dcece2;
  color: #276243;
}

.async-state__indicator--error {
  background: #f8e2de;
  color: #a43c2e;
}

.async-state__retry {
  padding: 0;
  border: 0;
  background: transparent;
  color: #276243;
  font: inherit;
  text-decoration: underline;
  text-underline-offset: 0.15em;
  cursor: pointer;
}

.async-state__retry:focus-visible {
  border-radius: 0.2rem;
  outline: 2px solid #276243;
  outline-offset: 3px;
}

@media (prefers-reduced-motion: reduce) {
  .async-state__indicator--loading {
    animation: none;
    border-right-color: transparent;
  }
}

@keyframes async-state-spin {
  to {
    transform: rotate(1turn);
  }
}
</style>
