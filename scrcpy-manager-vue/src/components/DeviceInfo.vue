<template>
  <div v-if="device">
    <v-list class="bg-transparent">
      <v-list-item>
        <template #prepend>
          <v-icon :color="getStatusColor()">{{ getStatusIcon() }}</v-icon>
        </template>

        <v-list-item-title class="d-flex align-center">
          <span class="text-h6 font-weight-bold">
            {{ displayName }}
          </span>

          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="!device"
            @click="openEditDialog"
          >
            <v-icon size="small">mdi-pencil</v-icon>
          </v-btn>
        </v-list-item-title>

        <v-list-item-subtitle class="d-flex align-center">
          <v-chip
            :color="getStatusColor()"
            size="small"
            variant="tonal"
            class="mr-2"
          >
            <v-icon
              start
              size="small"
              >{{ getStatusIcon() }}</v-icon
            >
            {{ getStatusText() }}
          </v-chip>

          <v-chip
            v-if="device.active"
            color="success"
            size="small"
            variant="tonal"
          >
            <v-icon
              start
              size="small"
            >
              mdi-cast-connected
            </v-icon>
            Mirror Activo
          </v-chip>
        </v-list-item-subtitle>
      </v-list-item>

      <v-list-item v-if="device.name && device.name !== displayName">
        <template #prepend>
          <v-icon>mdi-cellphone</v-icon>
        </template>
        <v-list-item-title>Modelo</v-list-item-title>
        <v-list-item-subtitle>{{ device.name }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item>
        <template #prepend>
          <v-icon>mdi-identifier</v-icon>
        </template>
        <v-list-item-title>Serial</v-list-item-title>
        <v-list-item-subtitle class="font-mono">{{
          device.serial
        }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item v-if="device.alias && device.alias !== device.name">
        <template #prepend>
          <v-icon>mdi-tag</v-icon>
        </template>
        <v-list-item-title>Alias Personalizado</v-list-item-title>
        <v-list-item-subtitle>{{ device.alias }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item v-if="device.last_seen">
        <template #prepend>
          <v-icon>mdi-clock-outline</v-icon>
        </template>
        <v-list-item-title>Última Conexión</v-list-item-title>
        <v-list-item-subtitle>{{
          formatLastSeen(device.last_seen)
        }}</v-list-item-subtitle>
      </v-list-item>
    </v-list>

    <v-dialog
      v-model="editDialog"
      max-width="450"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-tag-outline</v-icon>
          Editar Alias del Dispositivo
        </v-card-title>

        <v-card-text>
          <v-text-field
            v-model="newAlias"
            label="Alias personalizado"
            :placeholder="device.name || 'Mi dispositivo'"
            variant="outlined"
            density="compact"
            :rules="[rules.maxLength]"
            counter="30"
            autofocus
            clearable
            @keyup.enter="saveAlias"
          >
            <template #prepend-inner>
              <v-icon size="small">mdi-tag</v-icon>
            </template>
          </v-text-field>

          <div class="text-caption text-grey mt-2">
            <div><strong>Serial:</strong> {{ device.serial }}</div>
            <div v-if="device.name">
              <strong>Modelo:</strong> {{ device.name }}
            </div>
            <div>
              <strong>Estado:</strong>
              <v-chip
                :color="getStatusColor()"
                size="x-small"
                class="ml-1"
              >
                {{ getStatusText() }}
              </v-chip>
            </div>
          </div>

          <v-alert
            v-if="!newAlias.trim()"
            type="info"
            density="compact"
            class="mt-3"
          >
            Si no especificas un alias, se usará el nombre del modelo.
          </v-alert>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn @click="editDialog = false">Cancelar</v-btn>
          <v-btn
            color="primary"
            :loading="updating"
            @click="saveAlias"
          >
            Guardar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>

  <div
    v-else
    class="text-center py-4"
  >
    <v-icon
      size="64"
      color="grey"
    >
      mdi-cellphone-off
    </v-icon>
    <p class="text-grey mt-2">No hay dispositivo seleccionado</p>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed } from "vue";
  import type { Device } from "../types";

  interface Props {
    device: Device | null;
  }

  interface Emits {
    (e: "alias-updated", serial: string, alias: string): void;
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const editDialog = ref(false);
  const newAlias = ref("");
  const updating = ref(false);

  const rules = {
    maxLength: (value: string) =>
      !value || value.length <= 30 || "Máximo 30 caracteres",
  };

  const displayName = computed(() => {
    if (!props.device) return "";
    return (
      props.device.alias ||
      props.device.name ||
      `Dispositivo ${props.device.serial.slice(-4)}`
    );
  });

  const getStatusColor = (): string => {
    if (!props.device) return "grey";
    return props.device.connected ? "teal-darken-1" : "red-darken-2";
  };

  const getStatusIcon = (): string => {
    if (!props.device) return "mdi-cellphone-off";
    return props.device.connected ? "mdi-usb" : "mdi-usb-off";
  };

  const getStatusText = (): string => {
    if (!props.device) return "Sin dispositivo";
    return props.device.connected ? "Conectado" : "Desconectado";
  };

  const formatLastSeen = (lastSeen: string): string => {
    try {
      const date = new Date(lastSeen);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / (1000 * 60));

      if (diffMins < 1) return "Ahora mismo";
      if (diffMins < 60)
        return `Hace ${diffMins} minuto${diffMins > 1 ? "s" : ""}`;

      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24)
        return `Hace ${diffHours} hora${diffHours > 1 ? "s" : ""}`;

      const diffDays = Math.floor(diffHours / 24);
      return `Hace ${diffDays} día${diffDays > 1 ? "s" : ""}`;
    } catch {
      return "Fecha no válida";
    }
  };

  const openEditDialog = () => {
    if (!props.device) return;
    newAlias.value = props.device.alias || "";
    editDialog.value = true;
  };

  const saveAlias = async () => {
    if (!props.device) return;

    updating.value = true;

    try {
      const alias =
        newAlias.value.trim() ||
        props.device.name ||
        `Dispositivo ${props.device.serial.slice(-4)}`;
      emit("alias-updated", props.device.serial, alias);
      editDialog.value = false;
    } finally {
      updating.value = false;
    }
  };
</script>

<style scoped>
  .font-mono {
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 0.9em;
  }
</style>
