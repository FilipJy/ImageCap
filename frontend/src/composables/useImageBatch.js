import { computed, ref } from 'vue'

export function useImageBatch({ hasPromptText, hasSelectedModel, isGenerating, requestCaptionForFile }) {
  const batchItems = ref([])
  const isBatchRunning = ref(false)
  const batchError = ref('')

  const batchButtonLabel = computed(() => {
    const total = batchItems.value.length
    if (!total) {
      return 'Generate batch captions'
    }
    if (isBatchRunning.value) {
      const runningIndex = batchItems.value.findIndex((item) => item.status === 'running')
      const completed = batchItems.value.filter((item) => item.status === 'success' || item.status === 'error').length
      const currentPosition = runningIndex >= 0 ? runningIndex + 1 : Math.min(completed + 1, total)
      return `Processing ${currentPosition}/${total}…`
    }
    if (batchItems.value.length && batchItems.value.every((item) => item.status === 'success')) {
      return `Re-run batch (${total})`
    }
    if (batchItems.value.some((item) => item.status === 'error')) {
      return `Retry batch (${total})`
    }
    return `Generate batch captions (${total})`
  })

  const batchSummary = computed(() => {
    const total = batchItems.value.length
    if (!total) {
      return ''
    }
    const succeeded = batchItems.value.filter((item) => item.status === 'success').length
    const failed = batchItems.value.filter((item) => item.status === 'error').length
    if (isBatchRunning.value) {
      const processed = succeeded + failed
      if (processed === 0) {
        return `Processing ${total} images…`
      }
      return `Processed ${processed} of ${total} images${failed ? `, ${failed} failed` : ''}`
    }
    if (!succeeded && !failed) {
      return ''
    }
    return `Batch complete: ${succeeded}/${total} succeeded${failed ? `, ${failed} failed` : ''}`
  })

  function handleBatchFiles(event) {
    if (isBatchRunning.value) {
      return
    }
    const files = Array.from(event.target.files ?? [])
    batchItems.value = files.map((file) => ({
      file,
      name: file.name,
      status: 'pending',
      caption: '',
      error: '',
    }))
    batchError.value = ''
    if (event.target instanceof HTMLInputElement) {
      event.target.value = ''
    }
  }

  function clearBatch() {
    if (isBatchRunning.value) {
      return
    }
    batchItems.value = []
    batchError.value = ''
    const input = document.getElementById('batch-input')
    if (input instanceof HTMLInputElement) {
      input.value = ''
    }
  }

  async function generateBatch() {
    if (!batchItems.value.length) {
      batchError.value = 'Add at least one image to the batch.'
      return
    }
    if (!hasPromptText()) {
      batchError.value = 'Provide prompt text before running the batch.'
      return
    }
    if (!hasSelectedModel()) {
      batchError.value = 'Select an Ollama model before running the batch.'
      return
    }
    if (isBatchRunning.value || isGenerating()) {
      return
    }

    batchError.value = ''
    isBatchRunning.value = true

    batchItems.value = batchItems.value.map((item) => ({
      ...item,
      status: 'pending',
      caption: '',
      error: '',
    }))

    try {
      for (let index = 0; index < batchItems.value.length; index += 1) {
        batchItems.value[index] = {
          ...batchItems.value[index],
          status: 'running',
          error: '',
          caption: '',
        }
        batchItems.value = [...batchItems.value]

        try {
          const caption = await requestCaptionForFile(batchItems.value[index].file)
          batchItems.value[index] = {
            ...batchItems.value[index],
            status: 'success',
            caption,
          }
        } catch (error) {
          batchItems.value[index] = {
            ...batchItems.value[index],
            status: 'error',
            error: error instanceof Error ? error.message : String(error),
          }
        }

        batchItems.value = [...batchItems.value]
      }
    } finally {
      isBatchRunning.value = false
    }
  }

  return {
    batchItems,
    isBatchRunning,
    batchError,
    batchButtonLabel,
    batchSummary,
    handleBatchFiles,
    clearBatch,
    generateBatch,
  }
}
