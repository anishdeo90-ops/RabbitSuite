<template>
  <Dialog v-model="showDialog">
    <template #body-title>
      <h2 class="text-lg font-bold">{{ __('Install Hire Rabbits CRM') }}</h2>
    </template>
    <template #body-content>
      <p>{{ __('Get the app on your device for easy access & a better experience!') }}</p>
    </template>
    <template #actions>
      <Button variant="solid" class="w-full" @click="install">
        <template #prefix>
          <span class="lucide-download size-4" aria-hidden="true" />
        </template>
        {{ __('Install') }}
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { Button, Dialog } from 'frappe-ui'
import { ref } from 'vue'

const deferredPrompt = ref(null)
const showDialog = ref(false)

window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault()
  deferredPrompt.value = event
})

window.addEventListener('hirerabbits:install', () => {
  showDialog.value = true
})

window.addEventListener('appinstalled', () => {
  showDialog.value = false
  deferredPrompt.value = null
})

async function install() {
  if (!deferredPrompt.value) {
    alert(__('Use your browser menu to install Hire Rabbits.'))
    return
  }
  deferredPrompt.value.prompt()
  showDialog.value = false
  await deferredPrompt.value.userChoice
  deferredPrompt.value = null
}
</script>
