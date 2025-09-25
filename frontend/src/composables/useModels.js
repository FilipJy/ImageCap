import { computed, ref } from 'vue'

export function useModels({ apiBase, defaultModel = '' }) {
  const models = ref([])
  const loadingModels = ref(false)
  const modelsError = ref('')
  const selectedModel = ref(defaultModel)

  const hasSelectedModel = computed(() => selectedModel.value.trim().length > 0)

  async function loadModels() {
    loadingModels.value = true
    modelsError.value = ''

    try {
      const response = await fetch(`${apiBase}/models`)
      if (!response.ok) {
        throw new Error(`Failed to fetch models (${response.status})`)
      }

      const payload = await response.json()
      if (!Array.isArray(payload)) {
        throw new Error('Unexpected response when loading models.')
      }

      models.value = payload

      if (models.value.length) {
        if (selectedModel.value && !models.value.includes(selectedModel.value)) {
          selectedModel.value = models.value.includes(defaultModel)
            ? defaultModel
            : models.value[0]
        } else if (!selectedModel.value) {
          if (defaultModel && models.value.includes(defaultModel)) {
            selectedModel.value = defaultModel
          } else {
            selectedModel.value = models.value[0]
          }
        }
      } else {
        selectedModel.value = ''
      }
    } catch (error) {
      modelsError.value = error instanceof Error ? error.message : String(error)
    } finally {
      loadingModels.value = false
    }
  }

  return {
    models,
    loadingModels,
    modelsError,
    selectedModel,
    hasSelectedModel,
    loadModels,
  }
}
