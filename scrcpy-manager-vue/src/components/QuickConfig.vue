<template>
  <div>
    <v-card-subtitle class="d-flex align-center px-0">
      Configuración Rápida
    </v-card-subtitle>

    <div class="configuration-options px-1 d-flex flex-column gap-1">
      <v-switch
        v-model="localOptions.stayAwake"
        label="Mantener pantalla encendida"
        color="success"
        density="compact"
        hide-details
        class="mb-1"
        @update:model-value="updateOptions"
      />

      <v-switch
        v-model="localOptions.showTouches"
        label="Mostrar toques"
        color="success"
        density="compact"
        hide-details
        class="mb-1"
        @update:model-value="updateOptions"
      />

      <v-switch
        v-model="localOptions.noAudio"
        label="Sin audio"
        color="success"
        density="compact"
        hide-details
        class="mb-1"
        @update:model-value="updateOptions"
      />

      <v-switch
        v-model="localOptions.turnScreenOff"
        label="Apagar pantalla al conectar"
        color="success"
        density="compact"
        hide-details
        @update:model-value="updateOptions"
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
