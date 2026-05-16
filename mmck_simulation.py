import random
import time
import math

def get_inputs():
    print("--- m/m/c/k queue simulation ---")

    while True:
        try:
            k = int(input("enter system capacity (k): "))
            if k < 1:
                print("  error: k must be >= 1")
                continue
            break
        except ValueError:
            print("  error: k must be an integer")

    while True:
        try:
            c = int(input("enter number of servers (c): "))
            if c < 1:
                print("  error: c must be >= 1")
                continue
            break
        except ValueError:
            print("  error: c must be an integer")

    while True:
        try:
            lam = float(input("enter arrival rate (lambda): "))
            if lam <= 0:
                print("  error: lambda must be > 0")
                continue
            break
        except ValueError:
            print("  error: lambda must be a number")

    while True:
        try:
            mu = float(input("enter service rate (mu): "))
            if mu <= 0:
                print("  error: mu must be > 0")
                continue
            break
        except ValueError:
            print("  error: mu must be a number")

    
    while True:
        try:
            sim_time = float(input("enter simulation time: "))
            if sim_time <= 0:
                print("error: simulation time must be > 0")
                continue
            break
        except ValueError:
            print("  error: mu must be a number")
    

    return k, c, lam, mu, sim_time

def run_simulation(k, c, lam, mu, sim_time=50.0):
    clock = 0
    queue = []
    servers = [None] * c  # each slot is None or (customer_id, service_end_time)
    next_arrival = random.expovariate(lam)
    customer_id = 0
    events_log = []

    arrival_times = {}
    service_start_times = {}
    departure_times = {}
    rejected = []

    while clock < sim_time:
        # find next service completion among busy servers
        next_departure = float('inf')
        for s in servers:
            if s is not None:
                if s[1] < next_departure:
                    next_departure = s[1]

        # move clock to next event
        if next_arrival < next_departure:
            clock = next_arrival
            customer_id += 1
            cid = customer_id
            arrival_times[cid] = clock

            total_in_system = sum(1 for s in servers if s is not None) + len(queue)

            if total_in_system >= k:
                rejected.append(cid)
                events_log.append((clock, f"customer {cid} arrived but system is full, rejected"))
            else:
                # check for free server
                free = None
                for i in range(len(servers)):
                    if servers[i] is None:
                        free = i
                        break
                if free is not None:
                    svc_time = random.expovariate(mu)
                    servers[free] = (cid, clock + svc_time)
                    service_start_times[cid] = clock
                    events_log.append((clock, f"customer {cid} arrived, goes to server {free+1}"))
                else:
                    queue.append(cid)
                    events_log.append((clock, f"customer {cid} arrived, joins queue (queue size: {len(queue)})"))

            next_arrival = clock + random.expovariate(lam)

        else:
            clock = next_departure
            # find which server finished
            for i in range(len(servers)):
                if servers[i] is not None and servers[i][1] == next_departure:
                    done_cid = servers[i][0]
                    departure_times[done_cid] = clock
                    events_log.append((clock, f"customer {done_cid} finished service at server {i+1}"))
                    servers[i] = None

                    if queue:
                        next_cid = queue.pop(0)
                        svc_time = random.expovariate(mu)
                        servers[i] = (next_cid, clock + svc_time)
                        service_start_times[next_cid] = clock
                        events_log.append((clock, f"customer {next_cid} moved from queue to server {i+1}"))
                    break

    return events_log, arrival_times, service_start_times, departure_times, rejected

def calc_metrics(arrival_times, service_start_times, departure_times):
    completed = [cid for cid in departure_times]
    if not completed:
        return 0, 0, 0, 0

    ts_list = [departure_times[c] - arrival_times[c] for c in completed]
    tq_list = [service_start_times[c] - arrival_times[c] for c in completed if c in service_start_times]

    ts = sum(ts_list) / len(ts_list)
    tq = sum(tq_list) / len(tq_list) if tq_list else 0

    # little's law approximation
    # average lambda effective
    total_time = max(departure_times.values()) - min(arrival_times.values()) if departure_times else 1
    lam_eff = len(completed) / total_time if total_time > 0 else 0

    ns = lam_eff * ts
    nq = lam_eff * tq

    return ts, tq, ns, nq

def main():
    k, c, lam, mu, sim_time = get_inputs()
    print("\nstarting simulation...\n")
    time.sleep(0.5)

    events_log, arrival_times, service_start_times, departure_times, rejected = run_simulation(k, c, lam, mu, sim_time)

    for t, msg in events_log:
        print(f"  [t={t:.3f}] {msg}")
        time.sleep(0.05)

    print("\n--- simulation ended ---\n")

    ts, tq, ns, nq = calc_metrics(arrival_times, service_start_times, departure_times)

    print(f"total customers arrived : {len(arrival_times)}")
    print(f"total rejected          : {len(rejected)}")
    print(f"total served            : {len(departure_times)}")
    print()
    print(f"ts (avg time in system) : {ts:.4f}")
    print(f"tq (avg time in queue)  : {tq:.4f}")
    print(f"ns (avg number in system): {ns:.4f}")
    print(f"nq (avg number in queue) : {nq:.4f}")

main()
