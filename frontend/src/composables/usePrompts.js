import { computed, ref, watch } from 'vue'

export function usePrompts({ apiBase }) {
  const prompts = ref([])
  const loadingPrompts = ref(false)
  const promptError = ref('')

  const selectedPromptId = ref('')
  const activePromptTab = ref('saved')
  const savedPromptText = ref('')
  const freePromptText = ref('')

  const newPromptLabel = ref('')
  const newPromptText = ref('')
  const isSavingPrompt = ref(false)
  const savePromptError = ref('')

  const selectedPrompt = computed(() =>
    prompts.value.find((item) => item.id === selectedPromptId.value) ?? null,
  )

  watch(selectedPrompt, (prompt) => {
    if (prompt) {
      savedPromptText.value = prompt.prompt
    } else {
      savedPromptText.value = ''
    }
  })

  async function loadPrompts() {
    loadingPrompts.value = true
    promptError.value = ''

    try {
      const response = await fetch(`${apiBase}/prompts`)
      if (!response.ok) {
        throw new Error(`Failed to fetch prompts (${response.status})`)
      }

      const payload = await response.json()
      if (!Array.isArray(payload)) {
        throw new Error('Unexpected response when loading prompts.')
      }

      prompts.value = payload

      if (prompts.value.length) {
        if (!selectedPromptId.value || !prompts.value.some((item) => item.id === selectedPromptId.value)) {
          selectedPromptId.value = prompts.value[0].id
        }
        if (activePromptTab.value === 'free' && !freePromptText.value) {
          activePromptTab.value = 'saved'
        }
        const firstMatch = prompts.value.find((item) => item.id === selectedPromptId.value)
        if (firstMatch) {
          savedPromptText.value = firstMatch.prompt
        }
      } else {
        selectedPromptId.value = ''
        savedPromptText.value = ''
        if (activePromptTab.value === 'saved') {
          activePromptTab.value = 'free'
        }
      }
    } catch (error) {
      promptError.value = error instanceof Error ? error.message : String(error)
    } finally {
      loadingPrompts.value = false
    }
  }

  async function savePrompt() {
    const label = newPromptLabel.value.trim()
    const prompt = newPromptText.value.trim()
    if (!label || !prompt) {
      savePromptError.value = 'Label and prompt are required.'
      return
    }

    isSavingPrompt.value = true
    savePromptError.value = ''

    try {
      const response = await fetch(`${apiBase}/prompts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label, prompt }),
      })

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null)
        const detail = errorPayload?.detail
        throw new Error(detail ?? `Failed to save prompt (${response.status})`)
      }

      const newPrompt = await response.json()
      prompts.value.push(newPrompt)
      selectedPromptId.value = newPrompt.id
      savedPromptText.value = newPrompt.prompt
      activePromptTab.value = 'saved'
      newPromptLabel.value = ''
      newPromptText.value = ''
    } catch (error) {
      savePromptError.value = error instanceof Error ? error.message : String(error)
    } finally {
      isSavingPrompt.value = false
    }
  }

  return {
    prompts,
    loadingPrompts,
    promptError,
    selectedPromptId,
    activePromptTab,
    savedPromptText,
    freePromptText,
    newPromptLabel,
    newPromptText,
    isSavingPrompt,
    savePromptError,
    loadPrompts,
    savePrompt,
  }
}
