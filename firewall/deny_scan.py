#!/bin/python
import os
import subprocess
import json
import sqlite3

BLOCK_COUNT = 3
bad_ip = {
    "": 0,
}
banned_ip = []

def print_dict():
    for k, v in bad_ip.items():
        print(f"ip: {k}, count: {v}")
    for ip in banned_ip:
        print(f"{ip}", end=" ")
    print("")

def init():
    conn = sqlite3.connect("./ip.db")
    cur = conn.cursor()
    cur.execute("select count(name) from sqlite_master where type='table' and name='ip_info'")
    if cur.fetchone()[0] == 0:
        # 表不存在
        cur.execute('''
            CREATE TABLE ip_info (
                ip TEXT NOT NULL,
                count INTEGER NOT NULL,
                deny INTEGER NOT NULL
            );
        ''')
    else:
        rows = cur.execute("select ip, count, deny from ip_info")
        for row in rows:
            (ip, count, deny) = row
            bad_ip[ip] = count
            if deny == 1:
                banned_ip.append(ip)
    conn.commit()
    conn.close()
    print_dict()
    return

def handle_data(data: dict):
    msg: str = data["MESSAGE"]
    if not msg or not msg.startswith("[UFW BLOCK]"):
        return
    src_ip = msg.split(" ")[5].split('=')[1]
    print(src_ip)
    if not bad_ip.get(src_ip):
        bad_ip[src_ip] = 1
    else:
        bad_ip[src_ip] += 1
    deny_ip()

def deny_ip():
    for ip, count in bad_ip.items():
        if count < BLOCK_COUNT:
            continue
        elif ip not in banned_ip:
            print(f"deny: {ip}")
            os.system(f"sudo ufw insert 1 deny from {ip}")
            banned_ip.append(ip)
    return

def save_data():
    conn = sqlite3.connect("./ip.db")
    cur = conn.cursor()
    for ip, count in bad_ip.items():
        deny = 0
        if ip in banned_ip:
            deny = 1
        rows = cur.execute("select * from ip_info where ip = ?", (ip,)).fetchall()
        if rows:
            # 更新ip信息
            cur.execute("update ip_info set count=?, deny=? where ip=?", (count, deny, ip))
        else:
            # 没有该ip
            cur.execute("insert into ip_info(ip, count, deny) values (?, ?, ?)", (ip, count, deny))
    conn.commit()
    conn.close()
    print_dict()
    return

def main():
    init()
    ret = subprocess.Popen(args=["sudo", "journalctl", "-f" ,"-o", "json"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        while True:
            line = ret.stdout.readline()
            data = json.loads(line.strip())
            handle_data(data)
    except KeyboardInterrupt:
        print("Ctrl+c .....")
        save_data()
        ret.kill()

if __name__ == "__main__":
    main()
