<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon left>mdi-cellphone-multiple</v-icon>
      Dispositivos
      <v-spacer />
      <v-btn
        @click="$emit('refresh')"
        :loading="loading"
        icon
        variant="text"
        size="small"
      >
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <v-list v-if="devices.length > 0">
        <v-list-item
          v-for="device in devices"
          :key="device.serial"
          @click="$emit('device-selected', device)"
          :active="selectedDevice?.serial === device.serial"
          :class="{
            'bg-surface-variant': selectedDevice?.serial === device.serial,
          }"
        >
          <template #prepend>
            <v-avatar :color="device.connected ? 'success' : 'error'">
              <v-icon>{{
                device.connected ? "mdi-cellphone-check" : "mdi-cellphone-off"
              }}</v-icon>
            </v-avatar>
          </template>

          <v-list-item-title>{{ device.alias }}</v-list-item-title>
          <v-list-item-subtitle>{{ device.name }}</v-list-item-subtitle>

          <template #append>
            <div class="d-flex flex-column align-end">
              <v-chip
                :color="
                  device.active
                    ? 'success'
                    : device.connected
                    ? 'warning'
                    : 'error'
                "
                size="x-small"
                variant="tonal"
              >
                {{ getStatusText(device) }}
              </v-chip>
              <small class="text-medium-emphasis mt-1">
                {{ device.serial.slice(-8) }}
              </small>
            </div>
          </template>
        </v-list-item>
      </v-list>

      <div
        v-else-if="loading"
        class="text-center py-4"
      >
        <v-progress-circular indeterminate />
        <p class="mt-2">Cargando dispositivos...</p>
      </div>

      <div
        v-else
        class="text-center py-8"
      >
        <v-icon
          size="64"
          color="grey-lighten-1"
          >mdi-cellphone-off</v-icon
        >
        <p class="text-h6 mt-2">No hay dispositivos</p>
        <p class="text-body-2 text-medium-emphasis">
          Conecta un dispositivo Android via USB o WiFi
        </p>
        <v-btn
          @click="$emit('refresh')"
          color="primary"
          class="mt-2"
        >
          <v-icon left>mdi-refresh</v-icon>
          Buscar dispositivos
        </v-btn>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import type { Device } from "../types";

  interface Props {
    devices: Device[];
    loading: boolean;
    selectedDevice: Device | null;
  }

  defineProps<Props>();

  defineEmits<{
    "device-selected": [device: Device];
    refresh: [];
  }>();

  const getStatusText = (device: Device): string => {
    if (device.active) return "Activo";
    if (device.connected) return "Conectado";
    return "Desconectado";
  };
</script>
