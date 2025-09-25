import { computed } from 'vue'

export function useGenerate({
  apiBase,
  selectedModel,
  activePromptTab,
  selectedPromptId,
  savedPromptText,
  freePromptText,
  imageFile,
  isGenerating,
  isBatchRunning,
}) {
  const currentPromptText = computed(() => {
    if (activePromptTab.value === 'free') {
      return freePromptText.value
    }
    if (activePromptTab.value === 'saved') {
      return savedPromptText.value
    }
    return ''
  })

  const hasPromptText = computed(() => currentPromptText.value.trim().length > 0)

  const canGenerate = computed(
    () =>
      !!imageFile.value &&
      hasPromptText.value &&
      !isGenerating.value &&
      !isBatchRunning.value &&
      selectedModel.value.trim().length > 0,
  )

  async function requestCaptionForFile(file) {
    const modelName = selectedModel.value.trim()
    if (!modelName) {
      throw new Error('Select an Ollama model before generating.')
    }

    const promptTextValue = currentPromptText.value.trim()
    if (!promptTextValue) {
      throw new Error('Provide prompt text before generating.')
    }

    const formData = new FormData()
    formData.append('file', file)

    if (activePromptTab.value === 'saved' && selectedPromptId.value) {
      formData.append('prompt_id', selectedPromptId.value)
    }

    formData.append('prompt_text', promptTextValue)
    formData.append('model', modelName)

    const response = await fetch(`${apiBase}/generate`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      let detail = `Generation failed (${response.status})`
      try {
        const errorPayload = await response.json()
        if (errorPayload && typeof errorPayload.detail === 'string') {
          detail = errorPayload.detail
        }
      } catch (error) {
        // Ignore JSON parse errors and fall back to the default message.
      }
      throw new Error(detail)
    }

    const payload = await response.json()
    if (payload && typeof payload.output === 'string') {
      return payload.output
    }
    return ''
  }

  return {
    currentPromptText,
    hasPromptText,
    canGenerate,
    requestCaptionForFile,
  }
}
