from inspect import signature
import time
from threading import Timer
import os
import functools

def filter_files(extensions_to_filter=[], filterDirectory=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            event_arg_name = 'event'  # Replace with the actual argument name
            event = bound_args.arguments.get(event_arg_name)
            if not filterDirectory and event.is_directory:
                return
            # Skip non-markdown files
            for extension in extensions_to_filter:
                isIn = False
                if event.src_path.lower().endswith(extension):
                    isIn = True
                if not isIn:
                    return

            func(*args, **kwargs)
            
        return wrapper
    return decorator


def debounce(wait):
    def decorator(fn):
        sig = signature(fn)
        caller = {}

        def debounced(*args, **kwargs):
            nonlocal caller

            try:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                called_args = fn.__name__ + str(dict(bound_args.arguments))
            except:
                called_args = ''

            t_ = time.time()

            def call_it(key):
                try:
                    # always remove on call
                    caller.pop(key)
                except:
                    pass

                fn(*args, **kwargs)

            try:
                # Always try to cancel timer
                caller[called_args].cancel()
            except:
                pass

            caller[called_args] = Timer(wait, call_it, [called_args])
            caller[called_args].start()

        return debounced

    return decorator

def log_time_elapsed(id, group):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            log_dir = ".log"
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, f"{id}.log")
            with open(file_path, "a") as log_file:
                log_file.write(f"{group} - {func.__name__} - {elapsed:.6f}s\n")
            return result
        return wrapper
    return decorator