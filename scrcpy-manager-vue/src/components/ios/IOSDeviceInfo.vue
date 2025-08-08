<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\src\components\ios\IOSDeviceInfo.vue -->
<template>
  <div v-if="device">
    <v-list class="bg-transparent">
      <v-list-item>
        <template #prepend>
          <v-icon :color="getStatusColor()">mdi-apple</v-icon>
        </template>

        <v-list-item-title class="d-flex align-center">
          <span class="text-h6 font-weight-bold">
            {{ displayName }}
          </span>
          
          <v-chip
            color="blue-grey"
            size="x-small"
            variant="outlined"
            class="ml-2"
          >
            iOS
          </v-chip>

          <!-- Botón para editar alias -->
          <v-btn
            icon
            size="small"
            variant="text"
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
            <v-icon start size="small">{{ getStatusIcon() }}</v-icon>
            {{ getStatusText() }}
          </v-chip>
          
          <v-chip
            v-if="device.active"
            color="success"
            size="small"
            variant="tonal"
          >
            <v-icon start size="small">mdi-cast-connected</v-icon>
            Mirror Activo
          </v-chip>
        </v-list-item-subtitle>
      </v-list-item>

      <!-- Información específica de iOS -->
      <v-list-item>
        <template #prepend>
          <v-icon>mdi-apple</v-icon>
        </template>
        <v-list-item-title>Modelo</v-list-item-title>
        <v-list-item-subtitle>{{ device.model }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item>
        <template #prepend>
          <v-icon>mdi-cellphone-cog</v-icon>
        </template>
        <v-list-item-title>iOS</v-list-item-title>
        <v-list-item-subtitle>{{ device.ios_version }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item>
        <template #prepend>
          <v-icon>mdi-identifier</v-icon>
        </template>
        <v-list-item-title>UDID</v-list-item-title>
        <v-list-item-subtitle class="font-mono">{{ device.serial }}</v-list-item-subtitle>
      </v-list-item>

      <!-- Sesión de mirror si está activa -->
      <v-list-item v-if="mirrorSession">
        <template #prepend>
          <v-icon color="success">mdi-cast</v-icon>
        </template>
        <v-list-item-title>Mirror Activo</v-list-item-title>
        <v-list-item-subtitle>
          Puerto: {{ mirrorSession.port }} | 
          Calidad: {{ mirrorSession.options.quality }} |
          FPS: {{ mirrorSession.options.fps }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>

    <!-- Dialog para editar alias -->
    <v-dialog v-model="editDialog" max-width="450">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-tag-outline</v-icon>
          Editar Alias - Dispositivo iOS
        </v-card-title>

        <v-card-text>
          <v-text-field
            v-model="newAlias"
            label="Alias personalizado"
            :placeholder="device.name || 'Mi iPhone'"
            variant="outlined"
            density="compact"
            counter="30"
            autofocus
            @keyup.enter="saveAlias"
            clearable
          >
            <template #prepend-inner>
              <v-icon size="small">mdi-tag</v-icon>
            </template>
          </v-text-field>

          <div class="text-caption text-grey mt-2">
            <div><strong>UDID:</strong> {{ device.serial }}</div>
            <div><strong>Modelo:</strong> {{ device.model }}</div>
            <div><strong>iOS:</strong> {{ device.ios_version }}</div>
          </div>
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

  <div v-else class="text-center py-4">
    <v-icon size="64" color="grey">mdi-apple</v-icon>
    <p class="text-grey mt-2">No hay dispositivo iOS seleccionado</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { IOSDevice, IOSMirrorSession } from '../../types/ios';

interface Props {
  device: IOSDevice | null;
  mirrorSession?: IOSMirrorSession;
}

interface Emits {
  (e: 'alias-updated', udid: string, alias: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Estado para edición
const editDialog = ref(false);
const newAlias = ref('');
const updating = ref(false);

// Nombre a mostrar
const displayName = computed(() => {
  if (!props.device) return '';
  return props.device.alias || props.device.name || `iPhone ${props.device.serial.slice(-4)}`;
});

const getStatusColor = (): string => {
  if (!props.device) return "grey";
  return props.device.connected ? "success" : "error";
};

const getStatusIcon = (): string => {
  if (!props.device) return "mdi-apple";
  return props.device.connected ? "mdi-usb" : "mdi-usb-off";
};

const getStatusText = (): string => {
  if (!props.device) return "Sin dispositivo";
  return props.device.connected ? "Conectado" : "Desconectado";
};

const openEditDialog = () => {
  if (!props.device) return;
  newAlias.value = props.device.alias || '';
  editDialog.value = true;
};

const saveAlias = async () => {
  if (!props.device) return;
  
  updating.value = true;
  
  try {
    const alias = newAlias.value.trim() || props.device.name || `iPhone ${props.device.serial.slice(-4)}`;
    emit('alias-updated', props.device.serial, alias);
    editDialog.value = false;
  } finally {
    updating.value = false;
  }
};
</script>

<style scoped>
.font-mono {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}
</style>