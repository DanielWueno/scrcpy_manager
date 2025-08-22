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
        :options="mirrorOptions.value"
        :deviceActive="device.active"
        :actionLoading="actionLoading"
        @toggle-mirror="toggleMirror"
      />
      <DeviceActions
        :actionLoading="actionLoading"
        @execute-action="$emit('execute-action', $event)"
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  // ...existing code...
  import type { Device } from "../../types";
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

  import { ref, watch } from "vue";
  const mirrorOptions = ref({
    StayAwake: true,
    NoAudio: true,
    ShowTouches: false,
    TurnScreenOff: false,
  });

  watch(
    () => props.device,
    (newDevice) => {
      mirrorOptions.value = {
        StayAwake: true,
        NoAudio: true,
        ShowTouches: false,
        TurnScreenOff: false,
      };
    }
  );

  const toggleMirror = () => {
    if (props.device.active) {
      emit("execute-action", "stop_mirror");
    } else {
      emit("execute-action", "start_mirror", { ...mirrorOptions.value });
    }
  };
</script>
