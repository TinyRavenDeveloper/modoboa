<template>
<div>
  <v-toolbar flat>
    <v-toolbar-title><translate>Identities</translate></v-toolbar-title>
    <v-spacer />
    <v-btn class="mr-2">
      <v-icon>mdi-file-import-outline</v-icon>
    </v-btn>
    <v-btn class="mr-2">
      <v-icon>mdi-file-export-outline</v-icon>
    </v-btn>
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="primary" v-bind="attrs" v-on="on">
          <v-icon left>mdi-plus</v-icon>
          <translate>New</translate>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item @click="showCreationWizard = true">
          <v-list-item-title><translate>Account</translate></v-list-item-title>
        </v-list-item>
        <v-list-item @click="showAliasCreationWizard = true">
          <v-list-item-title><translate>Alias</translate></v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-toolbar>
  <identity-list ref="identities" />

  <v-dialog
    v-model="showCreationWizard"
    fullscreen
    scrollable
    transition="dialog-bottom-transition"
    persistent
    >
    <account-creation-form @close="closeCreationWizard" @created="updateIdentities" />
  </v-dialog>
    <v-dialog
    v-model="showAliasCreationWizard"
    fullscreen
    scrollable
    transition="dialog-bottom-transition"
    persistent
    >
    <alias-creation-form @close="closeAliasWizard" @created="updateIdentities" />
  </v-dialog>
</div>
</template>

<script>
import AccountCreationForm from '@/components/identities/AccountCreationForm'
import AliasCreationForm from '@/components/identities/AliasCreationForm'
import IdentityList from '@/components/identities/IdentityList'

export default {
  components: {
    AccountCreationForm,
    AliasCreationForm,
    IdentityList
  },
  data () {
    return {
      showAliasCreationWizard: false,
      showCreationWizard: false
    }
  },
  methods: {
    closeAliasWizard () {
      this.showAliasCreationWizard = false
    },
    closeCreationWizard () {
      this.showCreationWizard = false
    },
    updateIdentities () {
      this.$refs.identities.fetchIdentities()
    }
  }
}
</script>

<style scoped>
.v-toolbar {
  background-color: #f7f8fa !important;
}
</style>
