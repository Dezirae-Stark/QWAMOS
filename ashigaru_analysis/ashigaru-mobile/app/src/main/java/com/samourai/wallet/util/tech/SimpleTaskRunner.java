package com.samourai.wallet.util.tech;

import android.os.Handler;
import android.os.Looper;

import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SimpleTaskRunner {

    private static final String TAG = SimpleTaskRunner.class.getSimpleName();
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());

    private SimpleTaskRunner() {}

    public static SimpleTaskRunner create() {
        return new SimpleTaskRunner();
    }

    public void executeAsyncAndShutdown(final Runnable runnable) {
        executor.execute(() -> {
            runnable.run();
            shutdown();
        });
    }

    public void executeAsync(final Runnable runnable) {
        executor.execute(runnable);
    }

    public <T> void executeAsync(
            final Callable<T> callable,
            final SimpleCallback<T> simpleCallback) {

        executeAsync(false, callable, simpleCallback);
    }

    public <T> void executeAsync(
            final boolean shutdownAfterComplete,
            final Callable<T> callable,
            final SimpleCallback<T> simpleCallback) {

        Objects.requireNonNull(callable);
        Objects.requireNonNull(simpleCallback);
        executor.submit(() -> {
            final T result;
            try {
                result = callable.call();
            } catch (final Exception e) {
                simpleCallback.onException(e);
                return;
            }
            handler.post(() -> {
                simpleCallback.onComplete(result);
                if (shutdownAfterComplete) {
                    shutdown();
                }
            });
        });
    }

    public void shutdown() {
        executor.shutdown();
    }

}
