<script setup lang="ts">
import { useI18n } from "vue-i18n";
import HealthIndicatorContainer from "./components/HealthIndicatorContainer.vue";

const { t } = useI18n();
</script>

<template>
  <main class="home-page">
    <p class="home-page__eyebrow">TEKTON</p>
    <h1>{{ t("ui.home.title") }}</h1>
    <HealthIndicatorContainer />
  </main>
</template>

<style scoped>
.home-page {
  display: grid;
  min-height: 100vh;
  align-content: center;
  justify-items: center;
  gap: 1rem;
  padding: 2rem;
  background: #f5f4f0;
  color: #172a26;
  text-align: center;
}

.home-page__eyebrow {
  margin: 0;
  color: #47766a;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.2em;
}

h1 {
  max-width: 16ch;
  margin: 0 0 1rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2.5rem, 7vw, 5.5rem);
  font-weight: 500;
  line-height: 1.05;
}
</style>
