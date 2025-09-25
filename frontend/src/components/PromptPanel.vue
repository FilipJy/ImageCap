<script setup>
const props = defineProps({
  modelsState: {
    type: Object,
    required: true,
  },
  promptsState: {
    type: Object,
    required: true,
  },
})

const modelsState = props.modelsState
const promptsState = props.promptsState

function onModelChange(event) {
  modelsState.selectedModel.value = event.target.value
}

function setPromptTab(tab) {
  promptsState.activePromptTab.value = tab
}

function onPromptSelect(event) {
  promptsState.selectedPromptId.value = event.target.value
}

function onSavedPromptInput(event) {
  promptsState.savedPromptText.value = event.target.value
}

function onFreePromptInput(event) {
  promptsState.freePromptText.value = event.target.value
}

function onNewPromptLabelInput(event) {
  promptsState.newPromptLabel.value = event.target.value
}

function onNewPromptTextInput(event) {
  promptsState.newPromptText.value = event.target.value
}
</script>

<template>
  <article class="panel panel--prompt">
    <h2 class="panel__title">Model &amp; prompt</h2>
    <div class="field">
      <div class="field__header">
        <label for="model-select">Model</label>
        <button
          class="btn btn--secondary"
          type="button"
          :disabled="modelsState.loadingModels.value"
          @click="modelsState.loadModels()"
        >
          {{ modelsState.loadingModels.value ? 'Reloading…' : 'Reload' }}
        </button>
      </div>
      <div class="select-wrapper">
        <select
          id="model-select"
          :value="modelsState.selectedModel.value"
          :disabled="modelsState.loadingModels.value || !modelsState.models.value.length"
          @change="onModelChange"
        >
          <option value="" disabled>Select model</option>
          <option v-for="model in modelsState.models.value" :key="model" :value="model">
            {{ model }}
          </option>
        </select>
      </div>
      <p v-if="modelsState.modelsError.value" class="status status--error">{{ modelsState.modelsError.value }}</p>
      <p v-else-if="!modelsState.loadingModels.value && !modelsState.models.value.length" class="status">
        No local models detected. Install an Ollama vision model and refresh.
      </p>
    </div>

    <nav class="tabs tabs--prompt" aria-label="Prompt mode">
      <button
        class="tabs__button"
        type="button"
        :class="{ 'tabs__button--active': promptsState.activePromptTab.value === 'saved' }"
        @click="setPromptTab('saved')"
        :disabled="!promptsState.prompts.value.length"
      >
        Saved prompts
      </button>
      <button
        class="tabs__button"
        type="button"
        :class="{ 'tabs__button--active': promptsState.activePromptTab.value === 'add' }"
        @click="setPromptTab('add')"
      >
        Add new prompt
      </button>
      <button
        class="tabs__button"
        type="button"
        :class="{ 'tabs__button--active': promptsState.activePromptTab.value === 'free' }"
        @click="setPromptTab('free')"
      >
        Free prompt mode
      </button>
    </nav>

    <div v-if="promptsState.activePromptTab.value === 'saved'" class="tab-section">
      <div class="field">
        <label for="prompt-select">Choose a prompt</label>
        <div class="select-wrapper">
          <select
            id="prompt-select"
            :value="promptsState.selectedPromptId.value"
            :disabled="promptsState.loadingPrompts.value"
            @change="onPromptSelect"
          >
            <option value="" disabled>Select prompt</option>
            <option v-for="prompt in promptsState.prompts.value" :key="prompt.id" :value="prompt.id">
              {{ prompt.label }}
            </option>
          </select>
        </div>
        <p v-if="promptsState.promptError.value" class="status status--error">{{ promptsState.promptError.value }}</p>
      </div>

      <div class="field">
        <label for="prompt-text">Prompt text</label>
        <textarea
          id="prompt-text"
          :value="promptsState.savedPromptText.value"
          rows="8"
          placeholder="Describe the image..."
          @input="onSavedPromptInput"
        ></textarea>
      </div>
    </div>

    <div v-else-if="promptsState.activePromptTab.value === 'add'" class="tab-section">
      <p class="panel__intro">
        Create a reusable prompt that will appear in your saved list.
      </p>
      <div class="field">
        <label for="prompt-label">Label</label>
        <input
          id="prompt-label"
          type="text"
          placeholder="Evening mood"
          :value="promptsState.newPromptLabel.value"
          @input="onNewPromptLabelInput"
        />
      </div>
      <div class="field">
        <label for="new-prompt-text">Prompt</label>
        <textarea
          id="new-prompt-text"
          rows="6"
          placeholder="Describe the atmosphere in the image..."
          :value="promptsState.newPromptText.value"
          @input="onNewPromptTextInput"
        ></textarea>
      </div>
      <button class="btn" type="button" :disabled="promptsState.isSavingPrompt.value" @click="promptsState.savePrompt()">
        {{ promptsState.isSavingPrompt.value ? 'Saving…' : 'Save prompt' }}
      </button>
      <p v-if="promptsState.savePromptError.value" class="status status--error">{{ promptsState.savePromptError.value }}</p>
    </div>

    <div v-else class="tab-section">
      <p class="panel__intro">
        Craft a one-off prompt without adding it to your saved list.
      </p>
      <div class="field">
        <label for="free-prompt-text">Prompt text</label>
        <textarea
          id="free-prompt-text"
          rows="8"
          placeholder="Describe the image..."
          :value="promptsState.freePromptText.value"
          @input="onFreePromptInput"
        ></textarea>
      </div>
    </div>
  </article>
</template>
