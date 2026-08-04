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

      <!-- go-ios (screenshot --stream) no abre ninguna ventana propia, asi que el
           mirror se muestra en una ventana Electron aparte (ver mirrorWindow.ts en
           el proceso main) - libre de mover, igual que la ventana de scrcpy. Este
           boton reabre esa ventana si el usuario la cerro sin detener el mirror. -->
      <v-btn
        v-if="device.active && mirrorUrl"
        variant="tonal"
        block
        class="mt-4"
        @click="openMirrorWindow"
      >
        <v-icon class="mr-2">mdi-open-in-new</v-icon>
        Abrir ventana del mirror
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import { computed } from "vue";
  import type { Device } from "../../types/common";
  import type { IOSDeviceStatus } from "../../types/ios";

  interface Props {
    device: Device;
    deviceStatus?: IOSDeviceStatus | null;
    actionLoading: boolean;
  }

  const props = defineProps<Props>();
  const emit = defineEmits<{
    "execute-action": [action: string, payload?: any];
  }>();

  const toggleMirror = () => {
    emit("execute-action", props.device.active ? "stop_mirror" : "start_mirror");
  };

  const mirrorUrl = computed(
    () => props.device.mirrorUrl || props.deviceStatus?.mirror_url,
  );

  function openMirrorWindow() {
    if (!mirrorUrl.value) return;
    window.mirrorApi?.open(
      mirrorUrl.value,
      `iOS Mirror - ${props.device.name ?? props.device.serial}`,
      props.device.serial,
    );
  }
</script>
