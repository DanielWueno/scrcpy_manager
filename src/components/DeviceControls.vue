<template>
  <div
    v-if="!device"
    class="text-center pa-8"
  >
    <v-card
      variant="flat"
      class="bg-grey-lighten-5"
    >
      <v-card-text class="pa-8">
        <v-icon
          size="64"
          color="grey-lighten-2"
          >mdi-hand-pointing-left</v-icon
        >
        <h3 class="text-h6 mt-4 text-grey">Selecciona un dispositivo</h3>
        <p class="text-body-2 text-grey">
          Elige un dispositivo de la lista para ver sus controles
        </p>
      </v-card-text>
    </v-card>
  </div>
  <div v-else>
    <ConnectionStatus
      :device="device"
      :is-active="isDeviceActive"
      :loading="actionLoading"
    />

    <!-- Controles específicos del dispositivo -->
    <AndroidControls
      v-if="device.platform && device.platform.toLowerCase() === 'android'"
      :device="device"
      :actionLoading="actionLoading"
      @execute-action="
        (action, payload) => $emit('execute-action', action, payload)
      "
    />
    <IOSControls
      v-else-if="device.platform && device.platform.toLowerCase() === 'ios'"
      :device="device"
      :deviceStatus="deviceStatus"
      :actionLoading="actionLoading"
      @execute-action="
        (action, payload) => $emit('execute-action', action, payload)
      "
      @notify="(message, color) => $emit('notify', message, color)"
    />
  </div>
</template>

<script setup lang="ts">
  import ConnectionStatus from "./ConnectionStatus.vue";
  import AndroidControls from "./android/AndroidControls.vue";
  import IOSControls from "./ios/IOSControls.vue";
  import { defineProps, computed } from "vue";

  const props = defineProps<{
    device: any;
    deviceStatus?: any;
    actionLoading: boolean;
  }>();
  const isDeviceActive = computed(() => props.device?.active || false);
</script>
