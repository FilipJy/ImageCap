<script setup>
const props = defineProps({
  imagePreview: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="panel panel--preview">
    <h2 class="panel__title">Image preview</h2>
    <div v-if="props.imagePreview.value" class="preview">
      <img :src="props.imagePreview.value" alt="Preview" />
    </div>
    <p v-else class="placeholder">Upload an image to see it here.</p>
  </article>
</template>
