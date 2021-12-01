// Copyright 2016-2020, Pulumi Corporation.  All rights reserved.
import * as azuread from "@pulumi/azuread";
import * as pulumi from "@pulumi/pulumi";
import * as random from "@pulumi/random";
import * as tls from "@pulumi/tls";
import * as k8s from "@pulumi/kubernetes";

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

// export const provider = new k8s.Provider("askK8s",
//   {
//     kubeconfig: kubeconfig,
//   });

/* =======
Argo CD
======= */

// // Create a new namespace for ArgoCD
// const name = "argocd"
// const ns = new k8s.core.v1.Namespace("argocd", {
//     metadata: { name: name },
// }, { provider });

// const argocd = new k8s.yaml.ConfigFile(
//   "argocd",
//   {
//     file: "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
//   }
// )

// //Export the private cluster IP address of ArgoCD
// const argocdIp = argocd.getResource("v1/Service", "argocd");
// export const privateIp = argocdIp.spec.clusterIP

// // export const url = argocd.getResourceProperty("v1/Service", `${name}/argocd-server`, "status").apply(status => status.loadBalancer.ingress[0].hostname)
