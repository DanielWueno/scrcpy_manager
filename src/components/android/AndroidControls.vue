<template>
  <v-card class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon
        class="mr-2"
        color="green"
        >mdi-android</v-icon
      >
      <span>Controles Android</span>
    </v-card-title>
    <v-card-text>
      <MirrorOptions
        :options="mirrorOptions"
        :deviceActive="Boolean(device.active)"
        :actionLoading="actionLoading"
        @update:options="mirrorOptions = $event"
        @toggle-mirror="toggleMirror"
      />
      <DeviceActions
        :actionLoading="actionLoading"
        @execute-action="
          (action, payload) => $emit('execute-action', action, payload)
        "
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import type { Device } from "../../types/common";
  import MirrorOptions from "./MirrorOptions.vue";
  import DeviceActions from "./DeviceActions.vue";

  interface Props {
    device: Device;
    actionLoading: boolean;
  }

  const props = defineProps<Props>();
  const emit = defineEmits<{
    "execute-action": [action: string, payload?: any];
  }>();

  import { ref, computed, watch } from "vue";

  // Mapa de opciones por dispositivo (clave: serial) para que cada dispositivo tenga su propio estado
  const optionsMap = ref<Record<string, any>>({});

  const defaultOptions = () => ({
    stayAwake: true,
    noAudio: true,
    showTouches: false,
    turnScreenOff: false,
  });

  const mirrorOptions = computed({
    get: () => optionsMap.value[props.device?.serial] ?? defaultOptions(),
    set: (val: any) => {
      optionsMap.value[props.device?.serial] = val;
    },
  });

  // Inicializar opciones para un dispositivo nuevo que no tenga estado guardado
  watch(
    () => props.device?.serial,
    (serial) => {
      if (serial && !optionsMap.value[serial]) {
        optionsMap.value[serial] = defaultOptions();
      }
    },
    { immediate: true },
  );

  const toggleMirror = () => {
    if (props.device.active) {
      emit("execute-action", "stop_mirror");
    } else {
      emit("execute-action", "start_mirror", { ...mirrorOptions.value });
    }
  };
</script>
