<template>
  <v-card class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon
        color="blue"
        class="mr-2"
        >mdi-apple</v-icon
      >
      <span>Controles iOS</span>
    </v-card-title>
    <v-card-text>
      <v-btn
        :color="device.active ? 'error' : 'primary'"
        :loading="actionLoading"
        block
        size="large"
        class="mb-4"
        @click="toggleMirror"
      >
        <v-icon class="mr-2">
          {{ device.active ? "mdi-stop" : "mdi-play" }}
        </v-icon>
        {{ device.active ? "Detener Mirror" : "Iniciar Mirror" }}
      </v-btn>

      <v-btn
        variant="outlined"
        block
        :loading="actionLoading"
        @click="$emit('execute-action', 'screenshot')"
      >
        <v-icon class="mr-2">mdi-camera</v-icon>
        Capturar pantalla
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import type { Device } from "../../types/common";

  interface Props {
    device: Device;
    actionLoading: boolean;
  }

  const props = defineProps<Props>();
  const emit = defineEmits<{
    "execute-action": [action: string, payload?: any];
  }>();

  const toggleMirror = () => {
    emit("execute-action", props.device.active ? "stop_mirror" : "start_mirror");
  };
</script>
