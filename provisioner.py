import subprocess
import time

class AzureProvisioner:
    """Interfaces securely with the Azure CLI to deploy and destroy VM."""

    def __init__(self):
        self.az_available = self._check_azure_cli()

    def _check_azure_cli(self):
        try:
            subprocess.run(["az", "--version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def _run_az_cmd(self, args, success_msg, failure_msg):
        if not self.az_available:
            print("[!] Aborted: Azure CLI is not installed or accessible in the current PATH.")
            return False
        
        print(f"Executing: az {' '.join(args[1:])}")
        try:
            subprocess.run(args, check=True)
            print(f"[+] Success: {success_msg}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[!] Error: {failure_msg}\nDetails: {e}")
            return False

    def deploy_vm(self, rg_name, vm_name, location):
        print(f"Initializing Azure Deployment Pipeline in [{location}]")

        rg_created = self._run_az_cmd(
            ["az", "group", "create", "--name", rg_name, "--location", location],
            f"Resource Group '{rg_name}' created.",
            f"Failed to create resource group '{rg_name}'."
        )
        if not rg_created:
            return
            
        time.sleep(5)   
            
        vm_created = self._run_az_cmd(
            [
                "az", "vm", "create",
                "--resource-group", rg_name,
                "--name", vm_name,
                "--location", location,
                "--image", "Ubuntu2404",
                "--size", "Standard_B2ats_v2",
                "--storage-sku", "Standard_LRS",
                "--boot-diagnostics-storage", "",
                "--admin-username", "azureuser",
                "--generate-ssh-keys", 
                #"--priority", "Spot",
                #"--max-price", "-1"
            ],
            f"Virtual Machine '{vm_name}' successfully provisioned.",
            f"Failed to provision Virtual Machine '{vm_name}'."
        )
        if not vm_created:
            return
        
        time.sleep(5) 

        self._run_az_cmd(
            [
                "az", "vm", "auto-shutdown",
                "--resource-group", rg_name,
                "--name", vm_name,
                "--time", "2100"
            ],
            f"Auto-shutdown window hardcoded to 21:00 UTC daily on '{vm_name}'.",
            f"Failed to bind auto-shutdown schedules to '{vm_name}'."
        )

    def teardown_infrastructure(self, rg_name):
        print(f"[WARNING] Initiating Complete Teardown Lifecycle for Group: [{rg_name}]")
        confirm = input(f"Are you sure you want to permanently delete group '{rg_name}'? (y/n): ").strip().lower()
        
        if confirm == "y":
            self._run_az_cmd(
                ["az", "group", "delete", "--name", rg_name, "--yes"],
                f"Resource group '{rg_name}' and all associated resources have been destroyed.",
                f"Failed to destroy '{rg_name}'."
            )
        else:
            print("Teardown cancelled.")