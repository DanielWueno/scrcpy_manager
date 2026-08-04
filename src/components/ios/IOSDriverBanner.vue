<template>
  <v-alert
    v-if="visible"
    type="warning"
    variant="tonal"
    density="comfortable"
    class="mb-4"
    icon="mdi-apple"
  >
    <div class="d-flex align-center flex-wrap ga-3">
      <div class="flex-grow-1">
        <div class="font-weight-medium">Drivers de Apple no detectados</div>
        <div class="text-body-2 text-medium-emphasis">
          Sin ellos, Windows no reconoce el iPhone por USB. Instálalos una vez y listo.
        </div>
      </div>
      <v-btn
        color="warning"
        variant="flat"
        :loading="installing"
        @click="install"
      >
        <v-icon class="mr-2">mdi-download</v-icon>
        Instalar drivers
      </v-btn>
    </div>
  </v-alert>
</template>

<script setup lang="ts">
  import { onMounted, ref } from "vue";
  import { iosApi } from "../../services/iosApi";

  const emit = defineEmits<{
    notify: [message: string, color?: string];
  }>();

  // null = todavía no se sabe (no mostrar nada mientras se consulta el estado).
  const installed = ref<boolean | null>(null);
  const supported = ref(true);
  const installing = ref(false);

  const visible = ref(false);

  function updateVisibility() {
    visible.value = supported.value && installed.value === false;
  }

  async function checkStatus() {
    try {
      const status = await iosApi.getDriverStatus();
      installed.value = status.installed;
      supported.value = status.supported;
    } catch {
      // Si la API todavía no responde (p.ej. arrancando), no molestamos con el aviso.
      installed.value = true;
    }
    updateVisibility();
  }

  async function install() {
    installing.value = true;
    try {
      const result = await iosApi.installDriver();
      emit("notify", result.message || "Instalación finalizada", result.success ? "success" : "error");
      if (result.success) {
        installed.value = true;
        updateVisibility();
      }
    } catch {
      emit("notify", "Error al instalar el driver de Apple", "error");
    } finally {
      installing.value = false;
    }
  }

  onMounted(checkStatus);
</script>
