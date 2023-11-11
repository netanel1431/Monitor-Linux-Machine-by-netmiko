from netmiko import ConnectHandler
from datetime import datetime
import pandas as pd
import numpy as np
import time


def MonitorLinuxMachine(ip,username,password):
    try:
        linux = {
            'device_type': 'linux',
            'ip':ip,
            'username': username,
            'password': password,
            'verbose': True
        }

        connection = ConnectHandler(**linux)
        output1 = connection.send_command('free -t -h -g')
        output2 = connection.send_command("sudo docker stats --no-stream")
        connection.disconnect()

        df_dn48_memory = pd.read_excel("dn48_memory.xlsx")
        for line in output1.splitlines():
            if "Mem: " in line:
                line = line.split()
                timestamp = dt_string
                memory_used = line[2]
                memory_free = line[3]
                memory_shared = line[4]
                memory_buff_cache = line[5]
                memory_available = line[6]
                df_dn48_memory.loc[len(df_dn48_memory.index)] = [timestamp, memory_used, memory_free, memory_shared,
                                                                 memory_buff_cache, memory_available]
                writer = pd.ExcelWriter("dn48_memory.xlsx")
                df_dn48_memory.to_excel(writer, sheet_name="Sheet1", index=False)
                writer._save()

        df_dn48_docker_cpu = pd.read_excel("dn48_docker.xlsx", sheet_name="cpu")
        df_dn48_docker_cpu[dt_string] = np.nan
        df_dn48_docker_name = pd.read_excel("dn48_docker.xlsx", sheet_name="docker_name")
        df_dn48_docker_name[dt_string] = np.nan
        df_dn48_docker_mem_usage = pd.read_excel("dn48_docker.xlsx", sheet_name="docker_mem_usage")
        df_dn48_docker_mem_usage[dt_string] = np.nan
        df_dn48_docker_mem_percentage = pd.read_excel("dn48_docker.xlsx", sheet_name="mem_percentage")
        df_dn48_docker_mem_percentage[dt_string] = np.nan

        for line in output2.splitlines():
            if "CONTAINER ID" in line or line == "" or line == "\n":
                continue
            else:
                line = line.split()
                docker_id = line[0]
                docker_cpu = line[2]
                docker_name = line[1]
                mem_usage = line[3]
                mem_percentage = line[6]
                if docker_id in df_dn48_docker_cpu['docker_id'].unique():
                    userindex1 = df_dn48_docker_cpu.index[df_dn48_docker_cpu['docker_id'] == docker_id]
                    userindex2 = df_dn48_docker_name.index[df_dn48_docker_name['docker_id'] == docker_id]
                    userindex3 = df_dn48_docker_mem_usage.index[df_dn48_docker_mem_usage['docker_id'] == docker_id]
                    userindex4 = df_dn48_docker_mem_percentage.index[
                        df_dn48_docker_mem_percentage['docker_id'] == docker_id]
                    df_dn48_docker_cpu.loc[userindex1, [dt_string]] = docker_cpu
                    df_dn48_docker_name.loc[userindex2, [dt_string]] = docker_name
                    df_dn48_docker_mem_usage.loc[userindex3, [dt_string]] = mem_usage
                    df_dn48_docker_mem_percentage.loc[userindex4, [dt_string]] = mem_percentage

                else:
                    df_dn48_docker_cpu.loc[len(df_dn48_docker_cpu)] = {"docker_id": docker_id, dt_string: docker_cpu}
                    df_dn48_docker_name.loc[len(df_dn48_docker_name)] = {"docker_id": docker_id, dt_string: docker_name}
                    df_dn48_docker_mem_usage.loc[len(df_dn48_docker_mem_usage)] = {"docker_id": docker_id,
                                                                                   dt_string: mem_usage}
                    df_dn48_docker_mem_percentage.loc[len(df_dn48_docker_mem_percentage)] = {"docker_id": docker_id,
                                                                                             dt_string: mem_percentage}

        writer = pd.ExcelWriter("dn48_docker.xlsx")
        df_dn48_docker_cpu.to_excel(writer, sheet_name="cpu", index=False)
        df_dn48_docker_name.to_excel(writer, sheet_name="docker_name", index=False)
        df_dn48_docker_mem_usage.to_excel(writer, sheet_name="docker_mem_usage", index=False)
        df_dn48_docker_mem_percentage.to_excel(writer, sheet_name="mem_percentage", index=False)
        writer._save()

    except Exception as e:
        print("Failed RUN at time:{0} because :{1} ".format(dt_string, e))


if __name__ == "__main__":
    while True:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        MonitorLinuxMachine(ip="192.168.1.1", username="test", password="test_pass")
        time.sleep(60)

