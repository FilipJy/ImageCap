<script setup>
const props = defineProps({
  generateError: {
    type: Object,
    required: true,
  },
  outputText: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="panel panel--output">
    <h2 class="panel__title">Model output</h2>
    <p v-if="props.generateError.value" class="status status--error">{{ props.generateError.value }}</p>
    <pre v-else-if="props.outputText.value" class="output__text">{{ props.outputText.value }}</pre>
    <p v-else class="placeholder">Run generation to see the results.</p>
  </article>
</template>
