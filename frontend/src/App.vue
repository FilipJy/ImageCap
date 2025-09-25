<script setup>
import { onMounted, ref } from 'vue'

import ImagesPanel from './components/ImagesPanel.vue'
import OutputPanel from './components/OutputPanel.vue'
import PreviewPanel from './components/PreviewPanel.vue'
import PromptPanel from './components/PromptPanel.vue'
import { useGenerate } from './composables/useGenerate'
import { useImageBatch } from './composables/useImageBatch'
import { useImageSingle } from './composables/useImageSingle'
import { useModels } from './composables/useModels'
import { usePrompts } from './composables/usePrompts'

const apiBase = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const defaultModel = import.meta.env.VITE_OLLAMA_MODEL ?? ''

const modelsState = useModels({ apiBase, defaultModel })
const promptsState = usePrompts({ apiBase })

const activeImageTab = ref('single')

let generateState

const imageState = useImageSingle({
  hasPromptText: () => generateState?.hasPromptText.value ?? false,
  hasSelectedModel: () => modelsState.hasSelectedModel.value,
  requestCaptionForFile: (file) => {
    if (!generateState) {
      throw new Error('Generation is not ready yet.')
    }
    return generateState.requestCaptionForFile(file)
  },
})

const batchState = useImageBatch({
  hasPromptText: () => generateState?.hasPromptText.value ?? false,
  hasSelectedModel: () => modelsState.hasSelectedModel.value,
  isGenerating: () => imageState.isGenerating.value,
  requestCaptionForFile: (file) => {
    if (!generateState) {
      throw new Error('Generation is not ready yet.')
    }
    return generateState.requestCaptionForFile(file)
  },
})

generateState = useGenerate({
  apiBase,
  selectedModel: modelsState.selectedModel,
  activePromptTab: promptsState.activePromptTab,
  selectedPromptId: promptsState.selectedPromptId,
  savedPromptText: promptsState.savedPromptText,
  freePromptText: promptsState.freePromptText,
  imageFile: imageState.imageFile,
  isGenerating: imageState.isGenerating,
  isBatchRunning: batchState.isBatchRunning,
})

onMounted(() => {
  promptsState.loadPrompts()
  modelsState.loadModels()
})
</script>

<template>
  <main class="page">
    <header class="page__header">
      <h1>Image Caption Playground</h1>
      <p>Test different prompts against your local Ollama vision model.</p>
    </header>

    <div class="page__grid">
      <section class="column column--settings">
        <PromptPanel :models-state="modelsState" :prompts-state="promptsState" />
        <ImagesPanel
          v-model:active-image-tab="activeImageTab"
          :image-state="imageState"
          :batch-state="batchState"
          :has-prompt-text="generateState.hasPromptText"
          :has-selected-model="modelsState.hasSelectedModel"
          :can-generate="generateState.canGenerate"
        />
      </section>

      <section class="column column--results">
        <PreviewPanel :image-preview="imageState.imagePreview" />
        <OutputPanel :generate-error="imageState.generateError" :output-text="imageState.outputText" />
      </section>
    </div>
  </main>
</template>

<style>
.page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page__header h1 {
  margin: 0;
  font-size: 2rem;
}

.page__header p {
  margin: 0;
  color: #555;
}

.page__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: 1.5rem;
  align-items: start;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.panel {
  border: 1px solid #d9d9d9;
  border-radius: 12px;
  padding: 1.25rem;
  background: #fff;
  box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.05);
}

.panel__title {
  margin-top: 0;
  margin-bottom: 0.75rem;
}

.panel__intro {
  margin-top: -0.25rem;
  margin-bottom: 1rem;
  color: #666;
  font-size: 0.95rem;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.field label {
  font-weight: 600;
}

.field__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #e2e8f6;
}

.tabs__button {
  border: none;
  background: #f0f3ff;
  color: #2f54eb;
  border-radius: 999px;
  padding: 0.4rem 1rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.tabs__button:not(:disabled):hover {
  background: #d8e0ff;
}

.tabs__button--active {
  background: #2f54eb;
  color: #fff;
}

.tabs__button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tab-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

input[type='text'],
textarea,
select {
  border: 1px solid #bfbfbf;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  font-family: inherit;
}

textarea {
  resize: vertical;
}

.select-wrapper {
  max-width: 360px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: #2f54eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.btn[disabled] {
  background: #bfbfbf;
  cursor: not-allowed;
}

.btn:not([disabled]):hover {
  transform: translateY(-1px);
  box-shadow: 0 0.5rem 1rem rgba(47, 84, 235, 0.25);
}

.btn--secondary {
  background: #f0f3ff;
  color: #2f54eb;
  border: 1px solid #c5d0f5;
}

.btn--secondary.btn[disabled] {
  background: #e5e7f2;
  color: #7a88b6;
  border-color: #d1d8f2;
  cursor: not-allowed;
  box-shadow: none;
}

.btn--secondary:not([disabled]):hover {
  box-shadow: 0 0.5rem 1rem rgba(47, 84, 235, 0.15);
}

.btn--link {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.25rem;
  padding: 0.2rem 0;
  background: transparent;
  color: #2f54eb;
  border: none;
  border-radius: 4px;
  box-shadow: none;
  transform: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.15s ease;
  align-self: flex-start;
}

.btn--link:hover {
  color: #1d3ac9;
  box-shadow: none;
  transform: none;
  text-decoration: underline;
}

.btn--link:focus-visible {
  outline: 2px solid #2f54eb;
  outline-offset: 2px;
}

.preview {
  width: 100%;
  max-height: 440px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #d9d9d9;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview img {
  display: block;
  max-width: 100%;
  max-height: 420px;
  width: auto;
  height: auto;
  object-fit: contain;
}

.status {
  margin: 0;
  font-size: 0.95rem;
  color: #555;
}

.status--error {
  color: #c0392b;
}

.batch-list {
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.batch-list__item {
  border: 1px solid #e2e8f6;
  border-radius: 10px;
  padding: 0.75rem 0.9rem;
  background: #f9fbff;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.batch-list__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  font-size: 0.95rem;
}

.batch-list__name {
  font-weight: 600;
  word-break: break-all;
}

.batch-list__status {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: #6674c5;
}

.batch-list__item--success .batch-list__status {
  color: #2d7a46;
}

.batch-list__item--error .batch-list__status {
  color: #c0392b;
}

.batch-list__item--running .batch-list__status {
  color: #2f54eb;
}

.batch-list__caption {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.9rem;
  padding: 0.5rem;
  border-radius: 6px;
  background: #fff;
  border: 1px solid #dbe2f1;
}

.batch-list__error {
  margin: 0;
  color: #c0392b;
  font-size: 0.9rem;
}

.placeholder {
  margin: 0;
  color: #888;
  font-style: italic;
}

.output__text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Fira Code', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  background: #f9fafb;
  border: 1px solid #dbe2f1;
  border-radius: 10px;
  padding: 1rem;
}

@media (max-width: 900px) {
  .page {
    padding: 1.25rem;
  }

  .page__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .page {
    padding: 1rem;
  }

  .panel {
    padding: 1rem;
  }
}
</style>
