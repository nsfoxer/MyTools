use std::collections::HashMap;
use std::io::{BufRead, BufReader, Seek, SeekFrom};
use std::time::Duration;
use std::{error::Error, fs::File};
use std::{fs, thread};

use libc::{sysconf, _SC_CLK_TCK};
use notify_rust::{Notification, Timeout};
use clap::Parser;


static CPU_FILE_PATH: &str = "/proc/stat";

/// Listen CPU usage, if found high usage, will notify highest CPU usage process.
#[derive(Parser, Debug)]
#[clap(author, version, about)]
struct Args {
    /// Seconds to wait between CPU usage calculate
    #[clap(short='n', long, value_parser, default_value_t = 5)]
    interval: usize,
    
    /// Seconds to notify timeout
    #[clap(short, long, value_parser, default_value_t = 10)]
    timeout: u32,

    /// Threshold CPU usage, only when all cpu usage more than this value, can notify 
    #[clap(short, long, value_parser, default_value_t = 20)]
    threshold: u8,
}

// get cpu time split
fn c_sysconf() -> i64 {
    unsafe { sysconf(_SC_CLK_TCK) }
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();
    // 1. init data
    // 1.1 get split time (ms)
    let c = c_sysconf();
    let split_time = 1000 / c;
    let duration = Duration::from_secs(args.interval as u64);
    // 1.3 init cpu file
    let mut cpu_f = File::open(CPU_FILE_PATH).expect("Can't open {{/proc/stat}}");
    let mut old_tasks_usage = HashMap::new();
    let mut old_notify_task_id = 0;

    loop {
        // 2. measure cpu usage
        let cpu_usage = measure_cpu_usage(&duration, &mut cpu_f)?;
        println!("Current CPU usage: {cpu_usage}");

        // 3. if cpu usage is less than threshold, ingnore
        if cpu_usage < args.threshold {
            continue;
        }

        // 4. start find most cpu usage process
        let (max_id, max_usage, new_tasks_usage) =
            get_most_task_usage(args.interval, old_tasks_usage, split_time as usize)?;

        old_tasks_usage = new_tasks_usage;

        // if max_id is invalid or already notify, then don't notify info
        if max_id == 0 || old_notify_task_id == max_id {
            continue;
        }
        if let Some(cmd) = get_cmd_by_task_id(max_id) {
            notify(max_id, max_usage, cmd, args.timeout);
            old_notify_task_id = max_id;
        }
    }
}

// measure cpu usage
fn measure_cpu_usage(interval: &Duration, mut cpu_f: &File) -> Result<u8, Box<dyn Error>> {
    let old_stat = read_first_line(&cpu_f)?;
    cpu_f.seek(SeekFrom::Start(0))?;
    thread::sleep(*interval);
    let new_stat = read_first_line(&cpu_f)?;
    cpu_f.seek(SeekFrom::Start(0))?;

    Ok(calculate_usage(&old_stat, &new_stat))
}

// get most task of cpu usage
// return: (max_task_id, max_usage, new_task_usage)
fn get_most_task_usage(
    second: usize,
    old_task_usage: HashMap<usize, usize>,
    split_time: usize,
) -> Result<(usize, usize, HashMap<usize, usize>), Box<dyn Error>> {
    let (mut max_id, mut max_usage) = (0, 0);
    let mut new_task_usage = HashMap::new();
    for entry in fs::read_dir("/proc/")? {
        let entry = entry?;
        let mut path = entry.path();
        // only find directory
        if !path.is_dir() {
            continue;
        }
        // only process directory and get task id
        let task_id = match path.file_name().unwrap().to_str().unwrap().parse::<usize>() {
            Ok(task_id) => task_id,
            Err(_) => {
                continue;
            }
        };

        // get split time usage and save
        path.push("stat");
        let task_cpu_f = File::open(path)?;
        let (utime, stime) = read_task_time(&task_cpu_f)?;
        let new_ustime = utime + stime;
        new_task_usage.insert(task_id, new_ustime);

        // try calculate task usage
        if let Some(ustime) = old_task_usage.get(&task_id) {
            let usage = (new_ustime - ustime) * split_time / (second * 1000 / 100);
            if usage > max_usage {
                max_id = task_id;
                max_usage = usage;
            }
        }
    }

    Ok((max_id, max_usage, new_task_usage))
}

fn notify(max_id: usize, max_usage: usize, cmd: String, timeout: u32) {
    let cmd = cmd.trim();
    Notification::new()
        .summary("HIGH CPU PROCESS")
        .body(format!("CPU: {max_usage} -- Process: {cmd}[{max_id}]").as_str())
        .icon("dialog-information")
        .hint(notify_rust::Hint::Urgency(notify_rust::Urgency::Normal))
        .timeout(Timeout::Milliseconds(timeout * 1000))
        .show().unwrap();
    println!("Find High CPU Usage Task: {cmd}[{max_id}] --> {max_usage}");
}

// get comm by task id
fn get_cmd_by_task_id(task_id: usize) -> Option<String> {
    let path = format!("/proc/{}/comm", task_id);
    match fs::read_to_string(path) {
        Ok(s) => Some(s),
        Err(_) => None,
    }
}

// get utime and stime
fn read_task_time(f: &File) -> Result<(usize, usize), Box<dyn Error>> {
    let mut buf = BufReader::new(f);
    let mut s = String::new();
    buf.read_line(&mut s)?;

    let data: Vec<&str> = s.split(' ').collect();
    Ok((data[13].parse().unwrap(), data[14].parse().unwrap()))
}

// CPU usage status
struct CPUStat;

#[allow(dead_code)]
impl CPUStat {
    const USER_TIME: u8 = 0;
    const NICE_TIME: u8 = 1;
    const SYSTEM_TIME: u8 = 2;
    const IDLE_TIME: u8 = 3;
    const IOWAIT_TIME: u8 = 4;
    const IRQ_TIME: u8 = 5;
    const SOFTIRQ_TIME: u8 = 6;
}

fn read_first_line(f: &File) -> Result<Vec<usize>, Box<dyn Error>> {
    let mut buf = BufReader::new(f);
    let mut s = String::new();
    buf.read_line(&mut s)?;

    let data: Vec<usize> = s
        .strip_prefix("cpu")
        .unwrap()
        .trim()
        .split(' ')
        .map(|x| x.parse().unwrap())
        .take(7)
        .collect();
    Ok(data)
}

fn calculate_usage(old_stat: &[usize], new_stat: &[usize]) -> u8 {
    let oldsum: usize = old_stat.iter().sum();
    let newsum: usize = new_stat.iter().sum();
    let idlesum: usize =
        new_stat[CPUStat::IDLE_TIME as usize] - old_stat[CPUStat::IDLE_TIME as usize];

    let idle_usage = (idlesum * 100 / (newsum - oldsum)) as u8;

    100 - idle_usage
}
