<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\scrcpy-manager-vue\src\components\ToolbarFrame.vue -->
<template>
  <div>
    <v-card-subtitle class="d-flex align-center px-0">
      <v-icon left>mdi-wrench</v-icon>
      Herramientas
    </v-card-subtitle>

    <!-- Captura y Control -->
    <v-row
      dense
      class="mb-3"
    >
      <v-col cols="6">
        <v-btn
          @click="$emit('action-payload', 'screenshot', { download: true })"
          :disabled="!device || loading"
          :loading="loading"
          block
          variant="tonal"
          color="blue-grey-darken-1"
        >
          <v-icon>mdi-camera</v-icon>
          <span class="ml-1">Screenshot</span>
        </v-btn>
      </v-col>
      <v-col cols="6">
        <v-btn
          @click="$emit('action', 'record')"
          :disabled="!device || loading"
          :loading="loading"
          block
          variant="tonal"
          color="red-darken-2"
        >
          <v-icon>mdi-record-rec</v-icon>
          <span class="ml-1">Record</span>
        </v-btn>
      </v-col>
    </v-row>

    <!-- Control de Pantalla -->
    <v-card-subtitle class="px-0">Control de Pantalla</v-card-subtitle>
    <v-row
      dense
      class="mb-3"
    >
      <v-col cols="6">
        <v-btn
          @click="$emit('action', 'screen_off')"
          :disabled="!device || loading"
          block
          variant="tonal"
          color="amber-darken-2"
          size="small"
        >
          <v-icon>mdi-monitor-off</v-icon>
          <span class="ml-1">Screen OFF</span>
        </v-btn>
      </v-col>
      <v-col cols="6">
        <v-btn
          @click="$emit('action', 'screen_on')"
          :disabled="!device || loading"
          block
          variant="tonal"
          color="teal-darken-1"
          size="small"
        >
          <v-icon>mdi-monitor</v-icon>
          <span class="ml-1">Screen ON</span>
        </v-btn>
      </v-col>
      <v-col cols="6">
        <v-btn
          @click="$emit('action', 'mirror_screen_off')"
          :disabled="!device || loading"
          block
          variant="tonal"
          color="blue-grey-darken-2"
          size="small"
        >
          <v-icon>mdi-eye-off</v-icon>
          <span class="ml-1">Mirror OFF</span>
        </v-btn>
      </v-col>
      <v-col cols="6">
        <v-btn
          @click="$emit('action', 'mirror_screen_on')"
          :disabled="!device || loading"
          block
          variant="tonal"
          color="indigo-darken-1"
          size="small"
        >
          <v-icon>mdi-eye</v-icon>
          <span class="ml-1">Mirror ON</span>
        </v-btn>
      </v-col>
    </v-row>

    <!-- Controles Rápidos -->
    <v-card-subtitle class="px-0">Controles Rápidos</v-card-subtitle>
    <v-row dense>
      <v-col cols="4">
        <v-btn
          @click="$emit('action', 'home')"
          :disabled="!device || loading"
          block
          variant="outlined"
          color="blue-grey-darken-1"
          size="small"
        >
          <v-icon>mdi-home</v-icon>
        </v-btn>
      </v-col>
      <v-col cols="4">
        <v-btn
          @click="$emit('action', 'back')"
          :disabled="!device || loading"
          block
          variant="outlined"
          color="blue-grey-darken-1"
          size="small"
        >
          <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
      </v-col>
      <v-col cols="4">
        <v-btn
          @click="$emit('action', 'recent')"
          :disabled="!device || loading"
          block
          variant="outlined"
          color="blue-grey-darken-1"
          size="small"
        >
          <v-icon>mdi-view-carousel</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
  import type { Device, DeviceAction } from "../types";

  interface Props {
    device: Device | null;
    loading: boolean;
  }

  defineProps<Props>();

  defineEmits<{
    action: [action: DeviceAction, payload?: any];
    "action-payload": [action: DeviceAction, payload: any];
  }>();
</script>
