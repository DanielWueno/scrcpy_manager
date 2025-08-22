<template>
  <v-card
    variant="outlined"
    class="mb-4"
  >
    <v-card-subtitle class="pb-2">
      <v-icon
        class="mr-1"
        size="16"
        >mdi-settings</v-icon
      >
      Opciones de Mirror
    </v-card-subtitle>
    <v-card-text class="pt-0">
      <v-row
        dense
        class="mb-3"
      >
        <v-col cols="6">
          <v-switch
            v-model="options.stayAwake"
            color="success"
            hide-details
            density="compact"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon
                  class="mr-1"
                  size="16"
                  >mdi-eye</v-icon
                >
                <span class="text-caption">Mantener Despierto</span>
              </div>
            </template>
          </v-switch>
        </v-col>
        <v-col cols="6">
          <v-switch
            v-model="options.noAudio"
            color="primary"
            hide-details
            density="compact"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon
                  class="mr-1"
                  size="16"
                  >mdi-volume-off</v-icon
                >
                <span class="text-caption">Sin Audio</span>
              </div>
            </template>
          </v-switch>
        </v-col>
        <v-col cols="6">
          <v-switch
            v-model="options.showTouches"
            color="warning"
            hide-details
            density="compact"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon
                  class="mr-1"
                  size="16"
                  >mdi-hand-pointing-up</v-icon
                >
                <span class="text-caption">Mostrar Toques</span>
              </div>
            </template>
          </v-switch>
        </v-col>
        <v-col cols="6">
          <v-switch
            v-model="options.turnScreenOff"
            color="purple"
            hide-details
            density="compact"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon
                  class="mr-1"
                  size="16"
                  >mdi-monitor-off</v-icon
                >
                <span class="text-caption">Apagar Pantalla</span>
              </div>
            </template>
          </v-switch>
        </v-col>
      </v-row>
      <v-btn
        :color="deviceActive ? 'error' : 'success'"
        :variant="'elevated'"
        :loading="actionLoading"
        :disabled="actionLoading"
        size="large"
        block
        @click="toggleMirror"
      >
        <v-icon class="mr-2">{{
          deviceActive ? "mdi-stop" : "mdi-play"
        }}</v-icon>
        {{ deviceActive ? "Detener Mirror" : "Iniciar Mirror" }}
      </v-btn>
      <div
        v-if="hasActiveOptions"
        class="mt-2"
      >
        <v-chip-group>
          <v-chip
            v-if="options.stayAwake"
            size="x-small"
            color="success"
            ><v-icon
              start
              size="12"
              >mdi-eye</v-icon
            >Despierto</v-chip
          >
          <v-chip
            v-if="options.noAudio"
            size="x-small"
            color="primary"
            ><v-icon
              start
              size="12"
              >mdi-volume-off</v-icon
            >Sin Audio</v-chip
          >
          <v-chip
            v-if="options.showTouches"
            size="x-small"
            color="warning"
            ><v-icon
              start
              size="12"
              >mdi-hand-pointing-up</v-icon
            >Toques</v-chip
          >
          <v-chip
            v-if="options.turnScreenOff"
            size="x-small"
            color="purple"
            ><v-icon
              start
              size="12"
              >mdi-monitor-off</v-icon
            >Pantalla Off</v-chip
          >
        </v-chip-group>
      </div>
    </v-card-text>
  </v-card>
</template>
<script setup lang="ts">
  import { ref, computed, watch } from "vue";
  const props = defineProps<{
    options: any;
    deviceActive: boolean;
    actionLoading: boolean;
  }>();
  const emit = defineEmits<{
    (e: "update:options", value: any): void;
    (e: "toggle-mirror"): void;
  }>();
  const options = ref({ ...props.options });
  watch(options, (val) => emit("update:options", val), { deep: true });
  const hasActiveOptions = computed(() =>
    Object.values(options.value).some(Boolean)
  );
  const toggleMirror = () => emit("toggle-mirror");
</script>
