import { ref } from 'vue'

export function useImageSingle({ hasPromptText, hasSelectedModel, requestCaptionForFile }) {
  const imageFile = ref(null)
  const imagePreview = ref('')
  const isGenerating = ref(false)
  const generateError = ref('')
  const outputText = ref('')

  function handleFileChange(event) {
    const [file] = event.target.files ?? []
    if (!file) {
      imageFile.value = null
      imagePreview.value = ''
      return
    }

    imageFile.value = file
    const reader = new FileReader()
    reader.onload = () => {
      imagePreview.value = reader.result
    }
    reader.readAsDataURL(file)
  }

  function clearImage() {
    imageFile.value = null
    imagePreview.value = ''
    const input = document.getElementById('image-input')
    if (input instanceof HTMLInputElement) {
      input.value = ''
    }
  }

  async function generateCaption() {
    if (!imageFile.value || !hasPromptText()) {
      return
    }
    if (!hasSelectedModel()) {
      generateError.value = 'Select an Ollama model before generating.'
      return
    }

    isGenerating.value = true
    generateError.value = ''
    outputText.value = ''

    try {
      const caption = await requestCaptionForFile(imageFile.value)
      outputText.value = caption
    } catch (error) {
      generateError.value = error instanceof Error ? error.message : String(error)
    } finally {
      isGenerating.value = false
    }
  }

  return {
    imageFile,
    imagePreview,
    isGenerating,
    generateError,
    outputText,
    handleFileChange,
    clearImage,
    generateCaption,
  }
}
