#!/usr/bin/env python3
"""
The Network Sentinel - Sensor Module
Zero-State: Liest offene Netzwerkverbindungen aus und zeigt sie im Terminal an.
Keine blockierenden Aktionen.
"""
import sys
import platform
import subprocess

def get_network_connections():
    print("🛡️  The Network Sentinel - Zero-State Sensor")
    print("=" * 60)
    print("Scanne aktive Netzwerkverbindungen (ESTABLISHED)...\n")
    
    try:
        import psutil
        connections = psutil.net_connections(kind='inet')
        established = [c for c in connections if c.status == 'ESTABLISHED']
        
        print(f"Gefundene ESTABLISHED Verbindungen: {len(established)}")
        print(f"{'Protokoll':<10} | {'Lokale Adresse':<22} | {'Remote Adresse':<22} | {'PID':<8}")
        print("-" * 75)
        
        for conn in established[:20]: # Max. 20 Connections als erste Übersicht
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
            print(f"{'TCP/UDP':<10} | {laddr:<22} | {raddr:<22} | {conn.pid or 'N/A':<8}")
            
        if len(established) > 20:
            print(f"... und {len(established) - 20} weitere.")
            
    except ImportError:
        # Fallback falls psutil nicht zur Verfügung steht
        print("⚠️ psutil nicht installiert. Nutze System-Tools als Fallback...\n")
        cmd = "netstat -an | findstr ESTABLISHED" if platform.system() == "Windows" else "netstat -an | grep ESTABLISHED"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            for line in lines[:20]:
                print(line.strip())
            
            if len(lines) > 20:
                print(f"... und {len(lines) - 20} weitere.")
        except Exception as e:
            print(f"Fehler beim Lesen der Verbindungen: {e}")

if __name__ == "__main__":
    get_network_connections()
