<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\scrcpy-manager-vue\src\components\QuickConfig.vue -->
<template>
  <div>
    <v-card-subtitle class="d-flex align-center px-0">
      <v-icon left>mdi-cog</v-icon>
      Configuración Rápida
    </v-card-subtitle>

    <div class="configuration-options">
      <v-switch
        v-model="localOptions.stayAwake"
        @update:model-value="updateOptions"
        label="Mantener pantalla encendida"
        color="success"
        density="compact"
        hide-details
        class="mb-2"
      />

      <v-switch
        v-model="localOptions.showTouches"
        @update:model-value="updateOptions"
        label="Mostrar toques"
        color="info"
        density="compact"
        hide-details
        class="mb-2"
      />

      <v-switch
        v-model="localOptions.noAudio"
        @update:model-value="updateOptions"
        label="Sin audio"
        color="warning"
        density="compact"
        hide-details
        class="mb-2"
      />

      <v-switch
        v-model="localOptions.turnScreenOff"
        @update:model-value="updateOptions"
        label="Apagar pantalla al conectar"
        color="error"
        density="compact"
        hide-details
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, watch } from "vue";
  import type { ConnectionOptions } from "../types";

  interface Props {
    modelValue: ConnectionOptions;
  }

  const props = defineProps<Props>();

  const emit = defineEmits<{
    "update:modelValue": [value: ConnectionOptions];
  }>();

  const localOptions = ref<ConnectionOptions>({ ...props.modelValue });

  const updateOptions = () => {
    emit("update:modelValue", { ...localOptions.value });
  };

  watch(
    () => props.modelValue,
    (newValue) => {
      localOptions.value = { ...newValue };
    },
    { deep: true }
  );
</script>

<style scoped>
  .configuration-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
</style>
