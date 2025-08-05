<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\scrcpy-manager-vue\src\components\DeviceInfo.vue -->
<template>
  <div v-if="device">
    <v-card-subtitle class="d-flex align-center px-0">
      <v-icon left>mdi-information</v-icon>
      Información del Dispositivo
    </v-card-subtitle>

    <v-list
      density="compact"
      class="bg-transparent"
    >
      <v-list-item>
        <v-list-item-title>Estado</v-list-item-title>
        <template #append>
          <v-chip
            :color="getStatusColor()"
            size="small"
            variant="tonal"
            class="me-2"
            :prepend-icon="getStatusIcon()"
          >
            {{ getStatusText() }}
          </v-chip>
        </template>
      </v-list-item>

      <v-list-item>
        <v-list-item-title>Alias</v-list-item-title>
        <v-list-item-subtitle>{{ device.alias }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item>
        <v-list-item-title>Modelo</v-list-item-title>
        <v-list-item-subtitle>{{ device.name }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item>
        <v-list-item-title>Serial</v-list-item-title>
        <v-list-item-subtitle class="font-mono">{{
          device.serial
        }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item v-if="device.last_seen">
        <v-list-item-title>Última conexión</v-list-item-title>
        <v-list-item-subtitle>{{ device.last_seen }}</v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </div>

  <div
    v-else
    class="text-center py-4"
  >
    <v-icon
      size="48"
      color="grey-lighten-2"
      >mdi-cellphone-off</v-icon
    >
    <p class="text-body-2 text-medium-emphasis mt-2">
      Selecciona un dispositivo para ver su información
    </p>
  </div>
</template>

<script setup lang="ts">
  import type { Device } from "../types";

  interface Props {
    device: Device | null;
  }

  const props = defineProps<Props>();

  const getStatusColor = (): string => {
    if (!props.device) return "grey";
    if (props.device.active) return "success";
    if (props.device.connected) return "warning";
    return "error";
  };

  const getStatusIcon = (): string => {
    if (!props.device) return "mdi-help";
    if (props.device.active) return "mdi-play-circle";
    if (props.device.connected) return "mdi-pause-circle";
    return "mdi-stop-circle";
  };

  const getStatusText = (): string => {
    if (!props.device) return "Desconocido";
    if (props.device.active) return "Activo (Mirror)";
    if (props.device.connected) return "Conectado";
    return "Desconectado";
  };
</script>

<style scoped>
  .font-mono {
    font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
    font-size: 0.9em;
  }
</style>
