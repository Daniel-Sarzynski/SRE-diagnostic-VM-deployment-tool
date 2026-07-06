#!/usr/bin/env python3

import sys
from datetime import datetime

from diagnostics import LocalDiagnostics, LogParser
from provisioner import AzureProvisioner

class DiagnosticApp:
    """Ties diagnostics and log parsing routines into a terminal UI layer."""
    
    def __init__(self):
        self.diagnostics = LocalDiagnostics()
        self.parser = LogParser()
        self.provisioner = AzureProvisioner()

    def generate_full_report(self):
        """Generates system statistics report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("\n" + "="*70)
        print(f"       SRE SYSTEM DIAGNOSTICS REPORT ({timestamp})")
        print("="*70)
        
        print(self.diagnostics.get_memory_utilization())
        print("-" * 40)
        print(self.diagnostics.get_disk_utilization())
        print("-" * 40)
        print(self.diagnostics.get_cpu_and_processes())
        print("-" * 40)
        print(self.diagnostics.get_network_connections())
        print("="*70 + "\n")

    def run_menu(self):
        while True:
            print("\n" + "="*45)
            print("   SRE DIAGNOSTIC & AUTOMATION TOOL")
            print("="*45)
            print(" [LOCAL SYSTEM UTILITIES]")
            print("1. Run Full System Diagnostics Report")
            print("2. Parse Custom Application/System Log File")
            print(" [AUTOMATED CLOUD DEPLOYMENTS]")
            print("3. Deploy VM")
            print("4. Execute Teardown Routine")
            print(" [SYSTEM]")
            print("0. Exit")
            print("="*45)
            
            choice = input("Select a operation [1-4]: ").strip()
            
            if choice == "1":
                self.generate_full_report()
            elif choice == "2":
                path = input("Provide path to log file target: ").strip()
                print("\n" + self.parser.calculate_error_frequencies(path))
            elif choice == "3":
                rg = input("Enter Resource Group Name [sre-project0]: ").strip() or "sre-project0"
                vm = input("Enter VM Name [vm-diagnostic-01]: ").strip() or "vm-diagnostic-01"
                location = input("Enter Region [koreacentral]: ").strip() or "koreacentral"
                if rg and vm:
                    self.provisioner.deploy_vm(rg, vm, location)
            elif choice == "4":
                rg = input("Enter Resource Group Name to Destroy: ").strip()
                if rg:
                    self.provisioner.teardown_infrastructure(rg)
                else:
                    print("[!] Target cannot be blank.")
            elif choice == "0":
                print("\nExiting. Goodbye.")
                sys.exit(0)
            else:
                print("\n[!] Invalid input. Please select an option from 1 to 4.")

if __name__ == "__main__":
    
    app = DiagnosticApp()
    app.run_menu()