import { computed, ref } from "vue";
import type { ExtensionDevice, ExtensionStatus } from "../types/extension";

const extensionDevices = ref<ExtensionDevice[]>([]);
const isExtensionLoading = ref(false);
const extensionError = ref<string | null>(null);
const isExtensionAvailable = ref(false);
const isExtensionInitialized = ref(false);
const hasUsbPermission = ref(false);

export function useMobileRemoteToolkit() {
  const extensionDeviceCount = computed(() => extensionDevices.value.length);

  async function requestExtensionUsbPermission(): Promise<void> {
    extensionError.value = "La solicitud de permisos USB requiere la extension de navegador.";
  }

  async function refreshExtensionDevices(): Promise<void> {
    isExtensionLoading.value = true;
    try {
      extensionDevices.value = [];
    } finally {
      isExtensionLoading.value = false;
    }
  }

  function getExtensionStatus(): ExtensionStatus {
    return {
      available: isExtensionAvailable.value,
      initialized: isExtensionInitialized.value,
      hasUsbPermission: hasUsbPermission.value,
      devices: extensionDevices.value,
      error: extensionError.value,
    };
  }

  return {
    extensionDevices,
    isExtensionLoading,
    extensionError,
    isExtensionAvailable,
    isExtensionInitialized,
    hasUsbPermission,
    extensionDeviceCount,
    requestExtensionUsbPermission,
    refreshExtensionDevices,
    getExtensionStatus,
  };
}
