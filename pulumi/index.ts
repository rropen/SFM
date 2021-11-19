// Copyright 2016-2020, Pulumi Corporation.  All rights reserved.
import * as azuread from "@pulumi/azuread";
import * as pulumi from "@pulumi/pulumi";
import * as random from "@pulumi/random";
import * as tls from "@pulumi/tls";

import * as containerservice from "@pulumi/azure-native/containerservice";
import * as resources from "@pulumi/azure-native/resources";

// Create an Azure Resource Group
const resourceGroup = new resources.ResourceGroup("azure-aks-sfm");

// Create an AD service principal
const adApp = new azuread.Application("aks-sfm", {
  displayName: "sfm",
});
const adSp = new azuread.ServicePrincipal("aksSp-sfm", {
  applicationId: adApp.applicationId,
});

// Generate random password
const password = new random.RandomPassword("password", {
  length: 20,
  special: true,
});

// Create the Service Principal Password
const adSpPassword = new azuread.ServicePrincipalPassword("aksSpSFMPassword", {
  servicePrincipalId: adSp.id,
  value: password.result,
  endDate: "2099-01-01T00:00:00Z",
});

// Generate an SSH key
const sshKey = new tls.PrivateKey("ssh-key", {
  algorithm: "RSA",
  rsaBits: 4096,
});

const config = new pulumi.Config();
const managedClusterName = config.get("managedClusterName") || "azure-aks-sfm";
const cluster = new containerservice.ManagedCluster(managedClusterName, {
  resourceGroupName: resourceGroup.name,
  agentPoolProfiles: [
    {
      count: 3,
      maxPods: 110,
      mode: "System",
      name: "agentpool",
      nodeLabels: {},
      osDiskSizeGB: 30,
      osType: "Linux",
      type: "VirtualMachineScaleSets",
      vmSize: "Standard_B2s",
    },
  ],
  dnsPrefix: resourceGroup.name,
  enableRBAC: true,
  kubernetesVersion: "1.22.2",
  linuxProfile: {
    adminUsername: "testuser",
    ssh: {
      publicKeys: [
        {
          keyData: sshKey.publicKeyOpenssh,
        },
      ],
    },
  },
  nodeResourceGroup: `MC_azure-ts_${managedClusterName}`,
  servicePrincipalProfile: {
    clientId: adApp.applicationId,
    secret: adSpPassword.value,
  },
});

const creds = containerservice.listManagedClusterUserCredentialsOutput({
  resourceGroupName: resourceGroup.name,
  resourceName: cluster.name,
});

const encoded = creds.kubeconfigs[0].value;
export const kubeconfig = encoded.apply((enc) =>
  Buffer.from(enc, "base64").toString()
);
