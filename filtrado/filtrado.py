import subprocess


def subir_a_hdfs(local_path, hdfs_path):
    subprocess.run(["hdfs", "dfs", "-mkdir", "-p", "/datos"], check=True)
    subprocess.run(["hdfs", "dfs", "-put", "-f", local_path, hdfs_path], check=True)
    print("Archivo subido a HDFS")

if __name__ == "__main__":
    with open("archivo2.txt", "w") as f:
        f.write("hola mundo")

    subir_a_hdfs("archivo2.txt", "/datos/archivo2.txt")
