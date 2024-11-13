import sys

# Selection Sort: Sort by Salary
def selection_sort(applications, key, reverse=False):
    n = len(applications)
    for i in range(n):
        selected = i
        for j in range(i + 1, n):
            try:
                # Compare values with `get` to handle missing keys
                if (applications[j].get(key, float('inf')) < applications[selected].get(key, float('inf'))) != reverse:
                    selected = j
            except KeyError:
                continue  # Skip if key is missing
        # Swap if a new selected index was found
        applications[i], applications[selected] = applications[selected], applications[i]
    
    # Space complexity is approximately the size of applications list
    space_complexity_bytes = sys.getsizeof(applications)
    return applications, space_complexity_bytes

def shell_sort(applications, key, reverse=False):
    n = len(applications)
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            temp = applications[i]
            j = i
            # Compare using the provided key
            while j >= gap and (applications[j - gap][key] > temp[key]) != reverse:
                applications[j] = applications[j - gap]
                j -= gap
            applications[j] = temp
        gap //= 2
    
    # Space complexity is approximately the size of applications list
    space_complexity_bytes = sys.getsizeof(applications)
    return applications, space_complexity_bytes

def bucket_sort_with_selection(applications, key, reverse=False):
    # Creating buckets for the provided key
    buckets = {}
    for app in applications:
        bucket_key = app[key]
        if bucket_key not in buckets:
            buckets[bucket_key] = []
        buckets[bucket_key].append(app)
    
    # Sort each bucket using selection sort
    sorted_apps = []
    for bucket_key in sorted(buckets, reverse=reverse):
        sorted_bucket, _ = selection_sort(buckets[bucket_key], key, reverse)
        sorted_apps.extend(sorted_bucket)
    
    # Space complexity includes size of applications list and buckets dictionary
    space_complexity_bytes = sys.getsizeof(applications) + sys.getsizeof(buckets) + sum(sys.getsizeof(b) for b in buckets.values())
    return sorted_apps, space_complexity_bytes

def bucket_sort_with_shell(applications, key, reverse=False):
    # Creating buckets for the provided key
    buckets = {}
    for app in applications:
        bucket_key = app[key]
        if bucket_key not in buckets:
            buckets[bucket_key] = []
        buckets[bucket_key].append(app)
    
    # Sort each bucket using shell sort
    sorted_apps = []
    for bucket_key in sorted(buckets, reverse=reverse):
        sorted_bucket, _ = shell_sort(buckets[bucket_key], key, reverse)
        sorted_apps.extend(sorted_bucket)
    
    # Space complexity includes size of applications list and buckets dictionary
    space_complexity_bytes = sys.getsizeof(applications) + sys.getsizeof(buckets) + sum(sys.getsizeof(b) for b in buckets.values())
    return sorted_apps, space_complexity_bytes
