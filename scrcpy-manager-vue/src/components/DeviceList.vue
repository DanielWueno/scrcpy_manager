<template>
  <v-card>
    <div class="d-flex align-center mb-2">
      <v-switch
        :model-value="monitoring"
        @change="$emit('toggle-monitoring', !monitoring)"
        label="Autodetectar dispositivos (monitoring)"
        color="primary"
        hide-details
        inset
      />
    </div>
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
      <div v-if="devices.length > 0">
        <DeviceItem
          v-for="device in devices"
          :key="device.id"
          :device="device"
          :isSelected="selectedDevice?.id === device.id"
          @select="$emit('device-selected', device)"
        />
      </div>

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
          Conecta un dispositivo Android via USB/WiFi o iOS via USB
        </p>
        <v-btn
          color="primary"
          class="mt-2"
          @click="$emit('refresh')"
        >
          <v-icon left>mdi-refresh</v-icon>
          Buscar dispositivos
        </v-btn>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import DeviceItem from "./DeviceItem.vue";
  import { defineProps } from "vue";

  defineProps<{
    devices: any[];
    selectedDevice: any;
    loading: boolean;
    monitoring: boolean;
  }>();
</script>

<style scoped>
  .v-list-item {
    cursor: pointer;
    transition: background-color 0.2s ease;
  }
  .v-list-item:hover {
    background-color: rgba(var(--v-theme-primary), 0.08);
  }
</style>
