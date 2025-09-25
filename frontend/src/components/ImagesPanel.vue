<script setup>
const props = defineProps({
  activeImageTab: {
    type: String,
    required: true,
  },
  imageState: {
    type: Object,
    required: true,
  },
  batchState: {
    type: Object,
    required: true,
  },
  hasPromptText: {
    type: Object,
    required: true,
  },
  hasSelectedModel: {
    type: Object,
    required: true,
  },
  canGenerate: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update:activeImageTab'])

function setImageTab(tab) {
  if (props.activeImageTab === tab) {
    return
  }
  emit('update:activeImageTab', tab)
}
</script>

<template>
  <article class="panel panel--images">
    <h2 class="panel__title">Images</h2>
    <nav class="tabs tabs--images" aria-label="Image mode">
      <button
        class="tabs__button"
        type="button"
        :class="{ 'tabs__button--active': props.activeImageTab === 'single' }"
        @click="setImageTab('single')"
      >
        Single image
      </button>
      <button
        class="tabs__button"
        type="button"
        :class="{ 'tabs__button--active': props.activeImageTab === 'batch' }"
        @click="setImageTab('batch')"
      >
        Batch mode
      </button>
    </nav>

    <div v-if="props.activeImageTab === 'single'" class="tab-section">
      <div class="field">
        <label for="image-input">Choose an image</label>
        <input
          id="image-input"
          type="file"
          accept="image/*"
          :disabled="props.batchState.isBatchRunning.value"
          @change="props.imageState.handleFileChange"
        />
        <button v-if="props.imageState.imageFile.value" class="btn btn--link" type="button" @click="props.imageState.clearImage()">
          Remove image
        </button>
      </div>
      <button class="btn" type="button" :disabled="!props.canGenerate.value" @click="props.imageState.generateCaption()">
        {{ props.imageState.isGenerating.value ? 'Generating…' : 'Generate caption' }}
      </button>
    </div>

    <div v-else class="tab-section">
      <p class="panel__intro">
        Select multiple images to caption them sequentially with the current prompt and model.
      </p>
      <div class="field">
        <label for="batch-input">Batch images</label>
        <input
          id="batch-input"
          type="file"
          accept="image/*"
          multiple
          :disabled="props.batchState.isBatchRunning.value"
          @change="props.batchState.handleBatchFiles"
        />
        <button
          v-if="props.batchState.batchItems.value.length"
          class="btn btn--link"
          type="button"
          :disabled="props.batchState.isBatchRunning.value"
          @click="props.batchState.clearBatch()"
        >
          Clear list
        </button>
      </div>
      <button
        class="btn"
        type="button"
        :disabled="
          !props.batchState.batchItems.value.length ||
          props.batchState.isBatchRunning.value ||
          !props.hasPromptText.value ||
          !props.hasSelectedModel.value ||
          props.imageState.isGenerating.value
        "
        @click="props.batchState.generateBatch()"
      >
        {{ props.batchState.batchButtonLabel.value }}
      </button>
      <p v-if="props.batchState.batchError.value" class="status status--error">
        {{ props.batchState.batchError.value }}
      </p>
      <p v-else-if="props.batchState.batchSummary.value" class="status">
        {{ props.batchState.batchSummary.value }}
      </p>
      <ul v-if="props.batchState.batchItems.value.length" class="batch-list">
        <li
          v-for="(item, index) in props.batchState.batchItems.value"
          :key="`${item.name}-${index}`"
          :class="['batch-list__item', `batch-list__item--${item.status}`]"
        >
          <div class="batch-list__header">
            <span class="batch-list__name">{{ item.name }}</span>
            <span class="batch-list__status">
              <template v-if="item.status === 'pending'">Pending</template>
              <template v-else-if="item.status === 'running'">Processing…</template>
              <template v-else-if="item.status === 'success'">Done</template>
              <template v-else-if="item.status === 'error'">Failed</template>
            </span>
          </div>
          <pre v-if="item.caption" class="batch-list__caption">{{ item.caption }}</pre>
          <p v-else-if="item.status === 'error' && item.error" class="batch-list__error">
            {{ item.error }}
          </p>
        </li>
      </ul>
    </div>
  </article>
</template>
